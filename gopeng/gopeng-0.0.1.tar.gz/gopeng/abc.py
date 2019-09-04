

class RapidAPIRequest:
    def __init__(self, host, key):
        self.host, self.key = host, key
        self.headers = {'x-rapidapi-host': host, 'x-rapidapi-key': key}
