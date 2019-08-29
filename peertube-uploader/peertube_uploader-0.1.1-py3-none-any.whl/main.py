#!/usr/bin/env python3
from __future__ import print_function

import inspect
import os
import sys
from importlib import import_module

import pkg_resources
from cliff.app import App
from cliff.commandmanager import CommandManager

from peertube_uploader.commands.types import RequiredType
from peertube_uploader.utils import COMMAND_SUFFIX, camel2kebab

API_DOC_URL = "https://docs.joinpeertube.org/api-rest-reference.html"
VERSION = pkg_resources.resource_string(__name__, "VERSION").decode().strip()


class PeertubeCommandManager(CommandManager):

    def load_commands(self, namespace):
        """
        Creates commands from all *Command classes in the namespace

        :type namespace: basestring
        """
        module = import_module(namespace)
        for name, o in inspect.getmembers(module):
            if not (inspect.isclass(o) and name.endswith(COMMAND_SUFFIX)):
                continue

            # We make sure to remove the redundant "Command" suffix
            self.add_command(
                camel2kebab(name[:-len(COMMAND_SUFFIX)]),
                o
            )


App.NAME = "peertube-uploader"


class PeerUploaderApp(App):

    def __init__(self):
        super(PeerUploaderApp, self).__init__(
            description="""
A script to make uploading to peertube instances easier.

For documentation on the API used see {api_doc_url}
""".format(api_doc_url=API_DOC_URL),
            version=VERSION,
            command_manager=PeertubeCommandManager("peertube_uploader.commands")
        )

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        parser = super(PeerUploaderApp, self).build_option_parser(description, version, argparse_kwargs)

        # Required
        parser.add_argument('-u', '--username', help='Username',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_USERNAME', RequiredType.DEFAULT))
        parser.add_argument('-p', '--password', help='Password',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_PASSWORD', RequiredType.DEFAULT))
        parser.add_argument('-e', '--endpoint', help='Host name',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_ENDPOINT', RequiredType.DEFAULT))

        # Optional
        parser.add_argument('-c', '--client_id', help='Client ID to use',
                            default=os.getenv('PEERTUBE_CLIENT_ID'))
        parser.add_argument('-s', '--client_secret', help='Client secret to use',
                            default=os.getenv('PEERTUBE_CLIENT_SECRET'))
        parser.add_argument('-t', '--access_token', help='Access token to use',
                            default=os.getenv('PEERTUBE_ACCESS_TOKEN'))
        return parser


def main(argv=sys.argv[1:]):
    pt_app = PeerUploaderApp()
    return pt_app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
