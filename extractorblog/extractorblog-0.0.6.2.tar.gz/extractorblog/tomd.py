# coding: utf-8

import re
import os
import warnings

MARKDOWN = {
    'h1': ('\n# ', '\n'),
    'h2': ('\n## ', '\n'),
    'h3': ('\n### ', '\n'),
    'h4': ('\n#### ', '\n'),
    'h5': ('\n##### ', '\n'),
    'h6': ('\n###### ', '\n'),
    'code': ('`', '`'),
    'ul': ('', ''),
    'ol': ('', ''),
    'li': ('- ', ''),
    'blockquote': ('\n> ', '\n'),
    'em': ('*', '*'),
    'strong': ('**', '**'),
    'block_code': ('\n```\n', '\n```\n'),
    'span': ('', ''),
    'p': ('\n', '\n\n'),
    'p_with_out_class': ('\n', '\n'),
    'inline_p': ('', ''),
    'inline_p_with_out_class': ('', ''),
    'b': ('**', '**'),
    'i': ('*', '*'),
    'del': ('~~', '~~'),
    'hr': ('\n---', '\n'),
    'thead': ('\n', '|------\n'),
    'tbody': ('\n', '\n'),
    'td': ('|', ''),
    'th': ('|', ''),
    'tr': ('', '\n'),
    'table': ('', '\n'),
    'e_p': ('', '\n'),
    'img': ('', '\n')
}

BlOCK_ELEMENTS = {
    'h1': '<h1.*?>(.*?)</h1>',
    'h2': '<h2.*?>(.*?)</h2>',
    'h3': '<h3.*?>(.*?)</h3>',
    'h4': '<h4.*?>(.*?)</h4>',
    'h5': '<h5.*?>(.*?)</h5>',
    'h6': '<h6.*?>(.*?)</h6>',
    'hr': '<hr/>',
    'blockquote': '<blockquote.*?>([\s\S].*?)</blockquote>',
    'ul': '<ul.*?>(.*?)</ul>',
    'ol': '<ol.*?>(.*?)</ol>',
    'block_code': '<pre.*?><code.*?>([\s\S].*?)</code></pre>',
    'p': '<p\s.*?>(.*?)</p>',
    'p_with_out_class': '<p>([\s\S].*?)</p>',
    'thead': '<thead.*?>([\s\S].*?)</thead>',
    'tr': '<tr.*?>([\s\S].*?)</tr>',
    'img': '(<img [\s\S].*?/>)',

}
'''
<pre><span>import</span> <span>pandas</span> <span>as</span> <span>pd</span> <span># This is the standard</span>
</pre>
'''
INLINE_ELEMENTS = {
    'td': '<td.*?>((.|\n)*?)</td>',  # td element may span lines
    'tr': '<tr.*?>((.|\n)*?)</tr>',
    'th': '<th.*?>(.*?)</th>',
    'b': '<b.*?>(.*?)</b>',
    'i': '<i.*?>(.*?)</i>',
    'del': '<del.*?>(.*?)</del>',
    'inline_p': '<p\s.*?>(.*?)</p>',
    'p': '<p\s.*?>(.*?)</p>',
    'inline_p_with_out_class': '<p>(.*?)</p>',
    'code': '<code.*?>(.*?)</code>',
    'span': '<span.*?>(.*?)</span>',
    'ul': '<ul.*?>(.*?)</ul>',
    'ol': '<ol.*?>(.*?)</ol>',
    'li': '<li.*?>(.*?)</li>',
    'img': '<img.*?src="(.*?)".*?>(.*?)</img>',
    'img_single': '<img.*?src="(.*?)".*?/>',
    'img_single_no_close': '<img.*?src="(.*?)".*?>',
    'a': '<a.*?href="(.*?)".*?>(.*?)</a>',
    'em': '<em.*?>(.*?)</em>',
    'strong': '<strong.*?>(\s*)(.*?)(\s*)</strong>',
    'tbody': '<tbody.*?>([\s\S].*?)</tbody>',
}

DELETE_ELEMENTS = ['<span.*?>', '</span>', '<div.*?>', '</div>', '<br clear="none"/>', '<center.*?>', '</center>']


