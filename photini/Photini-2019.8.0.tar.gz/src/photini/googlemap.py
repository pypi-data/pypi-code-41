##  Photini - a simple photo metadata editor.
##  http://github.com/jim-easterbrook/Photini
##  Copyright (C) 2012-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
##
##  This program is free software: you can redistribute it and/or
##  modify it under the terms of the GNU General Public License as
##  published by the Free Software Foundation, either version 3 of the
##  License, or (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see
##  <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import locale
import logging
import re

import pkg_resources
import requests

from photini.photinimap import PhotiniMap
from photini.pyqt import Busy, QtCore, QtWidgets, scale_font

logger = logging.getLogger(__name__)


class TabWidget(PhotiniMap):
    @staticmethod
    def tab_name():
        return QtCore.QCoreApplication.translate('TabWidget', 'Map (&Google)')

    def get_head(self):
        url = 'http://maps.googleapis.com/maps/api/js?callback=initialize&v=3'
        if self.app.test_mode:
            url += '.exp'
        url += '&key=' + self.api_key
        lang, encoding = locale.getdefaultlocale()
        if lang:
            match = re.match('[a-zA-Z]+[-_]([A-Z]+)', lang)
            if match:
                name = match.group(1)
                if name:
                    url += '&region=' + name
        return '''
    <script type="text/javascript"
      src="{}" async>
    </script>
'''.format(url)

    def search_terms(self):
        widget = QtWidgets.QLabel(self.tr('Search powered by Google'))
        scale_font(widget, 80)
        return '', widget

    def do_google_geocode(self, params):
        self.disable_search()
        params['key'] = self.api_key
        lang, encoding = locale.getdefaultlocale()
        if lang:
            params['language'] = lang
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        with Busy():
            try:
                rsp = requests.get(url, params=params, timeout=5)
            except Exception as ex:
                logger.error(str(ex))
                return []
        if rsp.status_code >= 400:
            logger.error('Search error %d', rsp.status_code)
            return []
        self.enable_search()
        rsp = rsp.json()
        if rsp['status'] != 'OK':
            if 'error_message' in rsp:
                logger.error(
                    'Search error: %s: %s', rsp['status'], rsp['error_message'])
            else:
                logger.error('Search error: %s', rsp['status'])
            return []
        results = rsp['results']
        if not results:
            logger.error('No results found')
            return []
        return results

    def geocode(self, search_string, bounds=None):
        params = {
            'address': search_string,
            }
        if bounds:
            north, east, south, west = bounds
            params['bounds'] = '{!r},{!r}|{!r},{!r}'.format(
                south, west, north, east)
        for result in self.do_google_geocode(params):
            bounds = result['geometry']['viewport']
            yield (bounds['northeast']['lat'], bounds['northeast']['lng'],
                   bounds['southwest']['lat'], bounds['southwest']['lng'],
                   result['formatted_address'])
