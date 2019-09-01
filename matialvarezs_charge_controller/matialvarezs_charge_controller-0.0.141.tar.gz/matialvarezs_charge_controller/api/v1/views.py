from django.http import JsonResponse
from ohm2_handlers_light.parsers import get_as_or_get_default
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import dispatcher


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def create_crontab_job_get_data_charge_controller(request):
    keys = (
        ("minutes_frecuency","minutes_frecuency",0),
    )
    print("request.data create_crontab_job_get_data_charge_controller: ", request.data)
    res, error = dispatcher.create_crontab_job_get_data_charge_controller(request, get_as_or_get_default(request.data, keys))
    if error:
        print("ERROR ORIGINAL create_crontab_job_get_data_charge_controller ", error.original)
        return JsonResponse({"error": error.regroup()})
    return JsonResponse(res)
