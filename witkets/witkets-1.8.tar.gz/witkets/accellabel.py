"""A label which displays an accelerator key on the right of the text.

**Imperative:**

    >>> import tkinter as tk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> style = wtk.Style()
    >>> style.theme_use('clam')
    >>> style.apply_default()
    >>> a = wtk.AccelLabel(root, labeltext='Copy', acceltext='CTRL+C')
    >>> a.pack(expand=1, fill=tk.X, padx=20, pady=20)
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <accellabel wid='lbl-new' labeltext='New' acceltext='CTRL+N' />
        <accellabel wid='lbl-open' labeltext='Open...' acceltext='CTRL+O' />
        <geometry>
            <pack for='lbl-new' />
            <pack for='lbl-open' />
        </geometry>
    </root>

**Styles:**

The following styles affect this widget's appearance:

* MenuEntry.TLabel --- main label style
* Accelerator.TLabel --- accelerator style (defaults to gray)
* TFrame --- the frame as a whole

"""

import tkinter as tk
import tkinter.ttk as ttk


class AccelLabel(ttk.Frame):
    """A label which displays an accelerator key on the right of the text.

    Parameters:
        master (object): Parent widget

    The following options can be used in several ways:
     - upon construction (e.g.: :code:`widget = Widget(parent, option=value)`)
     - by *tkinter* standard :code:`config()` method 
       (e.g. :code:`widget.config(option=value)`) or
     - in a dict-like access (e.g.: widget['option'] = value)
    
    Keyword Arguments:
        labeltext (str): Main label text
        acceltext (str): Accelerator text
        kw (dict): All :class:`Frame` widget options
    """

    def __init__(self, master=None, labeltext='', acceltext='', **kw):
        """Initializer"""
        ttk.Frame.__init__(self, master, **kw)
        self._label = ttk.Label(self, text=labeltext, 
                                style='MenuEntry.TLabel')
        self._label['justify'] = tk.LEFT
        self._label.pack(side=tk.LEFT, padx=(0, 30), expand=1, fill=tk.X)
        self._accel = ttk.Label(self, text=acceltext, 
                                style='Accelerator.TLabel')
        self._accel['justify'] = tk.RIGHT
        self._accel.pack(side=tk.RIGHT, fill=tk.X)

    # =====================================================================            
    # Introspection
    # =====================================================================

    widget_keys = {
        'labeltext': str,
        'acceltext': str
    }

    # =====================================================================
    # Properties
    # =====================================================================

    @property
    def label(self):
        """Label containing the main text."""
        return self._label

    @property
    def accel(self):
        """Label containing the accelerator string."""
        return self._accel

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key == 'labeltext':
            self._label['text'] = val
        elif key == 'acceltext':
            self._accel['text'] = val
        else:
            ttk.Frame.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'labeltext':
            return self._label['text']
        elif key == 'acceltext':
            return self._accel['text']
        return ttk.Frame.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        for key in self.widget_keys:
            if key in kw:
                self.__setitem__(key, kw[key])
            kw.pop(key, False)
        ttk.Frame.config(self, **kw)

# =====================================================================
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()