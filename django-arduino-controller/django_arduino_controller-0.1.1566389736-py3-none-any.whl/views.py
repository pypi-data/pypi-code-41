from django.apps import apps
from django.http import HttpResponseBadRequest
from django.shortcuts import render


# Create your views here.


def index(request):
    sr = apps.get_app_config("django_arduino_controller").serial_reader
    if sr is None:
        return HttpResponseBadRequest(content="Serial Reader not running")
    return render(request, "django_arduino_controller_index.html")


def logger(request):
    sr = apps.get_app_config("django_arduino_controller").serial_reader
    if sr is None:
        return HttpResponseBadRequest(content="Serial Reader not running")
    return render(request, "django_arduino_controller_logger.html")
