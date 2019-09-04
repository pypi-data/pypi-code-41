from matialvarezs_charge_controller import utils as matialvarezs_charge_controller_utils
from matialvarezs_charge_controller import settings
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
def send_local_data_to_server():
    data = matialvarezs_charge_controller_utils.filter_local_data_backup(send_to_server=True)
    for item in data:
        try:
            res = matialvarezs_request_handler_utils.send_post_and_get_response(
                headers=settings.SISNBYTED_REQUEST_HEADERS,
                url=settings.MATIALVAREZS_CHARGE_CONTROLLER_CREATE_DATA_CHARGE_CONTROLLER_URL, data=item.data,
                convert_data_to_json=True)
            print("RES REENVIAR DATOS A SERVIDOR: ", res)
            item.send_to_server = False
            item.save()
        except:
            continue
