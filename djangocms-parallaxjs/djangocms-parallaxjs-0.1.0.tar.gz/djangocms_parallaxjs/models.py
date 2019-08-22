from cms.models import CMSPlugin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from filer.fields.image import FilerImageField
from filer.models import ThumbnailOption


class ParallaxWindow(CMSPlugin):
    id_name = models.CharField(max_length=255, blank=True)
    css_classes = models.CharField(max_length=255, blank=True)
    image_src = FilerImageField()
    natural_width = models.PositiveSmallIntegerField(null=True, blank=True)
    natural_height = models.PositiveSmallIntegerField(null=True, blank=True)
    position_x = models.CharField(max_length=10, blank=True)
    position_y = models.CharField(max_length=10, blank=True)
    speed = models.FloatField(null=True, blank=True, validators=[
        MinValueValidator(0.0),
        MaxValueValidator(1.0)
    ])
    z_index = models.SmallIntegerField(null=True, blank=True, validators = [MaxValueValidator(-1)])
    bleed = models.SmallIntegerField(null=True, blank=True)
    ios_fix = models.NullBooleanField(null=True, blank=True)
    android_fix = models.NullBooleanField(null=True, blank=True)
    thumbnail_option = models.ForeignKey(ThumbnailOption, null=True, blank=True)

    def image_url(self):
        return (self.thumbnail_option and self.image_src.easy_thumbnails_thumbnailer.get_thumbnail(self.thumbnail_option.as_dict) or self.image_src).url