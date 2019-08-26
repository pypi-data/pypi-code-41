from django.conf.urls import url
from drf_docs.views import DRFDocsView

urlpatterns = [
    # Url to view the API Docs
    url(r'^$', DRFDocsView.as_view(), name='drfdocs'),
]
