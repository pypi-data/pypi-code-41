from datetime import datetime


def jwt_payload_handler(user):
    return {
        'user_id': user.id,
        'uuid': str(user.uuid),
        'exp': datetime(2100, 1, 1),
    }
