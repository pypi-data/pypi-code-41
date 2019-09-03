from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'service', views.ServiceViewSet)
router.register(r'status', views.StatusViewSet)
router.register(r'webhook', views.HookViewSet)
router.register(r'userservicetoken', views.UserServiceTokenViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^api/v1/userservicetoken/generate/$',
        views.UserServiceTokenTriggerView.as_view(),
        name='generate-user-tokens'),
    url(r'^api/v1/', include(router.urls)),
]
