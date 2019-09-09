from django import template
from psu_infotext.models import Infotext
from ast import literal_eval
from psu_base.classes.Log import Log
from psu_base.services import utility_service
from django.utils.html import format_html

register = template.Library()
log = Log()


@register.simple_tag(takes_context=True)
def infotext(context, text_code, default_text, replacements=None, auto_prefix=True):
    """
    Render user-editable text content
    """
    log.trace('infotext_taglib.infotext', [text_code])

    # Get current app name
    app = utility_service.get_app_code()

    # Get relative path (url) with slashes converted to dots
    path = context['request'].get_full_path().replace('/', '.').strip('.').lower()

    # If url does not start with app name, prepend app name to the prefix
    if not path.startswith(app):
        prefix = "{0}.{1}".format(app, path)
    else:
        prefix = path

    # Determine full text_code. Convert to lowercase for case insensitivity.
    if auto_prefix:
        infotext_code = f"{prefix}.{text_code}".strip().lower()

    else:
        infotext_code = text_code.strip().lower()

    # Look for instance in database
    result = Infotext.objects.filter(app_code=app.upper()).filter(text_code=infotext_code)

    # If not found, add it
    if not result:
        instance = Infotext(
            app_code=app.upper(),
            text_code=infotext_code,
            content=default_text
        )
        instance.save()

    else:
        instance = result[0]

    # Compare unedited text content to the coded value, and update if the coded content changed
    if instance.user_edited == 'N' and instance.content != default_text:
        instance.content = default_text
        instance.save()

    # If user-edited text has been updated in the code (or restored by user), remove user-edited indicator
    elif instance.user_edited == 'Y' and instance.content == default_text:
        instance.user_edited = 'N'
        instance.save()

    # If user-edited text differs from coded content in development environment, log it as warning
    elif instance.user_edited == 'Y' and utility_service.get_environment() == 'DEV':
        log.warn(f"{infotext_code} has been updated to: '{instance.content}'")

    # Get text content
    content = instance.content

    # Process any replacements
    # Note: replacements should be a string that is formatted like a dict
    if replacements is not None:
        for key, val in literal_eval(replacements).items():
            content = content.replace(key, val)

    log.end('infotext_taglib.infotext')
    return format_html(content)
