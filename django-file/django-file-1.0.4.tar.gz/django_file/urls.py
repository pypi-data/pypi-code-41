# -*- coding: utf-8 -*-

from django.conf.urls import url
from django_file_download import views as file_download_views
from django_file_upload import views as file_upload_views


urlpatterns = [
    url(r'^upload$', file_upload_views.file_upload, name='file_upload'),
    url(r'^download$', file_download_views.file_download, name='file_download'),
]
