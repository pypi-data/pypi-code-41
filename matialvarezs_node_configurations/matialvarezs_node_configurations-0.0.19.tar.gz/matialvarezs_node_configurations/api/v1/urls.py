from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, path, re_path as url
else:
	from django.conf.urls import include, url

from . import views

app_name = "matialvarezs_node_configurations_api_v1"
if DJANGO_VERSION >= (2, 0):
	urlpatterns = [
		path('create_identity/', views.create_identity, name='create_identity'),
		path('create_or_update/', views.create_or_update, name='create_or_update'),

	]
else:
	urlpatterns = [
		url('create_identity/', views.create_identity, name='create_identity'),
		url('create_or_update/', views.create_or_update, name='create_or_update'),

	]
