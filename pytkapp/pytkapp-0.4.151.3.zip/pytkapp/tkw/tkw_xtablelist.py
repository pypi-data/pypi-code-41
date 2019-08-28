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
import os
import os.path
import codecs
import datetime
import locale
import tempfile
import gettext
if __name__ == '__main__':
    if sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if sys.hexversion >= 0x03000000:
    from tkinter import Frame, Scrollbar, StringVar
    from tkinter.constants import N, S, W, E, X, END, CENTER, YES
    from tkinter.constants import LEFT, RIGHT, VERTICAL, HORIZONTAL
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Frame, Scrollbar, StringVar
    from Tkconstants import N, S, W, E, X, END, CENTER, YES
    from Tkconstants import LEFT, RIGHT, VERTICAL, HORIZONTAL
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

# pytkapp
from pytkapp.tkw.tablelistwrapper import TableList
from pytkapp.tkw.tkw_searchdialog import SearchDialog
from pytkapp.tkw.tkw_routines import get_estr, toolbar_button_generator, toolbar_separator_generator, make_widget_ro
import pytkapp.tkw.tkw_icons as tkw_icons
from pytkapp.pta_routines import gv_defenc, tu, convert_fname, novl, xprint, Others
from pytkapp.dia.dia_pumselector import BasePUMSelector
from pytkapp.dia.dia_tlreconfdialog import TLReconfDialog
from pytkapp.dia.dia_tlreconfdialog import TABLELIST_CONFOPTS
from pytkapp.tkw.tkw_tooltippedentry import ToolTippedEntry

###################################
## globals
###################################
# bottom frame controls
XTL_BFG_RESIZE = 'resize'
XTL_BFG_EXPORT = 'export'
XTL_BFG_ITEMS = (XTL_BFG_RESIZE, XTL_BFG_EXPORT,)

XTL_BF_HIDE = 'HIDE'
XTL_BF_SHOW = 'SHOW'

# additional keywords for tl
XTL_AKW = ('allowreconf',
           'allowsearch',
           'allowresize',
           'allowexport',
           'allowkeepsel',
           'allowfilter',
           'filtercmd',
           'exportdir',
           'hscroll',
           'vscroll',
           'presearchcmd',
           'postsearchcmd',
           'prepopupcmd',
           'postconfcmd',)

###################################
## routines
###################################


def datesort(lhs, rhs):
    """ sort for data in text format """

    lv_out = 0

    lv_lhs = lhs
    lv_rhs = rhs

    # short date
    if len(lhs) == 10:
        lv_source = lhs
        if lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_lhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_lhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    if len(rhs) == 10:
        lv_source = rhs
        if lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_rhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_rhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    lv_out = cmp(lv_lhs, lv_rhs)
    if lv_out not in [0, 1, -1]:
        lv_out = 0

    return lv_out


def help_tlfilter():
    """simple help about syntax"""

    ll_out = []

    ll_out.append('Operators:')
    ll_out.append('<val1>~<val2> - filter by cells (row must contain <val1> and <val2>')
    ll_out.append('<val1>+<val2> - filter in cell (cell must contain <val1> and <val2>')
    ll_out.append('<val1>,<val2> - filter in cell (cell must contain <val1> or <val2>')
    ll_out.append('[<val1>]      - filter for cell (strict clause for <val1>)')
    ll_out.append('')
    ll_out.append('Priority:')
    ll_out.append('~ + [] ,')

    return '\n'.join(ll_out)


def refreshselvar_tlfilter(pw_tlwidget, pv_tlselvar):
    """refresh sel var for tl-widget"""

    lt_selection = novl(pw_tlwidget.curselection(), [])
    pv_tlselvar.set('%s' % len(lt_selection))


def selectall_tlfilter(pw_tlwidget, **kw):
    """apply select all for visible rows"""

    lw_tl = pw_tlwidget
    for row_idx in range(lw_tl.size()):
        if not lw_tl.rowcget(row_idx, '-hide') == 1:
            lw_tl.selection_set(row_idx)


def unselectall_tlfilter(pw_tlwidget, **kw):
    """apply unselect all for visible rows"""

    lw_tl = pw_tlwidget
    lt_selection = lw_tl.curselection()
    if lt_selection and len(lt_selection) > 0:
        for row_num in lt_selection:
            lw_tl.selection_clear(row_num)


