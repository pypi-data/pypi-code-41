import datetime
import logging

import jwt
from django.conf import settings

from .handlers import jwt_encode

logger = logging.getLogger('backend')

def set_cookie(response, key, value, days_expire = 7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60 
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    response.set_cookie(key, value, max_age=None, expires=expires, path='/', domain=settings.COOKIE_DOMAIN, secure=None, httponly=False)

def invalidate_cookie(response):
    response.set_cookie('jwt', None, max_age=None, expires='Thu, 01 Jan 1970 00:00:01 GMT', path='/', domain=settings.COOKIE_DOMAIN, secure=None, httponly=False)

def get_request_jwt(request):
    jwt_header = request.META.get('HTTP_AUTHORIZATION', None)
    if jwt_header is not None:
        jwt_header = jwt_header.replace('Bearer ', '')
        
    return request.COOKIES.get('jwt', jwt_header)

def update_response_jwt(received_jwt, jwt_user, request, response):
    unverified_payload = jwt.decode(received_jwt, None, False)
    jwt_fingerprint = unverified_payload['fp']

    logger.info('Updating response JWT for User {0} with fingerprint {1}'.format(request.user, jwt_fingerprint))

    # creates new actual_device
    actual_device = jwt_user.add_user_device(jwt_fingerprint)
    
    token = jwt_encode(jwt_user, actual_device)
    #max_age = 365 * 24 * 60 * 60  #one year
    #expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")

    set_cookie(response, 'jwt', token, None)
