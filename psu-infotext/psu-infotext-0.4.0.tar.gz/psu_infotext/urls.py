from django.urls import path
from . import views

urlpatterns = [
    # A simple test page
    path('', views.index, name='index'),
    path('update', views.update, name='update'),
]
