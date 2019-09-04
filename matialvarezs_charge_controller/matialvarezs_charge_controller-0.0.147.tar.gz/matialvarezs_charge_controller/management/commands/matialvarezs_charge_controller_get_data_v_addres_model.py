from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from matialvarezs_charge_controller import utils as matialvarezs_charge_controller_utils, settings
import os, simplejson as json
from django.utils import timezone
from matialvarezs_charge_controller.github import registers, client
from matialvarezs_request_handler import utils as matialvarezs_request_handler_utils
from matialvarezs_node_configurations import utils as matialvarezs_node_configurations_utils


class Command(BaseCommand):
    def add_arguments(seTlf, parser):
        pass  # parser.add_argument('-f', '--foo')

    def get_data(self):
        try:
            commands = matialvarezs_charge_controller_utils.filter_registers_data()
            clc = client.EPsolarTracerClient()
            clc.connect()
            data = {
                'datetime': str(timezone.now()),
                'node_identity': matialvarezs_node_configurations_utils.get_identity()
            }
            print("DATA ANTES DE PROCESAR", data)
            for item in commands:

                # reg = registers.Register(name='', address=int(item.address, 16), description='', unit=item.unit,
                #                          times=item.times)
                # print("item.is_coil(),item.is_discrete_input(),item.is_input_register(),item.is_holding_register()",item.is_coil(),item.is_discrete_input(),item.is_input_register(),item.is_holding_register())
                print(item.code, ' - ', int(item.address), '- ', clc.read_input(item).value, ' - ', item.bits)
                if item.code == "batery_current_charge":
                    data[item.code] = int(clc.read_input(item).value)
                else:
                    data[item.code] = float(clc.read_input(item).value)
            return data
        except:
            return None

    def send_data(self, data):
        try:
            res = matialvarezs_request_handler_utils.send_post_and_get_response(
                headers=settings.SISNBYTED_REQUEST_HEADERS,
                url=settings.MATIALVAREZS_CHARGE_CONTROLLER_CREATE_DATA_CHARGE_CONTROLLER_URL, data=data,
                convert_data_to_json=True)
            print("RES ENVIAR DATOS A SERVIDOR: ",res)
            # if json.loads(res)['error'] and json.loads(res)['error'] is not None:
            #     matialvarezs_charge_controller_utils.create_local_data_backup(data=data, send_to_server=True)
            # print("RES ALMACENAMIENTO EN SERVIDOR AWS: ", res)
        except Exception as e:
            print("ERROR AL OBTENER DATOS CONTROLADOR DE CARGA: ", str(timezone.now()), e)
            matialvarezs_charge_controller_utils.create_local_data_backup(data=data, send_to_server=True)

    def handle(self, *args, **options):
        # foo = options["foo"]
        # commands = matialvarezs_charge_controller_utils.filter_registers_data()
        # clc = client.EPsolarTracerClient()
        # clc.connect()
        # data = {
        #     'datetime': str(timezone.now()),
        #     'node_identity': matialvarezs_node_configurations_utils.get_identity()
        # }
        # print("DATA ANTES DE PROCESAR", data)
        # for item in commands:
        #
        #     # reg = registers.Register(name='', address=int(item.address, 16), description='', unit=item.unit,
        #     #                          times=item.times)
        #     # print("item.is_coil(),item.is_discrete_input(),item.is_input_register(),item.is_holding_register()",item.is_coil(),item.is_discrete_input(),item.is_input_register(),item.is_holding_register())
        #     print(item.code, ' - ', int(item.address), '- ', clc.read_input(item).value, ' - ', item.bits)
        #     if item.code == "batery_current_charge":
        #         data[item.code] = int(clc.read_input(item).value)
        #     else:
        #         data[item.code] = float(clc.read_input(item).value)
        data = self.get_data()
        if data:
            self.send_data(data)
