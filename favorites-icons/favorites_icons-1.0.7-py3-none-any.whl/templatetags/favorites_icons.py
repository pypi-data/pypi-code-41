"""
@copyright Amos Vryhof

"""
import os

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from .utils import generate_icons, url_join, generate_manifest

register = template.Library()


@register.simple_tag
def touch_icons(overwrite=False):
    generate_icons(overwrite=overwrite)
    generate_manifest(overwrite=overwrite)

    static_root = getattr(settings, "STATIC_URL", False)
    icon_path = os.path.join(static_root, "favicons")

    icon_sizes = getattr(
        settings, "ICON_SIZES", [16, 32, 57, 60, 64, 72, 76, 96, 114, 120, 144, 152, 180, 192, 256, 512]
    )

    icons = []
    for icon_size in icon_sizes:
        icon_url = url_join(icon_path, "favicon-%ix%i.png" % (icon_size, icon_size))

        icons.append('<link rel="apple-touch-icon" sizes="%ix%i" href="%s">' % (icon_size, icon_size, icon_url))
        icons.append('<link rel="icon" type="image/png" sizes="%ix%i"  href="%s">' % (icon_size, icon_size, icon_url))

    icons.append(
        '<meta name="msapplication-TileImage" content="%s">' % url_join(icon_path, "favicon-%ix%i.png" % (144, 144))
    )
    icons.append('<meta name="msapplication-TileColor" content="%s">' % getattr(settings, "TILE_COLOR", "#FFFFFF"))
    icons.append('<meta name="theme-color" content="%s">' % getattr(settings, "THEME_COLOR", "#FFFFFF"))

    favicon_url = url_join(icon_path, "favicon.ico")
    icons.append('<link rel="shortcut icon" href="%s" type="image/x-icon">' % favicon_url)
    icons.append('<link rel="icon" href="%s" type="image/x-icon">' % favicon_url)

    manifest_url = url_join(icon_path, "manifest.json")
    icons.append('<link rel="manifest" href="%s">' % manifest_url)

    return mark_safe("\n".join(icons))
