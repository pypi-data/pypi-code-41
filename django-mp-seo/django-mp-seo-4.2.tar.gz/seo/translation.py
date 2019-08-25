
from modeltranslation.translator import translator

from seo.models import PageMeta


translator.register(PageMeta, fields=[
    'title', 'keywords', 'description', 'breadcrumb', 'header'])
