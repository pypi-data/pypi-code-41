from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ServiceApiViewSet


urlpatterns = [

    url(r'^$',
        ServiceApiViewSet.as_view({'get': 'list'}),
        name='services_list'),

    url(r'^(?P<pk>\d+)/$',
        ServiceApiViewSet.as_view({'get': 'retrieve'}),
        name='services_detail'),

    url(r'^(?P<pk>\d+)/subscribe/$',
        ServiceApiViewSet.as_view({'post': 'subscribe'}),
        name='services_subscription'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
