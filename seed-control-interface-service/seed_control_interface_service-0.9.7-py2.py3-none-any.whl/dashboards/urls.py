from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'dashboard', views.DashboardViewSet)
router.register(r'userdashboard', views.UserDashboardViewSet)
router.register(r'definition', views.DefinitionViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
]
