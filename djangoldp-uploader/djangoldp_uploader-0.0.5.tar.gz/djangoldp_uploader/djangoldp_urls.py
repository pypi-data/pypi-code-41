"""djangoldp uploader URL Configuration"""

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt

from djangoldp_uploader import views
from djangoldp_uploader.views import FileUploadView

urlpatterns = [
    url(r'^upload/$', csrf_exempt(FileUploadView.as_view()), name='upload'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^demo/$', views.home, name='home'),
        url(r'^demo/sib/$', views.demo_sib, name='upload_sib'),
        url(r'^demo/simple/$', views.upload_view, name='simple_upload'),
        url(r'^demo/form/$', views.model_form_upload, name='model_form_upload'),
    ]
