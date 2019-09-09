import pkg_resources

from directory_client_core.base import AbstractAPIClient


class DirectorySSOTestAPIClient(AbstractAPIClient):

    endpoints = {
        'user_by_email': 'testapi/user-by-email/{email}/'
    }
    version = pkg_resources.get_distribution(__package__).version

    def get_user_by_email(self, email):
        url = self.endpoints['user_by_email'].format(email=email)
        return self.get(url=url)

    def delete_user_by_email(self, email):
        url = self.endpoints['user_by_email'].format(email=email)
        return self.delete(url=url)

    def flag_user_email_as_verified_or_not(self, email, verified):
        url = self.endpoints['user_by_email'].format(email=email)
        data = {"is_verified": verified}
        return self.patch(url=url, data=data)
