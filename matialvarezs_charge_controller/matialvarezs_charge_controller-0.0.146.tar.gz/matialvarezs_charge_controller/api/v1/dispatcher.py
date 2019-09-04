from .decorators import api_v1_safe_request
from ohm2_handlers_light import utils as h_utils
from django.contrib.auth.models import User
import binascii
from . import errors as api_v1_errors
from matialvarezs_handlers_easy import crontab_jobs_utils
from matialvarezs_charge_controller import settings as matialvarezs_charge_controller_settings


@api_v1_safe_request
def create_crontab_job_get_data_charge_controller(request, params):
    # p = h_utils.cleaned(params, (
    #     ("string", "minutes_frecuency", 0),
    # ))
    command = matialvarezs_charge_controller_settings.SCRIPTS_PATH + 'charge_controller_send_data_to_server.sh >>' + matialvarezs_charge_controller_settings.CRON_JOB_LOGS_PATH + 'charge_controller_send_data_to_server.log 2>&1'
    comment = ''
    if matialvarezs_charge_controller_settings.PRODUCTION_CONFIG:
        comment = 'production_charge_controller_send_data_to_server'
    else:
        comment = 'development_charge_controller_send_data_to_server'
    find = crontab_jobs_utils.find_job_by_comment(comment=comment)
    if find:
        crontab_jobs_utils.delete_cron(comment=comment)
    crontab_jobs_utils.create_cron_execute_between_x_minutes(minutes=params['minutes_frecuency'],command=command, comment=comment)

    ret = {
        "error": None,
        "ret": True,
    }
    return ret

