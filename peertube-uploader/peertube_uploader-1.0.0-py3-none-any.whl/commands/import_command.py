from enum import auto

from peertube_uploader.commands.upload_base import UploadBaseCommand
from peertube_uploader.utils import StringListEnum


class ImportTypes(StringListEnum):
    HTTP = auto()
    MAGNET = auto()
    TORRENT_FILE = auto()


class ImportCommand(UploadBaseCommand):
    """
    Trigger an import of a URI
    """
    API_ENDPOINT = "/api/v1/videos/imports"

    def get_parser(self, prog_name):
        parser = super(ImportCommand, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            choices=list(ImportTypes),
            default=ImportTypes.HTTP,
            type=ImportTypes.get,
            help='What type of import it will be. Http by default'
        )
        parser.add_argument('uri', help='magnet or http URI')
        return parser

    def _build_request_kwargs(self, parsed_args):
        if parsed_args.name:
            self.upload_data["name"] = parsed_args.name
        if "name" not in self.upload_data:
            raise ValueError("Use the --name arg or pass the name in the JSON of --json")

        uri = parsed_args.uri

        if parsed_args.type == ImportTypes.HTTP:
            self.upload_data["targetUrl"] = uri
        elif parsed_args.type == ImportTypes.MAGNET:
            self.upload_data["magnetUri"] = uri
        elif parsed_args.type == ImportTypes.TORRENT_FILE:
            raise NotImplementedError("Cannot import torrent files yet")
        else:
            raise ValueError("Unknown import type")

        return {
            "data": self.upload_data
        }
