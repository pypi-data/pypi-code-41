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

# Get values of the cache section
'''Get values of the cache section'''

# standard library imports
import os.path
import sys

def parsecache(clioption, config):
    '''Parse configuration values and get values of the hashtaglist section'''
    cachefile = ''
    cachelimit = 100
    section = 'cache'
    if not clioption:
        ##################
        # cachefile option
        ##################
        confoption = 'cachefile'
        if config.has_section(section):
            cachefile = config.get(section, confoption)
        else:
            sys.exit('You should provide a {confoption} parameter in the [{section}] section'.format(section=section, confoption=confoption))
        cachefile = os.path.expanduser(cachefile)
        cachefileparent = os.path.dirname(cachefile)
        if cachefileparent and not os.path.exists(cachefileparent):
            sys.exit('The parent directory of the cache file does not exist: {cachefileparent}'.format(cachefileparent=cachefileparent))
    else:
        cachefile = clioption
    ####################
    # cache_limit option
    ####################
    if config.has_section(section):
        confoption = 'cache_limit'
        if config.has_option(section, confoption):
            try:
                cachelimit = int(config.get(section, confoption))
            except ValueError as err:
                sys.exit('Error in configuration with the {confoption} parameter in [{section}]: {err}'.format(confoption=confoption, section=section, err=err))
        else:
            cachelimit = 100
    return cachefile, cachelimit
