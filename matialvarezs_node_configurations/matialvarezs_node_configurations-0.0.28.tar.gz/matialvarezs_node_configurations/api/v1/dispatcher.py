from .decorators import api_v1_safe_request
from ohm2_handlers_light import utils as h_utils
from django.contrib.auth.models import User
import binascii
from . import errors as api_v1_errors
from matialvarezs_node_configurations import utils as matialvarezs_node_configuration_utils
from matialvarezs_node_accounts import utils as matialvarezs_node_accounts_utils


@api_v1_safe_request
def create_or_update(request, params):
    update_configuration = params.get('update_configuration',False)
    config = matialvarezs_node_configuration_utils.create_configuration(key=params['key'], value=params['value'],update_configuration=update_configuration)
    ret = {
        "error": None,
        "ret": True,
    }
    return ret


@api_v1_safe_request
def create_identity(request, params):
    config = matialvarezs_node_configuration_utils.create_configuration(key='identity', value=params['identity'])
    token_user_api = matialvarezs_node_accounts_utils.create_user_api_if_not_exist_and_return_token()
    ret = {
        "token_user_api": token_user_api.key
    }
    return ret
