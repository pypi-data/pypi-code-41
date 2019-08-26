""" Url router for the administration site
"""
from django.contrib import admin
from django.conf.urls import url
from core_schema_viewer_app.views.admin import views as admin_views, ajax as admin_ajax

admin_urls = [
    url(r'^schema-viewer$', admin_views.manage_template,
        name='core_schema_viewer_app_template'),
    url(r'^schema-viewer/toggle-visibility$', admin_ajax.toggle_template_schema_visibility,
        name='core_schema_viewer_app_toggle_visibility'),
    url(r'^schema-viewer/set-default$', admin_ajax.set_template_schema_default,
        name='core_schema_viewer_app_set_default'),
]


urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
