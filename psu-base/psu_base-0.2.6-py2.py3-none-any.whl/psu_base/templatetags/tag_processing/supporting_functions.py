from django import template
from psu_base.classes.Log import Log

log = Log()


class ConditionalResponseNode(template.Node):
    """This responds to all of the conditional tags"""
    def __init__(self, nodelist, condition_satisfied):
        self.nodelist = nodelist
        self.condition_satisfied = condition_satisfied

    def render(self, context):
        if self.condition_satisfied:
            return self.nodelist.render(context)
        else:
            return ''


def process_args(p_args, context=None, p_allow_no_key=True):
    """
    Process args by converting variables into values.

    :param p_args: Args passed to the taglib. Do not remove arg[0] (the tag name)
    :param context: context provided by the tag
    :param p_allow_no_key: If True, keyless args will be allowed (i.e. not in key="value" format)
    :return: dict of args, not including the tag name (arg[0])
    """
    # Prepare attributes
    attrs = {}
    for arg in p_args[1:]:
        key = val = None
        if '=' in arg:
            key, val = arg.split('=')
        else:
            val = arg

        if key:
            # Double-quoted values need to be stripped and are no variables
            if val.startswith('"'):
                val = val.strip('"')
            # Non-quoted values must be converted to their true values
            else:
                val_str = template.Variable(val)
                val = val_str.resolve(context)

        # If no key was given, and that is allowed
        elif p_allow_no_key:
            # Create a key that matches the value
            # This prevents multiple keyless args from overwriting each other
            # Calling function can detect and handle this, if needed
            key = val  # i.e. selected="selected"

        else:
            log.error(
                f"Invalid argument for template tag {p_args[0]}: {val}. Attributes must be in key=\"value\" format"
            )
            continue

        attrs[key.lower()] = val
    return attrs


def get_tag_params(nodelist, tokens, context):
    """
    Get attributes and body from a custom template tag
    This must be called from the render function of a Node, because I can't find any other way to get the context

    Returns attributes and body/content.
    Example:

        {% sometag name="Mike" title=somevar checked %}
            This is some html content...
        {% end_sometag %}

    Would return:
    {'name': "Mike", 'title': "Resolved Title", 'checked': "checked"},  "This is some html content..."
    """
    attrs = process_args(tokens, context)
    body = nodelist.render(context)
    return attrs, body
