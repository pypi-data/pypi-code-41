from django.contrib import admin

from . import models as m


# Register your models here.

@admin.register(m.InterfaceHistory)
class InterfaceHistoryAdmin(admin.ModelAdmin):
    change_form_template = 'weblogtools/change_form.html'
    list_display = (
        'id', 'created', 'service_name', 'time_it', 'http_status', 'http_response_content',)
    date_hierarchy = 'created'
    list_filter = ('service_name', 'http_status')
    fields = (
        ('service_name', 'url'),
        ('http_status', 'time_it', 'created'),
        ('payload',),
        ('http_response_header', 'http_response_content'),
        ('http_error',)
    )
    ordering = ('-created',)
    search_fields = ('service_name', 'http_response_content', 'input_common', 'input_service')
    list_display_links = ('id', 'http_response_content')

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
