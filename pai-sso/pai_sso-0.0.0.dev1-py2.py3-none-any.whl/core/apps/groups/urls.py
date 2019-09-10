from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import GroupViewSet


urlpatterns = [
    url(r'^$', GroupViewSet.as_view({'get': 'list'}), name="list"),
    url(r'^(?P<pk>\w+)/$', GroupViewSet.as_view({'get': 'retrieve'}), name="detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
