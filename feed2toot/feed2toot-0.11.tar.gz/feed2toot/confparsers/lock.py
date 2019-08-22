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

# Get values of the lock section
'''Get values of the lock section'''

# standard library imports
import os.path
import sys

def parselock(lockfile, locktimeout, config):
    '''Parse configuration values and get values of the hashtaglist section'''
    lockfile = lockfile
    locktimeout = locktimeout
    section = 'lock'
    ##################
    # lockfile option
    ##################
    confoption = 'lock_file'
    if config.has_section(section):
        lockfile = config.get(section, confoption)
    lockfile = os.path.expanduser(lockfile)
    lockfileparent = os.path.dirname(lockfile)
    if lockfileparent and not os.path.exists(lockfileparent):
        sys.exit('The parent directory of the lock file does not exist: {lockfileparent}'.format(lockfileparent=lockfileparent))
    ######################
    # lock_timeout option
    ######################
    if config.has_section(section):
        confoption = 'lock_timeout'
        if config.has_option(section, confoption):
            try:
                locktimeout = int(config.get(section, confoption))
            except ValueError as err:
                sys.exit('Error in configuration with the {confoption} parameter in [{section}]: {err}'.format(confoption=confoption, section=section, err=err))
    return lockfile, locktimeout
