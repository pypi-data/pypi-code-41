from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient


class EnrolmentAPIClient(AbstractAPIClient):

    endpoints = {
        'enrolment': '/enrolment/',
        'trusted-code': '/trusted-code/{code}/',
        'preverified': '/enrolment/preverified-company/{key}/',
        'preverified-claim': '/enrolment/preverified-company/{key}/claim/',

    }

    def send_form(self, form_data):
        return self.post(
            self.endpoints['enrolment'],
            data=form_data
        )

    def retrieve_prepeveried_company(self, key):
        url = self.endpoints['preverified'].format(key=key)
        return self.get(url, use_fallback_cache=True)

    def claim_prepeveried_company(self, sso_session_id, key, data):
        return self.post(
            url=self.endpoints['preverified-claim'].format(key=key),
            data=data,
            authenticator=SessionSSOAuthenticator(sso_session_id),
        )
