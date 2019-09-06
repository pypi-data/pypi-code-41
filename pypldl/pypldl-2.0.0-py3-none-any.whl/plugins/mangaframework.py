import re
import os
import logging
from collections import OrderedDict
from .manga import _MangaTask

logger = logging.getLogger('mangaframework')


def normalize_title(title):
    """Normalize a manga title"""
    return title.lower().replace(' ', '_').replace('-', '_')


class _MangaFrameworkTask(_MangaTask):
    """
    Download manga chapters on several websites based on the same framework.

    Subclasses must define the following class attributes:
      hostname
      handler_name

    """

    hostname = None


    @classmethod
    def match_uri(cls, uri): 
        return re.match(r"^(?:https?:)?//%s/(?P<type>manga|chapter)/(?P<title>[^/]+)(?:/(?P<chapter>[^/]+))?$" % cls.hostname, uri)

    @classmethod
    def from_uri(cls, uri):
        m = cls.match_uri(uri)
        if m is None:
            return None
        if m.group('chapter'):
            chapters = [m.group('chapter')]
        else:
            chapters = None
        return cls(title=m.group('title'), chapters=chapters)

    @classmethod
    def build_manga_url(cls, title):
        return f"http://{cls.hostname}/manga/{title}"

    @classmethod
    def build_chapter_url(cls, title, chapter):
        return f"http://{cls.hostname}/chapter/{title}/{chapter}"

    @classmethod
    def get_manga_info(cls, dm, title):
        soup = dm.request_soup(cls.build_manga_url(normalize_title(title)))
        if soup.find(text=re.compile("Sorry, the page you have requested cannot be found.")):
            return False

        # get pretty title
        s = soup.find('meta', property='og:title')['content']
        pretty_title = s.split(' Manga Online')[0]
        # get path title
        s = soup.find('meta', property='og:url')['content']
        path_title = cls.match_uri(s).group('title')

        chapters = OrderedDict()
        for e in soup.find('div', class_='chapter-list').find_all('a')[::-1]:
            chapter_name = e.text.strip()
            path = cls.match_uri(e['href']).group('chapter')
            chapters[chapter_name] = path

        return {'title': pretty_title, 'path': path_title, 'chapters': chapters}


    def get_chapter_pages_paths(self, chapter):
        soup = self.request_soup(self.build_chapter_url(self.title, chapter))
        pages = []
        for e in soup.find('div', id='vungdoc').find_all('img'):
            pages.append(e['src'])
        return pages

    def get_image_url(self, page):
        return page


class MangakakalotTask(_MangaFrameworkTask):
    handler_name = 'mangakakalot'
    hostname = "mangakakalot.com"

class ManganeloTask(_MangaFrameworkTask):
    handler_name = 'manganelo'
    hostname = "manganelo.com"

