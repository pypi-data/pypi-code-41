from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import ImageExtension

class ImageExtensionAdmin(PageExtensionAdmin):
    pass
admin.site.register(ImageExtension, ImageExtensionAdmin)
