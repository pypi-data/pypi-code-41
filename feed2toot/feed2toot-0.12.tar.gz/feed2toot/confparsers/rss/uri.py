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

# Get value of the uri option of rss section
'''Get value of the uri option of the rss section'''

# standard library imports
import feedparser
import sys
import re

def parseuri(config, clioption, feeds):
    '''Parse configuration value of the uri option of the rss section'''
    rssuri = ''
    feedname =''
    nopatternurinoglobalpattern = False
    section = 'rss'
    if config.has_section(section):
        ############
        # uri option
        ############
        if not feeds and not clioption:
            confoption = 'uri'
            if config.has_option(section, confoption):
                urifeed = config.get('rss', 'uri')
                feedname = None
                if '<' in urifeed:
                    matches = re.match('(.*) <(.*)>', urifeed)
                    if not matches:
                        sys.exit('This uri to parse is not formatted correctly: {urifeed}'.format(urifeed))
                    feedname, finaluri = matches.groups()
                    rssuri = finaluri
                else:
                    rssuri = config.get('rss', 'uri')
            else:
                sys.exit('{confoption} parameter in the [{section}] section of the configuration file is mandatory. Exiting.'.format(section=section, confoption=confoption))
        else:
            rssuri = clioption
        # get the rss feed for rss parameter of [rss] section
        feed = feedparser.parse(rssuri)
        if not feed:
            sys.exit('Unable to parse the feed at the following url: {rss}'.format(rss=rss))
        #########################################
        # no_uri_pattern_no_global_pattern option
        #########################################
        currentoption = 'no_uri_pattern_no_global_pattern'
        # default value
        if config.has_option(section, currentoption):
            nopatternurinoglobalpattern = config.getboolean(section, currentoption)
        return rssuri, feed, feedname, nopatternurinoglobalpattern
