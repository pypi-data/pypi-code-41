"""
WSGI config for django_arduino_controller project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from plug_in_django.plug_in_django.settings import DEBUG

websocket_urlpatterns = []

if len(__name__.split(".")) == 2:
    from templatetags.installed_apps import get_apps
    from .manage import logger
else:
    from ..templatetags.installed_apps import get_apps
    from ..manage import logger

import importlib

for app in get_apps():
    try:
        if hasattr(app, "baseurl"):
            routing = importlib.import_module(app.module_path + ".routing")
            prefix = app.baseurl + "/"
            if len(prefix) == 1:
                prefix = ""
            # for pattern in routing.urlpatterns:
            #    print(pattern.pattern)
            ws_paths = []
            for pattern in routing.urlpatterns:
                old_route = pattern["route"]
                pattern["route"] = prefix + old_route
                ws_paths.append(path(**pattern))
                pattern["route"] = old_route

            websocket_urlpatterns = [
                pattern for pattern in ws_paths
            ] + websocket_urlpatterns

    except ModuleNotFoundError as e:
        if DEBUG:
            logger.exception(e)
    except Exception as e:
        logger.exception(e)


application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    }
)
