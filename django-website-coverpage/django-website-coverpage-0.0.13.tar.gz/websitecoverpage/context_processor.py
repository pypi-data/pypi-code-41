import math

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from websitecoverpage.models import WebsiteCoverPage


def websitecoverpage(request):
    config = getattr(settings, 'WEBSITE_COVERPAGE', {})

    # bail if cookie already set, i.e. if the user has already
    # seen the coverpage we don't want to show it again
    cookie_name = config.get('cookie_name', 'coverpage')
    if cookie_name in request.COOKIES:
        # coverpage cookie exists: the user has already
        # seen the coverpage so no need to display it again
        return {}

    # bail if not a non-Ajax GET request
    if request.method != 'GET' or request.is_ajax():
        return {}

    # get ignore_urls
    ignore_urls = config.get('ignore_urls', '[]') + [
        '/favicon.ico',
        '/robots.txt'
    ]
    for ig in ignore_urls:
        if request.path.startswith(ig):
            return {}

    # ignore common bots
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    bots = [
        '360spider',
        'adsbot-google',
        'ahrefs',
        'apachebench', # not a bot, but it can go here
        'archive.org',
        'baiduspider',
        'bingbot',
        'bingpreview',
        'dotbot',
        'duckduckgo',
        'duckduckbot',
        'exabot',
        'facebook',
        'feedfetcher-google',
        'googlebot',
        'googleimageproxy',
        'ia_archiver',
        'mediapartners-google',
        'mj12bot',
        'msnbot',
        'panscient.com',
        'pinterest',
        'slackbot',
        'slurp',
        'sogou',
        'surveybot',
        'twitterbot',
        'voilabot',
        'yahoo-mmcrawler',
        'yahoomailproxy',
        'yandexbot'
    ]
    for bot in bots:
        if bot in ua:
            return {}

    # attempt to find from cache
    cache_key = config.get('cache_key', 'website-coverpage')
    coverpage = cache.get(cache_key, None)
    if coverpage is None:
        # find next available page from the database
        now = timezone.now()
        page = WebsiteCoverPage.objects \
                .filter(end_datetime__gt=now) \
                .order_by('start_datetime', 'end_datetime') \
                .first()

        if page is None:
            # there are no valid pages in the database
            # set a long, empty cache
            coverpage = {}
            cache_timeout = 60 * 60 * 24 * 28
        else:
            if page.start_datetime < now:
                # a coverpage is active
                # cache the results until it's end_datetime
                coverpage = {
                    'websitecoverpage': {
                        'cookie_name': cookie_name,
                        'html': page.html,
                        'style': page.style
                    }
                }
                cache_timeout = (page.end_datetime - now).total_seconds()
            else:
                # the next page is in the future
                # set an empty cache until that time
                coverpage = {}
                cache_timeout = (page.start_datetime - now).total_seconds()

        # save to cache
        cache.set(cache_key, coverpage, math.ceil(cache_timeout))

    # return
    return coverpage