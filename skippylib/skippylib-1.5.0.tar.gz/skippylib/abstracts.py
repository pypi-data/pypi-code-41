# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from PyTango import DevState

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class AbstractSkippyObj(object):
    def __init__(self, name, parent=None, *args, **kwargs):
        super(AbstractSkippyObj, self).__init__()
        if name is None:
            raise AssertionError("SkippyObj must have a name")
        self._name = name
        self._parent = parent

    @property
    def name(self):
        return self._name

    # TODO: python logging when there is no tango device above

    def debug_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: {0}".format(msg))

    def info_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.info_stream(msg)
        else:
            print("INFO:  {0}".format(msg))

    def warn_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.warn_stream(msg)
        else:
            print("WARN:  {0}".format(msg))

    def error_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.error_stream(msg)
        else:
            print("ERROR: {0}".format(msg))

    def _get_state(self):
        if hasattr(self, '_statemachine') and self._statemachine:
            return self._statemachine.state
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, 'get_state'):
            return self._parent.get_state()
        return DevState.UNKNOWN

    def _change_state_status(self, newState=None, newLine=None,
                             important=False):
        if hasattr(self, '_statemachine') and self._statemachine:
            if newState is not None:
                self._statemachine.state = newState
            if newLine is not None:
                self._statemachine.addStatusMessage(newLine, important)
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, '_change_state_status'):
            self._parent._change_state_status(newState, newLine, important)


class AbstractSkippyAttribute(AbstractSkippyObj):
    def __init__(self, *args, **kwargs):
        super(AbstractSkippyAttribute, self).__init__(*args, **kwargs)


class AbstractSkippyFeature(AbstractSkippyObj):
    def __init__(self, *args, **kwargs):
        super(AbstractSkippyFeature, self).__init__(*args, **kwargs)
