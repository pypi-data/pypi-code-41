from django.conf import settings

SETTING_VARIABLE = getattr(settings, 'SETTING_VARIABLE', 'DEFAULT-value')