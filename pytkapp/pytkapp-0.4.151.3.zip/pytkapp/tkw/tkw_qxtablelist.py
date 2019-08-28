#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tablelist widget with scrolling and additional
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: tablelist widget with scrolling and additional controls
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

if sys.hexversion >= 0x03000000:
    from tkinter import Frame
    from tkinter.constants import N, E
else:
    from Tkinter import Frame
    from Tkconstants import N, E

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_xtablelist import XTableList
from pytkapp.tkw.tkw_xtablelist import XTL_BF_HIDE, XTL_BF_SHOW
from pytkapp.tkw.tkw_routines import toolbar_button_generator, toolbar_separator_generator
import pytkapp.pta_icons as pta_icons

###################################
## globals
###################################
# bottom frame controls
XTL_BFG_TLQUERY = 'tlquery'
XTL_BFG_ITEMS = (XTL_BFG_TLQUERY,)

# additional kw for tl
XTL_AKW = ('allowtlquery', 'querycmd',)

###################################
## routines
###################################

###################################
## classes
###################################


class QXTableList(XTableList):
    """ XTablelist with external query func"""

    def __init__(self, parent, **kw):
        """ additional keywords:
              allowtlquery: True/False - quering allowed
              querycmd - routine with 2 arg
                part - last queried potion
                stop - True, False (for fast forward - False)
                should return list of tuples OR None
        """

        ld_kw = kw.copy()

        self._querycmd = None
        self._queryidx = 0

        lb_allowtlquery = False

        for akw in XTL_AKW:
            if akw == 'allowtlquery':
                lb_allowtlquery = ld_kw.pop('allowtlquery', False)
            elif akw == 'querycmd':
                self._querycmd = ld_kw.pop('querycmd', None)

        XTableList.__init__(self, parent, **ld_kw)

        self.set_xtl_flag('allowtlquery', lb_allowtlquery)

    def custom_bottom_subframe(self, pw_bframe, pv_r, pv_c):
        """ generate custom bottom subframe """

        lb_allowtlquery = self.get_xtl_flag('allowtlquery')

        lb_allowresize = self.get_xtl_flag('allowresize')
        lb_allowexport = self.get_xtl_flag('allowexport')

        lv_c = pv_c

        if lb_allowtlquery:
            lw_bf = Frame(pw_bframe)

            toolbar_button_generator(lw_bf,
                                     _('Fast rewind'),
                                     pta_icons.get_icon('gv_icon_player2_frewind'),
                                     self.call_ffrewind,
                                     padx=2, pady=2)

            toolbar_separator_generator(lw_bf, ppadx=2, ppady=2)

            toolbar_button_generator(lw_bf,
                                     _('Forward'),
                                     pta_icons.get_icon('gv_icon_arrow_state_blue_right'),
                                     self.call_forward,
                                     padx=2, pady=2)

            toolbar_separator_generator(lw_bf, ppadx=2, ppady=2)

            toolbar_button_generator(lw_bf,
                                     _('Fast forward'),
                                     pta_icons.get_icon('gv_icon_player2_fforward'),
                                     self.call_fforward,
                                     padx=2, pady=2)

            if lb_allowresize or lb_allowexport:
                toolbar_separator_generator(lw_bf, ppadx=3, ppady=2)

            lw_bf.grid(row=pv_r, column=lv_c, sticky=N+E)
            self.set_xtl_bf(XTL_BFG_TLQUERY, lw_bf)
            self.set_xtl_bfp(XTL_BFG_TLQUERY, lv_c)
            lv_c += 1

        return lv_c

    def manage_bottom_frame(self, pv_flag, pv_operation):
        """ hide/show bottom frame btn-groups """

        if pv_flag in XTL_BFG_ITEMS:
            if pv_operation in (XTL_BF_HIDE, XTL_BF_SHOW) and self.get_xtl_flag('allow%s' % pv_flag):
                lw_frame = self.get_xtl_bf(pv_flag)
                if lw_frame is not None:
                    if pv_operation == XTL_BF_HIDE:
                        lw_frame.grid_forget()
                    else:
                        lw_frame.grid(row=0, column=self.get_xtl_bfp(pv_flag), sticky=N+E)
        else:
            XTableList.manage_bottom_frame(self, pv_flag, pv_operation)

    def call_ffrewind(self, po_event=None):
        """call ffrewind"""

        self.get_datawidget().see("0")

    def call_forward(self, po_event=None):
        """call forward"""

        lb_allowtlquery = self.get_xtl_flag('allowtlquery')

        if lb_allowtlquery and self._querycmd:
            if self._queryidx is not None:
                lt_data = self._querycmd(self._queryidx)
            else:
                lt_data = None

            if lt_data:
                self._queryidx += 1
                self.insertlist("end", tuple(lt_data))

                self.refreshsorting()
                self.apply_tlfilter()

            self.get_datawidget().see("end")

    def call_fforward(self, po_event=None):
        """call fforward"""

        lb_allowtlquery = self.get_xtl_flag('allowtlquery')

        if lb_allowtlquery and self._querycmd:
            if self._queryidx is not None:
                lt_data = self._querycmd(self._queryidx, False)
            else:
                lt_data = None

            if lt_data:
                self._queryidx = None
                self.insertlist("end", tuple(lt_data))

                self.refreshsorting()
                self.apply_tlfilter()

            self.get_datawidget().see("end")
