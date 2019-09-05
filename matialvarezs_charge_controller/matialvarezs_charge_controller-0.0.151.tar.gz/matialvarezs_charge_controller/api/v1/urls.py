from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION >= (2, 0):
	from django.urls import include, path, re_path as url
else:
	from django.conf.urls import include, url

from . import views


app_name = "matialvarezs_charge_controller_api_v1"

urlpatterns = [
    url('create_crontab_job_get_data_charge_controller/', views.create_crontab_job_get_data_charge_controller,
         name='create_crontab_job_get_data_charge_controller'),
    # path('update_get_data_minutes_frecuency/', views.update_get_data_minutes_frecuency,
    #      name='update_get_data_minutes_frecuency'),
]
