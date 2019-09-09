from django import template
from psu_infotext.models import Infotext
from ast import literal_eval
from psu_base.classes.Log import Log
from psu_base.templatetags.tag_processing import supporting_functions as support
from psu_base.services import utility_service
from django.utils.html import format_html
from django.template import TemplateSyntaxError

register = template.Library()
log = Log()


@register.simple_tag(takes_context=True)
def infotext(context, code, alt, replacements=None, auto_prefix=True):
    """
    Render user-editable text content
    """
    log.trace()
    attrs = {'code': code, 'alt': alt, 'auto_prefix': str(auto_prefix)}
    if replacements:
        attrs['replacements'] = replacements

    return prepare_infotext(attrs, alt, context)


@register.tag()
def infotext_block(parser, token):
    """
    Render user-editable text content
    """
    log.trace()
    tokens = token.split_contents()
    try:
        nodelist = parser.parse((f"end_{tokens[0]}",))
        parser.delete_first_token()
    except TemplateSyntaxError:
        nodelist = None

    return InfotextNode(nodelist, tokens)


class InfotextNode(template.Node):
    def __init__(self, nodelist, tokens):
        self.nodelist = nodelist
        self.tokens = tokens

    def render(self, context):
        log.trace()
        attrs, body = support.get_tag_params(self.nodelist, self.tokens, context)
        return prepare_infotext(attrs, body, context)


def prepare_infotext(attrs, alt_text, context):
    """
    Prepare infotext for both tags (inline and block)
    """
    log.trace(attrs)

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
    if attrs.get('auto_prefix', "True").lower() not in ["false", "no", "n"]:
        infotext_code = f"{prefix}.{attrs['code']}".strip().lower()

    else:
        infotext_code = attrs['code'].strip().lower()

    log.debug(f"Infotext Code: {infotext_code}")

    # Look for instance in database
    result = Infotext.objects.filter(app_code=app.upper()).filter(text_code=infotext_code)

    # If not found, add it
    if not result:
        instance = Infotext(
            app_code=app.upper(),
            text_code=infotext_code,
            content=alt_text
        )
        instance.save()

    else:
        instance = result[0]

    # Compare unedited text content to the coded value, and update if the coded content changed
    if instance.user_edited == 'N' and instance.content != alt_text:
        instance.content = alt_text
        instance.save()

    # If user-edited text has been updated in the code (or restored by user), remove user-edited indicator
    elif instance.user_edited == 'Y' and instance.content == alt_text:
        instance.user_edited = 'N'
        instance.save()

    # If user-edited text differs from coded content in development environment, log it as warning
    elif instance.user_edited == 'Y' and utility_service.get_environment() == 'DEV':
        log.warn(f"{infotext_code} has been updated to: '{instance.content}'")

    # Get text content
    content = instance.content

    # Process any replacements
    if 'replacements' in attrs:
        replacements = attrs['replacements']
        # Note: replacements could be a string that is formatted like a dict
        if type(replacements) is str:
            for key, val in literal_eval(replacements).items():
                content = content.replace(key, val)
        elif type(replacements) is dict:
            for key, val in replacements.items():
                content = content.replace(key, val)

    log.end()
    return format_html(content)
