#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" """

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
import threading
import time
if __name__ == '__main__':
    if sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if sys.hexversion >= 0x03000000:
    from tkinter import Tk, Toplevel, Label, PhotoImage, Frame
    from tkinter.constants import N, S, W, E, CENTER, RAISED, SUNKEN
else:
    from Tkinter import Tk, Toplevel, Label, PhotoImage, Frame
    from Tkconstants import N, S, W, E, CENTER, RAISED, SUNKEN

# pytkapp
from pytkapp.pta_routines import novl

###################################
## globals
###################################
ICONDATA_STEP_LEFT = '''\
R0lGODlhIAAgAPcAAAAAAAAA/wBVqhdGixpNgBxMhB1Jih9Jhh9JiB9KiB9Lhh9Lhx9LiR9MhyBA
gCBJhyBJiSBKhyBKiSBLhiBLhyBLiCBLiSBQgCFJhiFKiCFLhyFLiCFLiSFMiCJEiCJKhiJLiCJM
iiNGiyNNiSNOiSRJgCRNiSZNjCZQiydOiSdPiihRjClRjClUjitVgCtVqixUji5doi5oojBgnzFY
kTJkojJkpDJlpDMzmTNlpDNmmTNmpDNmpTNmpjNmqDNmqjRkpDRkpTRlozRlpDRlpTRmozRnpTVk
pDVlpTVmpDVnpTVnpjZlpDZmpDZmpTZmpjZnpTZnpjZopjZopzZppjddlTddljdnpTdnpjdopTdt
pDhnpzhopjhppjlooTpflTpqpztinTtqpzxrqD1kmj1sqD1sqT5tqT9tqT9vqkBAgEBgn0CAv0Fv
qkJvqkNonkNwq0RzrUZto0ZyrEZzrUhtokp2rktzqUxxpExxpk1vok11qk15sU56sk96sFB6sFF4
rVF7slN7r1N9slR9slVVqlV+s1d5qVh9rViCtlp8rF+BsF+Etl+Gt2KHt2SHtWWHtWWKumWNvWWN
vmeMu2iMu2mMu2mNvGqPvWuOvWuPvWyTwW+UwnKXxnKax3Kfz3OTvnOfz3Ogz3SUv3SVwXSg0HSh
0HWXwXWh0HaUvXaWwHai0Xeax3edx3ij0Xqk0nuYwHuZwXybw32ZwX2hyn2m03+iy3+o1IKn0IOq
1YSgxISr1YWnz4Wo0IWs1YWs1oejx4ekyYmkx4mkyYuu1I2v1I2x2I6u046y2I+z2ZCz2ZKszpS2
2pW325a425e015e43Ji53Jm21pm215m425m63Jq22Jq63Zu52p252Z683p+83J+93aC93aG+36K+
3KLA36PB4KTA36TB36bA3anE4arE4KrF4qzF4a3H47PL5QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAAAgACAA
hwAAAAAA/wBVqhdGixpNgBxMhB1Jih9Jhh9JiB9KiB9Lhh9Lhx9LiR9MhyBAgCBJhyBJiSBKhyBK
iSBLhiBLhyBLiCBLiSBQgCFJhiFKiCFLhyFLiCFLiSFMiCJEiCJKhiJLiCJMiiNGiyNNiSNOiSRJ
gCRNiSZNjCZQiydOiSdPiihRjClRjClUjitVgCtVqixUji5doi5oojBgnzFYkTJkojJkpDJlpDMz
mTNlpDNmmTNmpDNmpTNmpjNmqDNmqjRkpDRkpTRlozRlpDRlpTRmozRnpTVkpDVlpTVmpDVnpTVn
pjZlpDZmpDZmpTZmpjZnpTZnpjZopjZopzZppjddlTddljdnpTdnpjdopTdtpDhnpzhopjhppjlo
oTpflTpqpztinTtqpzxrqD1kmj1sqD1sqT5tqT9tqT9vqkBAgEBgn0CAv0FvqkJvqkNonkNwq0Rz
rUZto0ZyrEZzrUhtokp2rktzqUxxpExxpk1vok11qk15sU56sk96sFB6sFF4rVF7slN7r1N9slR9
slVVqlV+s1d5qVh9rViCtlp8rF+BsF+Etl+Gt2KHt2SHtWWHtWWKumWNvWWNvmeMu2iMu2mMu2mN
vGqPvWuOvWuPvWyTwW+UwnKXxnKax3Kfz3OTvnOfz3Ogz3SUv3SVwXSg0HSh0HWXwXWh0HaUvXaW
wHai0Xeax3edx3ij0Xqk0nuYwHuZwXybw32ZwX2hyn2m03+iy3+o1IKn0IOq1YSgxISr1YWnz4Wo
0IWs1YWs1oejx4ekyYmkx4mkyYuu1I2v1I2x2I6u046y2I+z2ZCz2ZKszpS22pW325a425e015e4
3Ji53Jm21pm215m425m63Jq22Jq63Zu52p252Z683p+83J+93aC93aG+36K+3KLA36PB4KTA36TB
36bA3anE4arE4KrF4qzF4a3H47PL5QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAj+AAEIHEiwoMGDCBMmfKGwIcIdTpAoCeCwIoAb
ZqSRo8PDYkMZT6xVazYNShiPCYVMOhfKlLpAQVAejHHl265Pn6LZoiLT4BE+6XB+ypVtikcXB4mw
gib0lbkhOhwGQLBAw4SCUWgpE7oK3ZAfDiXQEJZKxQeCOTg5E1qrG5JCDVNogEXpFCwKIgYy6RNO
6K9jWBwqsLLsipNgehIM9HKlnCic1yQhcchhkaYhQ/zo6jBA4I8h4lB9urUtyxXKs+xgHhLsywOB
PaCIC1XKW6ImDglEAFZmNaVDBwDUGAJH2ydkvKDMcOghwrArqxspsgDACJpNyVxxOwOkooAFsdrQ
rK6EJwKALM/GvTLmaQjcihwg/VlNqkoDHUOwufoErtUQHxY98MYlmCUhywgFaDEENaZ8wkwnUngU
AgmguDEEF6pE4AEAWOCyiy/FdGEDShSQgYkTSYwCwgkAbBEHMb2kUYRMF1CAyCBDVAJDBAywEYUQ
SzRBkUwYrGDJGITUwYJ5AKzR00ACRCCHIWBk8kgHTxZkQAR5RDKEGI5EgEOWBIEw5RBOMBJBCWQO
BIEJgswBxx4ZtEnQBijcAUgLddopUAAMVLAAB2r4WZADhhoaEAA7
'''

