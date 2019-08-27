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

# Get values of the hashtaglist section
'''Get values of the hashtaglist section'''

# standard library imports
import os.path
import sys

def parsehashtaglist(clioption, config):
    '''Parse configuration values and get values of the hashtaglist section'''
    hashtaglist = ''
    section = 'hashtaglist'
    if not clioption:
        ####################################
        # several_words_hashtags_list option
        ####################################
        confoption = 'several_words_hashtags_list'
        if config.has_section(section):
            if config.has_option(section, confoption):
                hashtaglist = config.get(section, confoption)
                hashtaglist = os.path.expanduser(hashtaglist)
                if not os.path.exists(hashtaglist) or not os.path.isfile(hashtaglist):
                    sys.exit('The path to the several_words_hashtags_list parameter is not valid: {hashtaglist}'.format(hashtaglist=hashtaglist))
    return hashtaglist
