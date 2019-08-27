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
'''Get value of the addtags option of the rss section'''

# standard library imports
import logging
import sys

def parseaddtags(config):
    '''Parse configuration value of the addtags option of the rss section'''
    addtags = True
    section = 'rss'
    if config.has_section(section):
        if config.has_option(section, 'addtags'):
            try:
                addtags = config.getboolean(section, 'addtags')
            except ValueError as err:
                logging.warn(err)
                addtags = True
    return addtags
