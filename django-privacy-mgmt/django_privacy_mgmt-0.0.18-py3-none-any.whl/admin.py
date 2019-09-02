# -*- coding: utf-8 -*-
from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import TrackingItem


class TrackingItemAdmin(TranslatableAdmin):
    list_display = ('__unicode__', 'category', )
    search_fields = ('name', )
    list_filter = ('category', )

    filter_vertical = ('site', )


admin.site.register(TrackingItem, TrackingItemAdmin)
