from django.core.management.base import BaseCommand, CommandError
from charge_controller import settings
from manage_crontab_jobs import manage_crons


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass  # parser.add_argument('-f', '--foo')

    def handle(self, *args, **options):
        # foo = options["foo"]
        command = settings.SCRIPTS_PATH + 'charge_controller_resend_data_to_server.sh >>' + settings.CRON_JOB_LOGS_PATH + 'charge_controller_resend_data_to_server.log 2>&1'
        comment = ''
        if settings.PRODUCTION_CONFIG:
            comment = 'production_charge_controller_resend_data_to_server'
        else:
            comment = 'development_charge_controller_resend_data_to_server'
        manage_crons.create_cron_execute_by_x_hours(hours=1, command=command, comment=comment)
