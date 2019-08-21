"""django_arduino_controller URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from plug_in_django.plug_in_django.settings import CONFIG

if len(__name__.split(".")) == 2:
    from templatetags.installed_apps import get_apps
    from .manage import logger
else:
    from ..templatetags.installed_apps import get_apps
    from ..manage import logger

urlpatterns = []

for app in get_apps():
    apps = CONFIG.get("django_settings", "apps", "additional", default={})
    try:
        if hasattr(app, "baseurl"):
            if app.name in apps:
                app.baseurl = apps[app.name].get(
                    "baseurl", getattr(app, "baseurl", app.name)
                )
                app.data_dir = apps[app.name].get(
                    "data_dir", getattr(app, "data_dir", False)
                )

            if app.data_dir is True:
                app.data_dir = os.path.join(
                    os.path.dirname(CONFIG.get("django_settings", "BASE_DIR")),
                    "{}_data".format(app.name),
                )
            if app.data_dir:
                app.data_dir_url = (
                    "/"
                    + app.baseurl
                    + ("/" if len(app.baseurl) > 0 else "")
                    + "{}_data".format(app.name)
                )
                urlpatterns.extend(static(app.data_dir_url, document_root=app.data_dir))

            urlpatterns.insert(
                0,
                path(
                    app.baseurl + ("/" if len(app.baseurl) > 0 else ""),
                    include(
                        ("%s.urls" % app.module_path, app.label), namespace=app.label
                    ),
                ),
            )
        logger.info("load app: " + app.label)

    except ModuleNotFoundError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)

urlpatterns.extend(
    [
        path("admin/", admin.site.urls),
        path("", TemplateView.as_view(template_name="plug_in_django_index.html")),
        path(
            "accounts/",
            include(("django.contrib.auth.urls", "auth"), namespace="accounts"),
        ),
    ]
)
# print(urlpatterns)