ICONDATA_STEP_RIGHT = '''\
R0lGODlhIAAgAPcAAAAAAAAA/wBVqhdGixpNgBxMhB1Jih9Jhh9JiB9KiB9Lhh9Lhx9LiR9MhyBA
gCBJhyBJiSBKhyBKiSBLhiBLhyBLiCBLiSBQgCFJhiFKiCFLhyFLiCFLiSFMiCJEiCJKhiJLiCJM
iiNGiyNNiSNOiSRJgCRNiSZNjCZQiydOiSdPiihRjClRjClUjitVgCtVqixUji5doi5oojBgnzFY
kTJkojJkpDJlpDMzmTNlpDNmmTNmpDNmpTNmpjNmqDNmqjRkpDRkpTRlozRlpDRlpTRmozRnpTVk
pDVlpTVmpDVnpTVnpjZlpDZmpDZmpTZmpjZnpTZnpjZopjZopzZppjddlTddljdnpTdnpjdopTdt
pDhnpzhopjhppjlooTpflTpqpztinTtqpzxrqD1kmj1sqD1sqT5tqT9tqT9vqkBAgEBgn0CAv0Fv
qkJvqkNonkNwq0RzrUZto0ZyrEZzrUhtokp2rktzqUxxpExxpk1vok11qk15sU56sk96sFB6sFF4
rVF7slN7r1N9slR9slVVqlV+s1d5qVh9rViCtlp8rF+BsF+Etl+Gt2KHt2SHtWWHtWWKumWNvWWN
vmeMu2iMu2mMu2mNvGqPvWuOvWuPvWyTwW+UwnKXxnKax3Kfz3OTvnOfz3Ogz3SUv3SVwXSg0HSh
0HWXwXWh0HaUvXaWwHai0Xeax3edx3ij0Xqk0nuYwHuZwXybw32ZwX2hyn2m03+iy3+o1IKn0IOq
1YSgxISr1YWnz4Wo0IWs1YWs1oejx4ekyYmkx4mkyYuu1I2v1I2x2I6u046y2I+z2ZCz2ZKszpS2
2pW325a425e015e43Ji53Jm21pm215m425m63Jq22Jq63Zu52p252Z683p+83J+93aC93aG+36K+
3KLA36PB4KTA36TB36bA3anE4arE4KrF4qzF4a3H47PL5QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAAALAAAAAAgACAA
hwAAAAAA/wBVqhdGixpNgBxMhB1Jih9Jhh9JiB9KiB9Lhh9Lhx9LiR9MhyBAgCBJhyBJiSBKhyBK
iSBLhiBLhyBLiCBLiSBQgCFJhiFKiCFLhyFLiCFLiSFMiCJEiCJKhiJLiCJMiiNGiyNNiSNOiSRJ
gCRNiSZNjCZQiydOiSdPiihRjClRjClUjitVgCtVqixUji5doi5oojBgnzFYkTJkojJkpDJlpDMz
mTNlpDNmmTNmpDNmpTNmpjNmqDNmqjRkpDRkpTRlozRlpDRlpTRmozRnpTVkpDVlpTVmpDVnpTVn
pjZlpDZmpDZmpTZmpjZnpTZnpjZopjZopzZppjddlTddljdnpTdnpjdopTdtpDhnpzhopjhppjlo
oTpflTpqpztinTtqpzxrqD1kmj1sqD1sqT5tqT9tqT9vqkBAgEBgn0CAv0FvqkJvqkNonkNwq0Rz
rUZto0ZyrEZzrUhtokp2rktzqUxxpExxpk1vok11qk15sU56sk96sFB6sFF4rVF7slN7r1N9slR9
slVVqlV+s1d5qVh9rViCtlp8rF+BsF+Etl+Gt2KHt2SHtWWHtWWKumWNvWWNvmeMu2iMu2mMu2mN
vGqPvWuOvWuPvWyTwW+UwnKXxnKax3Kfz3OTvnOfz3Ogz3SUv3SVwXSg0HSh0HWXwXWh0HaUvXaW
wHai0Xeax3edx3ij0Xqk0nuYwHuZwXybw32ZwX2hyn2m03+iy3+o1IKn0IOq1YSgxISr1YWnz4Wo
0IWs1YWs1oejx4ekyYmkx4mkyYuu1I2v1I2x2I6u046y2I+z2ZCz2ZKszpS22pW325a425e015e4
3Ji53Jm21pm215m425m63Jq22Jq63Zu52p252Z683p+83J+93aC93aG+36K+3KLA36PB4KTA36TB
36bA3anE4arE4KrF4qzF4a3H47PL5QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAj+AAEIHEiwoMGDCAu+SMiQYQAlSJzsaEiRIA86
5KSZuVGRYhgo05pVs/ZERkeGQQKpMxXq3CQhJxNSsRXt06dd367EiHlwSrZcNj+l43OEZ0EdQ8y9
CgqNFZGDLjr+GIJuVVBltKIUnKBhAYIAFAsh6VYrqDNOOQh+UJFKGA0JFbEc+xU0XB8mA0VQgHWK
EiwNKSgikXTNpqhyV7wMTKAnmJMry6wooHgly7Zbn1CJG/JD4IAOuvwMGaJpEYeKTRJ5KxVKHJQe
Ah98CTZ6iJ1ZpynOgMIL2SdtcIbUAHDgEKXaZYBFIFARyBlurpJtQmMEgAVFjWpfGRbBQ8VCQzzR
GXs17lkWABHwVKrdJtYCARV9DGkF7pMrbEN0NKhCqvYfSLlVJEUnzHxiCjVDaFHACLIkMdolbzxw
kg1dFOPLLrhgAYAHEajCxRBugEJCCDEVkUYvxMSxBQAngDBKEk5gQgYFPAXQxBJCRMEGAxHAsN4g
iFBwgVECrSFQBCzUQcgYlqyAAZEFdfBIJmAYIkcE8EEpEA4ROCLGEJHkEYEBWgpUQgSMODGElSCU
OVAGe8AxhyAmQOCmQBm0AMgdKGxwp0BqcLBABQyA9adADhxKZEAAOw==
'''

