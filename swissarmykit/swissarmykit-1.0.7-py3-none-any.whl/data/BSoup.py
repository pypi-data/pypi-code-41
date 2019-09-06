import re
from bs4 import BeautifulSoup, NavigableString, SoupStrainer
from swissarmykit.utils.fileutils import FileUtils
from swissarmykit.utils.stringutils import StringUtils

class BItem:
    '''
    https://edmundmartin.com/beautiful-soup-vs-lxml-speed/
            Overhead	100,000 URLs    500,000 URLs
            Bs4         (html.parser)	0.09454	2.6	13.1
            Bs4         (html5lib)	    0.15564	4.3	21.6
            Bs4         (lxml)	        0.06388	1.8	8.9

    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parsing-only-part-of-a-document

    '''
    features = 'lxml'
    def __init__(self, html='', item: BeautifulSoup = None, html_path='', is_debug=False, type='', features='lxml', parse_only=None):
        '''

        :param parse_only: 'tag name'
        :param features: 'html.parser', 'lxml' for strictly HTML   The differences become clear on non well-formed HTML documents.
        '''
        self.item = item
        self.is_debug = is_debug
        self.type = type

        if BItem.features != features:
            BItem.features = features

        if parse_only:
            parse_only = SoupStrainer(parse_only)

        if html:
            self.item = BeautifulSoup(html, BItem.features, parse_only=parse_only)

        if html_path:
            h = FileUtils.load_html_file(html_path)
            self.item = BeautifulSoup(h, BItem.features, parse_only=parse_only)

    @staticmethod
    def get_empty():
        return BItem(item=None)

    def parent(self, level=1):
        item = self.item
        if self.is_not_null():
            # Ignore 1 level text node.
            for i in range(level + 1):
                item = item.parent
        return BItem(item=item, is_debug=self.is_debug)


    def find_by_text(self, text='', selector=None):
        item = self.item

        if self.is_not_null():
            item = self.item.find(name=selector, text=text)

        return BItem(item=item, is_debug=self.is_debug)

    def next_sibling(self, next=1):
        if next > 1:
            bs = self
            for i in range(0, next):
                bs = bs.next_sibling()
            return bs

        item = self.item
        if self.is_not_null():
            item = self.item.find_next_sibling()
            if isinstance(item, NavigableString):
                item = BeautifulSoup(item,  'html.parser')
        return BItem(item=item, is_debug=self.is_debug)

    def img_src(self, base_url=None):
        if base_url:
            return base_url + self.attr('src')
        return self.attr('src')

    def href(self, base_url=''):
        if base_url:
            return base_url + self.attr('href')
        return self.attr('href')

    def has_attr(self, key):
        if self.item and self.item.has_attr(key):
            return True
        return False

    def attr(self, attr=''):
        value = ''
        if self.item and self.item.has_attr(attr):
            value = self.item[attr]
        else:
            if self.is_debug:
                print('WARN: BItem is None, cant get text')
        return value

    def val(self):
        return self.attr('value')

    def get_prev_sibling(self):
        return self.item.previous_sibling if self.item else ''

    def get_next_sibling(self):
        return self.item.next_sibling if self.item else ''

    def is_disabled(self):
        return not self.attr('disabled')

    def is_display_none(self):
        attr = self.attr('style')
        return attr and ('display:none' in attr or ('display' in attr and 'display:none' in attr.replace(' ', '')))

    def set_type(self, tag):
        self.type = tag

    def html(self):
        value = ''
        if self.item:
                value = str(self.item)
        else:
            # print('WARN: BItem is None, cant get text')
            pass
        return value

    def get_text_node_only(self):
        '''  https://stackoverflow.com/questions/4995116/only-extracting-text-from-this-element-not-its-children  '''

        if self.item:
            text = self.item.find(text=True)
            if text:
                return text.strip()
        return ''

    def text(self, new_line=False, recursive=True, replace_white_space=False, remove_empty_line=False):
        value = ''
        if self.item:
            if new_line:
                value = self.item.get_text(separator='\n').strip()
            elif not recursive:
                text = self.item.find(text=True, recursive=recursive)
                value = text.strip() if text else ''
            elif replace_white_space:
                val = [i.strip() for i in self.item.text.split('\n')]
                value = ' '.join(val).strip()
            else:
                value = self.item.text.strip()
        else:
            # print('WARN: BItem is None, cant get text')
            pass

        if remove_empty_line:
            value = StringUtils.remove_empty_line(value)

        return value

    def find_last(self, *args, **kwargs):
        lst = self.find_all(*args, **kwargs)
        return lst[-1] if len(lst) else BItem.get_empty()

    def find(self, selector): # type: (str) -> BItem
        item = self.item
        if item:
            item = self.item.select_one(selector)
        return BItem(item=item)

    def child_at(self, selector, at=1):
        return self.find('%s:nth-of-type(%d)' % (selector, at))

    def find_all(self, selector, recursive=True):  # type: (str, bool) -> [BItem]
        lst = []
        if self.is_not_null():
            if recursive:
                lst = [BItem(item=item) for item in self.item.select(selector)]
            else:
                if ' ' in selector:
                    selector1, selector2 = selector.rsplit(' ', 1)
                    parent = self.item.select_one(selector1)
                else:
                    selector2 = selector
                    parent = self.item

                if parent:
                    tag, attr = self.parse_selector_simple(selector2)
                    for item in parent.find_all(tag, attrs=attr, recursive=recursive):
                        lst.append(BItem(item=item, is_debug=self.is_debug, type=tag))
        return lst

    def exists(self, selector):
        item = self.find(selector)
        return item.is_not_null()

    def find_by_texts(self, selector, text=None):
        lst = []

        if '.' in selector or '#' in selector or '[' in selector:
            raise Exception('This method use for single item only!!')

        if self.is_not_null():
            for item_ in self.item.find_all(selector, string=text):
                lst.append(BItem(item=item_, type=selector))

        return lst

    def parse_selector_simple(self, selector='div'):
        ''' https://www.w3schools.com/cssref/css_selectors.asp '''

        if selector[0] in ['#', '.', '[']:
            selector = 'div' + selector
        attr = {}

        if '#' in selector:
            tag, attr['id'] = selector.split('#')
            return tag, attr

        if '.' in selector:
            tag, attr['class'] = selector.split('.')
            return tag, attr

        if '[' in selector:
            tag, class_name = selector.split('[')
            key, value = class_name[:-1].split('=')
            attr[key] = value.strip('"').strip("'")
            return tag, attr

        return selector, attr

    def get_tag_name(self):
        return self.item.name if self.item else ''

    def is_not_null(self):
        return self.item != None

    def is_null(self):
        return self.item == None

    def get_html_src(self):
        return str(self.item)

    def inner_html(self):
        return str(self.item)

    def replace(self, text, new):
        return BItem(html=str(self.item).replace(text, new))

    def pop_element(self, selector):
        if self.item:
            item = self.item.select_one(selector)
            bs = BItem(html=str(item))
            item.decompose()
            return bs
        return BItem.get_empty()

    def remove_element(self, selector): # type: (str) -> BItem
        if self.item:
            self.item.select_one(selector).decompose()
        return self

    def remove_elements(self, selector):
        if self.item:
            for item in self.item.select(selector):
                item.decompose()
        return self

    def find_first_child(self):
        children = self.find_children()
        return children[0] if len(children) else BItem.get_empty()

    def find_last_child(self):
        children = self.find_children()
        return children[-1] if len(children) else BItem.get_empty()

    def find_children(self):
        if self.item:
            return [BItem(item=item) for item in self.item.findChildren(recursive=False)]
        return []

    def find_child(self):
        if self.item:
            return BItem(item=self.item.findChild())
        return BItem.get_empty()

    def split_by(self, selector=None, text=None, in_text=None):
        if self.item:
            val = None
            selector = selector if selector else 'div'
            if in_text:
                for v in self.find_by_texts(selector):
                    if in_text in v.text():
                        val = v.item
                        break
            elif text:
                val = self.find_by_text(text, selector).item
            else:
                val = self.item.select_one(selector)

            if val:
                html = str(self.item)
                sub = str(val)
                first, second = html.split(sub, 1)
                return BItem(first), BItem(second)

        return BItem.get_empty(), BItem.get_empty()

    def add_element(self, tag='div', text='', position=0, **kwargs):
        new_tag = self.item.new_tag(tag, id='file_history', **kwargs)
        new_tag.string = text
        self.item.insert(position, new_tag)
        return BItem(item=self.item, is_debug=self.is_debug)

    def to_html_desktop(self):
        FileUtils.output_html_to_desktop(str(self.item))
        return True

    def get_html(self):
        return str(self.item)

    def __str__(self):
        re = 'INFO: '
        if self.type == 'a':
            re += 'Link: "%s",  %s' % (self.href(), self.text())
        if self.type == 'div':
            re += 'Div: %s' % self.text()
        if self.type == 'img':
            re += 'Img: "%s"' % self.img_src()

        re += '\n' + str(self.item) + '\n'
        return re

if __name__ == '__main__':
    bsoup = BItem()
    print(bsoup.parse_selector_simple('div.test'))