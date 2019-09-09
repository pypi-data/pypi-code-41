from django.conf.urls import url, include
from . import settings
from . import views

app_name = "ohm2_pushes_light_api_v1"

urlpatterns = []

if settings.ONESIGNAL_ENABLED:
	urlpatterns += [
		url(r'^gateways/onesignal/register-device/android/$', views.gateways_onesignal_register_device_android, name = 'gateways_onesignal_register_device_android'),
		url(r'^gateways/onesignal/register-device/ios/$', views.gateways_onesignal_register_device_ios, name = 'gateways_onesignal_register_device_ios'),
	]

