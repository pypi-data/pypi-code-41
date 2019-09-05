from django.conf import settings

JWT_VERIFY_EXPIRATION = False
JWT_VERIFY = True
JWT_LEEWAY = 0
JWT_AUDIENCE = None
JWT_ISSUER = None
JWT_ALGORITHM = 'HS256'

JWT_AUTH = {
    'JWT_DECODE_HANDLER': 'auth_uuid.helper_jwt.jwt_decode_handler',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'auth_uuid.helper_jwt.jwt_get_username_from_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'auth_uuid.jwt_response_payload_handler.jwt_response_payload_handler',
    'JWT_PAYLOAD_HANDLER': 'auth_uuid.jwt_payload_handler.jwt_payload_handler',
    'JWT_SECRET_KEY': getattr(settings, 'JWT_SECRET_KEY', ''),
}

JWT_SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', '')
URL_VALIDATE_USER_UUID = getattr(settings, 'URL_VALIDATE_USER_UUID', '')

URL_VALIDATE_USER_COOKIE = getattr(settings, 'URL_VALIDATE_USER_COOKIE', '')

LOGGER_NAME = 'auth_uuid'

settings.JWT_AUTH = JWT_AUTH
