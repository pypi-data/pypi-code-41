from directory_api_client.base import AbstractAPIClient


class NotificationsAPIClient(AbstractAPIClient):

    endpoints = {
        'anonymous-unsubscribe': '/notifications/anonymous-unsubscribe/',
    }

    def anonymous_unsubscribe(self, signed_email_address):
        url = self.endpoints['anonymous-unsubscribe']
        return self.post(url, {'email': signed_email_address})
