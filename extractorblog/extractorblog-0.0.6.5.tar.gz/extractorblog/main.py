from .extractor_blog import ExtractorBlog


class extractor(ExtractorBlog):
    def __init__(self, method, url, params=None, **kwargs):  # 先继承，再重构
        ExtractorBlog.__init__(self)  # 继承父类的构造方法
        if str(method).upper()=='GET':
            self.get(url, params=params, **kwargs)

    @property
    def getHtml(self):
        return self.html

    @property
    def getTitle(self):
        return self.title

    @property
    def getMarkdown(self):
        self.toMarkdown()
        return self.body_md

    @property
    def getBodyHtml(self):
        return self.body_html

    def getKeys(self, **kwargs):
        return self.getKeyWords(**kwargs)


if __name__ == '__main__':
    ua_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    }
    ET = extractor(method='get',url='https://statmodeling.stat.columbia.edu/2018/08/01/thanks-nvidia/', headers=ua_headers)

    print(ET.getHtml)
    print(ET.getMarkdown)
    print(ET.getKeys(n=10))
