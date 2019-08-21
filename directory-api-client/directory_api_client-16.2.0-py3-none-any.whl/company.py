from directory_client_core.authentication import SessionSSOAuthenticator

from directory_api_client.base import AbstractAPIClient


url_profile = '/supplier/company/'
url_case_study_detail = '/supplier/company/case-study/{id}/'
url_case_study_published_detail = '/public/case-study/{id}/'
url_case_study_create = '/supplier/company/case-study/'
url_validate_company_number = '/validate/company-number/'
url_verify_with_code = '/supplier/company/verify/'
url_verify_with_companies_house = '/supplier/company/verify/companies-house/'
url_verify_with_identity_request = 'supplier/company/verify/identity/'
url_published_profile_detail = '/public/company/{number}/'
url_search_find_a_supplier = '/company/search/'
url_search_investment_support_directory = '/investment-support-directory/search/'
url_transfer_invite_create = '/supplier/company/transfer-ownership-invite/'
url_transfer_invite_detail = '/supplier/company/transfer-ownership-invite/{invite_key}/'
url_collaborator_invite_create = '/supplier/company/collaboration-invite/'
url_collaborator_invite_detail = '/supplier/company/collaboration-invite/{invite_key}/'
url_collaborator_list = '/supplier/company/collaborators/'
url_collaborator_request = '/supplier/company/collaborator-request/'
url_collaborator_add = '/supplier/company/add-collaborator/'
url_collaborator_remove = '/supplier/company/remove-collaborators/'


class CompanyAPIClient(AbstractAPIClient):

    authenticator = SessionSSOAuthenticator

    def update_profile(self, sso_session_id, data):
        files = {}
        if 'logo' in data:
            files['logo'] = data.pop('logo')
        return self.patch(
            url=url_profile,
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_private_profile(self, sso_session_id):
        return self.get(url=url_profile, authenticator=self.authenticator(sso_session_id))

    def retrieve_public_profile(self, number):
        return self.get(url=url_published_profile_detail.format(number=number), use_fallback_cache=True,)

    def validate_company_number(self, number):
        return self.get(url=url_validate_company_number, params={'number': number})

    def create_case_study(self, data, sso_session_id):
        files = {}
        for field in ['image_one', 'image_two', 'image_three', 'video_one']:
            if data.get(field):
                files[field] = data.pop(field)
        return self.post(
            url=url_case_study_create,
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
            url=url_case_study_detail.format(id=case_study_id),
            data=data,
            files=files,
            authenticator=self.authenticator(sso_session_id),
        )

    def delete_case_study(self, sso_session_id, case_study_id):
        return self.delete(
            url=url_case_study_detail.format(id=case_study_id),
            authenticator=self.authenticator(sso_session_id)
        )

    def retrieve_private_case_study(self, sso_session_id, case_study_id):
        return self.get(
            url=url_case_study_detail.format(id=case_study_id),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def retrieve_public_case_study(self, case_study_id):
        return self.get(url=url_case_study_published_detail.format(id=case_study_id), use_fallback_cache=True)

    def verify_with_code(self, sso_session_id, code):
        return self.post(
            url=url_verify_with_code,
            data={'code': code},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_with_companies_house(self, sso_session_id, access_token):
        return self.post(
            url=url_verify_with_companies_house,
            data={'access_token': access_token},
            authenticator=self.authenticator(sso_session_id),
        )

    def verify_identity_request(self, sso_session_id):
        return self.post(url=url_verify_with_identity_request, authenticator=self.authenticator(sso_session_id),)

    def search_find_a_supplier(self, **kwargs):
        return self.get(url=url_search_find_a_supplier, params=kwargs, use_fallback_cache=True,)

    def search_investment_search_directory(self, **kwargs):
        return self.get(url=url_search_investment_support_directory, params=kwargs, use_fallback_cache=True)

    def create_transfer_invite(self, sso_session_id, new_owner_email):
        return self.post(
            url=url_transfer_invite_create,
            data={'new_owner_email': new_owner_email},
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_transfer_invite(self, sso_session_id, invite_key):
        return self.get(
            url=url_transfer_invite_detail.format(invite_key=invite_key),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def accept_transfer_invite(self, sso_session_id, invite_key):
        return self.patch(
            url=url_transfer_invite_detail.format(invite_key=invite_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def create_collaboration_invite(self, sso_session_id, collaborator_email):
        return self.post(
            url=url_collaborator_invite_create,
            data={'collaborator_email': collaborator_email},
            authenticator=self.authenticator(sso_session_id))

    def retrieve_collaboration_invite(self, sso_session_id, invite_key):
        return self.get(
            url=url_collaborator_invite_detail.format(invite_key=invite_key),
            authenticator=self.authenticator(sso_session_id),
            use_fallback_cache=True,
        )

    def accept_collaboration_invite(self, sso_session_id, invite_key):
        return self.patch(
            url=url_collaborator_invite_detail.format(invite_key=invite_key),
            data={'accepted': True},
            authenticator=self.authenticator(sso_session_id),
        )

    def remove_collaborators(self, sso_session_id, sso_ids):
        return self.post(
            url=url_collaborator_remove,
            data={'sso_ids': sso_ids},
            authenticator=self.authenticator(sso_session_id),
        )

    def retrieve_collaborators(self, sso_session_id):
        return self.get(url=url_collaborator_list, authenticator=self.authenticator(sso_session_id))

    def request_collaboration(self, **kwargs):
        return self.post(url=url_collaborator_request, data=kwargs)

    def add_collaborator(self, data):
        return self.post(url_collaborator_add, data=data)
