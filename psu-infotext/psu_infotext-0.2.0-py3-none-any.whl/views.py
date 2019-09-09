from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from psu_infotext.models import Infotext
from psu_base.classes.Log import Log
from psu_base.services import utility_service
log = Log()

# ToDo: Permission Checking
# ToDo: Error Handling/Messages


def index(request):
    """
    Search page for locating infotext to be edited
    """
    log.trace('infotext/index')
    text_instances = Infotext.objects.filter(app_code=utility_service.get_app_code())
    log.end('infotext/index')
    return render(
        request, 'index.html',
        {'text_instances': text_instances}
    )


@csrf_exempt
def update(request):
    """
    Update a given infotext instance
    """
    log.trace('infotext/update', request.POST)

    text_instance = Infotext.objects.get(pk=request.POST['id'])
    if text_instance:
        text_instance.set_content(request.POST['content'])

    log.end('infotext/update', text_instance.content)
    return HttpResponse(text_instance.content)

