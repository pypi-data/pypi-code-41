from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, path, re_path as url
else:
	from django.conf.urls import include, url

from . import views

app_name = "matialvarezs_charge_controller"
if DJANGO_VERSION >= (2, 0):
	urlpatterns = [
		#path(r'^matialvarezs_charge_controller/$', views.index, name = 'index'),
		path('api/', include('matialvarezs_charge_controller.api.urls', namespace='api')),
	]
else:
	urlpatterns = [
		url(r'^matialvarezs_charge_controller/$', views.index, name='index'),
		url('api/', include('matialvarezs_charge_controller.api.urls', namespace='api')),
	]

