import logging
from django.conf import settings

logger = logging.getLogger('profiles')


def get_country_language(country):
    logger.debug('Getting language for country {}'.format(country))
    if country == 'IT':
        return 'it'
    elif country == 'BR' or country == 'PT':
        return 'pt'
    elif country == 'ES':
        return 'es'

    return settings.LANGUAGE_CODE
