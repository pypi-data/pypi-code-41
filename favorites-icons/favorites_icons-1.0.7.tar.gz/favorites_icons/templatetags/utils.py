import datetime
import json
import logging
import os
import pprint
import re

from PIL import Image
from django.conf import settings
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


def log_message(message, **kwargs):
    pretty = kwargs.get("pretty", False)
    verbosity = kwargs.get('verbosity', False)

    if pretty:
        message = pprint.pformat(message)

    log_message = "%s: %s\n" % (datetime.datetime.now().isoformat()[0:19], message)

    logger.info(message)

    if verbosity:
        print(log_message)


def url_join(*args):
    os_path = os.path.join(*args)
    path_parts = re.split(r"/|\\", os_path)

    return "/".join(path_parts)


def generate_icons(**kwargs):
    overwrite = kwargs.get("overwrite", False)
    echo_status = kwargs.get("echo_status", False)

    static_root = getattr(settings, "STATIC_ROOT", False)
    icon_path = os.path.join(static_root, "favicons")

    icon_source = getattr(settings, "ICON_SRC", False)
    icon_sizes = getattr(
        settings, "ICON_SIZES", [16, 32, 57, 60, 64, 72, 76, 96, 114, 120, 144, 152, 180, 192, 256, 512]
    )
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]

    if icon_source:
        if not os.path.exists(icon_path):
            try:
                os.makedirs(icon_path)
            except:
                log_message('Failed to create %s' % icon_path, verbosity=echo_status)

        img = Image.open(icon_source)

        ico_target = os.path.join(icon_path, "favicon.ico")
        if overwrite or not os.path.exists(ico_target):
            try:
                img.save(ico_target, sizes=ico_sizes)
            except:
                log_message('Failed to Save %s' % ico_target, verbosity=echo_status)

        icon_sizes = sorted(icon_sizes, reverse=True)
        # Use the same image object, start with the largest size, and work our way down.
        for icon_size in icon_sizes:
            target_file = os.path.join(icon_path, "favicon-%ix%i.png" % (icon_size, icon_size))
            if overwrite or not os.path.exists(target_file):
                img.thumbnail((icon_size, icon_size), Image.ANTIALIAS)
                try:
                    img.save(target_file, "PNG")
                except:
                    log_message('Failed to save %s' % target_file, verbosity=echo_status)


def generate_manifest(**kwargs):
    overwrite = kwargs.get("overwrite", False)
    echo_status = kwargs.get("echo_status", False)

    static_root = getattr(settings, "STATIC_ROOT", False)
    static_url = getattr(settings, "STATIC_URL", False)

    icon_path = os.path.join(static_root, "favicons")
    icon_url_path = os.path.join(static_url, "favicons")

    target_file = os.path.join(icon_path, "manifest.json")

    icon_sizes = getattr(
        settings, "ICON_SIZES", [16, 32, 57, 60, 64, 72, 76, 96, 114, 120, 144, 152, 180, 192, 256, 512]
    )

    current_site = False

    if hasattr(settings, "SITE_ID"):
        current_site = Site.objects.get_current()

    site_name = getattr(settings, "SITE_NAME", current_site.name if current_site else "My App")

    manifest = {"name": site_name, "icons": []}

    density_factor = 48
    for icon_size in icon_sizes:
        icon_url = url_join(icon_url_path, "favicon-%ix%i.png" % (icon_size, icon_size))

        manifest["icons"].append(
            {
                "src": icon_url,
                "sizes": "%ix%i" % (icon_size, icon_size),
                "type": "image/png",
                "density": str(round(icon_size / density_factor, 2)),
            }
        )

    manifest_json = json.dumps(manifest)

    if overwrite and os.path.exists(target_file):
        os.remove(target_file)

    if overwrite or not os.path.exists(target_file):
        try:
            with open(target_file, "w") as manifest_file:
                manifest_file.write(manifest_json)
                manifest_file.close()
        except:
            log_message('Failed to create manifest.json', verbosity=echo_status)
