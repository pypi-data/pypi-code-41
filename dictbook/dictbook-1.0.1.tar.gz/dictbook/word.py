from urllib.request import urlopen
from .database import Database
from .exceptions import *
from .clear_html import *

import datetime
import re

url = 'http://www.iciba.com/'
content_pattern = '<ul class="base-list switch_part" class="">.*?</ul>'
#content_re = re.compile(content_pattern)

def clear(content):
    content = clear_space(content)
    content = re.sub(r'\\n', '', content)
    return content


def decode(content):
    l = []
    content = content.split('\\x')
    for each in content:
        if len(each) == 2:
            l.append(int(each, 16))
        elif len(each) > 2:
            l.append(int(each[0:2], 16))
            for c in each[2:]:
                l.append(ord(c))
    return bytes(l).decode()


class Word:
    def __init__(self, original_eng):
        self._content = ''
        self._url = url + original_eng

        self._eng = original_eng
        self._meaning = {}


    def _get_content(self):
        self._content = str(urlopen(self._url).read())
        if not self._content:
            raise NetworkNotConnected
        
        match = re.search(content_pattern, self._content)
        if not match:
            raise KeyError

        self._content = self._content[match.start():match.end()]
        self._content = clear(self._content)


    def _parse_into_dict(self):
        if not self._content:
            self._get_content()
        
        li = re.split(li_pattern, self._content)
        lli = []
        for each in li:
            s = clear_label(each)
            if s != '':
                lli.append(s)

        dict = {}
        for each in lli:
            two_parts = each.split('\\x', maxsplit=1)
            dict[two_parts[0]] = decode(two_parts[1])
        return dict


    @property
    def meaning(self):
        if not self._meaning:
            self._meaning = self._parse_into_dict()
        return self._meaning


    @property
    def eng(self):
        return self._eng


    def __str__(self):
        s = self._eng + '\n'
        for key, value in self.meaning.items():
            s = s + '{} {}\n'.format(key, value)
        return s


class WordList(list):
    pass



if __name__ == '__main__':
    words = WordList()
    
    while True:
        try:
            a = input('-----------------单词：')
            if a == '#':
                break
            word = Word(a)
            print(word)
            words.append(word)
        except KeyError as e:
            print('查无单词')
        except NetworkNotConnected:
            print('请检查网络')


    db = Database('d.db', 'words')
    for each in words:
        #插入数据库
        db.insert(each.eng, str(each.meaning), datetime.date.today())
        print(each)

    print('quit.')
