#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - pop-up selector based on menu """

# pytkapp: common dialogs - pop-up selector based on menu
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
    from tkinter import Tk, PhotoImage, Frame, Menu, IntVar
    from tkinter.constants import LEFT
else:
    from Tkinter import Tk, PhotoImage, Frame, Menu, IntVar
    from Tkconstants import LEFT

# pytkapp
import pytkapp.pta_icons as pta_icons

###################################
## globals
###################################

###################################
## routines
###################################


def pass_print(pv_arg):
    """call print from anywere"""
    print('called from %s' % pv_arg)

###################################
## classes
###################################


class BasePUMSelector(Menu):
    """ sample of selector dialog from menu """

    def __init__(self, pw_parent, po_event, **kw):
        """ init routines """

        # title, icon, command
        ll_variants = kw.pop('variants', [])
        self.__images = []

        Menu.__init__(self, pw_parent, **kw)
        lw_menu = self

        lw_mainmenu = self
        ld_menugroups = {}

        if ll_variants:
            for varindex, vardata in enumerate(ll_variants):
                if vardata[0] == '<separator>':
                    try:
                        lv_noper = ll_variants[varindex+1][0]
                    except:
                        lv_noper = None
                    if lv_noper and lv_noper not in ('<grouptail>',):
                        lw_menu.add_separator()
                elif vardata[0] == '<groupheader>':
                    lv_groupname = vardata[1]
                    ld_menugroups[lv_groupname] = lw_menu
                    try:
                        lo_image = PhotoImage(data=vardata[2])
                        self.__images.append(lo_image)
                    except:
                        lo_image = None
                    lw_nmenu = Menu(self, tearoff=0)
                    if lo_image:
                        lw_menu.add_cascade(label=_(lv_groupname), menu=lw_nmenu, compound=LEFT, image=lo_image)
                    else:
                        lw_menu.add_cascade(label=_(lv_groupname), menu=lw_nmenu)
                    lw_menu = lw_nmenu
                elif vardata[0] == '<grouptail>':
                    lv_groupname = vardata[1]
                    lw_menu = ld_menugroups.get(lv_groupname, lw_mainmenu)
                # obsoletted mode - dont use !
                elif vardata[0] == '<userdefined>':
                    lv_groupname = _('User-defined')
                    ld_menugroups[lv_groupname] = lw_menu
                    lw_nmenu = Menu(self, tearoff=0)
                    lw_menu.add_cascade(label=_(lv_groupname), menu=lw_nmenu)
                    lw_menu = lw_nmenu
                    #lw_menu.add_separator()
                    #lw_menu = Menu(self, tearoff=0)
                    #self.add_cascade(label=_('User-defined'), menu=lw_menu)
                elif vardata[0] == '<flag>':
                    menutitle, menuvar = vardata[1:]
                    lw_menu.add_checkbutton(label=menutitle, onvalue=1, offvalue=False, variable=menuvar)
                else:
                    menutitle, menuicon, menucommand = vardata
                    if menuicon:
                        try:
                            lo_image = PhotoImage(data=menuicon)
                            self.__images.append(lo_image)
                        except:
                            lo_image = None
                    else:
                        lo_image = None
                    if lo_image:
                        lw_menu.add_command(label=menutitle, command=menucommand, compound=LEFT, image=lo_image)
                    else:
                        lw_menu.add_command(label=menutitle, command=menucommand)

            #self.post(po_event.x_root, po_event.y_root)
            self.tk_popup(po_event.x_root, po_event.y_root)
            pw_parent.after_idle(lambda i=self: i.destroy())
        else:
            print('variants list is empty !')


def run_demo():
    """ local demo """

    root = Tk()

    frame = Frame(root, width=400, height=300)
    frame.pack()

    ll_variants = []
                        # text, icon, command
    ll_variants.append(('File', pta_icons.get_icon('gv_options_openfile'), lambda a='var:file': pass_print(a),))
    ll_variants.append(('Folder', pta_icons.get_icon('gv_options_openfolder'), lambda a='var:folder': pass_print(a),))

    ll_variants.append(('<separator>',))

    ll_variants.append(('Dummy1', pta_icons.get_icon('gv_options_openfolder'), lambda a='var:d1': pass_print(a),))

    ll_variants.append(('<groupheader>', 'Dummy1-group 1',))

    ll_variants.append(('Dummy11.1', None, lambda a='var:d11.1': pass_print(a),))
    ll_variants.append(('Dummy11.2', None, lambda a='var:d11.2': pass_print(a),))

    ll_variants.append(('<grouptail>', 'Dummy1-group 1',))

    ll_variants.append(('<groupheader>', 'Dummy1-group 2', pta_icons.get_icon('gv_options_openfolder'),))

    ll_variants.append(('Dummy12.1', None, lambda a='var:d12.1': pass_print(a),))
    ll_variants.append(('Dummy12.2', None, lambda a='var:d12.2': pass_print(a),))

    ll_variants.append(('<grouptail>', 'Dummy1-group 2',))

    ll_variants.append(('<separator>',))

    ll_variants.append(('<groupheader>', 'Dummy2', pta_icons.get_icon('gv_icon_dlist'),))

    ll_variants.append(('<flag>', 'flag-1', IntVar(),))
    ll_variants.append(('<flag>', 'flag-2', IntVar(),))

    ll_variants.append(('<grouptail>', 'Dummy2',))

    ll_variants.append(('<separator>',))

    ll_variants.append(('Dummy3', None, lambda a='var:d3': pass_print(a),))

    ll_variants.append(('<userdefined>',))

    ll_variants.append(('Dummy3.1', None, lambda a='var:d3.1': pass_print(a),))
    ll_variants.append(('Dummy3.2', None, lambda a='var:d3.2': pass_print(a),))

    frame.bind("<Button-3>", lambda e, f=frame: BasePUMSelector(f, e, variants=ll_variants, tearoff=0))

    root.mainloop()

if __name__ == '__main__':
    run_demo()
