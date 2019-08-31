from django.conf import settings as site_settings


__all__ = [
    'CONTEXT_PROCESSORS',
    'MANAGEMENT_DOMAIN',
    'QUEUE'
]


QUEUE = getattr(site_settings, 'MAIL_RQ_QUEUE', 'default')
CONTEXT_PROCESSORS = getattr(site_settings, 'MAIL_CONTEXT_PROCESSORS', [])
MANAGEMENT_DOMAIN = getattr(
    site_settings,
    'MAIL_MANAGEMENT_DOMAIN',
    'example.com'
)
