import argparse
import os

from peertube_uploader.commands.base_command import PeertubeBaseCommand


# noinspection PyAbstractClass
class BaseAuthenticatedCommand(PeertubeBaseCommand):
    """
    Commands that require authentication to operate
    like uploading or modifying users and videos should
    subclass this
    """

    def __init__(self, app, app_args):
        """

        :param app:
        :type app:  cliff.app.App
        :param app_args:
        :type app_args: argparse.Namespace
        """
        super(BaseAuthenticatedCommand, self).__init__(app, app_args)
        self._token_arg = None

    def get_parser(self, prog_name):
        parser = super(BaseAuthenticatedCommand, self).get_parser(prog_name)
        self._token_arg = parser.add_argument(
            '-t', '--access_token',
            help='MANDATORY! Access token to use.'
                 ' Can also be generated or be defined in env var PEERTUBE_ACCESS_TOKEN',
            default=os.getenv('PEERTUBE_ACCESS_TOKEN'))
        return parser

    def take_action(self, parsed_args):
        super(BaseAuthenticatedCommand, self).take_action(parsed_args)
        if not parsed_args.access_token:
            raise argparse.ArgumentError(
                self._token_arg,
                "Please pass a token or get one"
                " from the server with the get-access-token command"
            )

        self.s.headers.update({
            'Authorization': 'Bearer {0}'.format(parsed_args.access_token)
        })
