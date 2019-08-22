import re
from blogger.utils import string
from .base import Provider


class ManualProvider(Provider):
    def read(self, url, title_selector=None, content_selector=None):
        """
        Read content from a URL and return for processing to speech
        """
        if not title_selector or not content_selector:
            raise ValueError(
                "Missing --url-title-selector or --url-content-selector flags. These are required when using the manual content provider."
            )

        soup = self.download(url, soup=True)
        for pre in soup.find_all("pre"):
            pre.decompose()

        title = string.html_to_text(str(soup.find(**self._soup_selector(title_selector))))
        content = string.html_to_text(str(soup.find(**self._soup_selector(content_selector))))

        if not title or not content:
            raise ValueError("Could not find the title and content from article {}.".format(url))

        return "{}\n\n{}".format(title, content)

    def _soup_selector(self, selector):
        try:
            res = {"name": "", "class": []}
            parts = selector.replace(".", " .").replace("#", " #").split()

            res["name"] = parts.pop(0)
            for part in parts:
                if part[0] == ".":
                    res["class"].append(part[1:])
                elif part[0] == "#":
                    res["id"] = part[1:]
                else:
                    raise ValueError()

            return res
        except:
            raise ValueError("Could not parse your selector {}. Make sure it's in the format tag#id.class-1.class-2")
