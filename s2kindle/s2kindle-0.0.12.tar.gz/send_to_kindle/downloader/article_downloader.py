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


def get_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    template = load_template()
    article = Article(url=url, title=soup.title.text.strip(), template=template)
    article.content = extract_content(soup)
    return article
