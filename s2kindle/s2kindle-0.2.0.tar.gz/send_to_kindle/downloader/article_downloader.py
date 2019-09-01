from pathlib import Path

import requests
from bs4 import BeautifulSoup

from send_to_kindle.downloader.article import Article
from send_to_kindle.downloader.content_extractor import MediumExtractor

ROOT = Path(__file__).parent.parent.resolve()
TEMPLATE = Path(ROOT, "assets", "article-template.html")


def load_template():
    with open(TEMPLATE) as template_reader:
        article_template = BeautifulSoup(template_reader.read())
        return article_template


def extract_content(soup):
    content_extractor = MediumExtractor()
    return content_extractor.extract(soup)


def extract_images(article_soup):
    content_extractor = MediumExtractor()
    return content_extractor.replace_images(article_soup)


def get_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    template = load_template()
    article = Article(url=url, title=soup.title.text.strip(), template=template)
    soup = extract_content(soup)
    content, img_map = extract_images(soup)
    article.content = content
    article.image_map = img_map
    return article
