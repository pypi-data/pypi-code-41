# -*- coding: utf-8 -*-

from cs.behavior.footerhtmlcode import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IFooterHTMLCodeMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IFooterHTMLCode(model.Schema):
    """
    """

    html = schema.Text(
        title=_(u"Custom HTML code"),
        description=_(
            u"Enter your custom HTML code (usualy JS code) that will be shown in the footer of all pages below this folder"
        ),
        default=u"",
        required=False,
        readonly=False,
    )


@implementer(IFooterHTMLCode)
@adapter(IFooterHTMLCodeMarker)
class FooterHTMLCode(object):
    def __init__(self, context):
        self.context = context

    @property
    def html(self):
        if hasattr(self.context, "html"):
            return self.context.html
        return None

    @html.setter
    def html(self, value):
        self.context.html = value
