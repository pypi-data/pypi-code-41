from django import template
from django.contrib.messages import constants as message_constants
from .base import register
from materialize_nav.utils import render_tag
from materialize_nav.settings import mysettings


MESSAGE_LEVEL_CLASSES = {
    message_constants.DEBUG: "rounded yellow",
    message_constants.INFO: "rounded light-blue",
    message_constants.SUCCESS: "rounded green",
    message_constants.WARNING: "orange",
    message_constants.ERROR: "red",
}


@register.simple_tag
def material_icons_url():
    return render_tag('link', end_tag=False, rel='stylesheet', **mysettings.MATERIAL_ICONS_URL)


@register.simple_tag
def materialize_css_url():
    return render_tag('link', end_tag=False, rel='stylesheet', **mysettings.MATERIALIZE_CSS_URL)


@register.simple_tag
def materialize_js_url():
    return render_tag('script', type='text/javascript', **mysettings.MATERIALIZE_JS_URL)


@register.simple_tag
def materialize_jquery_url():
    if mysettings.MATERIALIZE_JQUERY_URL:
        return render_tag('script', type='text/javascript', **mysettings.MATERIALIZE_JQUERY_URL)
    return ''


@register.simple_tag
def materialize_nav_css_url():
    return render_tag('link', end_tag=False, rel='stylesheet', **mysettings.MATERIALIZE_NAV_CSS_URL)


@register.simple_tag
def materialize_nav_js_url():
    return render_tag('script', type='text/javascript', **mysettings.MATERIALIZE_NAV_JS_URL)


@register.simple_tag
def materialize_nav_color_js_url():
    return render_tag('script', type='text/javascript', **mysettings.MATERIALIZE_NAV_COLOR_JS_URL)


@register.filter
def materialize_message_classes(message):
    extra_tags = None
    try:
        extra_tags = message.extra_tags
    except AttributeError:
        pass
    if not extra_tags:
        extra_tags = ""
    classes = [extra_tags]
    try:
        level = message.level
    except AttributeError:
        pass
    else:
        try:
            classes.append(MESSAGE_LEVEL_CLASSES[level])
        except KeyError:
            classes.append("")
    return " ".join(classes).strip()


@register.inclusion_tag('materialize_nav/messages.html', takes_context=True)
def materialize_messages(context, *args, **kwargs):
    """Show django.contrib.messages in a Materialize css toast."""
    context.update({'message_constants': message_constants})
    return context
