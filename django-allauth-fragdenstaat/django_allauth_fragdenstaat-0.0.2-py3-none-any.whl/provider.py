from allauth.account.models import EmailAddress

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from allauth.socialaccount import app_settings


class FragdenstaatAccount(ProviderAccount):

    def to_str(self):
        default = super(FragdenstaatAccount, self).to_str()
        first_name = self.account.extra_data.get('first_name', '')
        last_name = self.account.extra_data.get('last_name', '')
        name = ('%s %s' % (first_name, last_name)).strip()
        return name or default


class FragdenstaatProvider(OAuth2Provider):
    id = 'fragdenstaat'
    name = 'FragDenStaat.de'
    package = 'fragdenstaat_auth'
    account_class = FragdenstaatAccount

    def get_default_scope(self):
        scope = ['read:user']
        if app_settings.QUERY_EMAIL:
            scope.append('read:email')
        return scope

    def extract_uid(self, data):
        return str(data['id'])

    def extract_email_addresses(self, data):
        if 'email' in data:
            return [EmailAddress(
                email=data.get('email').lower(),
                verified=True,
                primary=True
            )]
        return []

    def extract_common_fields(self, data):
        fields = {
            'last_name': data.get('last_name'),
            'first_name': data.get('first_name'),
        }
        if 'email' in data:
            fields['email'] = data.get('email')
        return fields


providers.registry.register(FragdenstaatProvider)
