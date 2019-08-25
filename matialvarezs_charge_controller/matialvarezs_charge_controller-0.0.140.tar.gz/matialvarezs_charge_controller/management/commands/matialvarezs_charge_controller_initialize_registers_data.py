from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from matialvarezs_charge_controller import utils as matialvarezs_charge_controller_utils
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass  # parser.add_argument('-f', '--foo')

    def handle(self, *args, **options):
        # foo = options["foo"]
        # charge_controller_utils.filter_registers_data().delete()
        # charge_controller_utils.create_registers_data(code='day_night', address='0x200C', count=1, unit=1,
        #                                               function_code=0x02,times=1)
        # charge_controller_utils.create_registers_data(code='temperature_inside_device', address='0x2000', count=1,
        #                                               unit=1, function_code=0x02,times=1)
        # charge_controller_utils.create_registers_data(code='pv_voltage_input', address='0x3100', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        #
        # charge_controller_utils.create_registers_data(code='pv_current_input', address='0x3101', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        #
        # charge_controller_utils.create_registers_data(code='pv_power_input', address='0x3102', count=2, unit=1,
        #                                               function_code=0x04,times=100)
        #
        # charge_controller_utils.create_registers_data(code='batery_voltage', address='0x331A', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='batery_current', address='0x331B', count=2, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='batery_current_charge', address='0x311A', count=1, unit=1,
        #                                               function_code=0x04,times=1)  # % de carga
        # charge_controller_utils.create_registers_data(code='batery_temperature', address='0x3110', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='load_voltage', address='0x310C', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='load_current', address='0x310D', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='load_power', address='0x310E', count=2, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='consumed_energy_today', address='0x3304', count=2, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='generated_energy_today', address='0x330C', count=2, unit=1,
        #                                               function_code=0x04,times=100)
        # charge_controller_utils.create_registers_data(code='device_temperature', address='0x3111', count=1, unit=1,
        #                                               function_code=0x04,times=100)
        matialvarezs_charge_controller_utils.filter_registers_data().delete()
        matialvarezs_charge_controller_utils.create_registers_data(code='day_night', address=0x200C, count=1, unit=1,
                                                                   function_code=0x02, times=1, bits=True)
        matialvarezs_charge_controller_utils.create_registers_data(code='temperature_inside_device', address=0x2000,
                                                                   count=1,
                                                                   unit=1, function_code=0x02, times=1, bits=True)
        matialvarezs_charge_controller_utils.create_registers_data(code='pv_voltage_input', address=0x3100, count=1,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)

        matialvarezs_charge_controller_utils.create_registers_data(code='pv_current_input', address=0x3101, count=1,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)

        matialvarezs_charge_controller_utils.create_registers_data(code='pv_power_input', address=0x3102, count=2,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)

        matialvarezs_charge_controller_utils.create_registers_data(code='batery_voltage', address=0x331A, count=1,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='batery_current', address=0x331B, count=2,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='batery_current_charge', address=0x311A,
                                                                   count=1, unit=1,
                                                                   function_code=0x04, times=1)  # % de carga
        matialvarezs_charge_controller_utils.create_registers_data(code='batery_temperature', address=0x3110, count=1,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='load_voltage', address=0x310C, count=1, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='load_current', address=0x310D, count=1, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='load_power', address=0x310E, count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='device_temperature', address=0x3111, count=1,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='consumed_energy_today', address=0x3304,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='consumed_energy_month', address=0x3306,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='consumed_energy_year', address=0x3308, count=2,
                                                                   unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='total_consumed_energy', address=0x330A,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='generated_energy_today', address=0x330C,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='generated_energy_month', address=0x330E,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='generated_energy_year', address=0x3310,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='total_generated_energy', address=0x3312,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
        matialvarezs_charge_controller_utils.create_registers_data(code='carbon_dioxide_reduction', address=0x3314,
                                                                   count=2, unit=1,
                                                                   function_code=0x04, times=100)
