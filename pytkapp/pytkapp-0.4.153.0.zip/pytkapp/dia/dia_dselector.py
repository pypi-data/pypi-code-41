#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - date selector """

# pytkapp: common dialogs - date selector
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
import itertools
import calendar
import datetime
if __name__ == '__main__':
    if sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if sys.hexversion >= 0x03000000:
    from tkinter import Tk, StringVar, PhotoImage, Frame, Label, Button
    from tkinter.constants import N, E, W, S, FLAT, SUNKEN, TOP, BOTH, YES, RAISED
    from tkinter.ttk import Combobox as ttkCombobox
else:
    from Tkinter import Tk, StringVar, PhotoImage, Frame, Label, Button
    from Tkconstants import N, E, W, S, FLAT, SUNKEN, TOP, BOTH, YES, RAISED
    from ttk import Combobox as ttkCombobox

# pytkapp
import pytkapp.pta_icons as pta_icons
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.pta_routines import novl, to_long, get_estr
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable
from pytkapp.pta_dialog import BaseDialog

###################################
## globals
###################################
SHOW_MODE_SIMPLE = 'simple'

LMONTHES = [x for x in calendar.month_name if x]

DEFDATE_FORMAT_NATIVE = 'dd.mm.yyyy'
DEFDATE_FORMAT_DT = '%d.%m.%Y'

ALLOWED_DATE_FORMATS = ('dd.mm.yyyy', 'yyyy.mm.dd', 'mm.dd.yyyy', 'yyyy.dd.mm',
                        'dd-mm-yyyy', 'yyyy-mm-dd', 'mm-dd-yyyy', 'yyyy-dd-mm'
                        'dd/mm/yyyy', 'yyyy/mm/dd', 'mm/dd/yyyy', 'yyyy/dd/mm')
DATE_MAP = {}
for fmt in ALLOWED_DATE_FORMATS:
    lv_part = fmt.replace('dd', '%d').replace('mm', '%m').replace('yyyy', '%Y')
    DATE_MAP[fmt] = lv_part

###################################
## routines
###################################


def validate_date(pv_value, pv_format=DEFDATE_FORMAT_NATIVE):
    """ validate string with date and return it

        return None or datetime
        or raise ValueError
    """

    if pv_value is None:
        return None
    else:
        if pv_format in DATE_MAP:
            lv_format = DATE_MAP[pv_format]
        else:
            lv_format = pv_format
        return datetime.datetime.strptime(pv_value, lv_format).date()

###################################
## classes
###################################


