class Environment(object):

    def __init__(self, sandbox):

        # Production
        if not sandbox:
            self.api = 'http://172.30.1.9:8000/cielo-post/'
            self.api_query = 'http://172.30.1.9:8000/cielo-get/'
        else:
            self.api = 'http://172.30.1.9:8000/cielo-post-sandbox/'
            self.api_query = 'http://172.30.1.9:8000/cielo-get-sandbox/'