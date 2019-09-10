from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (passepartout_login_view, passepartout_logout_view)

urlpatterns = [

    url(r'^login/(?P<token>\w+)/$',
        passepartout_login_view,
        name='passepartout_login'),
    
    url(r'^logout/(?P<device_id>\d+)/$',
        passepartout_logout_view,
        name='passepartout_logout')
]

urlpatterns = format_suffix_patterns(urlpatterns)
