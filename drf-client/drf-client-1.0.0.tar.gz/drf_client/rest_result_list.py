from time import sleep

from dotmap import DotMap


class RestResultList():
    def __init__(self, client, schema, app, model, ops, params):
        self.client = client
        self.schema = schema
        self.app = app
        self.model = model
        self.ops = ops
        self.params = params

    def first(self):
        response = self.client.action(self.schema, [self.app, self.model, self.ops], params=self.params)

        if 'results' in response:
            results = []
            for result in response['results']:
                results.append(DotMap(result, _dynamic=False))

            if results:
                return results[0]

            return None

        return response

    def all(self):
        response = self.client.action(self.schema, [self.app, self.model, self.ops], params=self.params)
        if 'results' in response:
            for result in response['results']:
                yield DotMap(result, _dynamic=False)

            next_page = response['next']
            # Paginate more pages if any
            while next_page:
                # This will prevent response failures from server if this
                # iterator is in tight loop
                sleep(0.8)
                for result in response['results']:
                    yield DotMap(result, _dynamic=False)

                response = self.client.get(next_page)
                next_page = response['next']
        else:
            return response
