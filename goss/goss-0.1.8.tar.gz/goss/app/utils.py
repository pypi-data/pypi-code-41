#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import click
import configparser
import os
import gevent
import time
import re

GOSS_CONFIG_HOME = '{}/.config/goss'.format(os.getenv("HOME"))
GOSS_CONFIG_PATH = '{}/config'.format(GOSS_CONFIG_HOME)
GOSS_CREDENTIAL_PATH = '{}/credentials'.format(GOSS_CONFIG_HOME)

def print_success(msg='Success!'):
    click.secho(msg, fg='cyan')

def print_failed(msg='Failed!'):
    click.secho(msg, fg='red')

def print_progress(msg='Waiting...'):
    click.secho(msg, fg='yellow')

def print_error(msg):
    click.secho(msg, fg='red')

def make_progress_msg(msg):
    return click.style(msg, fg = 'yellow')

def make_error_msg(msg):
    return click.style(msg, fg = 'red')

def print_dict(data, exclude=[], key_fg='magenta', val_fg=''):
    item = dict(data)
    for e in exclude:
        item.pop(e)
    max_len = max([len(k) for k, v in item.items()])
    max_len += 10
    click.echo('')
    for k, v in item.items():
        key = click.style(k.title(), fg=key_fg).ljust(max_len)
        value = click.style(f"{v}", fg=val_fg)
        line = f"{key}: {value}"
        click.echo(line)
    click.echo('')

#  def print_list(data, include, val_suffixs):
    #  click.echo("")
    #  title = ''.join(include).title()
    #  hor_len = len(title.replace('\t', '-' * 8))
    #  hor_line = click.style('-' * hor_len, fg='yellow')
    #  click.secho(title, fg='magenta')
    #  click.secho(hor_line)
    #  for d in data:
        #  lines = []
        #  for i in range(len(include)):
            #  f = include[i]
            #  field_len = len(f.replace('\t', '*' * 8))
            #  field_key = f.rstrip('\t')
            #  field_val = f"{d[field_key]}{val_suffixs[i]}"
            #  lines.append(field_val)
        #  line = ''.join(lines)
        #  click.echo(line)
    #  click.secho(hor_line)
    #  total = click.style(str(len(data)), fg='cyan')
    #  click.secho(f'Total : {total}')
    #  click.echo('')

def print_list(data, *include):
    max_len_dict = {o: len(o) for o in include}
    for d in data:
        for f in include:
            #  print(d[f])
            max_len_dict[f] = max(max_len_dict[f], charlen(str(d[f])))

    title = '\t'.join([o.ljust(max_len_dict[o]) for o in include])
    hor_len = sum([v for k, v in max_len_dict.items()])
    hor_line = click.style('-' * hor_len, fg='yellow')
    click.secho(title, fg='magenta')
    click.secho(hor_line)
    for l in data:
        for k in include:
            l[k] = charljust(str(l[k]), max_len_dict[k])
        line = '\t'.join([str(l[k]) for k in include])
        click.echo(line)
    click.secho(hor_line)
    total = click.style(str(len(data)), fg='cyan')
    click.secho(f'Total : {total}')
    #  click.echo('')


def config(filepath, section, **data):
    '''新建或修改配置'''
    conf = configparser.ConfigParser()
    if os.path.exists(filepath):
        conf.read(filepath)
    else:
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    if section in conf:
        val = conf[section]
        if val:
            val.update(data)
            data = val

    conf[section] = dict(data)

    with open(filepath, 'w') as f:
        conf.write(f)
        f.close()

is_done = False

def print_dynamic_progress(msg = 'Waiting...'):
    print('begin progress')
    gevent.sleep(0)
    count = 0
    pl = ('⠸' ,'⠼' ,'⠴' ,'⠦' ,'⠧' ,'⠏' ,'⠙' ,'⠹')
    while count < 10000:
        for p in pl:
            print(f'{p} {msg}', end='\r')
        count += 1
    print('Success!       ')

def work():
    print('begin work')
    gevent.sleep(0)
    time.sleep(2)
    is_done = True
    print('end work')

class Progress():
    is_done = False
    is_waiting = True

    def print_dynamic_progress(self, msg = 'Waiting...'):
        print('begin progress')
        pl = ('⠸' ,'⠼' ,'⠴' ,'⠦' ,'⠧' ,'⠏' ,'⠙' ,'⠹')
        while not self.is_done:
            print(self.is_done, self.is_waiting)
            while self.is_waiting:
                for p in pl:
                    print(msg)
                    print(f'{p} {msg}', end='\r')
        print('Success!       ')

RE_CHINESE = re.compile(u"[\u4e00-\u9fa5]+")  # 正则查找中文

def charlen(s):
    '''
    Return the str's char len
    '''
    ch_results = RE_CHINESE.findall(s)
    return len(s) + len(''.join(ch_results))

def charepr(s, width=30):
    realen = charlen(s)
    if realen <= width:
        return s
    substr = ''
    max_str_len = 0
    for a in s:
        if charlen(substr) + charlen(a) + 3 > width:
            break
        substr += a
        max_str_len = charlen(substr)
    return substr + '.' * (width - charlen(substr))

def charljust(s, width, fullchar=' '):
    w = width - (charlen(s) - len(s))
    return s.ljust(w, fullchar)

if __name__ == "__main__":
    #  gevent.joinall([
        #  gevent.spawn(work),
        #  gevent.spawn(print_dynamic_progress),
    #  ])
    #  print_dynamic_progress()
    lines = [
        dict(id = 17764214, name='vname', tag_name='v1.0.1'),
        dict(id = 17764214, name='', tag_name='v1.0.1'),
    ]
    #  print_list(lines, ['id\t\t', 'name\t', 'tag_name'])
    print_list(lines, 
                ['id\t\t', 'name\t', 'tag_name'],
                ['\t', '\t', ''],
            )


