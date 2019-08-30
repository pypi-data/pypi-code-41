import argparse
from mimetypes import guess_type
from pathlib import Path

from peertube_uploader.commands.upload_base import UploadBaseCommand


class UploadVideoCommand(UploadBaseCommand):
    """
    :type video_file: file
    """

    _description = "Upload videos from the file-system"

    API_ENDPOINT = "/api/v1/videos/upload"

    def __init__(self, app, app_args):
        super(UploadVideoCommand, self).__init__(app, app_args)
        self.file_mime_type = None
        self.video_file = None

    def get_parser(self, prog_name):
        parser = super(UploadVideoCommand, self).get_parser(prog_name)
        parser.add_argument('video', help='Video to upload', type=self.check_file)
        return parser

    def _build_upload_data(self, parsed_args):
        super(UploadVideoCommand, self)._build_upload_data(parsed_args)
        self.upload_data["name"] = parsed_args.name if parsed_args.name else parsed_args.video.stem

    def _build_request_kwargs(self, parsed_args):
        self.video_file = open(parsed_args.video, 'rb')
        return {
            "data": self.upload_data,
            "files": {
                "videofile": (self.upload_data["name"], self.video_file, self.file_mime_type)
            }
        }

    def _clean_upload(self):
        if self.video_file:
            self.video_file.close()

    def check_file(self, path_str):
        path = Path(path_str)
        if not path.is_file():
            raise argparse.ArgumentTypeError("Given path isn't accessible or doesn't exist")
        self.file_mime_type = guess_type(str(path))[0]
        return path
