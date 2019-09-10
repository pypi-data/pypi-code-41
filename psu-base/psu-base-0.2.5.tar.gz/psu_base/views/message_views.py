# message_views.py
#
#   These are views that are used for sending messages to the user
#

from django.shortcuts import render
from psu_base.classes.Log import Log

log = Log()


def messages(request):

    return render(
        request, 'template_components/messages.html', {}
    )
