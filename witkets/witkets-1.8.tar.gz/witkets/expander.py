"""Container capable of hiding its child.

The widget has a primitive emulation of *readline*, such that vertical arrow 
keys puts recent commands in the user input entry.

**Imperative:**

    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> expander = wtk.Expander(root, text='Test')
    >>> label = ttk.Label(expander.frame, text='Expanded content')
    >>> label.pack()
    >>> expander.pack()
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <expander wid='expander1' text='Test 2 (XML)'>
            <label wid='lbl1' text='Contents' />
            <geometry>
                <pack for='lbl1' />
            </geometry>
        </expander>
        <geometry>
            <pack for='expander1' />
        </geometry>
    </root>


**Styles:**

The following styles affect this widget's appearance:

* TFrame --- the container as a whole.
* Expander.TButton --- The expander button for toggling child visibility.
* Expander.TFrame --- The frame being collapsed or revealed.

"""

import tkinter as tk
import tkinter.ttk as ttk
import pkgutil as pkg

class Expander(ttk.Frame):
    """Container capable of hiding its child.

    Parameters:
        master (object): Parent widget

    The following options can be used in several ways:
     - upon construction (e.g.: :code:`widget = Widget(parent, option=value)`)
     - by *tkinter* standard :code:`config()` method 
       (e.g. :code:`widget.config(option=value)`) or
     - in a dict-like access (e.g.: widget['option'] = value)
    
    Keyword Arguments:
        text (str): The text to be shown in the button
        expanded (bool): Whether the child should be shown (defaults to True)
        kw (dict): :class:`Frame` widget options
    """

    def __init__(self, master=None, text='', expanded=True, **kw):
        tk.Frame.__init__(self, master, **kw)
        arrow_right_data = pkg.get_data('witkets', 'data/xbm/arrow-right-16.xbm')
        self._arrow_right = tk.BitmapImage(data=arrow_right_data)
        arrow_down_data = pkg.get_data('witkets', 'data/xbm/arrow-down-16.xbm')
        self._arrow_down = tk.BitmapImage(data=arrow_down_data)
        self._button = ttk.Button(self, text=text, image=self._arrow_down, 
                                  compound=tk.LEFT)
        self._button['style'] = 'Expander.TButton'
        self._button.pack(fill=tk.X)
        self._button['command'] = self._on_toggle
        self._frame = ttk.Frame(self)
        self._frame['style'] = 'Expander.TFrame'
        self._expanded = expanded
        if expanded:
            self._button['image'] = self._arrow_down
            self._frame.pack()
        else:
            self._button['image'] = self._arrow_right

    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'text': str,
        'expanded': bool
    }

    # =====================================================================
    # Properties
    # =====================================================================

    @property
    def button(self):
        """The inner Button widget."""
        return self._button

    @property
    def frame(self):
        """The inner Frame widget"""
        return self._frame

    # =====================================================================
    # Protected Methods
    # =====================================================================

    def _update(self):
        if self._expanded:
            self._button['image'] = self._arrow_down
            self._frame.pack()
        else:
            self._button['image'] = self._arrow_right
            self._frame.pack_forget()

    def _on_toggle(self):
        self._expanded = not self._expanded
        self._update()

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key == 'text':
            self._button['text'] = val
        elif key == 'expanded':
            self._expanded = val
            self._update()
        else:
            ttk.Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'text':
            return self._button['text']
        elif key == 'expanded':
            return self._expanded
        return ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in ('text', 'expanded'):
            if key in kw:
                self.__setitem__(key, kw[key])
                kw.pop(key, False)
        ttk.Frame.config(self, **kw)
        self._update()

# =====================================================================
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()