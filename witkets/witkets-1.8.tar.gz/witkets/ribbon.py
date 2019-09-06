#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
import witkets as wtk

class RibbonFactory:
    """Factory used to append widgets to either a ribbon tab or ribbon group"""

    def __init__(self, master):
        self._master = master

    def create_toolbar_item(self, imgfile, text):
        """Create a Toolbar item.

        Arguments:
          - imgfile -- The image file path
          - text -- The toolbar label

        Returns: The ImageButton widget just added
        """
        btn = wtk.ImageButton(self._master, imgfile, text=text, compound='top')
        btn['style'] = 'Ribbon.TButton'
        btn.pack(side='left', fill='y')
        return btn

    def create_separator(self):
        """Create a vertical separator.
        
        Returns: The Separator widget just added
        """
        sep = Separator(self._master, orient='vertical')
        sep.pack(side='left', fill='y', padx=3)
        return sep

    def create_v_group(self, buttons_info):
        """Add a group of buttons vertically stacked.

        Arguments:
          - buttons_info -- A list of button info as the pair (imgfile,text)

        Returns: The list of widgets just created
        """
        frame = Frame(self._master)
        frame['style'] = 'Ribbon.TFrame'
        buttons = []
        for imgfile, text in buttons_info:
            widget = wtk.ImageButton(frame, imgfile, text=text, compound='left')
            widget['style'] = 'Ribbon.TButton'
            widget.pack(side='top')
            buttons.append(widget)
        frame.pack(side='left')
        return buttons

    def create_h_group(self, text, corner=False):
        """Create a horizontal group.

        Arguments:
          - tab_idx -- The tab index
          - text -- The group label text
          - corner_button -- Add a button at the bottom right corner

        Returns:
        If corner is False, this functions returns a RibbonFactory for
        the group just created. If corner is True, a tuple (a, b) will
        be created, where a is the RibbonFactory and b the corner button
        widget.
        """
        whole = Frame(self._master)
        whole['style'] = 'RibbonGroup.TFrame'
        whole['borderwidth'] = 1
        main = Frame(whole)
        main.pack(expand=1, fill='both')
        main['style'] = 'RibbonGroupInner.TFrame'
        btn = None
        bottom = Frame(whole)
        bottom['style'] = 'RibbonBottom.TFrame'
        lbl = Label(bottom, text=text)
        lbl['style'] = 'RibbonBottom.TLabel'
        if not corner:
            lbl.pack(expand=0, fill='none', ipady=4)
        else:
            btn = Button(bottom, text='+')
            btn['style'] = 'RibbonBottom.TButton'
            lbl.pack(side='left', expand=1)
            btn.pack(side='left', expand=0)
        bottom.pack(expand=0, fill='x')
        whole.pack(side='left', fill='y', padx=3)
        factory = RibbonFactory(main)
        return factory if btn is None else (factory, btn)


class Ribbon(Notebook):
    """Tabbed toolbar widget (MS Ribbon-like interface)"""

    def __init__(self, master, **kw):
        Notebook.__init__(self, master, **kw)
        self._tabs = []
        # style.configure('Ribbon.TNotebook')
        self['style'] = 'Ribbon.TNotebook'

    def add_tab(self, text):
        """Adds a new tab to the Ribbon

        Arguments:
          - text -- The tab text

        Returns: A RibbonFactory to create widgets on the tab just added
        """
        frame = Frame(self)
        frame['style'] = 'Ribbon.TFrame'
        self.add(frame, text=text)
        self._tabs.append(frame)
        return RibbonFactory(frame)

    def remove_tab(self, index):
        """Removes a tab and all its children from the ribbon

        Arguments:
          - index -- The index of the tab to be erased
        """
        self._tabs[index].destroy()
        self._tabs.remove(self._tabs[index])


if __name__ == '__main__':
    root = Tk()
    ribbon = Ribbon(root)
    tab1 = ribbon.add_tab('Main')
    group1 = tab1.create_h_group("Document")
    btn_new = group1.create_toolbar_item('test/document-new.png', 'New')
    btn_open = group1.create_toolbar_item('test/document-open.png', 'Open')
    btn_save = group1.create_toolbar_item('test/document-save.png', 'Save')
    group2, btn = tab1.create_h_group("Edit", corner=True)
    btn_cut = group2.create_toolbar_item('test/edit-cut.png', 'Cut')
    btn_copy = group2.create_toolbar_item('test/edit-copy.png', 'Copy')
    btn_paste = group2.create_toolbar_item('test/edit-paste.png', 'Paste')
    btn_new['command'] = lambda: print('Hello, world!')
    vgroup1 = group2.create_v_group([
        ('test/edit-undo.png', 'Undo'),
        ('test/edit-redo.png', 'Redo')
    ])
    tab2 = ribbon.add_tab('Insert')
    tab2.create_toolbar_item('test/run.png', 'Run')
    tab2.create_separator()
    ribbon.pack(fill='x')
    
    style = wtk.Style()
    wtk.Style.set_default_fonts()
    style.apply_default()

    root.mainloop()
