import logging
try:
    from rest_framework.authtoken.models import Token
    token_auth = True
except:
    token_auth = False
# Get an instance of a logger
logger = logging.getLogger(__name__)


def default_auth(private_file):
    parent = private_file.parent_object
    if parent.published:
        return True
    user = private_file.request.user
    if not user.is_authenticated and token_auth:
        token_header = private_file.request.META.get(
            'HTTP_AUTHORIZATION', False)
        if token_header:
            token_string = token_header.split(' ')[-1].strip()
            try:
                token = Token.objects.get(key=token_string)
                user = token.user
            except:
                pass
    if not user.is_authenticated:
        return False
    if user == parent.owner:
        return True
    if parent.shared_with.filter(pk=user.pk).exists():
        return True
    if parent.collection:
        if parent.collection.owner == user:
            return True
        if parent.collection.shared_with.filter(pk=user.pk).exists():
            return True
    return False
