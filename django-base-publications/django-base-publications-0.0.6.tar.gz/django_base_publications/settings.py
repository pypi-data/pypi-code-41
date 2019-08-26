from django.conf import settings


LOGO_URL = getattr(settings, 'PUBLICATIONS_RSS_LOGO', None)
SQUARE_LOGO_URL = getattr(settings, 'PUBLICATIONS_RSS_SQUARE_LOGO', None)
