import logging
import os
import re
from pathlib import Path
from typing import List

import youtube_dl
from bs4 import BeautifulSoup
from furl import furl
from ordered_set import OrderedSet
from youtube_dl.utils import DEFAULT_OUTTMPL

LEVEL = logging.DEBUG if os.getenv("DWL_DEBUG") in ['1', 'true'] else 0
logging.basicConfig(level=LEVEL)
log = logging.getLogger(__name__)


CONFIG = {
    'src_dir': Path.home() / 'Downloads',
    'src_file_name': 'Watch Later Playlist - YouTube.html',
    'output_template': os.path.join(
        Path.home() / 'Downloads', DEFAULT_OUTTMPL
    ),
}


def path2content(path: str) -> str:
    with open(path) as f:
        content = f.read()
    log.debug("content length {}".format(len(content)))
    return content


def find_links(html_page) -> List[str]:
    soup = BeautifulSoup(html_page, 'html.parser')
    links = OrderedSet()
    a_tags = soup.find_all('a', attrs={'href': re.compile('list=WL&index=')})
    for a_tag in a_tags:
        href = a_tag.get('href')
        links.add(href)
    log.debug(f"found links {links}")
    return list(links)


def clean_url(dirty_url: str, rm_args: List[str] = None) -> str:
    rm_args = rm_args or ['t', 'index', 'list']
    url = furl(dirty_url)
    for rm_arg in rm_args:
        try:
            del url.args[rm_arg]
        except KeyError:
            pass
    return str(url)


def clean_urls(dirty_urls: List[str]) -> List[str]:
    cleaned_urls = [clean_url(url) for url in dirty_urls]
    log.debug(f"cleaned urls {cleaned_urls}")
    return cleaned_urls


def download_video(urls: List[str], ydl_opts=None):
    ydl_opts = ydl_opts or {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        log.debug(f"downloading {urls!r}")
        ydl.download(urls)


def main():
    path = CONFIG['src_dir'] / CONFIG['src_file_name']
    html_page = path2content(path)
    urls = find_links(html_page)
    urls = clean_urls(urls)
    download_video(urls, {'outtmpl': CONFIG.get('output_template')})


if __name__ == "__main__":
    main()
