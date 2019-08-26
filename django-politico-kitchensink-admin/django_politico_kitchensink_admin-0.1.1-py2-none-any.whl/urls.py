from django.urls import path

from .views import Home, PublishArchieDoc, PublishSheet

urlpatterns = [
    path("", Home.as_view(), name="kitchensink-home"),
    path(
        "publish/sheet/<str:pk>/",
        PublishSheet.as_view(),
        name="kitchensink-publish-sheet",
    ),
    path(
        "publish/archie-doc/<str:pk>/",
        PublishArchieDoc.as_view(),
        name="kitchensink-publish-archie-doc",
    ),
]
