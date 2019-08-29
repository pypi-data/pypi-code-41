#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for additional tkinter widgets (tooltips) """

# pytkapp: demo for additional tkinter widgets (tooltips)
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
import datetime
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
    from tkinter import Tk, Toplevel, Label
else:
    from Tkinter import Tk, Toplevel, Label

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

from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn
from pytkapp.tkw.tkw_tooltippedentry import ToolTippedEntry

###################################
## routines
###################################


def run_demo():
    """ local demo """

    root = Tk()

    # demo: tooltips
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('tooltips demo')

        lv_r = 0

        lv_r += 1
        Label(lw_demotop, text='Btn: default tooltip').grid(row=lv_r, column=0, sticky='w')
        ToolTippedBtn(lw_demotop, text='N', tooltip='default tooltip').grid(row=lv_r, column=1, sticky='we')

        lv_r += 1
        Label(lw_demotop, text='Btn: function-based tooltip').grid(row=lv_r, column=0, sticky='w')
        ToolTippedBtn(lw_demotop, text='FN', tooltipcmd=lambda: '%s' % datetime.datetime.now()).grid(row=lv_r, column=1, sticky='we')

        lv_r += 1
        Label(lw_demotop, text='Btn: random fn tooltip (1-10)').grid(row=lv_r, column=0, sticky='w')
        ToolTippedBtn(lw_demotop, text='rN', tooltipcmd=lambda: '%s' % random.randint(1, 10)).grid(row=lv_r, column=1, sticky='we')

        lv_r += 1
        Label(lw_demotop, text='Entry: default tooltip').grid(row=lv_r, column=0, sticky='w')
        ToolTippedEntry(lw_demotop, text='N', tooltip='default tooltip').grid(row=lv_r, column=1)

        lv_r += 1
        Label(lw_demotop, text='Entry: function-based tooltip').grid(row=lv_r, column=0, sticky='w')
        ToolTippedEntry(lw_demotop, text='FN', tooltipcmd=lambda: '%s' % datetime.datetime.now()).grid(row=lv_r, column=1)

        lv_r += 1
        Label(lw_demotop, text='Entry: random fn tooltip (1-10)').grid(row=lv_r, column=0, sticky='w')
        ToolTippedEntry(lw_demotop, text='rN', tooltipcmd=lambda: '%s' % random.randint(1, 10)).grid(row=lv_r, column=1)

    except:
        print('failed to create demo for "tooltips":\n %s' % (get_estr()))

    # show demos
    root.mainloop()

if __name__ == '__main__':
    run_demo()