###################################
## routines
###################################


def pass_(*args, **kw):
    """do PASS !!!"""

    pass


###################################
## classes
###################################


class GUILongopsDecorator:
    """ simple decorator for long-running operations """

    def __init__(self, pw_root, **kw):
        """ init routines
            kw may contain:
                message: displaing message
        """

        # common
        self.__root = pw_root
        self.__logo = None
        self.__logoname = None
        self.__logol = None
        self.__textl = None
        self.__window = None
        self.__afid = None

        self.__geom = ''

        self.__thread = None
        self.__stopevent = None

        self.__message = kw.get('message', _('Process is running...'))

    def __enter__(self):
        """ enter """

        # Create components of splash screen.
        window = Toplevel(self.__root,
                          bd=1,
                          relief=RAISED)
        window.withdraw()

        # logo >>>
        logo_frame = Frame(window, relief=SUNKEN)

        logo_image = PhotoImage(data=ICONDATA_STEP_LEFT)
        self.__logo = logo_image

        lw_label = Label(logo_frame, image=logo_image)
        lw_label.grid(row=0, column=0, sticky=N+E+W+S, padx=0, pady=0)
        self.__logol = lw_label

        logo_frame.rowconfigure(0, weight=1)
        logo_frame.grid(row=0, column=0, sticky=N+E+W+S, padx=1, pady=1)

        # text >>>
        text_frame = Frame(window)
        lw_label = Label(text_frame,
                         text=self.__message,
                         anchor=CENTER)
        lw_label.grid(row=0, column=0, sticky=N+E+W+S, padx=2, pady=1)
        self.__textl = lw_label

        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        text_frame.grid(row=0, column=1, sticky=N+E+W+S, padx=1, pady=1)

        window.rowconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)

        # Get the screen's width and height.
        lv_scrw = window.winfo_screenwidth()
        lv_scrh = window.winfo_screenheight()
        # Get the images's width and height.
        window.update_idletasks()
        lv_splashw = max(window.winfo_reqwidth(), 100)
        lv_splashh = max(window.winfo_reqheight(), 50)
        # Compute positioning for splash screen.
        lv_xpos = (lv_scrw - lv_splashw) // 2
        lv_ypos = (lv_scrh - lv_splashh) // 2
        # Configure the window showing the logo.
        window.overrideredirect(True)
        self.__geom = str(lv_splashw)+"x"+str(lv_splashh)+"+"+str(lv_xpos)+"+"+str(lv_ypos)
        window.geometry(self.__geom)
        window.deiconify()
        window.update()
        window.lift()
        window.focus_set()

        window.transient(self.__root.winfo_toplevel())
        window.update()

        # Save the variables for later cleanup.
        self.__window = window

        self.__stopevent = threading.Event()
        self.__thread = threading.Thread(None,
                                         target=self.animateit,
                                         name='animateit')
        self.__thread.start()

    def animateit(self, po_event=None):
        """ some routines """

        pass_(po_event)

        while not self.__stopevent.is_set():
            if novl(self.__logoname, 'right') == 'right':
                self.__logo.configure(data=ICONDATA_STEP_LEFT)
                self.__logoname = 'left'
            else:
                self.__logo.configure(data=ICONDATA_STEP_RIGHT)
                self.__logoname = 'right'

            self.__logol.configure(image=self.__logo)

            #self.__window.winfo_toplevel().update_idletasks()
            self.__window.update_idletasks()
            self.__textl.update_idletasks()
            self.__logol.update_idletasks()

            time.sleep(0.5)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ exit """

        self.__stopevent.set()
        self.__thread.join()

        del self.__logo
        self.__window.grab_release()
        self.__window.destroy()

        self.__root.update_idletasks()


def run_demo():
    """ demo routines """

    root = Tk()

    with GUILongopsDecorator(root, message='simple test'):
        for i in range(200):
            print('%s' % i)
            time.sleep(1)

if __name__ == '__main__':
    run_demo()
