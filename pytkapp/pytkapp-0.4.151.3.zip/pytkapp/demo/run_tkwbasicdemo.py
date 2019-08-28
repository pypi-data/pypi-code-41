#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for additional tkinter widgets (basic) """

# pytkapp: demo for additional tkinter widgets (basic)
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
import random
import gettext
if __name__ == '__main__':
    if sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if sys.hexversion >= 0x03000000:
    from tkinter import Tk, Toplevel, Button
    from tkinter.constants import NORMAL, NONE, TOP, LEFT, BOTH, YES
else:
    from Tkinter import Tk, Toplevel, Button
    from Tkconstants import NORMAL, NONE, TOP, LEFT, BOTH, YES

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

from pytkapp.tkw.tkw_routines import READONLY
from pytkapp.tkw.tkw_alistbox import AListBox, ALISTBOX_STYLE_NOENTRY, ALISTBOX_STYLE_SENTRY, ALISTBOX_STYLE_COMBO
from pytkapp.tkw.tkw_mlistbox import MListBox
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText

###################################
## routines
###################################


def run_demo():
    """ local demo """

    root = Tk()

    # demo: simple alistbox
    try:
        ll_demo = [10, 20, 30, 50, 60, 80]
        print(ll_demo)

        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox (simple) demo')

        lw_demowidget = AListBox(lw_demotop,
                                 ll_demo,
                                 style=ALISTBOX_STYLE_NOENTRY)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        root.wait_window(lw_demotop)
        print(ll_demo)
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))

    # demo: alistbox
    try:
        ll_demo = [10, 20, 30, 50, 60, 80]
        print(ll_demo)

        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox (normal) demo')

        lw_demowidget = AListBox(lw_demotop,
                                 ll_demo)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        root.wait_window(lw_demotop)
        print(ll_demo)
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))

    # demo: alistbox + combo
    try:
        ll_demo = [10, 20, 30, 50, 60, 80]
        print(ll_demo)

        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox+combo demo')

        lw_demowidget = AListBox(lw_demotop,
                                 ll_demo,
                                 style=ALISTBOX_STYLE_COMBO,
                                 values=[99, 88, 77, 66, 55])
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        root.wait_window(lw_demotop)
        print(ll_demo)
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))

    # demo: alistbox + selector
    try:
        ll_demo = [10, 20, 30, 50, 60, 80]
        print(ll_demo)

        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox+selector demo')

        lw_demowidget = AListBox(lw_demotop,
                                 ll_demo,
                                 style=ALISTBOX_STYLE_SENTRY,
                                 sentryfunc=lambda ui: 'test%s' % random.randint(10, 1000))
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        root.wait_window(lw_demotop)
        print(ll_demo)
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))

    # demo: mlistbox
    try:
        ll_demo = [10, 20, 30, 50, 60, 80]
        print(ll_demo)

        lw_demotop = Toplevel(root)
        lw_demotop.title('mlistbox demo')

        lw_demowidget = MListBox(lw_demotop,
                                 ll_demo,
                                 selectallbtn=True)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        root.wait_window(lw_demotop)
        print(ll_demo)
    except:
        print('failed to create demo for "mlistbox":\n %s' % (get_estr()))

    # demo: xscrolledtext
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('xscrolledtext demo')
        lw_demowidget = XScrolledText(lw_demotop,
                                      defwidth=80,
                                      defheight=15,
                                      search=True,
                                      clear=True,
                                      import_=True,
                                      unload=True,
                                      print_=True,
                                      wstate=READONLY,
                                      wrap=NONE)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)

        lw_udcf = lw_demowidget.get_udcf()
        lw_btn1 = Button(lw_udcf, text="Button1")
        lw_btn1.pack(side=LEFT)
        lw_btn2 = Button(lw_udcf, text="Button2")
        lw_btn2.pack(side=LEFT)
        lw_btn3 = Button(lw_udcf, text="Button3")
        lw_btn3.pack(side=LEFT)

        for i in range(50):
            lw_demowidget.insert_data('String: %s\n' % (i))

        lw_demowidget.set_wstate(NORMAL)
    except:
        print('failed to create demo for "xscrolledtext":\n %s' % (get_estr()))

    # show demos
    root.mainloop()

if __name__ == '__main__':
    run_demo()
