import json
import locale
import os
import sys
from argparse import FileType
from enum import auto
from mimetypes import add_type, guess_type
from pathlib import Path

from requests import HTTPError

from peertube_uploader.actions.append_dict_action import AppendDictAction
from peertube_uploader.commands.base_command import PeertubeBaseCommand
from peertube_uploader.commands.types import RequiredType
from peertube_uploader.utils import StringListEnum

# Add the correct mimetypes for captions to the db
add_type('text/vtt', '.vtt')
add_type('application/x-subrip', '.srt')


class SkipReasons(StringListEnum):
    SAME_NAME_ON_SERVER = auto()


class UploadBaseCommand(PeertubeBaseCommand):

    API_ENDPOINT = None

    def __init__(self, app, app_args):
        super().__init__(app, app_args)
        self.upload_data = {}

    def get_parser(self, prog_name):
        parser = super(UploadBaseCommand, self).get_parser(prog_name)
        parser.add_argument('-c', '--channel',
                            help='Channel ID to upload to. '
                                 'Can also come from PEERTUBE_CHANNEL_ID env var',
                            type=RequiredType(parser),
                            default=os.getenv('PEERTUBE_CHANNEL_ID', RequiredType.DEFAULT))

        parser.add_argument('-j', '--json', help='Path to JSON containing extra upload params',
                            type=FileType())
        parser.add_argument('-n', '--name', help='Name of the uploaded video')
        parser.add_argument('--private', help='Set video as private', action='store_true')
        parser.add_argument('--skip', help='Skip upload under certain conditions',
                            choices=list(SkipReasons),
                            type=SkipReasons.get,
                            dest="skip_reasons",
                            action='append')
        parser.add_argument('--nocomments', help='Disable comments', action='store_true')
        parser.add_argument(
            "--subs", action=AppendDictAction, dest="subs",
            nargs=2, help="Select the language-code and caption file. "
                          "One file per language."
                          "You can use this multiple times (once per language).",
            metavar=("CODE", "FILE"),
            key_choices=[alias for alias in locale.locale_alias.keys()
                         if len(alias) == 2]
        )
        return parser

    def _build_upload_data(self, parsed_args):
        self.upload_data = {
            'channelId': parsed_args.channel,
            'privacy': '2' if parsed_args.private else '1',
            'commentsEnabled': False if parsed_args.nocomments else True,
        }

    def _do_request(self, upload_kwargs):
        self.app.LOG.info("Making request")
        res = self.s.post(self.API_ENDPOINT, **upload_kwargs)
        res.raise_for_status()
        return res

    def _build_request_kwargs(self, parsed_args):
        return {}

    def _clean_upload(self):
        pass

    def take_action(self, parsed_args):
        super(UploadBaseCommand, self).take_action(parsed_args)
        try:
            int(parsed_args.channel)
        except ValueError:
            parsed_args.channel = self.get_channel_id(parsed_args.channel)

        self._build_upload_data(parsed_args)

        if parsed_args.json:
            self.app.LOG.info("Extending upload with extra data")
            j = json.load(parsed_args.json)
            self.upload_data.update(j)

        if parsed_args.skip_reasons:
            for skip_reason in parsed_args.skip_reasons:
                if skip_reason == SkipReasons.SAME_NAME_ON_SERVER:
                    vid_name = self.upload_data["name"].strip()
                    res = self.s.get("/api/v1/search/videos", params=dict(search=vid_name)).json()
                    if res.get("total", 0) < 1:
                        continue
                    # Check all returned search results
                    for result in res.get("data", []):
                        if result.get("name", "").strip() == vid_name:
                            self.app.LOG.warn("Skip reason %s: '%s' found on server", skip_reason, vid_name)
                            sys.exit(0)

        try:
            upload_result = self._do_request(self._build_request_kwargs(parsed_args))
            video_uuid = upload_result.json()['video']['uuid']
            self.app.LOG.info('{0}{1}/{2}'.format(
                self.app_args.endpoint, '/videos/watch', video_uuid)
            )
        except KeyError:
            self.app.LOG.error(upload_result.text)
            raise
        finally:
            self._clean_upload()

        self.upload_subs(parsed_args.subs, video_uuid)

    def get_channel_id(self, channel_name):
        # If the channel-id is not integer, get the actual id via API
        ret = self.s.get('{0}/{1}'.format('/api/v1/video-channels', channel_name))

        try:
            ret.raise_for_status()
            channel__json = ret.json()
            id_ = channel__json['id']
        except HTTPError:
            if ret.status_code == 404:
                self.app.LOG.error("Unknown channel %s", channel_name)
                sys.exit(1)
            else:
                raise
        except KeyError:
            self.app.LOG.error(ret.text)
            sys.exit(1)

        return id_

    def upload_subs(self, subs, video_uuid):
        if not isinstance(subs, dict):
            return
        # Best effort loop to add subs
        for lang, sub_path in subs.items():
            sub_path = Path(sub_path)
            try:
                with open(sub_path) as sub_file:
                    sub_mime_type = guess_type(str(sub_path))[0]
                    res = self.s.put("/api/v1/videos/{id}/captions/{captionLanguage}".format(
                        id=video_uuid,
                        captionLanguage=lang
                    ), files={
                        "captionfile": (sub_path.name, sub_file, sub_mime_type)
                    })
                    if res.status_code != 204:
                        try:
                            j = res.json()
                            errors = j["errors"]
                        except:
                            errors = res.content
                        raise HTTPError(res.status_code, errors)

                    self.LOG.info("Uploaded subtitle(%(lang)s) '%(file)s'." % {
                        "lang": lang,
                        "file": sub_path
                    })
            except FileNotFoundError as fnfe:
                self.app.LOG.error("Couldn't find subtitle file %s" % sub_path)
            except Exception as e:
                self.app.LOG.error("Couldn't publish subtitle for %s %s: %s" % (video_uuid, sub_path, e))
