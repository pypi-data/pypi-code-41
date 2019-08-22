#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import print_function
import re
import os.path
from codecs import open
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

INC_SYNTAX = re.compile(r'\{!\s*(.+?)\s*!\}')


class MarkdownIncludeCustom(Extension):
    def __init__(self, configs={}):
        self.config = {
            'base_path': ['.', 'Default location from which to evaluate ' \
                'relative paths for the include statement.'],
            'encoding': ['utf-8', 'Encoding of the files used by the include ' \
                'statement.'],
            'locale_dir':['.', 'Current locale directory'],
        }
        for key, value in configs.items():
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'includecustom', IncludeCustomPreprocessor(md,self.getConfigs()),'_begin'
        )


class IncludeCustomPreprocessor(Preprocessor):

    def __init__(self, md, config):
        super(IncludeCustomPreprocessor, self).__init__(md)
        self.base_path = config['base_path']
        self.encoding = config['encoding']
        self.locale_dir = config['locale_dir']
    def run(self, lines):
        done = False
        while not done:
            for line in lines:
                loc = lines.index(line)

                result = re.search('{! (ingredients/.*) !}', line)

                if result:
                  line = result.group(0)
                  target = result.group(1)

                  check = target[::-1]
                  checkComponent = self.locale_dir[::-1]
                  check = check.replace('/', '/' + checkComponent + '/',1)
                  check = 'multilang/'+check[::-1]

                  if os.path.exists(self.base_path + check):
                    lines[loc] = lines[loc].replace(target, check)
                    line = lines[loc]
                  else:
                      check = 'multilang/' + target

                      if os.path.exists(self.base_path + check):
                        lines[loc] = lines[loc].replace(target, check)
                        line = lines[loc]
                
                m = INC_SYNTAX.search(line)

                if m:
                    filename = m.group(1)
                    filename = os.path.expanduser(filename)
                    if not os.path.isabs(filename):
                        filename = os.path.normpath(
                            os.path.join(self.base_path,filename)
                        )
                    try:
                        with open(filename, 'r', encoding=self.encoding) as r:
                            text = r.readlines()
                    except Exception as e:
                        print('Warning: could not find file {}. Ignoring '
                            'include statement. Error: {}'.format(filename, e))
                        lines[loc] = INC_SYNTAX.sub('',line)
                        break

                    line_split = INC_SYNTAX.split(line,maxsplit=0)
                    if len(text) == 0: text.append('')
                    for i in range(len(text)):
                        text[i] = text[i][0:-1]
                    text[0] = line_split[0] + text[0]
                    text[-1] = text[-1] + line_split[2]
                    lines = lines[:loc] + text + lines[loc+1:]
                    break
            else:
                done = True
        return lines


def makeExtension(*args,**kwargs):
    return MarkdownIncludeCustom(kwargs)
