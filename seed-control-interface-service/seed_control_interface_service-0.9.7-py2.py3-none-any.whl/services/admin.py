from django.contrib import admin

from .models import Service, Status, UserServiceToken


class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "id", "name", "url", "up",
        "created_at", "updated_at", "created_by", "updated_by"]
    list_filter = ["name", "created_at", "updated_at"]


class StatusAdmin(admin.ModelAdmin):
    list_display = [
        "id", "service", "up", "created_at"]
    list_filter = ["up", "created_at", "service"]


class UserServiceTokenAdmin(admin.ModelAdmin):
    list_display = [
        "user_id", "email", "service", "token", "created_at", "updated_at"]
    list_filter = ["user_id", "created_at", "service"]


admin.site.register(UserServiceToken, UserServiceTokenAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Status, StatusAdmin)
