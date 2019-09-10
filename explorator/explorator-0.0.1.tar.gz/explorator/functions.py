import pandas as pd
import numpy as np

from os import listdir, getcwd
from os.path import isfile, join
import sys
import operator as op
from datetime import datetime

mapping = {'января':'01',
           'февраля':'02',
           'марта':'03',
           'апреля':'04',
           'мая':'05',
           'июня':'06',
           'июля':'07',
           'августа':'08',
           'сентября':'09',
           'октября':'10',
           'ноября':'11',
           'декабря':'12',
           'январь':'01',
           'февраль':'02',
           'март':'03',
           'апрель':'04',
           'май':'05',
           'июнь':'06',
           'июль':'07',
           'август':'08',
           'сентябрь':'09',
           'октябрь':'10',
           'ноябрь':'11',
           'декабрь':'12',
           }

def filtered_string(content, delete_words = []):
    '''
    params:
        - content (str) : целевая строка
        - delete_words (list of str) : подстроки, которые надо удалить из целевой строки
    Эта функция делает следующие  преобразования со строкой:
    - Удаляет пробелы по краям строки
    - Удаляет подстроки из списка delete_words
    - Удаляет пробелы подряд в строке, оставляя один

    returns:
        - content (str) : обработанная строка
    '''

    if content != float('nan'):
        content = str(content)
        if delete_words:
            for word in delete_words:
                content = content.replace(word, '')
        content = content.strip()
        tmp = ''
        i = 0
        while i < len(content):
            if (i < len(content) - 1) and (content[i] + content[i+1] != '  '):
                tmp += content[i]
            elif i == len(content) - 1:
                tmp += content[i]
            i += 1
        content = tmp
    return content

def to_str(S, filtering = False, delete_words = []):
    '''
    params:
        - S (pd.Series) : объект pd.Series, объекты которого нужно перевести в строки
        - filtering (boolean) : флаг, который отвечает за проведение фильтрации строк на лишние пробелы и какие-либо подстроки
        - delete_words,(list of str) : подстроки, которые надо удалить из каждого объекта S (только если filtering=True)
    Эта функция делает следующие  преобразования с объектами в S:
        - Переводит в строку
        - Удаляет пробелы по краям строки
        - Удаляет подстроки из списка delete_words
        - Удаляет пробелы подряд в строке, оставляя один

    returns:
        - mS (pd.Series) : обработанный S
    '''
    mS = None
    if isinstance(S, pd.Series):
        if filtering:
            try:
                mS = S.apply(lambda x : filtered_string(x, delete_words = delete_words))
            except Exception as error:
                print('Caught this error, when was trying to convert series object to str: {}'.format(repr(error)))
        else:
            try:
                mS = S.apply(str)
            except Exception as error:
                print('Caught this error, when was trying to convert series object to str: {}'.format(repr(error)))
    else:
        raise Exception('Passed object is not a pd.Series')
    return mS

def isint(s):
    '''
    params:
        - s (str) : строка с целым числом.
    Функция, которая возращает True, если  строка является целым числом, и False в ином случае.
    returns:
        - (boolean) True, если  строка является целым числом, и False в ином случае.

    '''
    if isinstance(s, str):
        try:
            s = int(s)
            return True
        except:
            return False
    else:
        return False

def to_date(input):
    '''
    Вариант 1 (input is string):
        params:
            - input (str) : строка, содержащая дату в одном из следующих форматов:
                • '01.01.2500'
                • '01-01-2050'
                • '01 01 2050'
                • '1 января 2050'
                • 'январь  2050'
        returns:
            - whole_date (datetime.datetime) объект datetime соответсвующей даты.

    Вариант 2 (input is pd.Series):
        params:
            - input (pd.Series) : объект pd.Series со строками, содержашими дату, и которые нужно перевести в объекты типа datetime
        Функция переводит все строки, содержащие дату в input в
        returns:
            - mS (pd.Series) : обработанный input, в котором все строки преобразованы в объекты datetime
    '''
    def to_date_single(date):
        global mapping
        date = filtered_string(date).lower()
        sep = 0
        if date.find(' ') != -1:
            sep = ' '
        elif date.find('-') != -1:
            sep = '-'
        elif date.find('.') != -1:
            sep = '.'
        else:
            raise Exception('No separator found. Passed string doesnt contain supportable string format.\n{}'.format(date))
        if sep:
            date_tmp = date.split(sep)
            if len(date_tmp) == 3:
                to_do_mapping = False
                for month_name in list(mapping.keys()):
                    if month_name in date:
                        to_do_mapping = True
                if to_do_mapping:
                    date_tmp[1] = mapping[date_tmp[1]] # месяц словами
            elif len(date_tmp) == 2:
                if not isint(date_tmp[0]):
                    if date_tmp[0].lower() in list(mapping.keys()):
                        date_tmp[0] = mapping[date_tmp[0]]
                        date_tmp = ['15'] + date_tmp # так как этот случай описывает дату без конкретного числа, возьмем середину месяца
            whole_date = '.'.join(date_tmp)
            whole_date = datetime.strptime(whole_date, '%d.%m.%Y').date()
            return whole_date
        else:
            return date
    if isinstance(input, str):
        date = input
        res = to_date_single(date)
        return res

    elif isinstance(input, pd.Series):
        S = input
        mS = None
        try:
            mS = S.apply(to_date_single)
        except Exception as error:
            print('Caught this error, when was trying to convert str to datetime: {}'.format(repr(error)))
        return mS
    else:
        raise Exception('Passed object is not string or a pd.Series')
        return input
