#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" base dialog """

# pytkapp: base dialog
#
# Copyright (c) 2015 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

###################################
## import
###################################
import sys
import gettext
if __name__ == '__main__':
    if sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

#if sys.hexversion >= 0x03000000:
    #import tkinter.messagebox as messagebox
#else:
    #import tkMessageBox as messagebox

# pytkapp
from pytkapp.tkw.tkw_xtk import *
from pytkapp.tkw.tkw_xtk import cpr_tkmessagebox as messagebox

from pytkapp.pta_routines import novl, xprint

###################################
## globals
###################################

###################################
## routines
###################################

###################################
## classes
###################################


class BaseDialog:
    """ base for project dialogs """

    def __init__(self, pw_parent, **kw):
        """ init routines """

        self.__parent = pw_parent
        self.__kw = kw

        self.__toplevel = None
        self.__title = kw.get('title', _('Sample of dialog'))
        self.__logopath = kw.get('logopath', None)
        self.__logoname = kw.get('logoname', None)

        self.__w_map = {}

    def add_wmapitem(self, pv_key, pw_item):
        """ add item to widget map """

        self.__w_map[pv_key] = pw_item

    def get_wmapitem(self, pv_key, pv_default=None):
        """ get item from widget map """

        return self.__w_map.get(pv_key, pv_default)

    def get_kwtitle(self):
        """ return title """

        return self.__title

    def get_kwlogopath(self):
        """ return logopath """

        return self.__logopath

    def get_kwlogoname(self):
        """ return logoname """

        return self.__logoname

    def get_kwdata(self, pv_key, pv_def=None):
        """ return data from initial kw """

        return self.__kw.get(pv_key, pv_def)

    def get_parent(self):
        """ return parent widget """

        return self.__parent

    def get_toplevel(self):
        """ return dialog toplevel widget """

        return self.__toplevel

    def set_toplevel(self, pw_toplevel):
        """ set dialog toplevel widget """

        if self.__toplevel is None or self.__toplevel != pw_toplevel:
            pw_toplevel.bind('<Escape>', self.call_back, '+')

        self.__toplevel = pw_toplevel

    def show(self, **kw):
        """ show routines """

        raise NotImplementedError

    def call_back(self, po_event=None):
        """ back to parent routines """

        if (self.get_kwdata('nobackconfirm', False) or
            self.dialog_askokcancel(self.__kw.get('backquestion',
                                                  _('Close dialog ?')))):
            self.__toplevel.destroy()

    def get_mcontainer(self):
        """ return object for parent of messageboxes """

        return self.get_toplevel()

    def dialog_message(self, pv_type, pv_message, **kw):
        """ show some message """

        pw_parent = self.get_parent()
        if pw_parent:
            lf_parmess = getattr(pw_parent, 'child_message', getattr(pw_parent, 'app_message', None))
        else:
            lf_parmess = None

        if lf_parmess:
            ld_kw = kw.copy()
            if 'parent' not in ld_kw:
                ld_kw['parent'] = self.get_mcontainer()

            return lf_parmess(pv_type, pv_message, **ld_kw)
        else:
            lv_silence = kw.get('silence', False)
            if lv_silence not in (True, False):
                lv_silence = False

            lv_detail = kw.get('detail', None)
            lw_parent = kw.get('parent', None)
            lv_title = kw.get('title', None)

            lv_reporter = self.__title.strip()
            if pv_type == 'caution':
                lv_deftitle = '[caution]'
                lf_func = messagebox.showwarning
            elif pv_type == 'warning':
                lv_deftitle = '[warning]'
                lf_func = messagebox.showwarning
            elif pv_type == 'error':
                lv_deftitle = '[error]'
                lf_func = messagebox.showerror
            else:
                lv_deftitle = '[info]'
                lf_func = messagebox.showinfo
            lv_title = novl(lv_title, lv_deftitle)

            ld_kw = {}
            if lv_detail:
                ld_kw['detail'] = lv_detail
            ld_kw['parent'] = novl(lw_parent, self.get_mcontainer())

            for akey in ('default', 'icon',):
                if akey in kw:
                    ld_kw[akey] = kw[akey]

            lv_header = '[%s] - %s' % (pv_type, lv_reporter,)
            xprint('\n'.join(('\n', lv_header,
                              novl(lv_title, '???'),
                              novl(pv_message, '???'),
                              novl(lv_detail, ''),)).strip())

            if not lv_silence:
                lf_func(lv_title,
                        pv_message,
                        **ld_kw)

    def dialog_showwarning(self, pv_message, **kw):
        """ show some warning """

        self.dialog_message('warning', pv_message, **kw)

    def dialog_showerror(self, pv_message, **kw):
        """ show some error """

        self.dialog_message('error', pv_message, **kw)

    def dialog_showcaution(self, pv_message, **kw):
        """ show some caution """

        kw.setdefault('silence', True)
        self.dialog_message('caution', pv_message, **kw)

    def dialog_showinfo(self, pv_message, **kw):
        """ show some info """

        kw.setdefault('silence', True)
        self.dialog_message('info', pv_message, **kw)

    def dialog_ask(self, pv_type, pv_message, **kw):
        """ask... from messagebox"""

        pw_parent = self.get_parent()
        if pw_parent:
            lf_parmess = getattr(pw_parent, 'child_ask', getattr(pw_parent, 'app_ask', None))
        else:
            lf_parmess = None

        if lf_parmess:
            ld_kw = kw.copy()
            if 'parent' not in ld_kw:
                ld_kw['parent'] = self.get_mcontainer()

            return lf_parmess(pv_type, pv_message, **ld_kw)
        else:
            lv_detail = kw.get('detail', None)
            lw_parent = kw.get('parent', None)
            lv_title = kw.get('title', None)

            lv_reporter = self.__title.strip()
            if pv_type == 'okcancel':
                lf_func = messagebox.askokcancel
            elif pv_type == 'yesno':
                lf_func = messagebox.askyesno
            elif pv_type == 'yesnocancel':
                lf_func = messagebox.askyesnocancel
            else:
                lf_func = messagebox.askokcancel
            lv_title = kw.get('title', '[confirm]')

            ld_kw = {}
            if lv_detail:
                ld_kw['detail'] = lv_detail
            ld_kw['parent'] = novl(lw_parent, self.get_mcontainer())

            for akey in ('default', 'icon',):
                if akey in kw:
                    ld_kw[akey] = kw[akey]

            lv_header = '[%s] - %s' % (pv_type, lv_reporter)
            xprint('\n'.join(('\n', lv_header,
                              novl(lv_title, '???'),
                              novl(pv_message, '???'),
                              novl(lv_detail, ''),)).strip())

            return lf_func(lv_title,
                           pv_message,
                           **ld_kw)

    def dialog_askokcancel(self, pv_message, **kw):
        """ask ok/cancel"""

        return self.dialog_ask('okcancel', pv_message, **kw)

    def dialog_askyesno(self, pv_message, **kw):
        """ask yes/no"""

        return self.dialog_ask('yesno', pv_message, **kw)

    def dialog_askyesnocancel(self, pv_message, **kw):
        """ask yes/no/cancel"""

        return self.dialog_ask('yesnocancel', pv_message, **kw)
