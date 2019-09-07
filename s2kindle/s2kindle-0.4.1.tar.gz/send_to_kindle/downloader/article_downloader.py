from pathlib import Path

import requests
import tldextract
from bs4 import BeautifulSoup

from send_to_kindle.downloader.article import Article
from send_to_kindle.downloader.content_extractor import (
    ContentExtractor,
    DevToExtractor,
    MediumExtractor,
)

ROOT = Path(__file__).parent.parent.resolve()
TEMPLATE = Path(ROOT, "assets", "article-template.html")
DEFAULT_EXTRACTOR = ContentExtractor()
REGISTERED_EXTRACTORS = {"medium.com": MediumExtractor(), "dev.to": DevToExtractor()}


def get_extractor(host):
    if host in REGISTERED_EXTRACTORS:
        return REGISTERED_EXTRACTORS[host]
    return DEFAULT_EXTRACTOR


def load_template():
    with open(TEMPLATE) as template_reader:
        article_template = BeautifulSoup(template_reader.read())
        return article_template


def extract_content(content_extractor, soup):
    return content_extractor.extract(soup)


def extract_images(content_extractor, article_soup):
    return content_extractor.replace_images(article_soup)


def get_article(url):
    tld_extractor = tldextract.TLDExtract(suffix_list_urls=None)
    url_parsed = tld_extractor(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    template = load_template()
    article = Article(url=url, title=soup.title.text.strip(), template=template)
    extractor = get_extractor(f"{url_parsed.domain}.{url_parsed.suffix}")
    soup = extract_content(extractor, soup)
    content, img_map = extract_images(extractor, soup)
    article.content = content
    article.image_map = img_map
    return article
