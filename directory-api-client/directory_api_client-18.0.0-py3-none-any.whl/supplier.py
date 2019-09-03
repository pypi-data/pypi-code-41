from directory_client_core.authentication import SessionSSOAuthenticator
from directory_api_client.base import AbstractAPIClient


url_supplier = '/supplier/'
url_unsubscribe = '/supplier/unsubscribe/'
url_csv_dump = '/supplier/csv-dump/'
url_disconnect_from_company = '/supplier/company/disconnect/'
url_supplier_sso_ids = '/external/supplier-sso/'


class SupplierAPIClient(AbstractAPIClient):

    authenticator = SessionSSOAuthenticator

    def profile_update(self, sso_session_id, data):
        return self.patch(url=url_supplier, data=data, authenticator=self.authenticator(sso_session_id))

    def retrieve_profile(self, sso_session_id):
        return self.get(url=url_supplier, authenticator=self.authenticator(sso_session_id))

    def unsubscribe(self, sso_session_id):
        return self.post(url=url_unsubscribe, authenticator=self.authenticator(sso_session_id))

    def get_csv_dump(self, token):
        return self.get(url=url_csv_dump, params={'token': token}, use_fallback_cache=True)

    def disconnect_from_company(self, sso_session_id):
        return self.post(url=url_disconnect_from_company, authenticator=self.authenticator(sso_session_id))

    def list_sso_ids(self):
        return self.get(url=url_supplier_sso_ids, use_fallback_cache=True)
