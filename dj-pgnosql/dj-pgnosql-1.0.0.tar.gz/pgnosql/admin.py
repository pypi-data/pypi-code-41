from django.contrib import admin
from .models import KV

class KVAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'created_date', 'modified_date',)
    search_fields = ('key','value',)

admin.site.register(KV, KVAdmin)
