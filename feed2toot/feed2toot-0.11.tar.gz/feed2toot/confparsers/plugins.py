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

# Get values of the plugins section
'''Get values of the plugins section'''

# standard library imports
import sys

def parseplugins(config):
    '''Parse configuration values and get values of the plugins section'''
    plugins = {}
    section = 'influxdb'
    if config.has_section(section):
        ##########################################
        # host, port, user, pass, database options
        ##########################################
        plugins[section] = {}
        for currentoption in ['host', 'port', 'user', 'pass', 'database', 'measurement']:
            if config.has_option(section, currentoption):
                plugins[section][currentoption] = config.get(section, currentoption)
        if 'host' not in plugins[section]:
            plugins[section]['host'] = '127.0.0.1'
        if 'port' not in plugins[section]:
            plugins[section]['port'] = 8086
        if 'measurement' not in plugins[section]:
            plugins[section]['measurement'] = 'toots'
        for field in ['user', 'pass', 'database']:
            if field not in plugins[section]:
                sys.exit('Parsing error for {field} in the [{section}] section: {field} is not defined'.format(field=field, section=section))
    return plugins
