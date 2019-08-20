from django.contrib.syndication.views import Feed
from django.template.defaultfilters import striptags
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import escape
from django.utils.http import urlquote
from funcy import last

from .settings import LOGO_URL, SQUARE_LOGO_URL


class CustomFeedGenerator(Rss201rev2Feed):
    content_type = 'text/xml; charset=utf-8'

    def __init__(self, title, link, description, **kwargs):
        super().__init__(title, link, description, **kwargs)
        # For removing atom link from xml document
        self.feed['feed_url'] = None

    def rss_attributes(self):
        return {
            'xmlns:yandex': 'https://news.yandex.ru',
            'xmlns:media': 'https://search.yahoo.com/mrss/',
            'version': self._version,
        }

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        logo = self.feed.get('logo')
        logo_square = self.feed.get('logo_square')

        if logo:
            handler.addQuickElement('yandex:logo', logo)

        if logo_square:
            handler.addQuickElement(
                'yandex:logo',
                logo_square,
                {'type': 'square'},
            )

    def add_item_elements(self, handler, item):
        super(CustomFeedGenerator, self).add_item_elements(handler, item)
        handler.addQuickElement('yandex:full-text', item['content'])

        images = item.get('images', [])

        for image in images:
            handler.addQuickElement('enclosure', '', {
                'url': image.get('url'),
                'type': image.get('type'),
            })


class ZenGenerator(CustomFeedGenerator):
    def rss_attributes(self):
        return {
            'xmlns:yandex': 'http://news.yandex.ru',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
            'version': self._version,
        }

    def add_item_elements(self, handler, item):
        super(ZenGenerator, self).add_item_elements(handler, item)
        handler.addQuickElement("content:encoded", "<![CDATA[%s]]>" % striptags(item["content"]))


class MailFeedGenerator(CustomFeedGenerator):
    def rss_attributes(self):
        return {
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
            'version': self._version,
        }

    def add_item_elements(self, handler, item):
        super(MailFeedGenerator, self).add_item_elements(handler, item)
        handler.addQuickElement("amplink", '{}amp/'.format(item["link"]))


class CustomFeed(Feed):
    feed_type = CustomFeedGenerator
    model = None
    items_per_feed = 20

    def items(self):
        return self.model.objects.get_published()[:self.items_per_feed]

    def feed_extra_kwargs(self, obj):
        kwargs = super().feed_extra_kwargs(obj)

        if LOGO_URL:
            kwargs['logo'] = self.get_with_domain(LOGO_URL)

        if SQUARE_LOGO_URL:
            kwargs['logo_square'] = self.get_with_domain(SQUARE_LOGO_URL)

        return kwargs

    def item_title(self, item):
        return escape(item.title)

    def item_description(self, item):
        return escape(striptags(item.description)) if item.description \
            else escape(striptags(item.content))

    def item_pubdate(self, item):
        return item.publication_date

    def item_author_name(self, item):
        return item.owner.get_full_name() if item.owner else None

    def item_author_email(self, item):
        return item.owner.email if item.owner else None

    def item_extra_kwargs(self, item):
        kwargs = super().item_extra_kwargs(item)

        # add images for <enclosure> tags
        images = self.item_images(item)

        kwargs.update({
            'content': escape(striptags(self.item_content(item))),
            'images': self._prepare_item_images(images),
        })
        return kwargs

    def _prepare_item_images(self, images):
        return [self._prepare_item_image(image) for image in images]

    def _prepare_item_image(self, image):
        extensions = last(image.name.split('.')).lower()
        image_url = urlquote(image.url).replace('%3A', ':')

        return {
            'image': image,
            'url': self.get_with_domain(image_url),
            'type': 'image/{}'.format(extensions.replace('jpg', 'jpeg')),
        }

    def item_images(self, item):
        """
        Return item images fields.
        """
        return []

    def item_content(self, item):
        return getattr(item, 'content', '')

    def get_with_domain(self, link):
        site = get_current_site(self.request)
        return add_domain(site.domain, link, self.request.is_secure)

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)
