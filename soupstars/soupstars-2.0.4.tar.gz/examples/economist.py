"""
Extract metadata from economist index and article pages

"""

import dateparser

from soupstars import parse


@parse
def date(soup):
    "The date of the article"

    string = self.find(attrs={'class': 'print-edition__main-title-header__date'})
    text = string.text.strip()
    return dateparser.parse(text).date()

@parse
def articles(soup):
    "The paths of the article urls"

    spans = self.find_all('span', attrs={'class': 'print-edition__link-title'})
    return [span.parent['href'] for span in spans]

@parse
def num_articles(soup):
    "The number of articles found on the page"

    return len(article_paths(soup))
