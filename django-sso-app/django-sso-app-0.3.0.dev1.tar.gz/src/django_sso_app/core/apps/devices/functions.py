import logging

import jwt

from .models import Device

from ...backend.functions import get_request_jwt

logger = logging.getLogger('devices')


def delete_request_device(request):
    removing_device = get_request_device(request)
    if removing_device is not None:
        logger.info('Removing logged out user device {0} for User {1}'.format(removing_device, request.user))
        request.user.remove_user_device(removing_device)
    else:
        logger.warning('User {0} is logging out WITHOUT removing device.'.format(request.user))


def get_request_device(request):
    received_jwt = get_request_jwt_fingerprint(request)
    return Device.objects.filter(fingerprint=received_jwt).first()


def get_request_jwt_fingerprint(request):
    received_jwt = get_request_jwt(request)
    if received_jwt is None:
        raise KeyError('No token specified')

    unverified_payload = jwt.decode(received_jwt, None, False)
    return unverified_payload.get('fp')
