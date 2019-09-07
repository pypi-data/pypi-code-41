# coding=utf-8
from urllib.parse import urljoin, urlparse, urlunparse
from posixpath import normpath
import requests
import re
import chardet
from readability import Readability
import tomd


class ExtractorBlog:
    def __init__(self):
        self.body_html = None
        self.title = None
        self.html = None
        self.body_md = None
        self.body_text = None

    def filterHtml(self, html):
        filter_map = {
            'amp;': ''
        }
        for (key, value) in filter_map.items():
            html = html.replace(key, value)
        return html

    def replaceCharEntity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            key = sz.group('name')
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def filterTags(self, htmlstr):
        re_doctype = re.compile('<!DOCTYPE.*?>')
        re_nav = re.compile('<nav.+</nav>')
        re_cdata = re.compile('//<!\[CDATA\[.*//\]\]>', re.DOTALL)
        re_script = re.compile(
            '<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.DOTALL | re.I)
        re_style = re.compile(
            '<\s*style[^>]*>.*?<\s*/\s*style\s*>', re.DOTALL | re.I)
        re_textarea = re.compile(
            '<\s*textarea[^>]*>.*?<\s*/\s*textarea\s*>', re.DOTALL | re.I)
        re_br = re.compile('<br\s*?/?>')
        re_h = re.compile('</?\w+.*?>', re.DOTALL)
        re_comment = re.compile('<!--.*?-->', re.DOTALL)
        re_space = re.compile(' +')
        s = re_cdata.sub('', htmlstr)
        s = re_doctype.sub('', s)
        s = re_nav.sub('', s)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_textarea.sub('', s)
        s = re_br.sub('', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        s = re.sub('\\t', '', s)
        s = re_space.sub(' ', s)
        s = self.replaceCharEntity(s)
        return s

    def urlJoin(self, base, url):
        '''
        url 拼接
        url = 'http://karpathy.github.io/2014/07/03/feature-learning-escapades/'

        url_join(url, '../assets/nips2012.jpeg')
        'http://karpathy.github.io/2014/07/03/assets/nips2012.jpeg'

        url_join(url, './assets/nips2012.jpeg')
        'http://karpathy.github.io/2014/07/03/feature-learning-escapades/assets/nips2012.jpeg'

        url_join(url, '/assets/nips2012.jpeg')
        'http://karpathy.github.io/assets/nips2012.jpeg'

        url_join(url,'http://karpathy.github.io/assets/nips2012.jpeg')
        'http://karpathy.github.io/assets/nips2012.jpeg'
        '''
        if not url.startswith('.') and not url.startswith('/'):
            return url
        url1 = urljoin(base, url)
        arr = urlparse(url1)
        path = normpath(arr[2])
        return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

    def fixUrl(self, article_url, text):
        fix_map = {
            'src': 'src=[\'|"](.*?)[\'|"]',
            'href': 'href=[\'|"](.*?)[\'|"]',
        }
        for key, value in fix_map.items():
            _re = re.compile(value)
            text = _re.sub('src="' + self.urlJoin(article_url, '\g<1>') + '"', text)
        return text

    def get(self, url, params=None, **kwargs):
        response = requests.get(url, params=params, **kwargs)
        encode_info = chardet.detect(response.content)
        response.encoding = encode_info['encoding']
        response_text = response.text
        html_filter = self.filterHtml(response_text)
        html_fix = self.fixUrl(url, html_filter)
        readability = Readability(html_fix, url)
        self.title = readability.title
        self.body_html = readability.content
        self.html = response_text
        self.body_text = self.filterTags(self.body_html)

    def toMarkdown(self):
        """
        生成markdown
        :return:
        """
        def fixMd(md):
            # 去除图片生成md时产生重复地址
            md_split = md.split('\n')
            fix_md_str = []
            for i in range(len(md_split)):
                if i < len(md_split) - 2 and md_split[i] == md_split[i + 2] and md_split[i] \
                        and '```' not in md_split[i]:
                    continue
                fix_md_str.append(md_split[i])
            return '\n'.join(fix_md_str)

        if self.body_html:
            md = tomd.Tomd(self.html).markdown
            self.body_md = fixMd(md)

    def getKeys(self, n=5):
        """
        获取文章关键词
        :param n: 关键词个数
        :return keys:
        """

        import re
        re_en_word = re.compile(r'([a-z]+)', re.I)
        # \u4E00-\u9FFF是中文的范围
        re_cn_word = re.compile(r'[\u4E00-\u9FFF]')
        body_text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+=\-—、~@#￥%…&*（）]+", " ", self.body_text)
        print(len(re_en_word.findall(body_text)), len(re_cn_word.findall(body_text)))
        pass

    def getSummary(self):
        """
        自动获取摘要
        :return:
        """
        pass


if __name__ == '__main__':
    ET = ExtractorBlog()
    ua_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    }
    html_content = ET.get('https://www.jiqizhixin.com/articles/2019-03-20-4', headers=ua_headers)
    print(ET.getKeys())
