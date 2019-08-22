from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase

from djangocms_parallaxjs.models import ParallaxWindow


@plugin_pool.register_plugin
class ParallaxWindowPlugin(CMSPluginBase):
    model = ParallaxWindow
    render_template = 'djangocms_parallaxjs/parallax.html'
    name = _('Parallax Window')
    allow_children = True
    fieldsets = (
        (None, {
            'fields': (
                'id_name',
                'css_classes',
            )
        }),
        (_('Parallax options'), {
            'fields': (
                'image_src',
                ('natural_width', 'natural_height'),
                ('position_x', 'position_y'),
                'speed',
                'z_index',
                'bleed',
                ('ios_fix', 'android_fix'),
                'thumbnail_option'
            ),
        })
    )
