from django.core.management.base import BaseCommand, CommandError
from matialvarezs_charge_controller import settings
from matialvarezs_handlers_easy import crontab_jobs_utils
class Command(BaseCommand):
    def add_arguments(self, parser):
        pass  # parser.add_argument('-f', '--foo')

    def handle(self, *args, **options):
        # foo = options["foo"]
        command = settings.SCRIPTS_PATH + 'charge_controller_send_data_to_server.sh >>' + settings.CRON_JOB_LOGS_PATH + 'charge_controller_send_data_to_server.log 2>&1'
        # comment = ''
        # if settings.PRODUCTION_CONFIG:
        #     comment = 'production_charge_controller_send_data_to_server'
        # else:
        comment = 'development_charge_controller_send_data_to_server'
        crontab_jobs_utils.create_cron_execute_between_x_minutes(minutes=15,command=command,comment=comment)