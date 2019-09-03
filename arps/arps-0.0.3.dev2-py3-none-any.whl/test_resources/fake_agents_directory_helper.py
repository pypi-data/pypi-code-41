import platform


class FakeAgentsDirectoryHelper:

    def __init__(self):
        self.registered = {}

    def access_resource(self, *, command=None, parameters=None):
        if command == 'get':
            return True, {'message':
                          {'address': platform.node(),
                           'port': self.registered[parameters['id']]},
                          'result': 'success'}
        if command == 'add':
            self.registered[str(parameters['id'])] = parameters['port']
            return True, {'message': 'agent {} added'.format(parameters['id']),
                          'result': 'success'}

        return False, {'message': None, 'result': 'failure'}
