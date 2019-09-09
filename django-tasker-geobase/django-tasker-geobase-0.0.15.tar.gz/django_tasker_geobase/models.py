from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Geobase(MPTTModel):
    TYPE = [
        (1, _('Country')),      # страна
        (2, _('Province')),     # область
        (3, _('Area')),         # район области
        (4, _('Locality')),     # населённый пункт: город / поселок / деревня / село и т. п.
        (5, _('District')),     # Россия, Москва, Северо-Восточный административный округ
        (6, _('Street')),       # улица
        (7, _('House')),        # отдельный дом
        (8, _('Hydro')),        # река / озеро / ручей / водохранилище и т. п.
        (9, _('Railway')),      # ж.д. станция
        (10, _('Route')),       # линия метро / шоссе / ж.д. линия
        (11, _('Vegetation')),  # лес / парк / сад и т. п.
        (12, _('Airport')),     # Россия, Московская область, аэропорт Домодедово
        (13, _('Metro')),       # Россия, Москва, Филевская линия, метро Арбатская
        (14, _('Other')),       # Россия, Свердловская область, Екатеринбург, Шабур остров
        (15, _('Apartment')),   # Квартира
    ]

    en = models.CharField(max_length=200, db_index=True)
    ru = models.CharField(max_length=200, db_index=True)
    type = models.SmallIntegerField(choices=TYPE, null=True)
    timezone = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("timezone"))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_("Longitude"))
    zipcode = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Zipcode"))
    openweathermap = models.IntegerField(null=True, blank=True, verbose_name=_("Open Weather Map"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['en']

    class Meta:
        verbose_name = "Geobase"
        verbose_name_plural = "Geobase"

    def __str__(self):
        return "{en} - {ru}".format(en=self.en, ru=self.ru)

    def get(self) -> dict:
        data = {}
        for item in self.get_family():
            key = str(item.get_type_display()).lower()
            data[key] = {
                'id': item.id,
                'ru': item.ru,
                'en': item.en,
                'latitude': item.latitude,
                'longitude': item.longitude,
                'zipcode': item.zipcode,
                'timezone': item.timezone,
                'openweathermap': item.openweathermap
            }
        return data


class ZipcodePostOffice(models.Model):
    zipcode = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Zipcode"))
    geobase = models.ForeignKey(Geobase, on_delete=models.CASCADE, null=True, blank=True)


class Weather(models.Model):
    geobase = models.ForeignKey(Geobase, on_delete=models.CASCADE, null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(null=True, blank=True, verbose_name=_("Temperature celsius"))
    temperature_min = models.FloatField(null=True, blank=True, verbose_name=_("Temperature celsius min"))
    temperature_max = models.FloatField(null=True, blank=True, verbose_name=_("Temperature celsius max"))
    pressure = models.FloatField(null=True, blank=True, verbose_name=_("Atmospheric pressure (hPa)"))
    humidity = models.FloatField(null=True, blank=True, verbose_name=_("Humidity (%)"))
    visibility = models.FloatField(null=True, blank=True, verbose_name=_("Visibility (meter)"))
    wind_speed = models.FloatField(null=True, blank=True, verbose_name=_("Wind speed (mps)"))
    wind_degrees = models.FloatField(null=True, blank=True, verbose_name=_("Wind degrees (meter/sec)"))
    clouds = models.FloatField(null=True, blank=True, verbose_name=_("Cloudiness (%)"))
