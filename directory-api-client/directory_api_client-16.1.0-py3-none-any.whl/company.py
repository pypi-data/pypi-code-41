from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient


class CompanyAPIClient(AbstractAPIClient):

    endpoints = {
        'profile': '/supplier/company/',
        'case-study-detail': '/supplier/company/case-study/{id}/',
        'case-study-list': '/supplier/company/case-study/',
        'validate-company-number': '/validate/company-number/',
        'verify': '/supplier/company/verify/',
        'verify-companies-house': '/supplier/company/verify/companies-house/',
        'verify-identity-request': 'supplier/company/verify/identity/',
        'public-case-study-detail': '/public/case-study/{id}/',
        'public-profile-detail': '/public/company/{number}/',
        'search-companies': '/company/search/',
        'search-investment-support-directories': (
            '/investment-support-directory/search/'
        ),
        'search-case-studies': '/case-study/search/',
        'transfer-invite': '/supplier/company/transfer-ownership-invite/',
        'transfer-invite-detail': (
            '/supplier/company/transfer-ownership-invite/{invite_key}/'
        ),
        'collaboration-invite': '/supplier/company/collaboration-invite/',
        'collaboration-invite-detail': (
            '/supplier/company/collaboration-invite/{invite_key}/'
        ),
        'remove-collaborators': '/supplier/company/remove-collaborators/',
        'collaborators': '/supplier/company/collaborators/',
        'request-collaboration': '/supplier/company/collaborator-request/',
        'add-company-collaborator': (
            '/supplier/company/add-collaborator/'
        ),
    }
    authenticator = SessionSSOAuthenticator

    def update_profile(self, sso_session_id, data):
        files = {}
        if 'logo' in data:
            files['logo'] = data.pop('logo')
        return self.patch(
            url=self.endpoints['profile'],
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_private_profile(self, sso_session_id):
        return self.get(
            url=self.endpoints['profile'],
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_public_profile(self, number):
        return self.get(
            url=self.endpoints['public-profile-detail'].format(number=number),
            use_fallback_cache=True,
        )

    def validate_company_number(self, number):
        return self.get(
            url=self.endpoints['validate-company-number'],
            params={'number': number},
        )

    def create_case_study(self, data, sso_session_id):
        files = {}
        for field in ['image_one', 'image_two', 'image_three', 'video_one']:
            if data.get(field):
                files[field] = data.pop(field)
        return self.post(
            url=self.endpoints['case-study-list'],
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def update_case_study(self, data, sso_session_id, case_study_id):
        files = {}
        for field in ['image_one', 'image_two', 'image_three', 'video_one']:
            if data.get(field):
                files[field] = data.pop(field)
        return self.patch(
            url=self.endpoints['case-study-detail'].format(id=case_study_id),
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def delete_case_study(self, sso_session_id, case_study_id):
        return self.delete(
            url=self.endpoints['case-study-detail'].format(id=case_study_id),
            authenticator=self.authenticator(sso_session_id)
        )

    def retrieve_private_case_study(self, sso_session_id, case_study_id):
        return self.get(
            url=self.endpoints['case-study-detail'].format(id=case_study_id),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def retrieve_public_case_study(self, case_study_id):
        return self.get(
            url=self.endpoints['public-case-study-detail'].format(id=case_study_id),
            use_fallback_cache=True
        )

    def verify_with_code(self, sso_session_id, code):
        return self.post(
            url=self.endpoints['verify'],
            data={'code': code},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_with_companies_house(self, sso_session_id, access_token):
        return self.post(
            url=self.endpoints['verify-companies-house'],
            data={'access_token': access_token},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_identity_request(self, sso_session_id):
        return self.post(
            url=self.endpoints['verify-identity-request'],
            authenticator=self.authenticator(sso_session_id),
        )

    def search_find_a_supplier(self, **kwargs):
        return self.get(
            url=self.endpoints['search-companies'],
            params=kwargs,
            use_fallback_cache=True,
        )

    def search_investment_search_directory(self, **kwargs):
        return self.get(
            url=self.endpoints['search-investment-support-directories'],
            params=kwargs,
            use_fallback_cache=True,
        )

    def create_transfer_invite(self, sso_session_id, new_owner_email):
        return self.post(
            url=self.endpoints['transfer-invite'],
            data={'new_owner_email': new_owner_email},
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_transfer_invite(self, sso_session_id, invite_key):
        return self.get(
            url=self.endpoints['transfer-invite-detail'].format(invite_key=invite_key),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def accept_transfer_invite(self, sso_session_id, invite_key):
        return self.patch(
            url=self.endpoints['transfer-invite-detail'].format(invite_key=invite_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def create_collaboration_invite(self, sso_session_id, collaborator_email):
        return self.post(
            url=self.endpoints['collaboration-invite'],
            data={'collaborator_email': collaborator_email},
            authenticator=self.authenticator(sso_session_id))

    def retrieve_collaboration_invite(self, sso_session_id, invite_key):
        return self.get(
            url=self.endpoints['collaboration-invite-detail'].format(invite_key=invite_key),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def accept_collaboration_invite(self, sso_session_id, invite_key):
        return self.patch(
            url=self.endpoints['collaboration-invite-detail'].format(invite_key=invite_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def remove_collaborators(self, sso_session_id, sso_ids):
        return self.post(
            url=self.endpoints['remove-collaborators'],
            data={'sso_ids': sso_ids},
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_collaborators(self, sso_session_id):
        return self.get(
            url=self.endpoints['collaborators'],
            authenticator=self.authenticator(sso_session_id)
        )

    def request_collaboration(self, company_number, collaborator_email):
        return self.post(
            url=self.endpoints['request-collaboration'],
            data={
                'company_number': company_number,
                'collaborator_email': collaborator_email
            },
        )

    def add_collaborator(self, data):
        return self.post(
            self.endpoints['add-company-collaborator'],
            data=data
        )
