from blogger.utils import string
from .base import Provider


class GhostProvider(Provider):
    def read(self, url, title_selector=None, content_selector=None):
        """
        Read content from a URL and return for processing to speech
        """
        soup = self.download(url, soup=True)
        for pre in soup.find_all("pre"):
            pre.decompose()

        title = string.html_to_text(str(soup.find("h1", "post-title")))
        content = string.html_to_text(str(soup.find("section", "post-content")))

        if not title or not content:
            raise ValueError("Could not find the title and content from article {}.".format(url))

        return "{}\n\n{}".format(title, content)
