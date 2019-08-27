#!/usr/bin/env python3
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
# Copyright © 2017 Carl Chenet <carl.chenet@ohmytux.com>
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

# standard libraires imports
import importlib

def activate_plugins(plugins, finaltweet):
    '''activate plugins'''
    for plugin in plugins:
        capitalizedplugin = plugin.title()
        pluginclassname = '{plugin}Plugin'.format(plugin=capitalizedplugin)
        pluginmodulename = 'feed2toot.plugins.{pluginmodule}'.format(pluginmodule=pluginclassname.lower())
        try:
            pluginmodule = importlib.import_module(pluginmodulename)
            pluginclass = getattr(pluginmodule, pluginclassname)
            pluginclass(plugins[plugin], finaltweet)
        except ImportError as err:
            print(err)
