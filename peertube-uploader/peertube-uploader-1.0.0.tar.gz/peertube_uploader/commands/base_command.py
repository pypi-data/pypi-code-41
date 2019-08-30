import argparse

from cliff.command import Command

from peertube_uploader.utils import RelativeSession


# noinspection PyAbstractClass
class PeertubeBaseCommand(Command):
    """

    :type s: RelativeSession
    """

    def __init__(self, app, app_args):
        """

        :param app:
        :type app:  cliff.app.App
        :param app_args:
        :type app_args: argparse.Namespace
        """
        super(PeertubeBaseCommand, self).__init__(app, app_args)
        self.s = None

    def take_action(self, parsed_args):
        if not self.app_args.endpoint:
            raise argparse.ArgumentError("Please target an endpoint with the --endpoint param")

        self.s = RelativeSession(self.app_args.endpoint)
