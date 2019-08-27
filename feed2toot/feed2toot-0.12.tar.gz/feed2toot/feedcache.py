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

'''Manage a cache with the ids of the feed entries'''

# standard libraires imports
from collections import deque
import os
import os.path

class FeedCache:
    '''FeedCache class'''

    def __init__(self, options):
        '''Constructore of the FeedCache class'''
        self.options = options
        self.main()

    def getdeque(self):
        '''return the deque'''
        return self.dbfeed

    def main(self):
        '''Main of the FeedCache class'''
        if os.path.exists(self.options['cachefile']):
            with open(self.options['cachefile']) as dbdsc:
                dbfromfile = dbdsc.readlines()
            dblist = [i.strip() for i in dbfromfile]
            self.dbfeed = deque(dblist, self.options['cache_limit'])
        else:
            self.dbfeed = deque([], self.options['cache_limit'])

    def append(self, rssid):
        '''Append a rss id to the cache'''
        self.dbfeed.append(rssid)

    def close(self):
        '''Close the cache'''
        with open(self.options['cachefile'], 'w') as dbdsc:
            dbdsc.writelines((''.join([i, os.linesep]) for i in self.dbfeed))
