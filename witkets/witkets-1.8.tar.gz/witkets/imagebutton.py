#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk

class ImageButton(ttk.Button):
    """A button with an image

    Options:
      - imgfile --- The image filepath
      - All :code:`Button` widget options (text, compound, width, height etc)

    Forms of access:
      >>> import tkinter as tk
      >>> import tkinter.ttk as ttk
      >>> import witkets as wtk
      >>> # ...
      >>> btn = ImageButton(imgfile='myicon.gif', compound='top')
      >>> btn['imgfile'] = 'othericon.png'
      >>> btn.config(imgfile='yet-another.png')
    
"""

    def __init__(self, master, imgfile=None, **kw):
        if 'compound' not in kw:
            kw['compound'] = 'top'
        self._imgfile = imgfile
        self._image = None
        if imgfile:
            self._image = tk.PhotoImage(file=imgfile)
            kw['image'] = self._image
        ttk.Button.__init__(self, master, **kw)

    # =====================================================================
    # Inherited Methods
    # =====================================================================

    def __setitem__(self, key, val):
        if key == 'imgfile':
            self._imgfile = val
            self._image = tk.PhotoImage(file=val)
            ttk.Button.__setitem__(self, 'image', self._image)
        else:
            ttk.Button.__setitem__(self, key, val)

    def __getitem__(self, key):
        if key == 'imgfile':
            return self._imgfile
        return ttk.Button.__getitem__(self, key)

    def config(self, **kw):
        """Standard Tk config method"""
        if 'imgfile' in kw:
            self.__setitem__('imgfile', kw['imgfile'])
            kw.pop('imgfile', False)
        ttk.Button.config(self, **kw)

if __name__ == '__main__':
    root = tk.Tk()
    btn = ImageButton(root, 'tests/data/document-new.png', text='New', 
                      compound='top')
    btn.pack()
    import witkets as wtk
    builder = wtk.TkBuilder(root)
    test_xml = '''
        <root>
            <imagebutton wid='imgbutton1' imgfile='tests/data/document-save.png' 
                         text='Save' compound='left' />
            <geometry><pack for='imgbutton1' /></geometry>
        </root>
    '''
    builder.build_from_string(test_xml)
    builder.nodes['imgbutton1'].config(imgfile='tests/data/document-save.png')
    root.mainloop()
