"""Special container that displays only one child at a time.

**Imperative:**

    >>> import tkinter as tk
    >>> import tkinter.ttk as ttk
    >>> import witkets as wtk
    >>> def change_card():
    ...    cards.next()
    ...
    >>> root = tk.Tk()
    >>> cards = wtk.CardLayout(root)
    >>> label1 = ttk.Label(cards, text='Some Card')
    >>> label2 = ttk.Label(cards, text='Other Card')
    >>> cards.add(label1, 'first-card')
    >>> cards.add(label2)  # will be named 'card2'
    >>> button = ttk.Button(root, text='Change Card')
    >>> button.pack(padx=10, pady=10)
    >>> button['command'] = change_card
    >>> cards.pack(padx=10, pady=10)
    >>> root.mainloop()

**Declarative:**

.. code-block:: xml

    <root>
        <cardlayout wid='card1'>
            <label wid='label1' text='Some content...' />
            <label wid='label2' text='Other content...' />
            <frame wid='frame1' />
            <geometry>
                <card for='label1' name='first' />
                <card for='label2' name='second' />
                <card for='frame1' />
            </geometry>
        </cardlayout>
        <button wid='button1' text='Change card...' />
        <geometry>
            <pack for='card1' />
            <pack for='button1' />
        </geometry>
    </root>

**Styles:**

The following styles affect this widget's appearance:

* TFrame

"""

from collections import OrderedDict
from tkinter import *
from tkinter.ttk import *


class CardLayout(Frame):
    """Special container that displays only one child at a time.

    Parameters:
        master (object): Parent widget
        
    Keyword Arguments:
        kw (dict): All :class:`Frame` widget options
    """

    def __init__(self, master=None, **kw):
        Frame.__init__(self, master, **kw)
        self._cards = OrderedDict()
        self._curr_card = None
        self._count = 1

    def add(self, widget, name:str=None):
        """Add a card to the layout manager.

        Parameters:
            widget (object): Widget to be added as this card. 
                             A simple widget or a container, like *Frame*.
            name (str): Card unique name. 
                        If not provided, defaults to card*NUM*.
                        If already used, overrides the previous card.
        """
        if not name:
            name = 'card%d' % self._count
        self._count += 1
        self._cards[name] = widget
        if not self._curr_card:
            widget.pack()
            self._curr_card = name

    def first(self):
        """Switch to the first card."""
        keys = list(self._cards.keys())
        self.show(keys[0])

    def last(self):
        """Switch to the last card."""
        keys = list(self._cards.keys())
        self.show(keys[-1])

    def next(self):
        """Switch to the next card, with circular increment."""
        keys = list(self._cards.keys())
        index = keys.index(self._curr_card)
        size = len(keys)
        new_idx = index + 1
        if new_idx > size - 1:
            new_idx -= size
        self.show(keys[new_idx])

    def previous(self):
        """Switch to the previous card, with circular decrement."""
        keys = list(self._cards.keys())
        index = keys.index(self._curr_card)
        size = len(keys)
        new_idx = index - 1
        if new_idx < 0:
            new_idx += size
        self.show(keys[new_idx])

    def show(self, name: str):
        """Switch to a given card specified by its name.
        
        Parameters:
            name (str): Card unique name.
        
        """
        for c in self._cards.values():
            c.pack_forget()
        self._cards[name].pack()
        self._curr_card = name

# =====================================================================
# Module DocTest
# =====================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod()
