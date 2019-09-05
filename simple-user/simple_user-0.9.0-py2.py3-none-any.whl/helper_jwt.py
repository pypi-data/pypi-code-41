from auth_uuid import settings
import jwt


def jwt_get_username_from_payload_handler(payload):
    return payload.get('uuid')


def jwt_decode_handler(token):
    options = {
        'verify_exp': settings.JWT_VERIFY_EXPIRATION,
    }

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_VERIFY,
        options=options,
        leeway=settings.JWT_LEEWAY,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=[settings.JWT_ALGORITHM]
    )
