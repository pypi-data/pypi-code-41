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

# Get value of the uri_list option of rss section
'''Get value of the uri_list option of the rss section'''

# standard library imports
import feedparser
import logging
import os.path
import sys
import re

def parseurilist(config, accept_bozo_exceptions):
    '''Parse configuration value of the uri_list option of the rss section'''
    bozoexception = False
    feeds = []
    patterns = []
    section = 'rss'
    stringsep = ','
    if config.has_section(section):
        #################
        # uri_list option
        #################
        currentoption = 'uri_list'
        if config.has_option(section, currentoption):
            rssfile = config.get(section, currentoption)
            rssfile = os.path.expanduser(rssfile)
            if not os.path.exists(rssfile) or not os.path.isfile(rssfile):
                sys.exit('The path to the uri_list parameter is not valid: {rssfile}'.format(rssfile=rssfile))
            with open(rssfile, 'r') as rsfo:
                rsslist = rsfo.readlines()
            for line in rsslist:
                line = line.strip()
                # split each line in two parts, rss link and a string with the different patterns to look for
                feedname = ''
                if '<' in line:
                    matches = re.match('(.*) <(.*)>', line)
                    if not matches:
                        sys.exit('This line in the list of uri to parse is not formatted correctly: {line}'.format(line))
                    feedname, line = matches.groups()
                confobjects = line.split('|')
                if len(confobjects) > 3 or len(confobjects) == 2:
                    sys.exit('This line in the list of uri to parse is not formatted correctly: {line}'.format(line))
                if len(confobjects) == 3:
                    rss, rssobject, patternstring = line.split('|')
                if len(confobjects) == 1:
                    rss = confobjects[0]
                    rssobject = ''
                    patternstring = ''
                # split different searched patterns
                patterns = [i for i in patternstring.split(stringsep) if i]
                # retrieve the content of the rss
                feed = feedparser.parse(rss)
                if 'bozo_exception' in feed:
                    bozoexception = True
                    logging.warning(feed['bozo_exception'])
                    if not accept_bozo_exceptions:
                        continue
                # check if the rss feed and the rss entry are valid ones
                if 'entries' in feed:
                    if rssobject and rssobject not in feed['entries'][0].keys():
                        sys.exit('The rss object {rssobject} could not be found in the feed {rss}'.format(rssobject=rssobject, rss=rss))
                else:
                    sys.exit('The rss feed {rss} does not seem to be valid'.format(rss=rss))
                feeds.append({'feed': feed, 'patterns': patterns, 'rssobject': rssobject, 'feedname': feedname})
            # test if all feeds in the list were unsuccessfully retrieved and if so, leave
            if not feeds and bozoexception:
                sys.exit('No feed could be retrieved. Leaving.')
    return feeds
