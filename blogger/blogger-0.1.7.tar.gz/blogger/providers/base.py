from abc import ABC, abstractmethod
import requests
from click import ClickException
from bs4 import BeautifulSoup


class Provider(ABC):
    """
    Base class for handling external content providers. The content providers
    are typically going to be Blogs.

    The concrete implementation of providers will be responsible for telling
    `blogger` how to handle parsing raw content requested from a URL. The
    raw content is assumed to be formatted as HTML for now.
    """

    @abstractmethod
    def read(self, url, title_selector=None, content_selector=None):
        """
        Read content from a URL and return for processing to speech
        """

    def download(self, url, soup=False):
        """
        Helper method for downloading the raw content from a URL.

        This exists instead of calling `requests` directly so that we can
        abstract up the error handling into a single method.
        """
        try:
            res = requests.get(url)
        except Exception as e:
            print(e)
            raise ClickException("The url {} is not accessible.".format(url))

        if not res.ok:
            raise ClickException("The url {} returned a bad status code [{}].".format(url, res.status_code))

        if soup:
            return BeautifulSoup(res.content, features="lxml")
        return res.content
