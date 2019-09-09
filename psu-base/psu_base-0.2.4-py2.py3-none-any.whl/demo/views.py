from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from psu_base.classes.Log import Log
from psu_base.services import utility_service
from psu_base.services import message_service
log = Log()


def index(request):
    """
    A landing page
    """
    log.trace()

    log.end()
    return render(
        request, 'landing.html',
    )


def alert_message(request):
    log.trace()
    alert = "alerts sent"
    msg = request.POST.get('msg')

    message_service.post_info(msg)
    message_service.post_success(msg)
    message_service.post_warning(msg)
    message_service.post_error(msg)

    log.end()
    return HttpResponse(alert)
