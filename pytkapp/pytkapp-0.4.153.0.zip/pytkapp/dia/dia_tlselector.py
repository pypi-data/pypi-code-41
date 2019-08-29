#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - simple tl-based selector """

# pytkapp: common dialogs - message with tabular details
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
    from tkinter import Tk, PhotoImage, Frame
    from tkinter.constants import NW, TOP, BOTH, YES, RAISED, LEFT, RIGHT, X, NE
else:
    from Tkinter import Tk, PhotoImage, Frame
    from Tkconstants import NW, TOP, BOTH, YES, RAISED, LEFT, RIGHT, X, NE

# pytkapp
from pytkapp.pta_dialog import BaseDialog
from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.tkw.tkw_xtablelist import XTableList
from pytkapp.tkw.tkw_routines import get_estr, toolbar_separator_generator, toplevel_footer, toplevel_header, make_widget_resizeable
import pytkapp.pta_icons as pta_icons

###################################
## globals
###################################


###################################
## routines
###################################


def pass_(*args, **kw):
    """do PASS !!!"""

    pass


###################################
## classes
###################################


class BaseTLSelector(BaseDialog):
    """tl-based selector"""

    def __init__(self, pw_parent, **kw):
        """ init routines """

        self._result = None

        self._tlheaders = []
        self._tldata = []

        self._tlpopulatecmd = kw.pop('populatecmd', None)

        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc

        BaseDialog.__init__(self, pw_parent, **kw)

    def call_apply(self, po_event=None):
        """call apply btn"""

        pass_(po_event)

        self._on_apply()

    def _on_apply(self):
        """apply routine"""

        ll_result = []

        lw_tl = self.get_wmapitem('datatl')
        lt_selection = lw_tl.curselection()
        if lt_selection and len(lt_selection) > 0:
            for row_num in lt_selection:
                ll_result.append(lw_tl.rowcget(row_num, '-text'))

        self._result = ll_result

        self.get_toplevel().destroy()

    def _on_populate(self):
        """fill initial data"""

        if self._tlpopulatecmd:
            ld_data = self._tlpopulatecmd()
        else:
            ld_data = {}

        self._tldata = ld_data.get('data', [])
        self._tlheaders = ld_data.get('headers', [])

        if self._tldata and not self._tlheaders:
            self._tlheaders = list(['sys%s' % x for x in range(len(self._tldata[0]))])

    def call_select_all(self, po_event=None):
        """call select all records"""

        pass_(po_event)

        self._on_select_all()

    def call_reset_all(self, po_event=None):
        """call reset selection"""

        pass_(po_event)

        self._on_reset_all()

    def _on_select_all(self):
        """select all routine"""

        lw_tl = self.get_wmapitem('datatl')
        for row_idx in range(lw_tl.size()):
            if not lw_tl.rowcget(row_idx, '-hide') == 1:
                lw_tl.selection_set(row_idx)
        lw_tl.apply_tlfilter()

    def _on_reset_all(self):
        """reset all routine"""

        lw_tl = self.get_wmapitem('datatl')
        lt_selection = lw_tl.curselection()
        if lt_selection and len(lt_selection) > 0:
            for row_num in lt_selection:
                lw_tl.selection_clear(row_num)
        lw_tl.apply_tlfilter()

    def show(self, **kw):
        """ show routines """

        lw_toplevel, lw_topframe = toplevel_header(self.get_parent(),
                                                   title=self.get_kwtitle(),
                                                   path=self.get_kwlogopath(),
                                                   logo=self.get_kwlogoname(),
                                                   destroycmd=self.call_back)
        self.set_toplevel(lw_toplevel)

        lv_tlselectmode = kw.get('tlselectmode', "single")

        # datawidget >>>
        lw_tl = XTableList(lw_topframe,
                           activestyle="none",
                           background="white",
                           selecttype="row",
                           selectmode=lv_tlselectmode,
                           stretch="all",
                           stripebackground="gray90",
                           height=kw.get('tlheight', 15),
                           width=kw.get('tlwidth', 0),
                           # additional
                           allowresize=kw.get('tlallowresize', False),
                           allowexport=kw.get('tlallowexport', False),
                           allowfilter=kw.get('tlallowfilter', True),
                           hscroll=kw.get('tlhscroll', True),
                           vscroll=kw.get('tlvscroll', True))
        lw_tl.xcontent()
        lw_tl.pack(side=TOP, fill=BOTH, expand=YES)

        self.add_wmapitem('datatl', lw_tl)
        lw_table = lw_tl.get_datawidget()
        if lv_tlselectmode == "single":
            lw_table.body_bind('<Double-Button-1>', self.call_apply)

        # data >>>
        try:
            self._on_populate()
        except:
            self.dialog_showerror(get_estr())
        else:
            # add headers
            lt_headers = ()
            for item in self._tlheaders:
                lt_headers += (0, item,)
            lw_tl.configure(columns=lt_headers)

            # add data
            for data_row in self._tldata:
                lw_table.insertchild("root", "end", data_row)

        # controls >>>
        lw_cframe = Frame(lw_topframe, relief=RAISED, bd=2)

        if lv_tlselectmode != "none":
            lw_btn = ToolTippedBtn(lw_cframe,
                                   image=pta_icons.get_icon('gv_icon_action_accept'),
                                   tooltip=_('Accept'),
                                   command=self.call_apply)
            lw_btn.pack(side=LEFT, anchor=NW, padx=2, pady=2)

        if lv_tlselectmode in ('multiple', 'extended',):
            toolbar_separator_generator(lw_cframe, 2, 2)

            lw_btn = ToolTippedBtn(lw_cframe,
                                   image=pta_icons.get_icon('gv_icon_action_add_multy'),
                                   tooltip=_('Select all'),
                                   command=self.call_select_all)
            lw_btn.pack(side=LEFT, anchor=NW, padx=2, pady=2)

            lw_btn = ToolTippedBtn(lw_cframe,
                                   image=pta_icons.get_icon('gv_icon_clear'),
                                   tooltip=_('Reset selection'),
                                   command=self.call_reset_all)
            lw_btn.pack(side=LEFT, anchor=NW, padx=2, pady=2)

        img = PhotoImage(data=pta_icons.get_icon('gv_app_action_back'))
        lw_backbtn = ToolTippedBtn(lw_cframe, image=img, tooltip=_('Back'), command=self.call_back)
        lw_backbtn.pack(side=RIGHT, anchor=NE, padx=2, pady=2)

        lw_cframe.pack(side=TOP, fill=X)

        make_widget_resizeable(lw_toplevel)
        lw_toplevel.update_idletasks()

        toplevel_footer(lw_toplevel,
                        self.get_parent(),
                        coords=kw.get('coords', None),
                        min_width=max(lw_toplevel.winfo_reqwidth(), kw.get('width', 150)),
                        min_height=max(lw_toplevel.winfo_reqheight(), kw.get('height', 100)),
                        hres_allowed=kw.get('hal', False),
                        wres_allowed=kw.get('wal', False))

        return self._result


def demo_populatecmd():
    """ demo routine """

    ld_result = {}

    ll_data = []
    ll_data.append((1, 2, 3, 'test1', 'test11', 'test111',))
    ll_data.append((4, 5, 6, 'test2', 'test22', 'test222',))
    ll_data.append((7, 8, 9, 'test3', 'test33', 'test333',))
    ll_data.append((10, 11, 12, 'test4', 'test44', 'test444',))
    ll_data.append((13, 14, 15, 'test5', 'test55', 'test555',))
    ll_data.append((16, 17, 18, 'test6', 'test66', 'test666',))

    ll_headers = ['h1', 'h2', 'h3', 't1', 't2', 't3']

    ld_result['data'] = ll_data
    ld_result['headers'] = ll_headers

    return ld_result


def run_demo():
    """ local demo"""

    root = Tk()

    lo_dialog = BaseTLSelector(root,
                               populatecmd=lambda x=None: demo_populatecmd(),
                               title='Test')
    print(lo_dialog.show(hal=True, wal=True,
                         tlallowresize=True,
                         tlselectmode="multiple"))

if __name__ == '__main__':
    run_demo()
