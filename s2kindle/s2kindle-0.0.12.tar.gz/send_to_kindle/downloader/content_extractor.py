class ContentExtractor:
    def extract(self, soup):
        return str(soup)


class MediumExtractor(ContentExtractor):

    exclude_for_tag = {"img": {"src", "alt"}}

    def extract(self, soup):
        article = soup.find("article")
        self._remove_attrs(article)
        title_div = self._find_title_div(article)
        sub_title = self._find_subtitle(title_div)
        if sub_title:
            author_info = self._find_author_div(sub_title)
        else:
            author_info = self._find_author_div(title_div)
        author_info.extract()
        _ = [hr.extract() for hr in soup.find_all("hr")]
        for figure in article.find_all("figure"):
            tag = self._find_interesting_figure(figure)
            if tag and tag.name == "img":
                figure.replace_with(tag)
            else:
                figure.extract()
        return article

    def _find_interesting_figure(self, figure):
        if figure.find("iframe"):
            return None
        noscript = figure.find("noscript")
        if noscript:
            return noscript.find("img")
        return None

    def _remove_attrs(self, article):
        for tag in article.findAll(True):
            exclude = MediumExtractor.exclude_for_tag.get(tag.name, set())
            available_attrs = set(tag.attrs.keys())
            available_attrs.difference_update(exclude)
            for attr in available_attrs:
                tag.attrs.pop(attr)
        return article

    def _find_title_div(self, article):
        for section in article.find_all("section"):
            div = section.select("div > h1")
            if div:
                return div[0].parent
        return None

    def _find_subtitle(self, title_div):
        current = title_div.next
        while current:
            if current.name == "div":
                if current.find("h2"):
                    return current
                if current.find("div"):
                    return None
            current = current.next

    def _find_author_div(self, title_div):
        current = title_div.next
        while current:
            if current.name == "div":
                if current.find("div"):
                    return current
            current = current.next
