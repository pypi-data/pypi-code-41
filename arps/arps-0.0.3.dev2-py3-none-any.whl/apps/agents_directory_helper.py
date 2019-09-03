import logging
import http.client
from typing import List, Tuple, Dict

import simplejson as json


class AgentsDirectoryHelper:

    def __init__(self, *, address: str, port: int) -> None:
        '''
        Initialize connection to the agents directory

        Access is done by access_resource method

        Args:
        - address: url to access the agents directory
        - port: port being listened by the agents directory
        '''
        self.port = port
        self.agents_directory_address = 'http://{}:{}'.format(address, self.port)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.conn = http.client.HTTPConnection(address, port)

    def access_resource(self, *, command: str = None, parameters: List[str] = None) -> Tuple[bool, Dict]:
        '''
        Execute commands available in agents directory

        Args:
        - command: command to be exeucted. See root of agents directory to check its availability
        - parameters: optional parameters that depend on the command
        '''
        if parameters is not None:
            parameters = '&'.join('{}={}'.format(parameter, value) for parameter, value in parameters.items())

        url = None
        if not command:
            url = '/'
        elif not parameters:
            url = '/{}'.format(command)
        else:
            url = '/{}?{}'.format(command, parameters)

        self.logger.info('Accessing {}'.format(self.agents_directory_address + url))
        try:
            self.conn.request('GET', url)
            request = self.conn.getresponse()
            request_content = request.read()
            self.logger.debug(f'Request response content: {request_content}')
            return True, json.loads(request_content.decode())
        except json.JSONDecodeError as err:
            return False, f'Error while decoding json {err}'
        except ConnectionError as err:
            return False, f'Error {err} occurred executing command {command} with parameters {parameters}'
