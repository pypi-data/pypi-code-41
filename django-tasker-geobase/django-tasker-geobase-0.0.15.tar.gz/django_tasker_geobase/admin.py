from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from . import models


class GeobaseAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('ru', 'type')


class WeatherAdmin(admin.ModelAdmin):
    list_display = (
        'geobase',
        'date_create',
        'temperature',
        'temperature_min',
        'temperature_max',
        'pressure',
        'humidity',
        'visibility',
        'wind_speed',
        'wind_degrees',
        'clouds',
    )


admin.site.register(models.Geobase, GeobaseAdmin)
admin.site.register(models.Weather, WeatherAdmin)
