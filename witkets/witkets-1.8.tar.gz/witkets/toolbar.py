from tkinter import *
from tkinter.ttk import *


class Toolbar(Frame):
    """Simple toolbar implementation
      
       Options: All :code:`Frame` widget options
    """

    def __init__(self, master=None, **kw):
        Frame.__init__(self, master, **kw)
        self['style'] = 'Toolbar.TFrame'

    def add_button(self, imagepath, command, text=None):
        """Adds a button to the toolbar.
        
        Returns:
            The Button added.
        """
        img = PhotoImage(file=imagepath)
        kw = {'image': img, 'command': command}
        if text:
            kw['text'] = text
            kw['compound'] = TOP
        btn = Button(self, **kw)  # both img needed
        btn.image = img
        btn.pack(side=LEFT, padx=2, pady=2, fill=X, expand=0)
        btn['style'] = 'Toolbar.TButton'
        return btn


if __name__ == '__main__':
    def hello():
        print('hello!!')


    icon1 = '/usr/share/icons/gnome/32x32/actions/add.png'
    icon2 = '/usr/share/icons/gnome/32x32/status/dialog-error.png'

    root = Tk()

    toolbar = Toolbar()
    toolbar.add_button(icon1, hello)
    toolbar.add_button(icon2, hello, text='Test')
    toolbar.pack()

    root.mainloop()
