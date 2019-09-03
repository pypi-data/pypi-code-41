from django import template

import seed_control_interface_service

register = template.Library()


@register.simple_tag
def current_version():
    return seed_control_interface_service.__version__
