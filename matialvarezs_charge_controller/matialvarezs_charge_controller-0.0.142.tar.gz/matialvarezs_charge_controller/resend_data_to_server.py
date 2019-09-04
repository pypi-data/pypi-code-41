from matialvarezs_charge_controller import utils as matialvarezs_charge_controller_utils
from matialvarezs_charge_controller import settings

def send_local_data_to_server():
    data = matialvarezs_charge_controller_utils.filter_local_data_backup(send_to_server=True)
    for item in data:
        res = send_requests.send_request(settings.MATIALVAREZS_CHARGE_CONTROLLER_CREATE_DATA_CHARGE_CONTROLLER_URL, data=item.data)
        if res['ret']:
            item.send_to_server = False
            item.save()
