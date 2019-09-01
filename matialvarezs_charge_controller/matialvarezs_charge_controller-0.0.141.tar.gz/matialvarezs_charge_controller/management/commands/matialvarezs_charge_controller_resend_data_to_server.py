from django.core.management.base import BaseCommand, CommandError
from matialvarezs_charge_controller import resend_data_to_server
from matialvarezs_handlers_easy import utils as matialvarezs_handlers_easy_utils
from django.utils import timezone


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass  # parser.add_argument('-f', '--foo')

    def handle(self, *args, **options):
        # foo = options["foo"]
        print("REVISION DATOS GUARDADOS LOCALMENTE PARA ENVIAR AL SERVIDOR EL: ",
              matialvarezs_handlers_easy_utils.datetime_utc_to_localtime(timezone.now(), 'America/Santiago'))
        resend_data_to_server.send_local_data_to_server()