class BaseDSelector(BaseDialog):
    """ base class for date selector """

    def __init__(self, pw_parent, **kw):
        """ init routines """

        self._result = None

        self._palette = {}

        # days abbrs
        self._palette['abbr_bg'] = kw.get('abbr_bg', '#cccccc')
        self._palette['abbr_fg'] = kw.get('abbr_fg', 'black')

        # cur selected date
        self._palette['sel_bg'] = kw.get('sel_bg', '#ffff00')
        self._palette['sel_fg'] = kw.get('sel_fg', 'black')

        # today
        self._palette['today_bg'] = kw.get('today_bg', '#000066')
        self._palette['today_fg'] = kw.get('today_fg', 'white')

        # default
        self._palette['def_bg'] = kw.get('def_bg', 'white')
        self._palette['def_fg'] = kw.get('def_fg', 'black')

        # bg for active elements
        self._palette['nact_bg'] = kw.get('nact_bg', '#f3f3f3')
        self._palette['act_bg'] = kw.get('act_bg', '#ffff99')

        # None or string or string from ALLOWED_DATE_FORMATS
        self._outformat = kw.get('outformat', None)

        # process today and selected values, convert if necessary
        self._today = datetime.date.today()

        self._selected = kw.get('selected', None)
        if isinstance(self._selected, datetime.date):
            pass
        elif isinstance(self._selected, str) and self._selected:
            self._selected = datetime.datetime.strptime(self._selected, self._get_outformat()).date()
        else:
            self._selected = None

        self._iselected = self._selected
        self._active = novl(self._selected, self._today)

        self._wbtns = list(itertools.repeat(None, 31))

        self._cm = StringVar()
        self._cm.set(LMONTHES[self._active.month-1])

        self._cy = StringVar()
        self._cy.set(self._active.year)

        self._cstorage = None
        self._cpanel = None

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        BaseDialog.__init__(self, pw_parent, **kw)

    def _get_outformat(self):
        """return out format"""

        if self._outformat and self._outformat in DATE_MAP:
            return DATE_MAP[self._outformat]
        elif self._outformat:
            return self._outformat
        else:
            return DATE_MAP[DEFDATE_FORMAT_NATIVE]

    def _do_preoutformat(self):
        """process out value with specified format"""
        try:
            if self._result and self._outformat:
                lv_out = self._result.strftime(self._get_outformat())
            elif self._result:
                lv_out = self._result
            else:
                lv_out = None
        except:
            self.dialog_showerror(get_estr())

        return lv_out

    def on_select(self, pv_result=None):
        """ set result on select """

        lv_last = self._selected

        self._selected = pv_result

        # repaint last
        if lv_last:
            if lv_last == self._selected:
                lv_bg = self._palette['sel_bg']
                lv_fg = self._palette['sel_fg']
                lv_relief = FLAT
            elif lv_last == self._today:
                lv_bg = self._palette['today_bg']
                lv_fg = self._palette['today_fg']
                lv_relief = FLAT
            else:
                lv_bg = self._palette['nact_bg']
                lv_fg = self._palette['def_fg']
                lv_relief = FLAT

            self._wbtns[lv_last.day-1].configure(bg=lv_bg, fg=lv_fg, relief=lv_relief)

        # repaint current
        self._active = novl(self._selected, self._today)
        if self._active == self._selected:
            lv_bg = self._palette['sel_bg']
            lv_fg = self._palette['sel_fg']
            lv_relief = FLAT
        elif self._active == self._today:
            lv_bg = self._palette['today_bg']
            lv_fg = self._palette['today_fg']
            lv_relief = FLAT
        else:
            lv_bg = self._palette['nact_bg']
            lv_fg = self._palette['def_fg']
            lv_relief = FLAT

        self._wbtns[self._active.day-1].configure(bg=lv_bg, fg=lv_fg, relief=lv_relief)

    def on_refresh(self):
        """restore initial position"""

        # recalc date
        self._selected = self._iselected
        self._active = novl(self._selected, self._today)
        self._cm.set(LMONTHES[self._active.month-1])
        self._cy.set(self._active.year)

        # recreate panel
        self._do_repanel()

    def on_now(self):
        """recreate panel with current date"""

        # recalc date
        self._selected = self._iselected
        self._active = self._today
        self._cm.set(LMONTHES[self._active.month-1])
        self._cy.set(self._active.year)

        # recreate panel
        self._do_repanel()

    def on_achange(self, pv_m=None, pv_y=None):
        """some change on active date"""

        # recalc date
        self._active = datetime.date(year=novl(pv_y, self._active.year),
                                     month=novl(pv_m, self._active.month),
                                     day=1)

        # recreate panel
        self._do_repanel()

    def on_apply(self):
        """apply selection"""

        self._result = novl(self._selected, self._today)
        self.get_toplevel().destroy()

    def on_qchange(self, pv_md=0):
        """some action on quick nav"""

        # recalc date
        lv_m = self._active.month
        lv_y = self._active.year

        lv_m += pv_md * 1
        if lv_m > 12:
            lv_m = 1
            lv_y += 1
        elif lv_m < 1:
            lv_m = 12
            lv_y -= 1

        self._active = datetime.date(year=lv_y, month=lv_m, day=1)

        self._cm.set(LMONTHES[lv_m-1])
        self._cy.set(self._active.year)

        # recreate panel
        self._do_repanel()

    def _do_repanel(self):
        """regenerate calendar panel"""

        if self._cpanel:
            self._cpanel.destroy()

        self._cpanel = Frame(self._cstorage, relief=FLAT, bd=0, bg=self._palette['def_bg'])

        lv_fd_year = self._active.year
        lv_fd_month = self._active.month

        lv_fd = datetime.date(year=lv_fd_year, month=lv_fd_month, day=1)
        lv_fd_dw = lv_fd.weekday()

        lv_ld = calendar.monthrange(lv_fd_year, lv_fd_month)[1]

        lv_r = 0
        for abbr_indx, abbr_val in enumerate(calendar.day_abbr):
            lv_bg = self._palette['abbr_bg']
            lv_fg = self._palette['abbr_fg']
            lv_relief = FLAT
            lv_bd = 0

            lw_db = Label(self._cpanel,
                          relief=lv_relief,
                          bd=lv_bd,
                          bg=lv_bg,
                          text=abbr_val,
                          takefocus=0,
                          fg=lv_fg)
            lw_db.grid(row=lv_r, column=abbr_indx, sticky=N+E+W+S, padx=2, pady=2)

        lv_r += 1
        lv_c = lv_fd_dw

        self._wbtns = list(itertools.repeat(None, 31))

        for i in range(0, lv_ld):

            lv_cd = datetime.date(year=lv_fd_year, month=lv_fd_month, day=i+1)

            if lv_cd == self._selected:
                lv_bg = self._palette['sel_bg']
                lv_fg = self._palette['sel_fg']
                lv_relief = FLAT
                lv_bd = 0
            elif lv_cd == self._today:
                lv_bg = self._palette['today_bg']
                lv_fg = self._palette['today_fg']
                lv_relief = FLAT
                lv_bd = 0
            else:
                lv_bg = self._palette['nact_bg']
                lv_fg = self._palette['def_fg']
                lv_relief = FLAT
                lv_bd = 0

            lw_db = ToolTippedBtn(self._cpanel,
                                  relief=lv_relief,
                                  activebackground=self._palette['act_bg'],
                                  bd=lv_bd,
                                  bg=lv_bg,
                                  fg=lv_fg,
                                  text='%s' % (i+1),
                                  tooltip=lv_cd.strftime(DATE_MAP[self._outformat]) if self._outformat and self._outformat in DATE_MAP else lv_cd.strftime(DEFDATE_FORMAT_DT),
                                  command=lambda e=None, d=lv_cd: self.on_select(d))
            lw_db.grid(row=lv_r, column=lv_c, sticky=N+E+W+S, padx=2, pady=2)
            lw_db.bind('<Double-Button-1>', lambda e=None: self.on_apply(), '+')

            # store panel buttons
            self._wbtns[i] = lw_db

            if lv_c != 0 and lv_c % 6 == 0:
                lv_r += 1
                lv_c = 0
            else:
                lv_c += 1

        for lv_r in range(lv_r+1, 7):

            lv_fg = self._palette['def_bg']
            lv_bg = self._palette['def_bg']
            lv_relief = FLAT
            lv_bd = 0

            lw_db = Button(self._cpanel,
                           relief=lv_relief,
                           bd=lv_bd,
                           bg=lv_bg,
                           takefocus=0,
                           fg=lv_fg)
            lw_db.grid(row=lv_r, column=0, sticky=N+E+W+S, padx=2, pady=2)

        self._cpanel.pack(side=TOP, pady=1, anchor="center")

    def show(self, **kw):
        """ show routines """

        lw_toplevel, lw_topframe = toplevel_header(self.get_parent(),
                                                   title=self.get_kwtitle(),
                                                   path=self.get_kwlogopath(),
                                                   logo=self.get_kwlogoname(),
                                                   destroycmd=self.call_back,
                                                   noresize=1)
        self.set_toplevel(lw_toplevel)

        lw_main = Frame(lw_topframe, relief=SUNKEN, bd=2)

        lv_r = 0
        lv_c = 0
        lw_ccontrol = Frame(lw_main, relief=RAISED, bd=1)

        lw_rbtn = ToolTippedBtn(lw_ccontrol,
                                image=pta_icons.get_icon('gv_icon_action_check'),
                                tooltip=_('Apply'),
                                command=lambda e=None: self.on_apply())
        lw_rbtn.grid(row=0, column=lv_c, sticky=N+E+W+S, padx=1, pady=1)

        lv_c += 1
        lw_rbtn = ToolTippedBtn(lw_ccontrol,
                                image=pta_icons.get_icon('gv_icon_refresh_green'),
                                tooltip=_('Go to selected'),
                                command=lambda e=None: self.on_refresh())
        lw_rbtn.grid(row=0, column=lv_c, sticky=N+E+W+S, padx=1, pady=1)

        lv_c += 1
        lw_rbtn = ToolTippedBtn(lw_ccontrol,
                                image=pta_icons.get_icon('gv_icon_refresh_blue'),
                                tooltip=_('Go to today'),
                                command=lambda e=None: self.on_now())
        lw_rbtn.grid(row=0, column=lv_c, sticky=N+E+W+S, padx=1, pady=1)

        lv_c += 1
        lw_cmlist = ttkCombobox(lw_ccontrol,
                                values=LMONTHES,
                                textvariable=self._cm,
                                state="readonly",
                                width=15)
        lw_cmlist.grid(row=0, column=lv_c, sticky=N+E+W+S)
        lw_cmlist.bind('<<ComboboxSelected>>', lambda e=None: self.on_achange(LMONTHES.index(self._cm.get())+1))

        lv_c += 1
        lw_cylist = ttkCombobox(lw_ccontrol,
                                values=tuple(range(1900,
                                                   2100,
                                                   1)),
                                textvariable=self._cy,
                                state="readonly",
                                width=4)
        lw_cylist.grid(row=0, column=lv_c, sticky=N+E+W+S)
        lw_cylist.bind('<<ComboboxSelected>>', lambda e=None: self.on_achange(None, to_long(self._cy.get())))

        lw_ccontrol.columnconfigure(lv_c-1, weight=1)
        lw_ccontrol.grid(row=lv_r, column=0, sticky=N+E+W+S)

        lv_r += 1
        lw_cmain = Frame(lw_main, relief=FLAT, bd=0)

        img = PhotoImage(data=pta_icons.get_icon('gv_icon_fullscr_quick_nav_left'))
        lw_qnl = Button(lw_cmain,
                        image=img,
                        bd=0,
                        command=lambda e=None, md=-1: self.on_qchange(md))
        lw_qnl._img = img
        lw_qnl.grid(row=0, column=0, sticky=N+W+S)

        self._cstorage = Frame(lw_cmain, relief=FLAT, bd=0, bg=self._palette['def_bg'])
        self._do_repanel()
        self._cstorage.grid(row=0, column=1, sticky=N+E+W+S)

        img = PhotoImage(data=pta_icons.get_icon('gv_icon_fullscr_quick_nav_right'))
        lw_qnr = Button(lw_cmain,
                        image=img,
                        bd=0,
                        command=lambda e=None, md=1: self.on_qchange(md))
        lw_qnr._img = img
        lw_qnr.grid(row=0, column=2, sticky=N+E+S)

        lw_cmain.rowconfigure(0, weight=1)
        lw_cmain.columnconfigure(1, weight=1)

        lw_cmain.grid(row=lv_r, column=0, sticky=N+E+W+S, pady=2)

        lw_main.columnconfigure(0, weight=1)
        lw_main.rowconfigure(lv_r, weight=1)

        lw_main.pack(side=TOP, fill=BOTH, expand=YES, padx=2, pady=2)

        make_widget_resizeable(lw_toplevel)
        lw_toplevel.update_idletasks()

        toplevel_footer(lw_toplevel,
                        self.get_parent(),
                        coords=kw.get('coords', None),
                        min_width=lw_toplevel.winfo_reqwidth(),
                        min_height=lw_toplevel.winfo_reqheight(),
                        hres_allowed=False,
                        wres_allowed=False)

        return self._do_preoutformat()


def run_test():
    """simple test"""

    root = Tk()

    ld_params = {}

    ld_params['title'] = 'Select date'
    ld_params['selected'] = datetime.date.today() - datetime.timedelta(days=4)
    lo_dialog = BaseDSelector(root,
                              **ld_params)
    print(lo_dialog.show())

if __name__ == '__main__':
    run_test()
