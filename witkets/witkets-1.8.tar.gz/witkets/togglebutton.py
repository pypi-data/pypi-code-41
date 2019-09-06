import tkinter as tk


class ToggleButton(tk.Button):
    """A Toggle Button derived from tk.Button"""

    def __init__(self, master=None, **kw):
        tk.Button.__init__(self, master, **kw)
        self._active = False
        self['command'] = self._toggle

    def get_active(self):
        """Gets the current state of the toggle button (True for active)"""
        return self._active

    def set_active(self, active):
        """Sets the current state of the toggle button (False for active)"""
        self._active = active
        self._update()

    def _toggle(self):
        self._active = not self._active
        self._update()
        self.event_generate('<<toggled>>')

    def _update(self):
        if self._active:
            self['relief'] = tk.RIDGE
        else:
            self['relief'] = tk.GROOVE


if __name__ == '__main__':
    def update_label(*args):
        if toggle.get_active():
            label['text'] = 'Active'
        else:
            label['text'] = 'Not active'


    root = tk.Tk()
    toggle = ToggleButton(root, text='Click me!')
    toggle.set_active(True)
    toggle.pack(pady=10)
    label = tk.Label(root, text='Active')
    label.pack(pady=5)
    toggle.bind('<<toggled>>', update_label)
    root.mainloop()
