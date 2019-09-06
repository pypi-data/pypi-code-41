"""A widget suitable for constructing interactive consoles.

The widget has a primitive emulation of *readline*, such that vertical arrow 
keys puts recent commands in the user input entry.

**Imperative:**

    >>> import tkinter as tk
    >>> import witkets as wtk
    >>> root = tk.Tk()
    >>> consoleview = wtk.ConsoleView(root)
    >>> consoleview.text['width'] = 32
    >>> consoleview.pack(expand=1, fill='both')
    >>> consoleview.write_line('Welcome to TEST Console')
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <style>
            [Console.TEntry]
                foreground=blue
        </style>
        <consoleview wid='console1' />
        <geometry>
            <pack for='console1' />
        </geometry>
    </root>

**Styles:**

The following styles affect this widget's appearance:

* Console.TEntry --- input entry style
* TFrame --- the frame as a whole

The main console area is an instance of :class:`tkinter.Text`. Therefore,
it cannot use ttk-based styling.

"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText

HISTORY_SIZE = 1000

class ConsoleView(ttk.Frame):
    """A widget suitable for constructing interactive consoles."""

    def __init__(self, master=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self._text = ScrolledText(self, height=5, width=16)
        self._text['bg'] = 'black'
        self._text['fg'] = '#080'
        self._text['font'] = ("Courier New", "16", 'bold')
        self._text['state'] = 'disabled'
        self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self._last_input_line = ''
        self._var_command = tk.StringVar()
        self._command_entry = ttk.Entry(self, textvariable=self._var_command)
        self._command_entry['font'] = ("Courier New", "16", 'bold')
        self._command_entry['width'] = 16
        self._command_entry.pack(side=tk.BOTTOM, fill=tk.X, expand=0)
        self._command_entry.bind('<Return>', self._on_return_key)
        self._command_entry.bind('<Up>', self._on_up_key)
        self._command_entry.bind('<Down>', self._on_down_key)
        self._command_entry['style'] = 'Console.TEntry'
        self._history = []
        self._cursor = 0

    # ========================================================================
    # Properties
    # ========================================================================

    @property
    def command_entry(self):
        """Command input entry."""
        return self._command_entry

    @property
    def text(self):
        """Scrolled text (console output)"""
        return self._text

    @property
    def last_command(self):
        """Last command issued to the console."""
        if self._history:
            return self._history[-1]
        return None

    @property
    def last_input_line(self):
        """Last line (possibly empty) entered by the user.
        
        Blank lines are neither added to the command history nor
        accessed through the *last_command* property.
        """
        return self._last_input_line

    # ========================================================================
    # Protected Methods
    # ========================================================================
    
    def _on_return_key(self, event):
        """Command issued"""
        new_cmd = self._var_command.get()
        self._last_input_line = new_cmd
        if new_cmd.strip():
            self.write_line(new_cmd)
            self._var_command.set('')
            self._history.append(new_cmd)
            self._history = self._history[-HISTORY_SIZE:]
        self.event_generate("<<NewCommand>>")
        
    def _on_up_key(self, event):
        """Previous command"""
        if -self._cursor <= len(self._history) - 1:
            self._cursor -= 1
            self._var_command.set(self._history[self._cursor])
        
    def _on_down_key(self, event):
        """Next command"""
        if self._cursor <= -1:
            self._cursor += 1
            new_entry = self._history[self._cursor] if self._cursor else ''
            self._var_command.set(new_entry)

    # ========================================================================
    # Public API
    # ========================================================================

    def write_line(self, line:str, tags:list=None):
        """Write a line to the console, without interpreting any command.
        
        Parameters:
            line (str): Text to be appended to the console

        Keyword Arguments:
            tags (list): List of tags to be applied to the line
        """
        #msg = '\n' + line if self._history else line
        msg = line.rstrip() + '\n'
        self._cursor = 0
        self._text['state'] = 'normal'
        if not tags:
            tags = ()
        self._text.insert(tk.END, msg, tags)
        self._text['state'] = 'disabled'
        self._text.yview(tk.END)
            
    def disable_input(self):
        """Disable command input."""
        self._command_entry['state'] = 'disabled'
        
    def enable_input(self):
        """Enable command input."""
        self._command_entry['state'] = 'normal'
        
    def focus_input(self):
        """Move UI focus to the command entry."""
        self._command_entry.focus()


# ============================================================================
# Module DocTest
# ============================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()