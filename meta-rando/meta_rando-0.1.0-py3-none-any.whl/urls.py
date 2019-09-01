from django.contrib import admin
from django.urls.conf import path
from django.views.generic.base import RedirectView

app_name = "meta_rando"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/meta_rando/admin/"), name="home_url"),
]
