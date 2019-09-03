import os
from bs4 import BeautifulSoup


config = {
    'boilerplate': os.path.abspath(os.path.join(os.path.dirname(__file__)) + '/res/boilerplate.txt')
}


def get_css_str(styles):
    if 'parent' in styles:
        parent = styles['parent']
        position = 'absolute'
        top = styles['top'] - parent['top']
        left = styles['left'] - parent['left']
    else:
        position = 'relative'
        top = styles['top']
        left = styles['left']
    css = ''
    css += 'position: ' + position + ';'
    css += 'height: ' + str(styles['height']) + 'px;'
    css += 'width: ' + str(styles['width']) + 'px;'
    css += 'left: ' + str(left) + 'px;'
    css += 'top: ' + str(top) + 'px;'
    css += 'opacity: ' + str(styles.get('opacity')) + ';'
    if not styles['visible']:
        css += 'visibility: hidden;'
    if styles.get('font_size'):
        css += 'font-size: ' + str(styles['font_size']) + 'px;'
    if styles.get('color'):
        css += 'color: ' + str(styles['color']) + ';'
    return css


class HtmlBuilder:

    def __init__(self, **kwargs):
        with open(config.get('boilerplate')) as fp:
            soup = BeautifulSoup(fp, 'lxml')
        self.soup = soup

    def add(self, element):
        self.soup.body.append(element)

    def div(self, content, **kwargs):
        text = self.soup.new_tag('div')
        # add attributes
        if kwargs['width']:
            text['width'] = kwargs['width']
        if kwargs['height']:
            text['height'] = kwargs['height']
        text['class'] = kwargs['class_name']
        text.append(content)

        # add styles
        css_str = get_css_str(kwargs)
        if css_str:
            text['style'] = css_str

        return text

    def image(self, href, **kwargs):
        image = self.soup.new_tag('img')
        # add attributes
        if kwargs['width']:
            image['width'] = kwargs['width']
        if kwargs['height']:
            image['height'] = kwargs['height']
        image['src'] = href
        image['class'] = kwargs['class_name']

        # add styles
        css_str = get_css_str(kwargs)
        if css_str:
            image['style'] = css_str

        return image

    def get(self):
        return self.soup.prettify()


class Group(HtmlBuilder):
    def __init__(self, **kwargs):
        super().__init__()
        group = self.soup.new_tag('div')
        group['class'] = kwargs['class_name']
        # add styles
        css_str = get_css_str(kwargs)
        if css_str:
            group['style'] = css_str
        self.container = group

    def add(self, element):
        self.container.append(element)

    def get(self):
        return self.container