def apply_tlfilter(pv_tlftextvar, pv_tlselvar, pv_tlfshowtvar, pv_tlfhidetvar, pw_tlwidget, **kw):
    """apply filter for tl-widget"""

    try:
        lw_table = pw_tlwidget

        # get filter text
        if pv_tlftextvar:
            lv_ftext = pv_tlftextvar.get()
        else:
            lv_ftext = None

        # prepare filter text
        if lv_ftext:
            lv_ftext = lv_ftext.strip().upper()
            ll_satoms = lv_ftext.split('~')
        else:
            ll_satoms = []

        lv_rows = pw_tlwidget.size()
        lt_selection = pw_tlwidget.curselection()
        lv_secounter = len(lt_selection)
        lv_hcounter = 0
        lv_scounter = 0

        # get list of hided columns
        ld_hidec = {}
        if lv_rows:
            try:
                lv_cols = len(lw_table.cget('-columntitles'))
                for col_index in range(lv_cols):
                    ld_hidec[col_index] = 'yes' if pw_tlwidget.columncget(col_index, '-hide') == 1 else 'no'
            except:
                pass

        # process table
        ld_hide = {}
        for row_index in range(lv_rows):
            # get row
            lt_rowdata = pw_tlwidget.rowcget(row_index, '-text')
            ld_hide[row_index] = 'yes' if pw_tlwidget.rowcget(row_index, '-hide') == 1 else 'no'

            # check row
            lb_rowaccepted = False
            if not lv_ftext or (lt_selection and row_index in lt_selection):
                lb_rowaccepted = True
            else:
                # check super-atoms (by cells)
                lb_rowaccepted = True
                for satom in ll_satoms:
                    lb_saaccepted = False

                    # check field-atom (in cell)
                    ll_fatoms = satom.split('+')
                    for celldata in ['%s' % x for i, x in enumerate(lt_rowdata) if ld_hidec.get(i, 'no') == 'no']:
                        # prepare cell
                        lv_cellvalue = celldata.strip().upper()

                        # check cell
                        lb_cellaccepted = True
                        for fatom in [a for a in ll_fatoms if a]:
                            # prepare atom
                            if fatom.startswith('!'):
                                lb_revert = True
                                lv_fatom = fatom[1:]
                            else:
                                lb_revert = False
                                lv_fatom = fatom

                            # check strict clause
                            if lv_fatom.startswith('[') and lv_fatom.endswith(']'):
                                lb_strict = True
                                lv_fatom = lv_fatom[1:-1]
                            else:
                                lb_strict = False

                            # check atom
                            lb_atomaccepted = False
                            if lv_fatom:
                                lv_fatom = lv_fatom.strip()
                                # sub-atomed clause >>>
                                if not lb_strict and ',' in lv_fatom:
                                    # prepare
                                    if lb_revert:
                                        lb_atomaccepted = True
                                    else:
                                        lb_atomaccepted = False

                                    # check sub-atom
                                    for fsatom in [b for b in lv_fatom.split(',') if b]:
                                        lv_fsatom = fsatom.strip()
                                        if lv_fsatom in lv_cellvalue:
                                            if lb_revert:
                                                lb_atomaccepted = False
                                                break
                                            else:
                                                lb_atomaccepted = True
                                                break
                                # single clause >>>
                                else:
                                    lb_atomaccepted = True
                                    if (lb_strict and lv_cellvalue == lv_fatom) or (not lb_strict and lv_fatom in lv_cellvalue):
                                        if lb_revert:
                                            lb_atomaccepted = False
                                    else:
                                        if not lb_revert:
                                            lb_atomaccepted = False

                            if not lb_atomaccepted:
                                lb_cellaccepted = False
                                break

                        # if at least one cell meet condition - show row
                        if lb_cellaccepted:
                            lb_saaccepted = True
                            break
                    # check
                    if not lb_saaccepted:
                        lb_rowaccepted = False
                        break

            # check custom filter cmd
            lf_customtlfilter = kw.get('customtlfilter', None)
            if lf_customtlfilter:
                try:
                    lb_rowaccepted = lf_customtlfilter(lt_rowdata, lb_rowaccepted)
                except Others:
                    # if any error - report it and ignore custom filter
                    lv_message = get_estr()
                    print(lv_message)

            if lb_rowaccepted:
                ld_hide[row_index] = 'no'
                lv_scounter += 1

                lv_parentkey = pw_tlwidget.parentkey(row_index)
                while lv_parentkey and lv_parentkey != 'root':
                    lv_parentindex = pw_tlwidget.index(lv_parentkey)
                    if ld_hide.get(lv_parentindex, 'no') == 'yes':
                        ld_hide[lv_parentindex] = 'no'
                        lv_scounter += 1
                        lv_hcounter -= 1
                    lv_parentkey = pw_tlwidget.parentkey(lv_parentkey)
            else:
                ld_hide[row_index] = 'yes'
                lv_hcounter += 1

        pv_tlselvar.set(lv_secounter)
        pv_tlfshowtvar.set(lv_scounter)
        pv_tlfhidetvar.set(lv_hcounter)

        # process rows
        for row_index in range(lv_rows):
            lw_table.rowconfigure(row_index, hide=ld_hide.get(row_index, 'no'))

        # see selection
        lt_selection = pw_tlwidget.curselection()
        if lt_selection and pw_tlwidget.cget('-selectmode') not in ('multiple', 'extended',) and isinstance(lt_selection, tuple):
            pw_tlwidget.see(lt_selection[0])

    except Others:
        lv_message = get_estr()
        print(lv_message)

###################################
## classes
###################################