class Element:
    def __init__(self, start_pos, end_pos, content, tag, folder, is_block=False):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.content = content
        self._elements = []
        self.is_block = is_block
        self.tag = tag
        self.folder = folder
        self._result = None

        if self.is_block:
            self.parse_inline()

    def __str__(self):
        wrapper = MARKDOWN.get(self.tag)
        # 代码块中嵌套```  ``` 会出现显示错乱问题
        re_block_code = re.compile("```([\s\S]*?)```", re.I)
        if self.tag == 'block_code' and re_block_code.search(self.content):
            _contents = ['\t' + content for content in self.content.split('\n')]
            self._result = '\n' + '\n'.join(_contents)
        else:
            if self.tag != 'code':
                self.content = self.filter_tag(self.content)
                # 添加google翻译
                # self.content = self.trans.translate_break_url(self.content)
                # time.sleep(0.5)
            self._result = '{}{}{}'.format(wrapper[0], self.content, wrapper[1])
        return self._result

    def replace_char_entity(self, htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()
            key = sz.group('name')
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    def filter_tag(self, htmlstr):
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
        s = re_nav.sub('', s)
        s = re_script.sub('', s)
        s = re_style.sub('', s)
        s = re_textarea.sub('', s)
        s = re_br.sub('', s)
        s = re_h.sub('', s)
        s = re_comment.sub('', s)
        s = re.sub('\\t', '', s)
        # s = re.sub(' ', '', s)
        s = re_space.sub(' ', s)
        s = self.replace_char_entity(s)
        return s

    def parse_inline(self):
        self.content = self.content.replace('\r', '')  # windows \r character
        self.content = self.content.replace('\xc2\xa0', ' ')  # no break space
        self.content = self.content.replace('&quot;', '\"')  # html quote mark

        for m in re.finditer("<img(.*?)en_todo.*?>", self.content):
            # remove img and change to [ ] and [x]
            # evernote specific parsing
            imgSrc = re.search('src=".*?"', m.group())
            imgLoc = imgSrc.group()[5:-1]  # remove source and " "
            imgLoc = imgLoc.replace('\\', '/')  # \\ folder slash rotate
            if os.stat(self.folder + "/" + imgLoc).st_size < 250:
                self.content = self.content.replace(m.group(), "[ ] ")
            else:
                self.content = self.content.replace(m.group(), "[x] ")

        if "e_" in self.tag:  # evernote-specific parsing
            for m in re.finditer(BlOCK_ELEMENTS['table'], self.content, re.I | re.S | re.M):
                # hmm can there only be one table?
                inner = Element(start_pos=m.start(),
                                end_pos=m.end(),
                                content=''.join(m.groups()),
                                tag='table', folder=self.folder,
                                is_block=True)
                self.content = inner.content
                return  # no need for further parsing ?

            # if no table, parse as usual
            self.content = self.content.replace('<hr/>', '\n---\n')
            self.content = self.content.replace('<br/>', '')

        if self.tag == "table":  # for removing tbody
            self.content = re.sub(INLINE_ELEMENTS['tbody'], '\g<1>', self.content)

        INLINE_ELEMENTS_LIST_KEYS = list(INLINE_ELEMENTS.keys())
        INLINE_ELEMENTS_LIST_KEYS.sort()
        for tag in INLINE_ELEMENTS_LIST_KEYS:
            pattern = INLINE_ELEMENTS[tag]
            if tag == 'a':
                self.content = re.sub(pattern, '[\g<2>](\g<1>)', self.content)
            elif tag == 'img':
                self.content = re.sub(pattern, '![\g<2>](\g<1>)\n', self.content)
            elif tag == 'img_single':
                self.content = re.sub(pattern, '![](\g<1>)\n', self.content)
            elif tag == 'img_single_no_close':
                self.content = re.sub(pattern, '![](\g<1>)\n', self.content)
            elif self.tag == 'ul' and tag == 'li':
                self.content = re.sub(pattern, '- \g<1>\n', self.content)
            elif self.tag == 'ol' and tag == 'li':
                self.content = re.sub(pattern, '1. \g<1>\n', self.content)
            elif self.tag == 'thead' and tag == 'tr':
                self.content = re.sub(pattern, '\g<1>\n', self.content.replace('\n', ''))
            elif self.tag == 'tr' and tag == 'th':
                self.content = re.sub(pattern, '|\g<1>', self.content.replace('\n', ''))
            elif self.tag == 'tr' and tag == 'td':
                self.content = re.sub(pattern, '|\g<1>|', self.content.replace('\n', ''))
                self.content = self.content.replace("||", "|")  # end of column also needs a pipe
            elif self.tag == 'table' and tag == 'td':
                self.content = re.sub(pattern, '|\g<1>|', self.content)
                self.content = self.content.replace("||", "|")  # end of column also needs a pipe
                self.content = self.content.replace('|\n\n', '|\n')  # replace double new line
                self.construct_table()
            else:
                wrapper = MARKDOWN.get(tag)

                if tag == "strong":
                    self.content = re.sub(pattern, '{}\g<2>{}'.format(wrapper[0], wrapper[1]), self.content)
                else:
                    self.content = re.sub(pattern, '{}\g<1>{}'.format(wrapper[0], wrapper[1]), self.content)

        if self.tag == "e_p" and self.content[-1:] != '\n' and len(self.content) > 2:
            # focusing on div, add new line if not there (and if content is long enough)
            self.content += '\n'

    def construct_table(self):
        # this function, after self.content has gained | for table entries,
        # adds the |---| in markdown to create a proper table

        temp = self.content.split('\n', 3)
        for elt in temp:
            if elt != "":
                count = elt.count("|")  # count number of pipes
                break
        pipe = "\n|"  # beginning \n for safety
        for i in range(count - 1):
            pipe += "---|"
        pipe += "\n"
        self.content = pipe + pipe + self.content + "\n"  # TODO: column titles?
        self.content = self.content.replace('|\n\n', '|\n')  # replace double new line
        self.content = self.content.replace("<br/>\n", "<br/>")  # end of column also needs a pipe


class Tomd:
    def __init__(self, html='', folder='', file='', options=None):
        self.html = html  # actual data
        self.folder = folder
        self.file = file
        self.options = options  # haven't been implemented yet
        self._markdown = self.convert(self.html, self.options)

    def convert(self, html="", options=None):
        if html == "":
            html = self.html
        # main function here
        elements = []
        for tag, pattern in BlOCK_ELEMENTS.items():
            for m in re.finditer(pattern, html, re.I | re.S | re.M):
                # now m contains the pattern without the tag
                element = Element(start_pos=m.start(),
                                  end_pos=m.end(),
                                  content=''.join(m.groups()),
                                  tag=tag,
                                  folder=self.folder,
                                  is_block=True)
                can_append = True
                for e in elements:
                    if e.start_pos < m.start() and e.end_pos > m.end():
                        can_append = False
                    elif e.start_pos > m.start() and e.end_pos < m.end():
                        elements.remove(e)
                if can_append:
                    elements.append(element)
        elements.sort(key=lambda element: element.start_pos)
        self._markdown = ''.join([str(e) for e in elements])
        for index, element in enumerate(DELETE_ELEMENTS):
            self._markdown = re.sub(element, '', self._markdown)
        return self._markdown

    @property
    def markdown(self):
        self.convert(self.html, self.options)
        return self._markdown

    def export(self, folder=False):
        if len(self.file) < 1:
            warnings.warn("file not specified, renamed to tmp.md")
            file = "tmp.md"
        else:
            file = self.file.replace('.html', '.md')  # rename to md
        if len(self.folder) < 2:
            warnings.warn("folder not specified, will save to pwd")
        elif not folder:
            file = self.folder + '/' + file
        else:  # if folder is specified
            file = folder + '/' + file
        f = open(file, 'w')
        f.write(self._markdown)
        f.close()


_inst = Tomd()
convert = _inst.convert
if __name__ == '__main__':
    html = '''
    <blockquote>
<p>本文由 Python 翻译组 最新翻译出品，原作者为 Jamal Moir，译者为 liubj2016，并由编程派作者 EarlGrey 校对。这是使用 Python 进行科学计算的系列文章，上一篇可点此查看：Matplotlib 快速入门。</p>
<p>译者简介：liubj2016，中南财经政法大学，金融工程系学生。Python使用方向：数据分析，机器学习和量化投资。</p>
<p>本文独家发布于编程派。未经许可，禁止转载。</p>
</blockquote>
<p><code>Pandas</code> 是我最喜爱的库之一。通过带有标签的列和索引，<code>Pandas</code> 使我们可以以一种所有人都能理解的方式来处理数据。它可以让我们毫不费力地从诸如 <code>csv</code> 类型的文件中导入数据。我们可以用它快速地对数据进行复杂的转换和过滤等操作。<code>Pandas</code> 真是超级棒。</p>
<p>我觉得它和 <code>Numpy</code>、<code>Matplotlib</code> 一起构成了一个 Python 数据探索和分析的强大基础。<code>Scipy</code> （将会在下一篇推文里介绍）当然也是一大主力并且是一个绝对赞的库，但是我觉得前三者才是 Python 科学计算真正的顶梁柱。</p>
<p>那么，赶紧看看 python 科学计算系列的第三篇推文，一窥 <code>Pandas</code> 的芳容吧。如果你还没看其它几篇文章的话，别忘了去看看。</p>
<h2>导入 Pandas</h2>
<p>第一件事当然是请出我们的明星 —— Pandas。</p>
<div><pre><span>import</span> <span>pandas</span> <span>as</span> <span>pd</span> <span># This is the standard</span>
</pre></div>
<p>这是导入 <code>pandas</code> 的标准方法。我们不想一直写 <code>pandas</code> 的全名，但是保证代码的简洁和避免命名冲突都很重要，所以折中使用 <code>pd</code> 。如果你去看别人使用  <code>pandas</code> 的代码，就会看到这种导入方式。</p>
<h2>Pandas 中的数据类型</h2>
<p>Pandas 基于两种数据类型，series 和 dataframe。</p>
<p>series 是一种一维的数据类型，其中的每个元素都有各自的标签。如果你之前看过这个系列关于 <a src="http://codingpy.com">Numpy</a> 的推文，你可以把它当作一个由带标签的元素组成的 <code>numpy</code> 数组。标签可以是数字或者字符。</p>
<p>dataframe 是一个二维的、表格型的数据结构。Pandas 的 dataframe 可以储存许多不同类型的数据，并且每个轴都有标签。你可以把它当作一个 series 的字典。</p>
<h2>将数据导入 Pandas</h2>
<p>在对数据进行修改、探索和分析之前，我们得先导入数据。多亏了 Pandas ，这比在 <code>Numpy</code> 中还要容易。</p>
<p>这里我鼓励你去找到自己感兴趣的数据并用来练习。你的（或者别的）国家的网站就是不错的数据源。如果要举例的话，首推<a src="https://data.gov.uk/data/search">英国政府数据</a>和<a src="http://catalog.data.gov/dataset">美国政府数据</a>。<a src="https://www.kaggle.com/">Kaggle</a>也是个很好的数据源。</p>
<p>我将使用英国降雨数据，这个数据集可以很容易地从英国政府网站上下载到。此外，我还下载了一些日本降雨量的数据。</p>
<blockquote>
<p>英国降雨数据：<a src="https://data.gov.uk/dataset/average-temperature-and-rainfall-england-and-wales/resource/3fea0f7b-5304-4f11-a809-159f4558e7da">下载地址</a>
日本的数据实在是没找到，抱歉。</p>
</blockquote>
<div><pre><span># Reading a csv into Pandas.</span>
<span>df</span> <span>=</span> <span>pd</span><span>.</span><span>read_csv</span><span>(</span><span>'uk_rain_2014.csv'</span><span>,</span> <span>header</span><span>=</span><span>0</span><span>)</span>
</pre></div>
<blockquote>
<p>译者注：如果你的数据集中有中文的话，最好在里面加上 <code>encoding = 'gbk'</code> ，以避免乱码问题。后面的导出数据的时候也一样。</p>
</blockquote>
<p>这里我们从 <code>csv</code> 文件里导入了数据，并储存在 dataframe 中。这一步非常简单，你只需要调用 <code>read_csv</code> 然后将文件的路径传进去就行了。<code>header</code> 关键字告诉 Pandas 哪些是数据的列名。如果没有列名的话就将它设定为 <code>None</code> 。Pandas 非常聪明，所以这个经常可以省略。</p>
<h2>准备好要进行探索和分析的数据</h2>
<p>现在数据已经导入到 Pandas 了，我们也许想看一眼数据来得到一些基本信息，以便在真正开始探索之前找到一些方向。</p>
<p>查看前 x 行的数据：</p>
<div><pre><span># Getting first x rows.</span>
<span>df</span><span>.</span><span>head</span><span>(</span><span>5</span><span>)</span>
</pre></div>
<p>我们只需要调用 <code>head()</code> 函数并且将想要查看的行数传入。</p>
<p>得到的结果如下：</p>
<p><img alt="image" src="https://i2.wp.com/www.datadependence.com/wp-content/uploads/2016/05/head-1.png?resize=640,124"/></p>
<p>你可能还想看看最后几行：</p>
<div><pre><span># Getting last x rows.</span>
<span>df</span><span>.</span><span>tail</span><span>(</span><span>5</span><span>)</span>
</pre></div>
<p>跟 <code>head</code> 一样，我们只需要调用 <code>tail</code> 并且传入想要查看的行数即可。注意，它并不是从最后一行倒着显示的，而是按照数据原来的顺序显示。</p>
<p>得到的结果如下：</p>
    '''
    md = Tomd(html).markdown
    # print(md)
