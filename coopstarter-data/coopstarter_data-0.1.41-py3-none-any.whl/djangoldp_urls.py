"""djangoldp project URL Configuration"""
from django.conf.urls import url
from .views import PendingResourcesViewSet

urlpatterns = [
    url(r'^resources/pending/', PendingResourcesViewSet.urls(model_prefix="resources-pending")),
]