from django.conf import settings
from django.template import Library

register = Library()
ri = register.inclusion_tag


def clutch_tag(context, company_id=None):
    if company_id is None:
        company_id = getattr(settings, 'CLUTCH_COMPANY_ID', None)

    context['company_id'] = company_id

    return context


ri("clutch/clutch.html", name='clutch', takes_context=True)(clutch_tag)