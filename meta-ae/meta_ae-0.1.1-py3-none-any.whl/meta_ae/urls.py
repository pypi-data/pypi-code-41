from django.urls.conf import path

# from meta_dashboard.views import AeHomeView

from .admin_site import meta_ae_admin

app_name = "meta_ae"

urlpatterns = [
    path("admin/", meta_ae_admin.urls),
    # path("", AeHomeView.as_view(), name="home_url"),
]
