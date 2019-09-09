# -*- coding: utf-8
from django.contrib import admin

from . import models


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    model = models.File
    list_display = (
        'name', 'url', 'path', 'relative_path', 'type',
        'active', 'created', 'modified'
    )
    search_fields = ('name', 'description')
    list_filter = ('active', 'relative_path', 'type')
    prepopulated_fields = {'hash': ('name',)}
    save_as = True
