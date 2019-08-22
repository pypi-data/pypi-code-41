# -*- coding: utf-8 -*-
# @Time     : 2019/5/14 17:55
# @Author   : Run 
# @File     : novel.py
# @Software : PyCharm

"""
todo
    1. try except for requests
    2. crawl cover image seperately
    3. inherit class
"""

import sys
import requests
from bs4 import BeautifulSoup
import os
from jinja2 import Environment, FileSystemLoader
import warnings;warnings.filterwarnings("ignore")

NOVEL_SPIDER_TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
_ENV = Environment(loader=FileSystemLoader(NOVEL_SPIDER_TEMPLATES_PATH))


def check_calibre_installed():
    """
    检查windows系统下是否已经安装了calibre，并将ebook-convert命令添加至了环境变量
    :return: bool
    """
    test = os.popen("ebook-convert --version")
    if 'calibre' not in test.read():
        print("please install calibre and add ebook-convert to environment virables")
        return False
    else:
        print('calibre installed')
        return True


class NovelSpider:

    def __init__(self):
        self.spiders_list = [
            SubSpider1(),
            SubSpider2()
        ]
        self.spider_books_list = []  # [(spider, [(book, author, url), ...]), ...]
        self.recipes_list = []

    def reset(self):
        self.spider_books_list = []
        self.recipes_list = []

    def search(self, book=None, author=None, target="one"):
        """

        :param book: 书名
        :param author: 作者名
        :param target:
            one: 在某个网站有搜到至少一本符合要求的书籍即停止
            all: 遍历所有网站，搜集所有符合要求的书籍
        :return:
        """
        if book is None and author is None:
            raise Exception("please input book name or author name")

        if target == "one":
            for spider in self.spiders_list:
                print("search {}, {}".format(spider.name, spider.url))
                res_list = spider.search(book, author)
                if len(res_list) > 0:
                    self.spider_books_list.append((spider, res_list))
                    break
        elif target == "all":
            for spider in self.spiders_list:
                print("search {}, {}".format(spider.name, spider.url))
                res_list = spider.search(book, author)
                if len(res_list) > 0:
                    self.spider_books_list.append((spider, res_list))
        else:
            pass

    def gen_recipes(self, target="one", folder="recipes"):
        """

        :param target:
            one: 在某个网站有搜到至少一本符合要求的书籍即停止
            all: 遍历所有网站，搜集所有符合要求的书籍
        :param folder: 存放recipes的文件夹
        :return:
            True: 成功生成recipe文件
            False: 未能成功生成recipe文件
        """
        if len(self.spider_books_list) == 0:  # 未能搜索到任何符合要求的书籍
            return False

        if target == "one":
            spider, tmp = self.spider_books_list[0]
            # book, author, index_url, img_url = tmp[0]
            recipe = spider.gen_recipe(*tmp[0], folder)
            self.recipes_list.append(recipe)
        elif target == "all":
            for spider, tmp in self.spider_books_list:
                for sub_tmp in tmp:
                    recipe = spider.gen_recipe(*sub_tmp, folder)
                    self.recipes_list.append(recipe)
        else:
            pass

        return True

    def gen_ebook(self, recipe, ebook=None):
        """
        由指定的recipe文件名生成对应的电子书文件，默认存放于ebooks文件夹下
        :param recipe: recipe的路径及文件名，e.g. recipes/1.recipe
        :param ebook: 想要转换的电子书路径文件名，kindle使用的通常是mobi格式，e.g. 1.mobi
        :return:
        :notes:
            1. 确保在windows系统下已经安装了calibre，并将ebook-convert命令添加至了环境变量
        """
        # test ebook-convert command
        if not check_calibre_installed():
            return

        # check exists
        if os.path.exists(recipe):
            recipe_name = os.path.basename(recipe)
            if not recipe_name.endswith('.recipe'):
                print("invalid recipe name: {}".format(recipe_name))
                return
            ebook_name = recipe_name.replace(".recipe", ".mobi")
            if ebook is None:
                if not os.path.exists("ebooks"):
                    os.makedirs("ebooks")
                ebook = os.path.join("ebooks", ebook_name)
                if os.path.exists(ebook):
                    print("this ebook already exists in folder 'ebooks/'")
                    return
            else:
                if os.path.exists(ebook):
                    print("this ebook already exists")
                    return
        else:
            print("can't find recipe: {}".format(recipe))
            return

        # convert
        try:
            print("generate {}".format(ebook_name))
            os.system('ebook-convert {} {}'.format(recipe, ebook))  # 在python console中运行时输出信息会乱码 todo
        except Exception as e:
            print("convert ebook failed: {}".format(e))

    def gen_ebooks(self, recipe_folder="recipes"):
        """
        将指定文件夹下的所有recipe文件都转换成对应的电子书
        :param recipe_folder:
        :return:
        :notes:
            1. 确保在windows系统下已经安装了calibre，并将ebook-convert命令添加至了环境变量
        """
        # test ebook-convert command
        if not check_calibre_installed():
            return

        # check exists
        if not os.path.exists(recipe_folder):
            print("recipe_folder {} doesn't exist".format(recipe_folder))
            return

        # convert
        files = os.listdir(recipe_folder)
        for file in files:
            self.gen_ebook(os.path.join(recipe_folder, file))

    def download(self, book=None, author=None):
        """
        下载指定书籍或者指定作者的所有书
        :param book: 如果传入书名，则只下载该书
        :param author: 如果传入作者名，则下载该作者能搜索到的所有不重名书籍
        :return:
        :notes:
            1. 中间生成的recipe文件和电子书分别存放于文件夹recipes和ebooks下面
        """
        if book is not None:
            self.search(book)
            if self.gen_recipes():
                self.gen_ebook(self.recipes_list[0])
        elif author is not None:
            self.search(author=author, target="all")
            if self.gen_recipes(target="all"):
                self.gen_ebooks()
        else:
            raise Exception("please input book or author")

    def download_books(self, book_list, style="one_by_one"):
        """
        下载列表中所有书籍
        :param book_list:
        :param style:
            one_by_one:
            recipe_first:
        :return:
        :notes:
            1. 中间生成的recipe文件和电子书分别存放于文件夹recipes和ebooks下面
        """
        if style == 'one_by_one':
            for book in book_list:
                self.download(book)
                self.reset()
        elif style == 'recipe_first':
            for book in book_list:
                self.search(book)
                self.gen_recipes()
                self.reset()
            self.gen_ebooks()


