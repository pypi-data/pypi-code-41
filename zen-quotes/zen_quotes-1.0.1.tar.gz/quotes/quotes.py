from config import Config
import requests, json

class Quotes():

    def __init__(self):
        self._url = Config.get('URL', 'api_quotes')

    def get_quotes(self, quote = None):
        """
        Busca na API Challenge Quotes, as citações 'Zen of Python'.
        """
        if quote is not None:
            response = requests.get(self._url + f"/{quote}")
        else:
            response = requests.get(self._url)

        return response.json()

if __name__ == "__main__":
    q = Quotes()
    q.get_quotes()