#-----------imports-----------
from tkinter import *
from pygui import *
try:
    from pygui import *
    from . import *
except:
    try:
        try:
            from .. import *
            
        except Exception as ex:
            try:
                from . import *
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
    try:
        from .GUIs import wheel_build
    except:
        try:
            try:
                from ..GUIs import wheel_build
            except Exception as ex:
                try:
                    from pygui.GUIs import wheel_build
                except Exception as Ex:
                    raise Ex from ex
        except Exception as exc:
            raise ImportError('cant find the pygui module shure you installed it?\n\
    you install it when you install os_sys.\n\
    try reinstalling os_sys else try to contact me\n\
    and send the error with it') from exc
    wheel_build.main()
def _file_editor():
    global file_editor
    try:
        from .GUIs import file_editor
    except:
        try:
            try:
                from GUIs import file_editor
            except Exception as ex:
                try:
                    from pygui.GUIs import file_editor
                except Exception as Ex:
                    raise Ex from ex
        except Exception as exc:
            raise ImportError('cant find the pygui module shure you installed it?\n\
    you install it when you install os_sys.\n\
    try reinstalling os_sys else try to contact me\n\
    and send the error with it') from exc
_file_editor()
def fileeditor():
    file_editor.main()
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
btn = Button(root, text='open file editor', command=fileeditor)
btn.place(x=100,y=0)
widgets['file editor'] = btn
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
root.mainloop()
