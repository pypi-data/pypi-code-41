import os
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls

admin.site.site_header = os.environ.get('SEED_CONTROL_INTERFACE_SERVICE_TITLE',
                                        'Seed Control Interface Service Admin')


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token-auth/', obtain_auth_token),
    url(r'^docs/', include_docs_urls("Seed Control Interface Service")),
    url(r'^', include('services.urls')),
    url(r'^', include('dashboards.urls')),
    url(r'^', include('audit.urls')),
]
