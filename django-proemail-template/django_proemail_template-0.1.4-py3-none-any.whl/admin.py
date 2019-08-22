from django.contrib import admin
from EmailTemplate.models import EmailTemplate
from django_summernote.admin import SummernoteModelAdminMixin


class EmailTemplateAdmin(SummernoteModelAdminMixin,admin.ModelAdmin):
    list_display = ['template_key', 'subject', 'from_email', 'to_email']
    save_as = True
    summernote_fields=('html_template',)


admin.site.register(EmailTemplate,EmailTemplateAdmin)
