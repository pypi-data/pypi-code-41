
from importlib import import_module

from django.apps import apps
from django.contrib import admin

from import_export.resources import ModelResource
from import_export.admin import ImportExportMixin, ExportActionMixin

from seo.models import PageMeta, RedirectRecord, ErrorRecord


def _get_page_meta_admin_base_class():

    if apps.is_installed('modeltranslation'):
        return import_module('modeltranslation.admin').TranslationAdmin

    return admin.ModelAdmin


class PageMetaResource(ModelResource):
    class Meta:
        model = PageMeta
        exclude = ('id', )


class ImportExportAdmin(
        ImportExportMixin,
        ExportActionMixin):
    actions_on_bottom = False


@admin.register(PageMeta)
class PageMetaAdmin(ImportExportAdmin, _get_page_meta_admin_base_class()):
    resource_class = PageMetaResource
    list_display = ['url', 'title', 'robots']
    list_editable = ['robots']
    list_filter = ['robots']
    search_fields = ['url', 'title']


@admin.register(RedirectRecord)
class RedirectRecordAdmin(ImportExportAdmin, admin.ModelAdmin):

    list_display = ['id', 'old_path', 'new_path']
    list_display_links = ['old_path', 'new_path']
    search_fields = ['old_path', 'new_path']


@admin.register(ErrorRecord)
class ErrorRecordAdmin(ExportActionMixin, admin.ModelAdmin):

    list_display = [
        'id', 'path', 'method', 'status_code', 'referrer', 'created']
    list_display_links = ['path']
    search_fields = ['path']
    list_filter = ['status_code']
