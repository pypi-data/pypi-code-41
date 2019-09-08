from django.utils import timezone
from django.utils.translation import gettext as _

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import WebsiteCoverPage


class WebsiteCoverPageAdmin(ModelAdmin):
    model = WebsiteCoverPage
    menu_icon = 'pick'
    add_to_settings_menu = True
    exclude_from_explorer = True
    list_display = ('name', 'start_datetime', 'end_datetime', 'date_status')
    search_fields = ('name',)

    def date_status(self, obj):
        now = timezone.now()
        if obj.end_datetime <= now:
            return _('Past')
        elif obj.start_datetime > now:
            return _('Future')
        else:
            return _('Active')
    date_status.short_description = _('Status')

modeladmin_register(WebsiteCoverPageAdmin)