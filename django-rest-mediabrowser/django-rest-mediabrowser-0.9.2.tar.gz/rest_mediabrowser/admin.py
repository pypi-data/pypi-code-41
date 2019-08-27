from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass


@admin.register(MediaImage)
class MediaImageAdmin(admin.ModelAdmin):
    pass


@admin.register(ImagePermission)
class ImagePermissionAdmin(admin.ModelAdmin):
    pass


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    pass


@admin.register(FilePermission)
class FilePermissionAdmin(admin.ModelAdmin):
    pass
