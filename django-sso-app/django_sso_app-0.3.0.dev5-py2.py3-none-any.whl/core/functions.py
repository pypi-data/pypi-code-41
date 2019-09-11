import logging

logger = logging.getLogger('django_sso_app.core')


def get_country_language(country):
    logger.debug('Getting language for country {}'.format(country))
    if country == 'IT':
        return 'it'
    elif country == 'BR' or country == 'PT':
        return 'pt'
    elif country == 'ES':
        return 'es'

    return 'en-gb'
