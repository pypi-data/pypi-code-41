from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext as _

from websitecoverpage.models import WebsiteCoverPage


class WebsiteCoverPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_datetime', 'end_datetime', 'date_status')

    def date_status(self, obj):
        now = timezone.now()
        if obj.end_datetime <= now:
            return _('Past')
        elif obj.start_datetime > now:
            return _('Future')
        else:
            return _('Active')
    date_status.short_description = _('Status')

admin.site.register(WebsiteCoverPage, WebsiteCoverPageAdmin)