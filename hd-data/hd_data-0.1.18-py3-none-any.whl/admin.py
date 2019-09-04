from django.contrib import admin
from .models import Contact

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'clientlocation', 'date', 'captain', 'collective', 'status']

admin.site.register(Contact, ContactAdmin)
