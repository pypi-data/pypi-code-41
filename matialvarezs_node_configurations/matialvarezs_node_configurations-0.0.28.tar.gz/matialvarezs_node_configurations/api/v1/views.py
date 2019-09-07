from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ohm2_handlers_light.parsers import get_as_or_get_default
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import dispatcher

@api_view(['POST'])
def create_or_update(request):
    keys = (
        ("key","key",0),
        ("value", "value", 0),
    )
    print("request.data create_or_update: ", request.data)
    res, error = dispatcher.create_or_update(request, get_as_or_get_default(request.data, keys))
    if error:
        print("ERROR ORIGINAL create_or_update ", error.original)
        return JsonResponse({"error": error.regroup()})
    return JsonResponse(res)


@api_view(['POST'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
#@csrf_exempt
def create_identity(request):
    keys = (
        ("identity","identity",0),
    )
    print("request.data create_or_update_identity: ", request.data)
    res, error = dispatcher.create_identity(request, get_as_or_get_default(request.data, keys))
    if error:
        print("ERROR ORIGINAL create_identity ", error.original)
        return JsonResponse({"error": error.regroup()})
    return JsonResponse(res)

