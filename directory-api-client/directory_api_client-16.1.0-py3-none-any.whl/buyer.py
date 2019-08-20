from directory_api_client.base import AbstractAPIClient


class BuyerAPIClient(AbstractAPIClient):

    endpoints = {
        'save': 'buyer/',
        'csv-dump': 'buyer/csv-dump/'
    }

    def send_form(self, form_data):
        return self.post(
            self.endpoints['save'],
            data=form_data
        )

    def get_csv_dump(self, token):
        url = self.endpoints['csv-dump']
        return self.get(
            url,
            params={'token': token},
            use_fallback_cache=True,
        )
