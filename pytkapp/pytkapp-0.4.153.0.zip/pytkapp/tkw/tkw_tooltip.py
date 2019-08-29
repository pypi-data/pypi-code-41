#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tkw - pop-up tooltip """

# pytkapp.tkw: entry with the pop-up tooltip
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
    from tkinter import Toplevel, StringVar, Message, Misc
else:
    from Tkinter import Toplevel, StringVar, Message, Misc

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.pta_routines import get_estr

###################################
## globals
###################################
TOOLTIP_CNF_PARAMS = ('tooltip', 'tooltipcmd', 'showdelay', 'hidedelay',
                      'tooliptopbg', 'toolipbg', 'toolipfg',)

###################################
## routines
###################################


def split_tooltip_cnf(**kw):
    """split tooltip and non-tooltip cnf options"""

    if isinstance(kw, dict):
        # ======================================================
        # GDW 8/28/19
        # For python 3, use kw.items() instead of kw.iteritems()
        # ======================================================
        if sys.version_info.major < 3:
            ld_tkw = dict([pair for pair in kw.iteritems() if pair[0] in TOOLTIP_CNF_PARAMS])
            ld_okw = dict([pair for pair in kw.iteritems() if pair[0] not in TOOLTIP_CNF_PARAMS])
        else:
            ld_tkw = dict([pair for pair in kw.items() if pair[0] in TOOLTIP_CNF_PARAMS])
            ld_okw = dict([pair for pair in kw.items() if pair[0] not in TOOLTIP_CNF_PARAMS])
    else:
        ld_tkw = dict()
        ld_okw = dict()

    return (ld_okw, ld_tkw,)


def extract_tooltip_cnf(**kw):
    """extract tooltip cnf options"""

    if isinstance(kw, dict):
        # ======================================================
        # GDW 8/28/19
        # For python 3, use kw.items() instead of kw.iteritems()
        # ======================================================
        if sys.version_info.major < 3:
            ld_kw = dict([pair for pair in kw.iteritems() if pair[0] in TOOLTIP_CNF_PARAMS])
        else:
            ld_kw = dict([pair for pair in kw.items() if pair[0] in TOOLTIP_CNF_PARAMS])
    else:
        ld_kw = dict()

    return ld_kw


def remove_tooltip_cnf(**kw):
    """del custom-keys"""

    if isinstance(kw, dict):
        ld_kw = kw.copy()
        for kname in TOOLTIP_CNF_PARAMS:
            if kname in ld_kw:
                del ld_kw[kname]
    else:
        ld_kw = kw

    return ld_kw

###################################
## classes
###################################


class ToolTip(Misc):
    """main attrs and methods"""

    def __init__(self, master, **kw):
        """init me"""

        self._state = 0
        self._hide_afid = None
        self._show_afid = None
        self._tooltiptext = kw.get('tooltip', '')
        self._tooltipcmd = kw.get('tooltipcmd', None)
        self._showdelay = kw.get('showdelay', 1)
        self._hidedelay = kw.get('hidedelay', 10)
        self._tooltipvar = StringVar()
        self._tooltipvar.set(self._tooltiptext)
        self._toplevel = Toplevel(master,
                                  bg=kw.get('tooliptopbg', 'black'),
                                  padx=1,
                                  pady=1)
        self._toplevel.withdraw()
        self._toplevel.overrideredirect(True)

        self._tooltip = Message(self._toplevel,
                                bg=kw.get('toolipbg', '#ffffcc'),
                                fg=kw.get('toolipfg', 'black'),
                                aspect=1000,
                                textvariable=self._tooltipvar)
        self._tooltip.pack()

        self.bind('<Enter>', self.init_tooltip, "+")
        self.bind('<Leave>', self.hide_tooltip, "+")

    def get_tooltiptext(self):
        """get"""

        return self._tooltiptext

    def init_tooltip(self, event=None):
        """ check parent activities """

        if self._tooltiptext or self._tooltipcmd:
            self._state = 1
            self._show_afid = self.after(int(self._showdelay * 1000), self.show_tooltip)

    def show_tooltip(self, event=None):
        """ show tooltip """

        # check or get message
        lv_tooltip = None
        try:
            if self._tooltiptext:
                lv_tooltip = self._tooltiptext
            elif self._tooltipcmd:
                lv_tooltip = self._tooltipcmd()
            else:
                lv_tooltip = None
        except:
            print(get_estr())

        if lv_tooltip:
            self._tooltipvar.set(lv_tooltip)

            self._state = 2
            self._show_afid = None
            # get self position & height
            lv_x = self.winfo_rootx()
            lv_y = self.winfo_rooty()
            lv_height = self.winfo_height()

            # calc coords
            lv_lx = (self.winfo_rootx() + self._tooltip.winfo_width() + 5)
            if lv_lx < self.winfo_screenwidth() - 5:
                lv_x += 5
            else:
                lv_x += self.winfo_screenwidth() - lv_lx

            lv_ly = (self.winfo_rooty() + self.winfo_height() + self._tooltip.winfo_height() + 5)
            if lv_ly < self.winfo_screenheight() - 5:
                lv_y += lv_height + 5
            else:
                lv_y += -(self._tooltip.winfo_height() + 5)

            self._toplevel.wm_geometry("+%d+%d" % (lv_x, lv_y))

            self._toplevel.deiconify()
            self._hide_afid = self.after(int(self._hidedelay * 1000), self.hide_tooltip)
        else:
            self.hide_tooltip()

    def hide_tooltip(self, event=None):
        """ hide tooltip """

        if self._show_afid is not None:
            self.after_cancel(self._show_afid)
            self._show_afid = None
        if self._hide_afid is not None:
            self.after_cancel(self._hide_afid)
            self._hide_afid = None
        self._state = 0
        self._toplevel.withdraw()

    def configure(self, **kw):
        """ configure widget """

        if 'tooltip' in kw:
            self._tooltiptext = kw.get('tooltip', '')
            self._tooltipvar.set(self._tooltiptext)
        if 'tooltipcmd' in kw:
            self._tooltipcmd = kw.get('tooltipcmd', None)
        if 'showdelay' in kw:
            self._showdelay = kw.get('showdelay', 1)
        if 'hidedelay' in kw:
            self._hidedelay = kw.get('hidedelay', 10)
        if 'tooliptopbg' in kw:
            self._toplevel.configure(bg=kw['tooliptopbg'])
        if 'toolipbg' in kw:
            self._tooltip.configure(bg=kw['toolipbg'])
        if 'toolipfg' in kw:
            self._tooltip.configure(bg=kw['toolipfg'])
