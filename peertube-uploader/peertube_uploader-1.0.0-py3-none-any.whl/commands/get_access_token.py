import os
import sys

from peertube_uploader.commands.base_command import PeertubeBaseCommand
from peertube_uploader.commands.types import RequiredType


class GetAccessTokenCommand(PeertubeBaseCommand):
    """
    Requests an access-token from the server.
    It's required for write or protected access to the server
    """

    def get_parser(self, prog_name):
        parser = super(GetAccessTokenCommand, self).get_parser(prog_name)

        # Required
        parser.add_argument('-u', '--username',
                            help='MANDATORY! '
                                 'Username (alternatively use PEERTUBE_USERNAME env var)',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_USERNAME', RequiredType.DEFAULT))
        parser.add_argument('-p', '--password',
                            help='MANDATORY! '
                                 'Password (alternatively use PEERTUBE_PASSWORD env var)',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_PASSWORD', RequiredType.DEFAULT))

        # Optional
        parser.add_argument('-c', '--client_id',
                            help='Client ID to use. '
                                 'Can also be generated or be defined in env var PEERTUBE_CLIENT_ID',
                            default=os.getenv('PEERTUBE_CLIENT_ID'))
        parser.add_argument('-s', '--client_secret',
                            help='Client secret to use. '
                                 'Can also be generated or be defined in env var PEERTUBE_CLIENT_SECRET',
                            default=os.getenv('PEERTUBE_CLIENT_SECRET'))

        return parser

    def take_action(self, parsed_args):
        super(GetAccessTokenCommand, self).take_action(parsed_args)

        client_id = parsed_args.client_id
        client_secret = parsed_args.client_secret
        if not (client_id or client_secret):
            local__json = self.s.get("/api/v1/oauth-clients/local").json()
            client_id = local__json["client_id"]
            client_secret = local__json["client_secret"]
            self.app.LOG.info("""Please reuse these credentials
            client-id:{client_id}
            client-secret:{client_secret}
            """.format(client_id=client_id, client_secret=client_secret))

        auth_data = {'client_id': client_id,
                     'client_secret': client_secret,
                     'grant_type': 'password',
                     'response_type': 'code',
                     'username': parsed_args.username,
                     'password': parsed_args.password
                     }

        auth_result = self.s.post('/api/v1/users/token', data=auth_data)
        try:
            access_token = (auth_result.json()['access_token'])
        except:
            self.app.LOG.error(auth_result.text)
            sys.exit(1)

        self.app.LOG.info(access_token)

