from django.contrib import admin

from . import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["label", "notification_type", "user", "created_on"]


@admin.register(models.NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "label", "period", "active"]


@admin.register(models.UserNotificationConf)
class UserNotificationConfAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "period"]
