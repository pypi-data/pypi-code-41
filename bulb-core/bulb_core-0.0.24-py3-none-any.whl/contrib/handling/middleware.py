from bulb.contrib.handling.node_models import WebsiteSettings
from django.shortcuts import render
from django.conf import settings


class HandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Call the view
        response = self.get_response(request)

        settings_object = WebsiteSettings.get()

        if settings_object:
            admin_base_path_name = settings.BULB_ADMIN_BASEPATH_NAME

            if settings_object.maintenance:
                if request.environ["PATH_INFO"].split("/")[1] != admin_base_path_name:
                    return render(request, "handling/pages/maintenance.html")

        return response
