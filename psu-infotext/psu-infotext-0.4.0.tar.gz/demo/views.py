from django.shortcuts import render
from psu_base.classes.Log import Log
log = Log()


def index(request):
    """
    A landing page
    """
    log.trace()

    log.end()
    return render(
        request, 'landing.html', {}
    )