class XTableList(Frame):
    """ Tablelist with search and additional controls """

    def __init__(self, parent, **kw):
        """ init widget

            kw: contain tablelist-specific keys and some additional:
                allowreconf: True/False - add re-conf dialog on popup
                allowsearch: True/False - call or not search dialog
                allowresize: True/False - show sizers btns
                allowexport: True/False - add btn to export table to csv
                allowfilter: True/False - create additional filter controls
                exportdir: default folder for export
                hscroll: True/False - add or not horizontal scrollbar
                vscroll: True/False - add or not vertical scrollbar
                presearchcmd: if not None than this func will be fired before dialog pop-up
                postsearchcmd: if not None than this func will be fired after dialog closing
                prepopupcmd: None or fnc(widget, event) that fired after B3 before std.popup
                postconfcmd: None or fnc(widget, event) that fired after conf.dialog
        """

        Frame.__init__(self, parent)

        self.__datawidget = None
        self.__lastsearch = None
        self.__presearchcmd = None
        self.__postsearchcmd = None

        self.__udcf = None

        self.__colaliases = []

        # extract additional keywords
        if isinstance(kw, dict):
            ld_kw = kw
        else:
            ld_kw = {}

        self.__xtl_flags = {}
        self.__xtl_flags['allowreconf'] = ld_kw.get('allowreconf', False)
        self.__xtl_flags['allowsearch'] = ld_kw.get('allowsearch', False)
        self.__xtl_flags['allowresize'] = ld_kw.get('allowresize', False)
        self.__xtl_flags['allowexport'] = ld_kw.get('allowexport', False)
        self.__xtl_flags['allowfilter'] = ld_kw.get('allowfilter', False)
        self.__filtercmd = ld_kw.get('filtercmd', None)

        self.__xtl_bf = {}
        self.__xtl_bfp = {}

        self.__exportdir = ld_kw.get('exportdir', os.getcwd())
        self.__presearchcmd = ld_kw.get('presearchcmd', None)
        self.__postsearchcmd = ld_kw.get('postsearchcmd', None)

        self.__prepopupcmd = ld_kw.get('prepopupcmd', None)
        self.__postconfcmd = ld_kw.get('postconfcmd', None)

        lb_hscroll = ld_kw.get('hscroll', False)
        lb_vscroll = ld_kw.get('vscroll', False)

        # clear ld_kw
        for akw in XTL_AKW:
            ld_kw.pop(akw, None)

        if 'exportselection' not in ld_kw:
            ld_kw['exportselection'] = False

        # filter vars >>>
        self._tlftextvar = StringVar()
        self._tlfselvar = StringVar()
        self._tlfshowvar = StringVar()
        self._tlfhidevar = StringVar()
        self._tlafid = None
        # filter vars <<<

        # user-defined cmd on double-button1 for select, active, hidden fields
        self._tlfseldm1cmd = None
        self._tlfvisdm1cmd = None
        self._tlfhiddm1cmd = None

        self.__filterframe = Frame(self, bd=0)
        self.__filterentry = None
        self.__datawidget = TableList(self, **ld_kw)
        self.__hscrollbar = Scrollbar(self) if lb_hscroll else None
        self.__vscrollbar = Scrollbar(self) if lb_vscroll else None
        self.__bottomframe = Frame(self, bd=0)

        ## forward the tablelist methods to myself (Frame)
        methods = TableList.__dict__.keys()
        for tdm in methods:
            if tdm not in ('clear',):
                setattr(self, tdm, getattr(self.__datawidget, tdm))

        # store default configurable options
        self.__defconfmatrix = {}
        for optkey in TABLELIST_CONFOPTS:
            lv_value = self.__datawidget.cget('-%s' % optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            self.__defconfmatrix['^%s' % optkey] = lv_value

    def restate(self, pstate=None):
        """override method"""

        if pstate is not None:
            lb_allowfilter = self.get_xtl_flag('allowfilter')
            if lb_allowfilter and self.__filterentry is not None:
                self.__filterentry.configure(state=pstate)

            self.__datawidget.configure(state=pstate)

    def xreconf(self, pv_attr, pv_value):
        """custom reconf"""

        if pv_attr in ('exportdir', 'unloaddir'):
            self.__exportdir = pv_value
        elif pv_attr == 'presearchcmd':
            self.__presearchcmd = pv_value
        elif pv_attr == 'postsearchcmd':
            self.__postsearchcmd = pv_value
        elif pv_attr == 'prepopupcmd':
            self.__prepopupcmd = pv_value
        elif pv_attr == 'postconfcmd':
            self.__postconfcmd = pv_value

    def configure_tlfilter(self, **kw):
        """configure some params for tl filter
        custom commands args - tlwidget, {tlfentry, tlfselvar, tlfvisvar, tlfhidvar}"""

        self._tlfseldm1cmd = kw.get('tlfseldm1cmd', None)
        self._tlfvisdm1cmd = kw.get('tlfvisdm1cmd', None)
        self._tlfhiddm1cmd = kw.get('tlfhiddm1cmd', None)

    def _on_dmouse1_tlfactive(self):
        """double-button-1 on "active" entry of tl filter"""

        lb_allowfilter = self.get_xtl_flag('allowfilter')
        if lb_allowfilter:
            lw_tl = self.__datawidget
            lv_tlftextvar = self._tlftextvar
            lv_tlfselvar = self._tlfselvar
            lv_tlfshowvar = self._tlfshowvar
            lv_tlfhidevar = self._tlfhidevar

            if self._tlfseldm1cmd is not None:
                self._tlfseldm1cmd(lw_tl,
                                   tlfentry=lv_tlftextvar,
                                   tlfselvar=lv_tlfselvar,
                                   tlfvisvar=lv_tlfshowvar,
                                   tlfhidvar=lv_tlfhidevar)

            refreshselvar_tlfilter(lw_tl, lv_tlfselvar)

    def _on_dmouse1_tlfvisible(self):
        """double-button-1 on "visible" entry of tl filter"""

        lb_allowfilter = self.get_xtl_flag('allowfilter')
        if lb_allowfilter:
            lw_tl = self.__datawidget
            lv_tlftextvar = self._tlftextvar
            lv_tlfselvar = self._tlfselvar
            lv_tlfshowvar = self._tlfshowvar
            lv_tlfhidevar = self._tlfhidevar

            if self._tlfvisdm1cmd is not None:
                self._tlfvisdm1cmd(lw_tl,
                                   tlfentry=lv_tlftextvar,
                                   tlfselvar=lv_tlfselvar,
                                   tlfvisvar=lv_tlfshowvar,
                                   tlfhidvar=lv_tlfhidevar)

            refreshselvar_tlfilter(lw_tl, lv_tlfselvar)

    def _on_dmouse1_tlfhidden(self):
        """double-button-1 on "hidden" entry of tl filter"""

        lb_allowfilter = self.get_xtl_flag('allowfilter')
        if lb_allowfilter:
            lw_tl = self.__datawidget
            lv_tlftextvar = self._tlftextvar
            lv_tlfselvar = self._tlfselvar
            lv_tlfshowvar = self._tlfshowvar
            lv_tlfhidevar = self._tlfhidevar

            if self._tlfhiddm1cmd is not None:
                self._tlfhiddm1cmd(lw_tl,
                                   tlfentry=lv_tlftextvar,
                                   tlfselvar=lv_tlfselvar,
                                   tlfvisvar=lv_tlfshowvar,
                                   tlfhidvar=lv_tlfhidevar)

            refreshselvar_tlfilter(lw_tl, lv_tlfselvar)

    def get_defconfmatrix(self):
        """get default tlmatrix"""

        return self.__defconfmatrix.copy()

    def get_defconfmatrix_value(self, matrix_key):
        """get value from default tlmatrix"""

        return self.__defconfmatrix.get(matrix_key, '')

    def xcontent(self):
        """ generate widget additional content """

        lb_allowsearch = self.get_xtl_flag('allowsearch')
        lb_allowresize = self.get_xtl_flag('allowresize')
        lb_allowexport = self.get_xtl_flag('allowexport')
        lb_allowfilter = self.get_xtl_flag('allowfilter')

        lv_mr = -1
        lv_mc = 0

        if lb_allowfilter:
            # show filter >>>
            lv_mr += 1

            lw_tlfilterframe = self.__filterframe
            lw_tlftext = ToolTippedEntry(lw_tlfilterframe, tooltip=_('Filter'), textvariable=self._tlftextvar)
            lw_tlftext.pack(side=LEFT, fill=X, expand=YES)
            self.__filterentry = lw_tlftext
            lw_tlftext.focus()

            lw_tlfstataentry = ToolTippedEntry(lw_tlfilterframe, justify=CENTER, tooltip=_('Active'), width=5,
                                               textvariable=self._tlfselvar)
            lw_tlfstataentry.pack(side=LEFT)
            make_widget_ro(lw_tlfstataentry)

            lw_tlfstatventry = ToolTippedEntry(lw_tlfilterframe, justify=CENTER, tooltip=_('Visible'), width=5, bg="gray",
                                               textvariable=self._tlfshowvar)
            lw_tlfstatventry.pack(side=LEFT)
            make_widget_ro(lw_tlfstatventry)
            lw_tlfstathentry = ToolTippedEntry(lw_tlfilterframe, justify=CENTER, tooltip=_('Hidden'), width=5, bg="gray",
                                               textvariable=self._tlfhidevar)
            lw_tlfstathentry.pack(side=LEFT)
            make_widget_ro(lw_tlfstathentry)
            lw_tlfilterframe.grid(row=lv_mr, column=lv_mc, columnspan=2 if self.__vscrollbar else 1, sticky=N+E+W+S, padx=2, pady=2)
            # show filter <<<

        lv_mr += 1
        self.__datawidget.grid(row=lv_mr, column=lv_mc, sticky=N+E+W+S)
        self.__datawidget.configure(labelcommand=self.on_header_click)
        self.__datawidget.body_bind('<Button-3>', self.call_datawidget_popup, '+')

        Frame.columnconfigure(self, lv_mc, weight=1)
        Frame.rowconfigure(self, lv_mr, weight=1)

        if lb_allowfilter:
            # configure filter >>>
            lw_tl = self.__datawidget
            lv_tlftextvar = self._tlftextvar
            lv_tlfselvar = self._tlfselvar
            lv_tlfshowvar = self._tlfshowvar
            lv_tlfhidevar = self._tlfhidevar
            lf_cf = self.__filtercmd

            lf_cmd = lambda v0=lv_tlftextvar, v1=lv_tlfselvar, v2=lv_tlfshowvar, v3=lv_tlfhidevar, w=lw_tl, cf=lf_cf: apply_tlfilter(v0, v1, v2, v3, w, customtlfilter=cf)

            lw_tlftext.bind('<KeyRelease>', lambda e=None, f=lf_cmd: self._delay_tlfilter(f), '+')
            lw_tlftext.bind('<FocusIn>', lambda e=None, f=lf_cmd: self._delay_tlfilter(f, 1000), '+')
            lw_tl.body_bind('<ButtonRelease-1>', lambda e=None, f=lf_cmd: f(), '+')

            lw_tlfstataentry.bind('<Double-Button-1>', lambda e=None: self._on_dmouse1_tlfactive())
            lw_tlfstatventry.bind('<Double-Button-1>', lambda e=None: self._on_dmouse1_tlfvisible())
            lw_tlfstathentry.bind('<Double-Button-1>', lambda e=None: self._on_dmouse1_tlfhidden())

            lw_tlftext.bind('<F1>', lambda e=None, p=self.__datawidget.winfo_toplevel(): messagebox.showinfo(_('Filter syntax'),
                                                                                                             help_tlfilter()))
            apply_tlfilter(None, lv_tlfselvar, lv_tlfshowvar, lv_tlfhidevar, lw_tl, customtlfilter=lf_cf)
            # configure filter <<<

        if self.__vscrollbar:
            vbar = self.__vscrollbar
            vbar.configure(orient=VERTICAL)
            self.__datawidget['yscrollcommand'] = vbar.set
            vbar['command'] = self.__datawidget.yview
            vbar.grid(row=lv_mr, column=lv_mc+1, sticky=N+E+W+S)

        if self.__hscrollbar:
            lv_mr += 1
            hbar = self.__hscrollbar
            hbar.configure(orient=HORIZONTAL)
            self.__datawidget['xscrollcommand'] = hbar.set
            hbar['command'] = self.__datawidget.xview
            hbar.grid(row=lv_mr, column=lv_mc, sticky=N+E+W+S)

        if lb_allowsearch:
            self.__lastsearch = StringVar()
            self.__datawidget.body_bind('<Control-KeyPress-f>', self.call_seach_dialog)
            self.__datawidget.body_bind('<F3>', lambda event, m='single': self.call_reseach(m))
            self.__datawidget.body_bind('<Control-F3>', lambda event, m='all': self.call_reseach(m))

        # bottom frame >>>
        lv_mr += 1
        lw_bottomframe = self.__bottomframe

        self.__udcf = Frame(lw_bottomframe, bd=0)
        self.__udcf.pack(side=LEFT, anchor=W, fill=X)

        lw_cf = Frame(lw_bottomframe, bd=0)

        lv_r = 0
        lv_c = self.custom_bottom_subframe(lw_cf, lv_r, 0)

        if lb_allowresize or lb_allowexport:

            if lb_allowresize:
                lw_bf = Frame(lw_cf)

                toolbar_button_generator(lw_bf,
                                         _('Resize by data'),
                                         tkw_icons.get_icon('gv_xtablelist_resizebydata'),
                                         self.call_resizebydata,
                                         padx=2, pady=2)

                toolbar_button_generator(lw_bf,
                                         _('Resize by headers'),
                                         tkw_icons.get_icon('gv_xtablelist_resizebyheaders'),
                                         self.call_resizebyheaders,
                                         padx=2, pady=2)

                if lb_allowexport:
                    toolbar_separator_generator(lw_bf, ppadx=3, ppady=2)

                lw_bf.grid(row=lv_r, column=lv_c, sticky=N+E)
                self.__xtl_bf[XTL_BFG_RESIZE] = lw_bf
                self.__xtl_bfp[XTL_BFG_RESIZE] = lv_c
                lv_c += 1

            if lb_allowexport:
                lw_bf = Frame(lw_cf)

                toolbar_button_generator(lw_bf,
                                         _('Export data'),
                                         tkw_icons.get_icon('gv_xtablelist_export'),
                                         self.call_export,
                                         padx=2, pady=2)

                lw_bf.grid(row=lv_r, column=lv_c, sticky=N+E)
                self.__xtl_bf[XTL_BFG_EXPORT] = lw_bf
                self.__xtl_bfp[XTL_BFG_EXPORT] = lv_c
                lv_c += 1

        lw_cf.pack(side=RIGHT, anchor=E)

        lw_bottomframe.grid(row=lv_mr, column=lv_mc, columnspan=2 if self.__vscrollbar else 1, sticky=N+E+W+S, pady=2)
        # bottom frame <<<

    def custom_bottom_subframe(self, pw_bframe, pv_r, pv_c):
        """ generate custom bottom subframe
            generate content and return next position
        """

        return pv_c

    def get_xtl_flag(self, pv_flag):
        """ get value of xtl flag """

        return self.__xtl_flags.get(pv_flag, None)

    def set_xtl_flag(self, pv_flag, pv_value):
        """ set value of xtl flag """

        self.__xtl_flags[pv_flag] = pv_value

    def get_xtl_bf(self, pv_key):
        """ get item from xtl_bf """

        return self.__xtl_bf.get(pv_key, None)

    def set_xtl_bf(self, pv_key, pv_value):
        """ set item to xtl_bf """

        self.__xtl_bf[pv_key] = pv_value

    def get_xtl_bfp(self, pv_key):
        """ get item from xtl_bfp """

        return self.__xtl_bfp.get(pv_key, None)

    def set_xtl_bfp(self, pv_key, pv_value):
        """ set item to xtl_bfp """

        self.__xtl_bfp[pv_key] = pv_value

    def manage_bottom_frame(self, pv_flag, pv_operation):
        """ hide/show bottom frame btn-groups """

        if pv_flag in XTL_BFG_ITEMS:
            if pv_operation in (XTL_BF_HIDE, XTL_BF_SHOW) and self.get_xtl_flag('allow%s' % pv_flag):
                lw_frame = self.__xtl_bf.get(pv_flag, None)
                if lw_frame is not None:
                    if pv_operation == XTL_BF_HIDE:
                        lw_frame.grid_forget()
                    else:
                        lw_frame.grid(row=0, column=self.__xtl_bfp[pv_flag], sticky=N+E)

    def call_datawidget_reconfdialog(self, po_event=None):
        """call datawidget reconfiguration dialog"""

        lo_dialog = TLReconfDialog(self,
                                   title=_('Configuration'),
                                   widget=self)
        lo_dialog.show()

        if self.__postconfcmd:
            self.__postconfcmd(self.__datawidget, po_event)

    def get_tlmatrix(self):
        """get matrix of datawidget"""

        ld_matrix = {}

        lw_tl = self
        lw_table = lw_tl.get_datawidget()

        lt_headers = lw_table.cget('-columntitles')

        if not isinstance(lt_headers, tuple):
            lt_headers = tuple()

        # columns >>>
        for col_indx in range(len(lt_headers)):
            # prepare data
            lv_header = lt_headers[col_indx]

            lv_hide = lw_table.columncget("%s" % col_indx, "-hide")

            ld_coldata = {}
            ld_coldata['hide'] = lv_hide

            ld_matrix[lv_header] = ld_coldata

        # others configurable options >>>
        for optkey in TABLELIST_CONFOPTS:
            lv_value = lw_tl.cget('-%s' % optkey)
            lv_value = getattr(lv_value, 'string', '%s' % lv_value)
            ld_matrix['^%s' % optkey] = lv_value

        return ld_matrix

    def apply_tlmatrix(self, pd_matrix=None):
        """apply matrix"""

        if pd_matrix:
            lw_tl = self
            lw_table = lw_tl.get_datawidget()

            lt_headers = lw_table.cget('-columntitles')

            if not isinstance(lt_headers, tuple):
                lt_headers = tuple()

            # column >>>
            for col_indx in range(len(lt_headers)):
                # prepare data
                lv_header = lt_headers[col_indx]

                ld_matrixdata = pd_matrix.get(lv_header, None)
                if ld_matrixdata:
                    # show/hide columns
                    lv_hide = ld_matrixdata.get('hide', 0)
                    lw_table.columnconfigure("%s" % col_indx, hide=lv_hide)

            # others configurable options
            for mkey, tlkey in [(mkey, mkey[1:],) for mkey in tuple(pd_matrix.keys()) if mkey.startswith('^')]:
                try:
                    lv_value = pd_matrix[mkey]

                    if lv_value == "None":
                        lv_value = None

                    ld_kw = {}
                    ld_kw[tlkey] = lv_value

                    lw_tl.configure(**ld_kw)
                except Others:
                    print('%s' % get_estr())

    def call_datawidget_popup(self, po_event=None):
        """call pop-up menu from datawidget"""

        if self.__prepopupcmd:
            ll_uservariants = self.__prepopupcmd(self.__datawidget, po_event)
        else:
            ll_uservariants = []

        ll_variants = []

        if self.get_xtl_flag('allowreconf'):
            ll_variants.append((_('Configuration'),
                                tkw_icons.get_icon('gv_icon_widget_configure'),
                                lambda e=po_event: self.call_datawidget_reconfdialog(e),))

        if ll_uservariants:
            ll_variants += ll_uservariants

        if ll_variants:
            BasePUMSelector(self,
                            po_event,
                            variants=ll_variants,
                            tearoff=0)

    def call_pass(self, po_event=None):
        """pass"""

        print('pass')

    def get_aliases(self):
        """ get current aliases """

        return self.__colaliases[:]

    def set_aliases(self, pl_aliases):
        """ set aliases for tablelist """

        self.__colaliases = pl_aliases

    def get_colindex4alias(self, pv_alias):
        """ get index of column by alias """

        for i, data in enumerate(self.__colaliases):
            if data.upper() == pv_alias.upper():
                return i

        raise IndexError

    def get_colindex4title(self, pv_title):
        """ get index of column by title """

        lv_res = self.__datawidget.cget('-columntitles')
        if isinstance(lv_res, tuple) and len(lv_res) > 0:
            for i, data in enumerate(lv_res):
                if data.upper() == pv_title.upper():
                    return i

        raise IndexError

    def get_udcf(self):
        """ return user-defined control frame """

        return self.__udcf

    def call_seach_dialog(self, po_event=None):
        """ call search dialog for widget """

        if self.__presearchcmd is not None:
            self.__presearchcmd()

        lo_dialog = SearchDialog(self,
                                 self.__datawidget,
                                 lastsearch=self.__lastsearch,
                                 postsearchcmd=self.__postsearchcmd)

        lv_index = lo_dialog.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see(lv_index)
            self.__datawidget.update_idletasks()

            return "break"

    def call_reseach(self, pv_mode=None):
        """ process single re-search without pop-up dialog """

        if self.__presearchcmd is not None:
            self.__presearchcmd()

        lo_dialog = SearchDialog(self,
                                 self.__datawidget,
                                 lastsearch=self.__lastsearch,
                                 research=pv_mode,
                                 postsearchcmd=self.__postsearchcmd)

        lv_index = lo_dialog.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see(lv_index)
            self.__datawidget.update_idletasks()

            return "break"

    def get_datawidget(self):
        """ return datawidget """

        return self.__datawidget

    def call_resizebydata(self, po_event=None):
        """ set width of columns by data """

        for column_indx in range(self.__datawidget.columncount()):
            self.__datawidget.columnconfigure(column_indx, width=0)

    def call_resizebyheaders(self, po_event=None):
        """ set width of columns by headers """

        for column_indx in range(self.__datawidget.columncount()):
            h_len = len(self.__datawidget.columncget(column_indx, '-title'))+1
            self.__datawidget.columnconfigure(column_indx, width=h_len)

    def directexport(self, pv_ext):
        """ call export in tempfile or call export routines """

        lv_ext = novl(pv_ext, '').lower()
        lv_exppath = None
        if lv_ext in ('.csv', '.html'):
            try:
                lf_file = tempfile.NamedTemporaryFile(delete=False, suffix=lv_ext)
                lf_file.close()
            except Others:
                lv_message = get_estr()
                print(lv_message)
            else:
                self.export_(lf_file.name)

                lv_exppath = lf_file.name
        else:
            lv_exppath = self.call_export()

        return lv_exppath

    def export_(self, pv_filename=None):
        """ export routines """

        if novl(pv_filename, '') != '':
            lv_ext = os.path.splitext(pv_filename.lower())[1]
            with codecs.open(pv_filename, 'w+', locale.getpreferredencoding()) as lo_f:
                lv_tlsize = self.__datawidget.size()
                # save header
                lt_headers = self.__datawidget.cget('-columntitles')

                if not isinstance(lt_headers, tuple):
                    lt_headers = tuple()

                if lv_ext == '.csv':
                    lo_f.write(tu(';').join([tu(i) for i in lt_headers])+'\n')
                else:
                    lo_f.write('<!DOCTYPE HTML PUBLIC  "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n')
                    lo_f.write('<HTML>\n')
                    lo_f.write('<HEAD>\n')
                    lo_f.write('<meta http-equiv="Content-Type" content="text/html; charset=%s">\n' % (gv_defenc.replace('_', '-')))
                    lo_f.write('<TITLE>%s</TITLE>\n' % (_('Export')))
                    lo_f.write('</HEAD>\n')
                    lo_f.write('<BODY>\n')
                    lo_f.write('<BASEFONT size="2">\n')
                    lo_f.write('<TABLE border="1" cellspacing="0">\n')

                    lo_f.write('<TR>\n')
                    lo_f.write(''.join(['%s%s' % (tu('<TH>'), tu(i)) for i in lt_headers])+'\n')

                # save data
                for row_indx in range(lv_tlsize):
                    ll_data = list(self.__datawidget.rowcget(row_indx, "-text"))

                    lv_bg = self.__datawidget.rowcget(row_indx, '-background')
                    lv_fg = self.__datawidget.rowcget(row_indx, '-foreground')

                    if getattr(lv_bg, 'string', '') != '':
                        lv_trbg = 'bgcolor="%s"' % lv_bg
                    else:
                        lv_trbg = ''
                    if getattr(lv_fg, 'string', '') != '':
                        lv_trfg = 'fgcolor="%s"' % lv_bg
                    else:
                        lv_trfg = ''

                    if lv_ext == '.csv':
                        lo_f.write(tu(';').join([tu(i) for i in ll_data])+'\n')
                    else:
                        lo_f.write('<TR %s %s>\n' % (lv_trbg, lv_trfg))

                        for i, data in enumerate(ll_data):
                            lv_bg = self.__datawidget.cellcget('%s,%s' % (row_indx, i), '-background')
                            lv_fg = self.__datawidget.cellcget('%s,%s' % (row_indx, i), '-foreground')

                            if getattr(lv_bg, 'string', '') != '':
                                lv_tdbg = 'bgcolor="%s"' % lv_bg
                            else:
                                lv_tdbg = ''
                            if getattr(lv_fg, 'string', '') != '':
                                lv_tdfg = '<span style="color:%s">' % (lv_fg)
                                lv_tdfg2 = '</span>'
                            else:
                                lv_tdfg = ''
                                lv_tdfg2 = ''

                            if novl(tu(data), '').strip() == '':
                                lv_data = '&nbsp;'
                            else:
                                lv_data = data

                            lo_f.write('<TD %s>%s%s%s' % (lv_tdbg, lv_tdfg, lv_data, lv_tdfg2))

                            if i == len(ll_data) - 1:
                                lo_f.write('\n')

                if lv_ext == '.html':
                    lo_f.write('</TABLE>\n')
                    lo_f.write('</BODY>\n')
                    lo_f.write('</HTML>\n')

    def call_export(self, po_event=None):
        """ export table to csv-file """

        lv_exppath = None
        lv_defexportpath = self.__exportdir
        if not os.path.isdir(lv_defexportpath):
            lv_defexportpath = os.getcwd()
            xprint('Warning! Default folder for export doesnt exists: %s' % (self.__exportdir))

        lv_exportpath = filedialog.asksaveasfilename(title=_('Export data'),
                                                     filetypes={"csv-file {.csv}": 0,
                                                                "html-file {.html}": 1},
                                                     initialdir=lv_defexportpath,
                                                     defaultextension='csv',
                                                     parent=self.__datawidget.winfo_toplevel())
        lv_exportpath = convert_fname(lv_exportpath)

        if novl(lv_exportpath, '') != '':
            lv_exportpath = os.path.realpath(lv_exportpath).lower()

            lv_ext = os.path.splitext(lv_exportpath.lower())[1]

            if lv_ext not in ('.csv', '.html'):
                lv_exportpath += '.csv'
                lv_ext = '.csv'

            lv_folder = os.path.split(lv_exportpath)[0]
            if os.path.exists(lv_folder):

                self.export_(lv_exportpath)
                lv_exppath = lv_exportpath

                messagebox.showinfo(_('Info'),
                                    _('Export completed !'),
                                    detail=lv_exportpath,
                                    parent=self.__datawidget.winfo_toplevel())

        return lv_exppath

    def on_header_click(self, pv_tlpath, pv_column):
        """ process sorting for column """

        lv_order = "-increasing"
        if self.__datawidget.sortcolumn() == int(pv_column) and self.__datawidget.sortorder() == "increasing":
            lv_order = "-decreasing"

        self.__datawidget.sortbycolumn(pv_column, lv_order)

    def clear_(self, po_event=None):
        """ clear internal structires """

        self.__colaliases = []
        if self.__lastsearch is not None:
            self.__lastsearch.set('')

    def clear_data(self, po_event=None, pb_grid=True):
        """ clear all stored data """

        lv_table = self.__datawidget

        if pb_grid:
            lv_table.grid_remove()
        try:
            lv_table.delete(0, "end")
        finally:
            if pb_grid:
                lv_table.grid()

        # align filter >>>
        if self.get_xtl_flag('allowfilter'):
            self._tlfselvar.set('0')
            self._tlfshowvar.set('0')
            self._tlfhidevar.set('0')
        # align filter <<<

    def insert_data(self, lv_pos=END, lt_data=()):
        """simple insert data"""

        self.__datawidget.insert(lv_pos, lt_data)

    def clear(self, po_event=None):
        """ clear all content of widget """

        lv_table = self.__datawidget

        lv_table.grid_remove()
        try:
            lv_table = self.__datawidget
            lt_ct = lv_table.cget('-columntitles')
            if isinstance(lt_ct, tuple) and len(lt_ct) > 0:
                lv_table.deletecolumns(0, len(lt_ct)-1)

            lv_table.delete(0, "end")
            lv_table.resetsortinfo()
        finally:
            lv_table.grid()

        # align filter >>>
        if self.get_xtl_flag('allowfilter'):
            self._tlftextvar.set('')
            self._tlfselvar.set('0')
            self._tlfshowvar.set('0')
            self._tlfhidevar.set('0')
        # align filter <<<

        self.clear_()

    def apply_tlfilter(self, **kw):
        """apply filter command manually"""

        lb_allowfilter = self.get_xtl_flag('allowfilter')
        if lb_allowfilter:
            lw_tl = self.__datawidget
            lv_tlftextvar = self._tlftextvar
            lv_tlfselvar = self._tlfselvar
            lv_tlfshowvar = self._tlfshowvar
            lv_tlfhidevar = self._tlfhidevar
            lf_cf = self.__filtercmd

            apply_tlfilter(None if kw.get('nofiltervar', False) else lv_tlftextvar, lv_tlfselvar, lv_tlfshowvar, lv_tlfhidevar, lw_tl, customtlfilter=lf_cf)

    def _delay_tlfilter(self, pf_cmd, pv_delay=500):
        """init tlfilter over delay"""

        if self._tlafid:
            self.after_cancel(self._tlafid)
            self._tlafid = None

        self._tlafid = self.after(pv_delay, lambda: self._fire_tlfilter(pf_cmd))

    def _fire_tlfilter(self, pf_cmd):
        """fire and call"""

        self._tlafid = None
        pf_cmd()
