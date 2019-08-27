
from ctypes import *

MessageBox = windll.User32.MessageBoxW
GetMessage = windll.User32.GetMessage

# BOOL WINAPI GetMessage(
#   __out     LPMSG lpMsg,
#   __in_opt  HWND hWnd,
#   __in      UINT wMsgFilterMin,
#   __in      UINT wMsgFilterMax
# );


# This was written for Python 3.  Python 2 would be similar, but pass a Unicode object instead
# of a string.
MessageBox(0, "Hello, World!", "Kelvin Test", 0)
