"""
Extract article links and article metadata from nytimes.com

"""

import re

from soupstars import parse


@parse
def title(self):
    """
    The title of the article.
    """

    return self.h1.text

@parse
def author(self):
    """
    The author(s) of the article.
    """

    return self.find(attrs={'itemprop': 'author creator'}).text
