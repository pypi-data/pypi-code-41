from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns
from .provider import FragdenstaatProvider

urlpatterns = default_urlpatterns(FragdenstaatProvider)
