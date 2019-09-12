import requests


class BandwidthAPI:
    BASE_URL = 'https://dashboard.bandwidth.com/api/'

    def __init__(self, account_id, username, password):
        """

        :param account_id: Account id from bandwidth dashboard
        :param username: This is username for account api and api token for messaging api
        :param password: This is password for account api and api token secret for messaging api
        """
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.account_id = account_id

    def _request(self, method, url, params=None, json=None, auth=None):
        params = params or {}
        # FIXME: use a better join url function
        url = f'{self.BASE_URL}{url}'
        response = self.session.request(method, url, params=params, json=json, auth=auth)
        response.raise_for_status()
        return response

    def _get(self, url, params=None):
        return self._request('GET', url, params=params)

    def _post(self, url, params=None, json=None):
        return self._request('POST', url, params=params, json=json)


class BandwidthAccountAPI(BandwidthAPI):
    BASE_URL = 'https://dashboard.bandwidth.com/api/'

    def search_available_numbers(self, **params):
        """
        Search available phone numbers in bandwidth account

        :param params: TODO: specific parameters to be added
        :return:
        """
        url = f'accounts/{self.account_id}/availableNumbers'
        response = self._get(url, params=params)
        numbers = response.json()
        return numbers


class BandwidthMessagingAPI(BandwidthAPI):
    BASE_URL = 'https://messaging.bandwidth.com/api/'

    def __init__(self, account_id, api_token, api_secret, application_id):
        super().__init__(account_id, api_token, api_secret)
        self.application_id = application_id

    def send_message(self, from_number, to_numbers, text, tag=''):
        """
        Sending A2P message from property number to tenant numbers

        :param str from_number: Number from message will be sent
        :param list[str] to_numbers: Numbers list to which the message will be sent
        :param str text: message text
        :param str tag: custom tag for later on filtering the messages
        :return:
        """
        url = f'v2/users/{self.account_id}/messages'
        data = {
            "to": to_numbers,
            "from": from_number,
            "text": text,
            "applicationId": self.application_id,
            "tag": tag,
        }
        return self._post(url, json=data)
