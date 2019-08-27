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

# Get values of the configuration file
'''Get values of the configuration file'''

# standard library imports
from configparser import SafeConfigParser
import logging
import os
import os.path
import sys
import re

# 3rd party library imports
import feedparser

# feed2toot library imports
from feed2toot.confparsers.cache import parsecache
from feed2toot.confparsers.hashtaglist import parsehashtaglist
from feed2toot.confparsers.feedparser import parsefeedparser
from feed2toot.confparsers.lock import parselock
from feed2toot.confparsers.media import parsemedia
from feed2toot.confparsers.plugins import parseplugins
from feed2toot.confparsers.rss.pattern import parsepattern
from feed2toot.confparsers.rss.toot import parsetoot
from feed2toot.confparsers.rss.uri import parseuri
from feed2toot.confparsers.rss.urilist import parseurilist
from feed2toot.confparsers.rss.addtags import parseaddtags

class ConfParse:
    '''ConfParse class'''
    def __init__(self, clioptions):
        '''Constructor of the ConfParse class'''
        self.clioptions = clioptions
        self.tweetformat = ''
        self.stringsep = ','
        self.confs = []
        self.main()

    def main(self):
        '''Main of the ConfParse class'''
        for pathtoconfig in self.clioptions.configs:
            options = {}
            # read the configuration file
            config = SafeConfigParser()
            if not config.read(os.path.expanduser(pathtoconfig)):
                sys.exit('Could not read config file')
            ####################
            # feedparser section
            ####################
            accept_bozo_exceptions = parsefeedparser(config)
            ###########################
            # the rss section
            ###########################
            self.tweetformat = parsetoot(config)
            #################################################
            # pattern and patter_case_sensitive format option
            #################################################
            options['patterns'], options['patternscasesensitive'] = parsepattern(config)
            #################################################
            # lock file options
            #################################################
            options['lockfile'], options['locktimeout'] = parselock(self.clioptions.lockfile, self.clioptions.locktimeout, config)
            ###############################
            # addtags option, default: True
            ###############################
            options['addtags'] = parseaddtags(config)
            #################
            # uri_list option
            #################
            feeds = []
            feeds = parseurilist(config, accept_bozo_exceptions)
            ############
            # uri option
            ############
            options['rss_uri'], feed, feedname, options['nopatternurinoglobalpattern']  = parseuri(config, self.clioptions.rss_uri, feeds)
            ###########################
            # the cache section
            ###########################
            options['cachefile'], options['cache_limit'] = parsecache(self.clioptions.cachefile, config)
            ###########################
            # the hashtag section
            ###########################
            options['hashtaglist'] = parsehashtaglist(self.clioptions.hashtaglist, config)
            ###########################
            # the media section
            ###########################
            options['media'] = parsemedia(config)
            ###########################
            # the plugins section
            ###########################
            plugins = parseplugins(config)
            ########################################
            # return the final configurations values
            ########################################
            if feeds:
                self.confs.append((options, config, self.tweetformat, feeds, plugins))
            else:
                self.confs.append((options, config, self.tweetformat, [{'feed': feed, 'patterns': [], 'rssobject': '', 'feedname': feedname}], plugins))

    @property
    def confvalues(self):
        '''Return the values of the different configuration files'''
        return self.confs
