from . import settings
from .models import Configuration
import json
from matialvarezs_node_configurations import utils as matialvarezs_node_configurations_utils


def json_configurations():
    array = [
        # {
        #     'key':'node_type',
        #     'value':settings.NODE_TYPE
        # },
        # {
        #     'key': 'network_interface',
        #     'value': settings.NETWORK_INTERFACE
        # },
        {
            'key': 'current_irrigation_sector',
            'value': 0
        },
        {
            'key': 'master_val_status',
            'value': 'CLOSE'
        },
        {
            'key': 'keep_running_master_val',
            'value': True
        },
        {
            'key': 'bool_stop_irrigation_control_event',
            'value': False
        },
        {
            'key': 'reason_stop_irrigation_control_event',
            'value': ''
        },
        {
            'key': 'id_blocking_irrigation_equipment',
            'value': 0
        },
        {
            'key': 'number_of_irrigation_sector',
            'value': 0
        },
        {
            'key': 'number_of_irrigation_sector_with_dropper_spillage_measuring',
            'value': 0
        },
        {
            'key':'charge_controller_modbus_tcp',
            'value':''
        }

    ]
    return json.dumps(array)


def initialize():
    #config = Configuration.objects.all()
    #config.delete()
    data = json.loads(json_configurations())
    for item in data:
        matialvarezs_node_configurations_utils.create_configuration(key=item['key'], value=item['value'])
        # config = matialvarezs_node_configurations_utils .get_or_none_configuration(key=item['key'])
        # if config is None:
        #     config = Configuration(key=item['key'], value=item['value'])
        #     config.save()
