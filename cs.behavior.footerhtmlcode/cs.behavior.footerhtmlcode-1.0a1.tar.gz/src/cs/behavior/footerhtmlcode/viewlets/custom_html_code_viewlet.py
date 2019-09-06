# -*- coding: utf-8 -*-

from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.multilingual.interfaces import ILanguageRootFolder
from Products.CMFPlone.interfaces import IPloneSiteRoot


class CustomHTMLCodeViewlet(ViewletBase):
    def update(self):
        self.html_code = self.get_html_code()

    def get_html_code(self):
        lrf = self.get_parent_lrf()
        if lrf is not None:
            return lrf.html

        return ""

    def get_parent_lrf(self):
        navigation_root = self.context
        while not (
            ILanguageRootFolder.providedBy(navigation_root)
            or IPloneSiteRoot.providedBy(navigation_root)
        ):
            navigation_root = api.portal.get_navigation_root(navigation_root)

        if ILanguageRootFolder.providedBy(navigation_root):
            return navigation_root

        return None

    def render(self):
        return super(CustomHTMLCodeViewlet, self).render()
