from django.urls import path
from . import views


urlpatterns = [
    path('ping', views.ping),
    path('timestamp', views.timestamp),
    path('echo', views.echo),
    path('getBooleanResult', views.getBooleanResult),
    path('getIntegerResult', views.getIntegerResult),
    path('getBytesResult', views.getBytesResult),
]
