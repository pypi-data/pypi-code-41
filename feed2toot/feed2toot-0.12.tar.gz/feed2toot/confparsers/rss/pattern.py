# -*- coding: utf-8 -*-
# Copyright © 2015-2019 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/

# Get value of the patterne option of rss section
'''Get value of the pattern option of the rss section'''

# standard library imports
import logging
import sys

def parsepattern(config):
    '''Parse configuration value of the pattern option of the rss section'''
    patterns = {}
    patternscasesensitive = {}
    stringsep = ','
    section = 'rss'
    if config.has_section(section):
        #######################
        # pattern format option
        #######################
        for pattern in ['summary_detail', 'published_parsed', 'guidislink', 'authors', 'links', 'title_detail', 'author', 'author_detail', 'comments', 'published', 'summary', 'tags', 'title', 'link', 'id']:
            currentoption = '{}_pattern'.format(pattern)
            if config.has_option(section, currentoption):
                tmppattern = config.get(section, currentoption)
                if stringsep in tmppattern:
                    patterns[currentoption] = [i for i in tmppattern.split(stringsep) if i]
                else:
                    patterns[currentoption] = [tmppattern]

            ###############################
            # pattern_case_sensitive option
            ###############################
            currentoption = '{}_pattern_case_sensitive'.format(pattern)
            if config.has_option(section, currentoption):
                try:
                    patternscasesensitive[currentoption] = config.getboolean(section, currentoption)
                except ValueError as err:
                    logging.warn(err)
                    patternscasesensitive[currentoption] = True
            else:
                # default value
                patternscasesensitive[currentoption] = False
    return patterns, patternscasesensitive
