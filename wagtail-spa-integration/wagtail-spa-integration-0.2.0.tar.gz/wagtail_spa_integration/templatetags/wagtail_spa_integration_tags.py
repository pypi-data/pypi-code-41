from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def get_preview_code():
    return settings.PREVIEW_DRAFT_CODE
