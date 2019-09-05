from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, path, re_path as url
else:
	from django.conf.urls import include, url

app_name = "matialvarezs_node_configurations_api"

if DJANGO_VERSION >= (2, 0):
	urlpatterns = [
		path('v1/', include('matialvarezs_node_configurations.api.v1.urls', namespace='v1')),
	]
else:
	urlpatterns = [
		url('v1/', include('matialvarezs_node_configurations.api.v1.urls', namespace='v1')),
	]
