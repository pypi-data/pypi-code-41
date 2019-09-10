from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProfileViewSet

urlpatterns = [
    url(r'^$', ProfileViewSet.as_view({'get': 'list'}), name="list"),
    url(r'^(?P<sso_id>[-\w]+)/$', ProfileViewSet.as_view({'get': 'retrieve'}), name="detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
