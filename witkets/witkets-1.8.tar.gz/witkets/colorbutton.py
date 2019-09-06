"""A button to launch a color selection dialog.

**Imperative:**

    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> ttk.Label(root, text='Color Button Example: click it!').pack(pady=9)
    >>> a = wtk.ColorButton(root, color='red')
    >>> var = tk.StringVar()
    >>> a['textvariable'] = var
    >>> var.set('#00F')
    >>> a.pack(padx=10, pady=10)
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <label wid='label1' text='Colors:' />
        <colorbutton wid='colorbutton1' color='#800000' />
        <colorbutton wid='colorbutton2'>
            <textvariable name='color2' type='text' value='#008000' />
        </colorbutton>
        <geometry>
            <pack for='label1' side='left' />
            <pack for='colorbutton1' side='left' />
            <pack for='colorbutton2' side='left' />
        </geometry>
    </root>

**Styles:**

The following styles affect this widget's appearance:

* TCanvas

"""


import tkinter as tk
import tkinter.ttk as ttk
from tkinter.colorchooser import askcolor


class ColorButton(tk.Canvas):
    """A button to launch a color selection dialog.
    
    This widget mocks GtkColorButton from the Gtk toolkit. It is "a button
    which displays the currently selected color an allows to open a color
    selection dialog".

    Parameters:
        master (object): Parent widget

    The following options can be used in several ways:
     - upon construction (e.g.: :code:`widget = Widget(parent, option=value)`)
     - by *tkinter* standard :code:`config()` method 
       (e.g. :code:`widget.config(option=value)`) or
     - in a dict-like access (e.g.: widget['option'] = value)
    
    Keyword Arguments:
        color (str): Selected/displayed color
        textvariable (object): Tk :class:`StringVar` to stock color
        kw (dict): :class:`Canvas` widget options (notably width and height)
    """

    def __init__(self, master, color='#CCC', textvariable=None, **kw):
        if 'width' not in kw:
            kw['width'] = 25
        if 'height' not in kw:
            kw['height'] = 25
        tk.Canvas.__init__(self, master, **kw)
        if not textvariable:
            self._var = tk.StringVar()
        else:
            self._var = textvariable
        self._var.set(color)
        self._var.trace('w', self._redraw)
        self._rect = None
        self._redraw()
        self.bind('<Button-1>', self._show_dialog)

    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'color': str
    }

    # =====================================================================            
    # Protected Methods
    # =====================================================================

    def _redraw(self, *args):
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        if self._rect:
            self.delete(self._rect)
        self._rect = self.create_rectangle(0, 0, w, h, fill=self._var.get())
                
    def _show_dialog(self, event=None):
        new_color = askcolor(color=self._var.get())[1]
        if new_color:
            self._var.set(new_color)
            self._redraw()
        
    # =====================================================================
    # Inherited Methods
    # =====================================================================
        
    def __setitem__(self, key, val):
        if key == 'color':
            self._var.set(val)
        elif key == 'textvariable':
            self._var = val
            self._var.trace('w', self._redraw)
        else:
            tk.Canvas.__setitem__(self, key, val)
        self._redraw()
        
    def __getitem__(self, key):
        if key == 'color':
            return self._var.get()
        elif key == 'textvariable':
            return self._var
        else:
            return tk.Canvas.__getitem__(self, key)
            
    def config(self, **kw):
        """Tk standard config method"""
        if 'textvariable' in kw:
            self._var = kw['textvariable']
            self._var.trace('w', self._redraw)
            kw.pop('textvariable', False)
        if 'color' in kw:
            self._var.set(kw['color'])
            kw.pop('color', False)
        tk.Canvas.config(self, **kw)

# =====================================================================
# Module DocTest
# =====================================================================
          
if __name__ == '__main__':
    import doctest
    doctest.testmod()