#-----------imports-----------
from tkinter import *
try:
    from . import GUIs
    from . import *
except:
    try:
        try:
            from .. import *
            from .. import GUIs
        except Exception as ex:
            try:
                from pygui import *
                import pygui.GUIs as GUIs
            except Exception as Ex:
                raise Ex from ex
    except Exception as exc:
        raise ImportError('cant find the pygui module shure you installed it?\n\
you install it when you install os_sys.\n\
try reinstalling os_sys else try to contact me\n\
and send the error with it') from exc
#-----------shaping tk window-----------
root = Tk(className='gui selector window')
root.geometry('400x300')
#-----------functions-----------
def get_button(button):
    assert isinstance(button, str), str(f'excpected an string but got an {type(button)}')
    return widgets[button.lower()]
def wheel_opener():
    from GUIs import wheel_build
    wheel_build.main()
class my_class(dict):
    def __init__(self):
        dict.__init__(self)
def main():
    pass
#-----------place buttons-----------
widgets = my_class()
btn = Button(root, text='open wheel build', command=wheel_opener)
btn.place(x='0',y='0')
widgets['wheel'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=100,y=0)
widgets['add file'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=200,y=0)
widgets['target file'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=0,y=40)
widgets['save'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=100,y=40)
widgets['add files'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=200,y=40)
widgets['extract wheel file'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=0, y=80)
widgets['convert zip to whl'] = btn
btn = Button(root, text='None', command=None)
btn.place(x=140, y=80)
widgets['convert whl to zip'] = btn
label = Message(root, text='select an GUI you want to open')
label.place(x=0,y=120)
widgets['help'] = label
label = Label(root, text='info:')
label.place(x=0, y=250)
widgets['working on...'] = label
label = Message(root, text='None')
label.place(x=50, y=250)
widgets.info = label
widgets.info = label
print_startup(succes)
