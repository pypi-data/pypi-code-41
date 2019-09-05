from django.db.models import Q
from django.template.loader import select_template
from django.utils import translation

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django.utils.translation import ugettext_lazy as _

from .models import ChildPagePreviewPlugin, SiblingPagePreviewPlugin


class PageImagePluginBase(CMSPluginBase):
    def render(self, context, instance, placeholder):
        self.render_template = select_template((
            self.TEMPLATE_NAME % instance.style,
            self.render_template,
        ))
        request = context['request']
        pages = self.get_pages(context, instance, placeholder)

        pages = pages.published(site=context['request'].site, language=translation.get_language())
        pages = pages.filter(
            Q(imageextension__show_preview=True) |
            Q(imageextension__isnull=True)
        )

        context['pages'] = pages
        # support for legacy templates
        context['subpages'] = context['pages']
        context['instance'] = instance
        context['current_page'] = context['request'].current_page
        return context


class CMSChildPagePreviewPlugin(PageImagePluginBase):
    model = ChildPagePreviewPlugin
    name = _("Child Page Preview")

    TEMPLATE_NAME = "djangocms_page_image/plugins/%s.html"
    render_template = TEMPLATE_NAME % 'child_page_preview'

    #Search
    search_fields = []

    def get_pages(self, context, instance, placeholder):
        return context['request'].current_page.get_child_pages()
plugin_pool.register_plugin(CMSChildPagePreviewPlugin)


class CMSSiblingPagePreviewPlugin(PageImagePluginBase):
    model = SiblingPagePreviewPlugin
    name = _("Sibling Page Preview")

    TEMPLATE_NAME = "djangocms_page_image/plugins/%s.html"
    render_template = TEMPLATE_NAME % 'sibling_page_preview'

    def get_pages(self, context, instance, placeholder):
        return context['request'].current_page.parent_page.get_child_pages()
plugin_pool.register_plugin(CMSSiblingPagePreviewPlugin)
