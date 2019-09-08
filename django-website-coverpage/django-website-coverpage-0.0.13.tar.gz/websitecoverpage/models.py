from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext as _


class WebsiteCoverPage(models.Model):
    DEFAULT_HTML = """<table onclick="websiteCoverPage.close()">
  <tr>
    <td>
      <img src="/path/to/image.png" />
    </td>
  </tr>
</table>"""

    DEFAULT_STYLE = """#websitecoverpage {
  background: rgba(0, 0, 0, 0.5);
  height: 100vh;
  left: 0;
  position: fixed;
  right: 0;
  top: 0;
  z-index: 9999998;
}

#websitecoverpage table, tr {
  height: 100vh;
  width: 100%;
}

#websitecoverpage td {
  padding: 25px;
  text-align: center;
  vertical-align: middle;
}

#websitecoverpage img {
  box-shadow: 0px 0px 25px 5px rgba(0, 0, 0, 0.5);
  cursor: pointer;
  max-width: 800px;
  width: 100%;
}"""

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    html = models.TextField(blank=True, default=DEFAULT_HTML, verbose_name=_('HTML'))
    style = models.TextField(blank=True, default=DEFAULT_STYLE, verbose_name=_('CSS'))
    start_datetime = models.DateTimeField(verbose_name=_('Start time'))
    end_datetime = models.DateTimeField(verbose_name=_('End time'))

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.remove_cache()

    def save(self, *args, **kwargs):
        # force start to be before end
        if self.start_datetime > self.end_datetime:
            tmp = self.start_datetime
            self.start_datetime = self.end_datetime
            self.end_datetime = tmp

        super().save(*args, **kwargs)
        self.remove_cache()

    def remove_cache(self):
        config = getattr(settings, 'WEBSITE_COVERPAGE', {})
        cache_key = config.get('cache_key', 'website-coverpage')
        cache.delete(cache_key)

    class Meta:
        verbose_name = _('Cover page')
        verbose_name_plural = _('Cover pages')
        ordering = ('start_datetime', 'end_datetime', 'name')