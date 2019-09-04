from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class HtmlBlockView(BaseBlock):
    template = ViewPageTemplateFile('templates/htmlblock.pt')

    def can_add(self):
        return api.user.has_permission('ftw.htmlblock: Add HTML block')
