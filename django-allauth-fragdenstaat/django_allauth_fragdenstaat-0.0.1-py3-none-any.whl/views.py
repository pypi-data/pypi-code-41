import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import FragdenstaatProvider


class FragdenstaatOAuth2Adapter(OAuth2Adapter):
    provider_id = FragdenstaatProvider.id
    access_token_url = 'https://fragdenstaat.de/account/token/'
    authorize_url = 'https://fragdenstaat.de/account/authorize/'
    profile_url = 'https://fragdenstaat.de/api/v1/user/'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FragdenstaatOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FragdenstaatOAuth2Adapter)
