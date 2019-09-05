from django.utils.safestring import mark_safe

from .base import register
from materialize_nav.settings import mysettings

__all__ = ["render_user_chip", "render_user_image", "render_user_background"]


def get_user_thumbnail(user):
    """Return the users thumbnail or None if not found."""
    # User Image
    prop = mysettings.USER_THUMBNAIL_PROPERTY
    attr = user
    while '.' in prop and attr is not None:
        p, prop = prop.split('.', 1)
        attr = getattr(user, p, None)

    if attr == user or attr is None:
        return attr
    return None


@register.inclusion_tag("materialize_nav/user/render_user_chip.html")
def render_user_chip(user, show_full_name=False, default_user_image=None):
    d = {"user": user, "show_full_name": show_full_name,
         'account_icon': mark_safe('<i class="material-icons">account_circle</i>'),
         'thumbnail': get_user_thumbnail(user)}
    return d


@register.inclusion_tag("materialize_nav/user/user_image.html")
def render_user_image(user, style="", class_names="", default_user_image=None):
    d = {"user": user, "style": style, "class_names": class_names,
         'account_icon': mark_safe('<i class="material-icons">account_circle</i>'),
         'thumbnail': get_user_thumbnail(user)}
    return d


@register.inclusion_tag("materialize_nav/user/user_background.html", takes_context=True)
def render_user_background(context, user, default_user_image=None, default_background_image=None):
    """Render the side bar with the user background and profile picture."""
    d = {"user": user, "url_path": context["request"].path}

    # User Image
    if default_user_image is None:
        try:
            default_user_image = get_user_model().get_default_thumbnail()
        except:
            default_user_image = get_default_thumbnail()
    d["default_user_image"] = default_user_image

    # Background Image
    if default_background_image is None:
        try:
            default_background_image = get_user_model().get_default_background_image()
        except:
            default_background_image = get_default_background()
    d["default_background_image"] = default_background_image

    return d
