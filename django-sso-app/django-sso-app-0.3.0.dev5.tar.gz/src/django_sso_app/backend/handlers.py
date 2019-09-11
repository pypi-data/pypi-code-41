import logging

import jwt
from allauth.account.signals import (email_added, password_reset)
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler as rest_framework_jwt_payload_handler

Users = get_user_model()
logger = logging.getLogger('backend')


def jwt_payload_handler(user, device=None):
    payload = rest_framework_jwt_payload_handler(user)
    if device is not None:
        # removing email from payload
        user_email = payload.pop('email', None)
        payload['user_id'] = str(user.sso_id)
        payload['rev'] = user.sso_rev
        payload['fp'] = device.fingerprint
        payload['iss'] = device.apigw_jwt_key

    return payload


def jwt_encode_handler(payload, device=None):
    if device is not None:
        key = device.apigw_jwt_secret
        return jwt.encode(
            payload,
            key,
            api_settings.JWT_ALGORITHM
        ).decode('utf-8')
    else:
        raise Exception('Encoding without device')
        # return rest_framework_jwt_encode_handler(payload)


def jwt_decode_handler(token, device=None):
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }

    if device is None:
        raise Exception('Decoding without device')

        # get user from token, BEFORE verification, to get user secret key

        unverified_payload = jwt.decode(token, None, False)
        secret_key = jwt_get_secret_key(unverified_payload)

        return jwt.decode(
            token,
            api_settings.JWT_PUBLIC_KEY or secret_key,
            api_settings.JWT_VERIFY,
            options=options,
            leeway=api_settings.JWT_LEEWAY,
            audience=api_settings.JWT_AUDIENCE,
            issuer=api_settings.JWT_ISSUER,
            algorithms=[api_settings.JWT_ALGORITHM]
        )


def jwt_encode(user, device=None):
    payload = jwt_payload_handler(user, device)

    return jwt_encode_handler(payload, device)


def login_handler(sender, user, request, **kwargs):
    if hasattr(request, 'data'):
        fingerprint = request.data.get('fingerprint')
        logger.info('User {0} logged in with fingerprint {1}'.format(user, fingerprint))


def email_added_handler(sender, request, email_address, **kwargs):
    logger.info('User {0} created unconfirmed email {1}'.format(request.user, email_address))


def password_reset_handler(sender, request, user, **kwargs):
    logger.info('User {0} resetted email'.format(user))


user_logged_in.connect(login_handler)
email_added.connect(email_added_handler)
password_reset.connect(password_reset_handler)
