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

# Get value of the toot/tweet option of rss section
'''Get value of the toot/tweet option of the rss section'''

# standard library imports
import sys
import logging

def parsetoot(config):
    '''Parse configuration value of the toot/tweet optionof the rss section'''
    section = 'rss'
    if config.has_section(section):
        ############################
        # tweet option
        ############################
        oldconfoption = 'tweet'
        confoption = 'toot'
        # manage 'tweet' for compatibility reason with first versions
        if config.has_option(section, oldconfoption):
            logging.warn("Your configuration file uses a 'tweet' parameter instead of 'toot'. 'tweet' is deprecated and will be removed in Feed2toot 0.7")
            tootformat = config.get(section, oldconfoption)
        elif config.has_option(section, confoption):
            tootformat = config.get(section, confoption)
        else:
            sys.exit('You should define a format for your tweet with the parameter "{confoption}" in the [{section}] section'.format(confoption=confoption, section=section))
    return tootformat
