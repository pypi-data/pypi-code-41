"""
@copyright KPH Health Care Services, Inc 2017

"""
from __future__ import unicode_literals

import datetime
import logging
import math
import os
import pprint

from django.conf import settings
from django.core.management.base import BaseCommand

from favorites_icons.templatetags.utils import generate_icons, generate_manifest

logger = logging.getLogger(__name__)

settings.DEBUG = False


class Command(BaseCommand):
    help = "Generate all icons, and the manifest."
    verbosity = 0

    init_time = None

    def _log_message(self, message, **kwargs):
        pretty = kwargs.get("pretty", False)

        if pretty:
            message = pprint.pformat(message)

        log_message = "%s: %s\n" % (datetime.datetime.now().isoformat()[0:19], message)

        logger.info(message)

        if self.verbosity > 0:
            self.stdout.write(log_message)

    def _timer(self):
        if not self.init_time:
            self.init_time = datetime.datetime.now()
            self._log_message("Command initiated.")
        else:
            self._log_message("Command completed.")

            complete_time = datetime.datetime.now()
            command_total_seconds = (complete_time - self.init_time).total_seconds()
            command_minutes = math.floor(command_total_seconds / 60)
            command_seconds = command_total_seconds - (command_minutes * 60)

            self._log_message("Command took %i minutes and %i seconds to run." % (command_minutes, command_seconds))

    def handle(self, *args, **options):
        self.verbosity = int(options["verbosity"])

        self._timer()

        static_root = getattr(settings, "STATIC_ROOT", False)
        static_url = getattr(settings, "STATIC_URL", False)

        icon_path = os.path.join(static_root, "favicons")
        icon_url_path = os.path.join(static_url, "favicons")

        self.stdout.write("Generating icons in: %s" % icon_path)
        self.stdout.write("URL Base: %s" % icon_url_path)

        overwrite = True
        generate_icons(overwrite=overwrite, echo_status=True)
        generate_manifest(overwrite=overwrite, echo_status=True)

        self._timer()
