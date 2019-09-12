from django.contrib import admin

from orionframework.media.settings import Document, Image


class DocumentAdmin(admin.ModelAdmin):
    model = Document
    list_display = ["id", "title", "original_filename", "file", "parent_type", "parent_id"]
    search_fields = ["title", "original_filename"]


class ImageAdmin(admin.ModelAdmin):
    model = Image
    list_display = ["id", "title", "original_filename", "file", "parent_type", "parent_id", "width", "height"]
    search_fields = ["title", "original_filename"]
