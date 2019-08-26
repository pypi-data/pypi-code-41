from datetime import datetime, timedelta
from django.contrib.sitemaps import Sitemap


class BasePublicationSitemap(Sitemap):
    model = None

    def items(self):
        return self.model.objects.get_published()

    def lastmod(self, obj):
        return obj.publication_date


class BaseGoogleNewsSitemap(Sitemap):
    protocol = 'https'
    limit = 1000
    model = None

    def items(self):
        date = datetime.now() - timedelta(days=2)
        return self.model.objects.get_published().filter(publication_date__gte=date)
