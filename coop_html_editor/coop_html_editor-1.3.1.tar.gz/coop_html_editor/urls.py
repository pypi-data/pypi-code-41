# -*- coding:utf-8 -*-
"""urls"""

from django.conf.urls import url

from .views import html_editor_init, browser_urls, browser_images, ckeditor_config


urlpatterns = [
    url(r'^html-editor-init.js$', html_editor_init, name='html_editor_init'),
    url(r'^ckeditor_config.js$', ckeditor_config, name='ckeditor_config'),
    url(r'^browser-images.js$', browser_images, name='browser_images'),
    url(r'^browser-urls.js$', browser_urls, name='browser_urls'),

]
