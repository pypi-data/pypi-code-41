from django.contrib import admin

# Register your models here.
from . import models


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "_type", "content"]


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["mobile", "status"]
    list_filter = ["status"]
