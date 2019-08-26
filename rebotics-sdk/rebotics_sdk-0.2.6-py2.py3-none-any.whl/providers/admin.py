from rebotics_sdk.providers.utils import is_valid_url
from .base import ReboticsBaseProvider, remote_service, ProviderHTTPClientException


class AdminProvider(ReboticsBaseProvider):
    @remote_service('/admin/', json=False)
    def admin_ping(self, **kwargs):
        return self.session.get()

    @remote_service('/nn_models/tf/models/')
    def get_retailer_tf_models(self):
        return self.session.get()

    @remote_service('/retailers/host/')
    def get_retailer(self, retailer_codename):
        response = self.session.post(data={
            'company': retailer_codename
        })
        return response

    def get_retailer_host(self, retailer_codename):
        return self.get_retailer(retailer_codename)['host']

    @remote_service('/retailers/')
    def get_retailer_list(self):
        return self.session.get()

    @remote_service('/retailers/host/{codename}/')
    def update_host(self, codename, host):
        if not is_valid_url(host):
            raise ProviderHTTPClientException('%s is not a valid url' % host, host=host)
        return self.session.patch(codename=codename, data={
            'host': host
        })

    def set_retailer_identifier(self, retailer_id, retailer_secret_key):
        self.headers['x-retailer-id'] = retailer_id
        self.headers['x-retailer-secret-key'] = retailer_secret_key

    @remote_service('/api/token-auth/')
    def token_auth(self, username, password):
        json_data = self.session.post(data={
            'username': username,
            'password': password
        })
        self.set_token(json_data['token'])
        return json_data
