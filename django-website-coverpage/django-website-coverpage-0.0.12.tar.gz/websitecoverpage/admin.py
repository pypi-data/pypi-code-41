from django.contrib import admin
from django.utils import timezone

from websitecoverpage.models import WebsiteCoverPage


class WebsiteCoverPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_datetime', 'end_datetime', 'date_status')

    def date_status(self, obj):
        now = timezone.now()

        if obj.start_datetime > obj.end_datetime:
            return 'INVALID DATES'
        elif obj.end_datetime <= now:
            return 'Past'
        elif obj.start_datetime > now:
            return 'Future'
        else:
            return 'Active'
    date_status.short_description = 'Status'

admin.site.register(WebsiteCoverPage, WebsiteCoverPageAdmin)