# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

'''Manage a lock file'''

# standard libraires imports
import datetime
import logging
import os
import os.path
import sys

def sort_entries(is_all, cache, entries):
    '''sort entries before sending'''
    totweet = []
    if not is_all:
        for i in entries:
            if 'id' in i:
                if i['id'] not in cache.getdeque():
                    totweet.append(i)
            elif 'guid' in i:
                if i['guid'] not in cache.getdeque():
                    totweet.append(i)
            else:
                # if id or guid not in the entry, use link
                if i['link'] not in cache.getdeque():
                    totweet.append(i)
    else:
        totweet = entries
    return totweet