class SubSpider:
    """针对每个小说网站的爬虫策略原型"""

    def __init__(self):
        self.url = ''
        self.name = ''
        self.template = ''  # 模板文件

    def search(self, book=None, author=None):
        """

        :param book:
        :param author:
        :return: [(book, author, index_url, img_url), ...]
        """

        # search
        # parse
        # filter
        pass

    def gen_recipe(self, book, author, index_url, img_url, folder="recipes"):
        """

        :param book:
        :param author:
        :param index_url: 索引页地址，不能为空
        :param img_url: 可以为空，不能成功下载封面图片
        :param folder:
        :return:
        """
        pass


class SubSpider1:

    def __init__(self):
        self.url = 'https://www.xbiquge6.com'
        self.name = '新笔趣阁'
        self.template = "template1.recipe"

    def search(self, book=None, author=None):
        """
        该网站仅允许一个关键词，所以当书名和作者名均传入时以书名为搜索关键词，但两者都会作为对搜索结果的筛选条件；
        该网页的查询结果会分页展示
        :param book:
        :param author:
        :return: [(book, author, index_url, img_url), ...]
        """
        keyword = book if book is not None else author

        # search
        def _parse_page_url(url):
            req = requests.get(url, timeout=10)
            cont = req.content
            soup = BeautifulSoup(cont, "lxml")
            books = soup.find_all('div', attrs={'class': "result-item result-game-item"})
            return books

        #
        books_list = []
        url = self.url + "/search.php?keyword={}".format(keyword)
        res_list = _parse_page_url(url)
        num = 1
        while len(res_list) > 0:
            print("page {} parsed, {} book(s) found".format(num, len(res_list)))
            books_list += res_list
            num += 1
            res_list = _parse_page_url(url + "&page={}".format(num))
        print('search {} page(s), find {} book(s)'.format(num, len(books_list)))

        # parse
        def _parse_details(soup):
            # image_url
            try:
                img_div = soup.find('div', attrs={'class': "result-game-item-pic"})
                img_url = img_div.a.img['src']
            except:
                img_url = ''
            # book, author, index_url
            try:
                details_div = soup.find('div', attrs={'class': 'result-game-item-detail'})
                a = details_div.h3.a
                book = a['title'].strip()
                index_url = a['href']
                author = details_div.div.p.find_all('span')[1].string.strip()
                # print(book, author, url)
            except:
                return None

            return book, author, index_url, img_url

        #
        details_list = []
        if len(books_list) > 0:
            for soup in books_list:
                tmp = _parse_details(soup)
                if tmp is not None:
                    details_list.append(tmp)
            print('after parsing, {} books left'.format(len(details_list)))

        # filter
        final_list = []
        if len(details_list) > 0:
            for book0, author0, index_url, img_url in details_list:
                if book is not None and book != book0:
                    continue
                if author is not None and author != author0:
                    continue
                final_list.append((book0, author0, index_url, img_url))
            print("after filtering, {} books left".format(len(final_list)))

        return final_list

    def gen_recipe(self, book, author, index_url, img_url, folder="recipes"):
        """

        :param book:
        :param author:
        :param index_url: 索引页地址，不能为空
        :param img_url: 可以为空，不能成功下载封面图片
        :param folder:
        :return: recipe文件路径
        """
        # check if recipe exists
        file_name = book + '_' + author + '.recipe'  # 书名_作者.recipe
        recipe = os.path.join(folder, file_name)
        if os.path.exists(recipe):
            print("this recipe already exists in folder {}".format(folder))
            return
        else:
            if not os.path.exists(folder):
                os.makedirs(folder)

        # fill template
        details_dict = {
            'title': book,
            'cover_url': img_url,
            'index_url': index_url,
            'web_url': self.url
        }
        template = _ENV.get_template(self.template)
        cont = template.render(**details_dict)

        # save
        with open(recipe, 'w', encoding="utf-8") as file:
            file.write(cont)

        return recipe


