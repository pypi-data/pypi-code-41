from blogger.utils import string
from .base import Provider


class MediumProvider(Provider):
    def read(self, url, title_selector=None, content_selector=None):
        """
        Read content from a URL and return for processing to speech
        """
        soup = self.download(url, soup=True)

        # Remove the header information from the article and all of the <pre>
        # tags which typically contain source code and are confusing to pass
        # through text to speech
        soup.find("article").find("div").find("section").find("div").find("div").decompose()
        for pre in soup.find_all("pre"):
            pre.decompose()

        title = string.html_to_text(str(soup.find("h1")))
        content = string.html_to_text(str(soup.find("article").find("div").find("section")))

        if not title or not content:
            raise ValueError("Could not find the title and content from article {}.".format(url))

        return "{}\n\n{}".format(title, content)
