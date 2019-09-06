import re
import os
import json
import logging
from collections import OrderedDict
from .manga import _MangaTask

HANDLER_NAME = 'batoto'
logger = logging.getLogger(HANDLER_NAME)


class BatotoTask(_MangaTask):
    """
    Download manga chapters on bato.to
    """

    handler_name = HANDLER_NAME
    base_url = "http://bato.to"
    title_re = re.compile(r"^https://bato.to/series/(\d+)$")
    chapter_re = re.compile(r"^https://bato.to/chapter/(\d+)$")

    @classmethod
    def from_uri(cls, uri):
        m = cls.title_re.match(uri)
        if m is not None:
            return cls(title=m.group(1))
        m = cls.chapter_re.match(uri)
        if m is not None:
            # hacky way to forward the chapter as title
            return cls(f"chapter:{m.group(1)}", chapters=[m.group(1)])
        return None

    @classmethod
    def build_manga_url(cls, title):
        return f"{cls.base_url}/series/{title}"

    @classmethod
    def build_chapter_url(cls, chapter):
        return f"{cls.base_url}/chapter/{chapter}"

    @classmethod
    def get_manga_info(cls, dm, title):
        if title.startswith("chapter:"):
            data = dm.request(cls.build_chapter_url(title.split(':', 1)[1])).data
            m = re.search(rb"var seriesId = (\d+);", data)
            title = m.group(1).decode('utf-8')
        soup = dm.request_soup(cls.build_manga_url(title))

        pretty_title = soup.find('title').text

        chapters = OrderedDict()
        # remove the manga title from the chapter name
        div = soup.find('div', id='series-page')
        div = div.find('div', class_='main')
        for i, e in enumerate(div.find_all('div', recursive=False)[::-1]):
            elink = e.find('a', class_='chapt')
            chapter_name = elink.find('b').text.strip()
            # don't use chapter IDs directly as they will result into bad names
            chapter_id = elink['href'].rsplit('/')[-1]
            chapters[chapter_name] = f"c{i:03}-{chapter_id}"

        return {'title': pretty_title, 'path': title, 'chapters': chapters}

    def get_chapter_pages_paths(self, chapter):
        chapter_id = chapter.split('-')[1]
        data = self.request(self.build_chapter_url(chapter_id)).data
        m = re.search(rb"var images = (\{.*?\});", data)
        images = json.loads(m.group(1))
        return images.values()

    def get_image_url(self, page):
        return page

