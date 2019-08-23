import uuid


def generate_uuid(as_string=False):
    _uuid = uuid.uuid4()
    return _uuid if not as_string else str(_uuid)
