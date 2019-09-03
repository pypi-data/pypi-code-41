from django.contrib import admin

from .models import Campaign


class CampaignAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = (
        'campaign_id',
        'name',
        'status',
        'total_users',
    )


admin.site.register(Campaign, CampaignAdmin)
