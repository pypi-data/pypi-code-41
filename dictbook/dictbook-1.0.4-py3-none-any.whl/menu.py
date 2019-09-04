import datetime
import sqlite3
import sys
from dictbook.word import Word, WordList
from dictbook.database import Database
from dictbook.exceptions import NetworkNotConnected

wl = WordList()
db = Database('d.db', 'words')


class Menu:

    def __init__(self):
        self.choices = {
            '1': self.search_net,
            '2': self.search_db_by_dt,
            '3': self.search_db_by_wd,
            '#': self.quit
        }

    def search_net(self):
        while True:
            try:
                a = input('---------------输入单词（#退出）： ')
                if a == '#':
                    return
                word = Word(a)
                print(word)
                wl.append(word)
            except KeyError as e:
                print(e.args)
            except NetworkNotConnected:
                print('请检查网络')

    def quit(self):
        try:
            for each in wl:
                db.insert(each, datetime.date.today())
        except sqlite3.IntegrityError:
            pass
        finally:
            sys.exit(0)

    def search_db_by_dt(self):
        while True:
            dt = input('输入指定日期，格式为 2019-09-01: ')
            if dt == '#':
                return
            db.content(s=dt)

    def search_db_by_wd(self):
        while True:
            wd = input('输入指定单词：')
            if wd == '#':
                return
            db.content(column='word', s=wd)

    def run(self):
        while True:
            choice = input('''
                [1] 网络查词
                [2] 历史查词（时间）
                [3] 历史查词（单词）
                [#] 退出
            ''')
            action = self.choices.get(choice)
            if action:
                action()


if __name__  == '__main__':
    menu = Menu()
    menu.run()

