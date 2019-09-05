from django.contrib import admin

from .models import Spectrum, Peak

admin.site.register(Spectrum)
admin.site.register(Peak)
