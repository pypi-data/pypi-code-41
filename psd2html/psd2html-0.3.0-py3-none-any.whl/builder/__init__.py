import os

from bs4 import BeautifulSoup


class Html:

    def __init__(self):
        boilerplate = os.path.abspath(os.path.join(os.path.dirname(__file__)) + '/res/boilerplate.txt')
        with open(boilerplate) as fp:
            soup = BeautifulSoup(fp, 'lxml')
        self.soup = soup

    def append(self, element):
        self.soup.body.append(element)

    @classmethod
    def _css_str(cls, styles):
        excluded = ('right', 'bottom')
        css = ''
        for style, value in styles.items():
            if value == '' or style in excluded:
                continue
            if type(value) == int:
                css += style + ': ' + str(value) + 'px; '
            else:
                css += style + ': ' + str(value) + '; '
        return css

    def __str__(self):
        return str(self.soup.prettify(formatter="html"))


class Div(Html):

    def __init__(self):
        super().__init__()
        self.elem = self.soup.new_tag('div')

    def render(self, attrs, content=''):
        elem = self.elem
        # add attributes
        if 'width' in attrs:
            elem['width'] = attrs['width']
        if 'height' in attrs:
            elem['height'] = attrs['height']
        if 'class' in attrs:
            elem['class'] = attrs['class']
        elem.append(content)

        # add style
        if 'style' in attrs:
            css_str = self._css_str(attrs['style'])
            if css_str:
                elem['style'] = css_str
        self.elem = elem

    def append(self, element):
        self.elem.append(element)

    def get(self):
        return self.elem


class Img(Html):

    def __init__(self):
        super().__init__()
        elem = self.soup.new_tag('img')
        self.elem = elem

    def render(self, src, attrs):
        image = self.elem
        image['src'] = src
        # add style
        if 'style' in attrs:
            css_str = self._css_str(attrs['style'])
            if css_str:
                image['style'] = css_str
        self.elem = image

    def get(self):
        return self.elem