class SubSpider2:

    def __init__(self):
        self.url = 'https://www.biquge.cc'
        self.name = '笔趣阁'
        self.template = "template2.recipe"

    def search(self, book=None, author=None):
        """
        该网站的搜索是通过一个接口以参数siteid传入站点名进行请求，允许多个关键词，可以同时筛选书名和作者名；
        该网页的查询结果只会有一页
        :param book:
        :param author:
        :return: [(book, author, index_url, img_url), ...]
        """

        # search
        keyword = "+".join(filter(lambda x: x is not None, [book, author]))
        url = "https://sou.xanbhx.com/search?siteid=biqugecc&q={}".format(keyword)
        try:
            req = requests.get(url, verify=False, timeout=10)
            cont = req.content
            soup = BeautifulSoup(cont, "lxml")
            books_list = soup.find('ul').find_all('li')[1:]
        except:
            books_list = []
        print('find {} book(s)'.format(len(books_list)))

        # parse
        def _parse_details(soup):
            # image_url
            img_url = ""  # todo
            # book, author, index_url
            try:
                a = soup.find('span', attrs={'class': 's2'}).a
                book = a.text.strip()
                index_url = a['href']
                author = soup.find('span', attrs={'class': 's4'}).text.strip()
                # print(book, author, url)
            except:
                return None

            return book, author, index_url, img_url

        #
        details_list = []
        if len(books_list) > 0:
            for soup in books_list:
                tmp = _parse_details(soup)
                if tmp is not None:
                    details_list.append(tmp)
            print('after parsing, {} books left'.format(len(details_list)))

        # filter
        final_list = []
        if len(details_list) > 0:
            for book0, author0, index_url, img_url in details_list:
                if book is not None and book != book0:
                    continue
                if author is not None and author != author0:
                    continue
                final_list.append((book0, author0, index_url, img_url))
            print("after filtering, {} books left".format(len(final_list)))

        return final_list

    def gen_recipe(self, book, author, index_url, img_url, folder="recipes"):
        """

        :param book:
        :param author:
        :param index_url: 索引页地址，不能为空
        :param img_url: 可以为空，不能成功下载封面图片
        :param folder:
        :return: recipe文件路径
        """
        # check if recipe exists
        file_name = book + '_' + author + '.recipe'  # 书名_作者.recipe
        recipe = os.path.join(folder, file_name)
        if os.path.exists(recipe):
            print("this recipe already exists in folder {}".format(folder))
            return
        else:
            if not os.path.exists(folder):
                os.makedirs(folder)

        # fill template
        details_dict = {
            'title': book,
            'cover_url': img_url,
            'index_url': index_url,
            'web_url': index_url
        }
        template = _ENV.get_template(self.template)
        cont = template.render(**details_dict)

        # save
        with open(recipe, 'w', encoding="utf-8") as file:
            file.write(cont)

        return recipe


class SubSpider3:
    # todo
    def __init__(self):
        self.url = 'https://www.biquku.com/'
        self.name = '笔趣库'


if __name__ == "__main__":
    """
    -h, --help                                      Show help
    -b, --book <book>                               Download book
    -bs, --books <book1 book2 book3 ...>            Download books
    -a, --author <author>                           Download author's all books
    """

    argvs = sys.argv
    if argvs[1] in ['-h', '--help']:
        print("""
    -h, --help                                      Show help
    -b, --book <book>                               Download book
    -bs, --books <book1 book2 book3 ...>            Download books
    -a, --author <author>                           Download author's all books
    """)
    elif argvs[1] in ['-bs', '--books']:
        spider = NovelSpider()
        spider.download_books(argvs[2:])
    elif argvs[1] in ['-a', '--author']:
        if len(argvs) == 3:
            spider = NovelSpider()
            spider.download(author=argvs[2])
        elif len(argvs) == 5 and argvs[3] in ['-b', '--book']:
            spider = NovelSpider()
            spider.download(author=argvs[2], book=argvs[4])
        else:
            print("invalid format, use -h or --help to get help.")
    elif argvs[1] in ['-b', '--book']:
        if len(argvs) == 3:
            spider = NovelSpider()
            spider.download(book=argvs[2])
        elif len(argvs) == 5 and argvs[3] in ['-a', '--author']:
            spider = NovelSpider()
            spider.download(book=argvs[2], author=argvs[4])
        else:
            print("invalid format, use -h or --help to get help.")
    else:
        print("invalid format, use -h or --help to get help.")
