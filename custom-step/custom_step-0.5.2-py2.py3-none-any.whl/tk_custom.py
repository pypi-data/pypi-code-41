# -*- coding: utf-8 -*-

"""The graphical part of a Custom step"""

import seamm
import custom_step
import Pmw
import pprint  # noqa: F401
import tkinter as tk


class TkCustom(seamm.TkNode):
    """The node_class is the class of the 'real' node that this
    class is the Tk graphics partner for
    """

    node_class = custom_step.Custom

    def __init__(
        self,
        tk_flowchart=None,
        node=None,
        canvas=None,
        x=120,
        y=20,
        w=200,
        h=50
    ):
        '''Initialize a node

        Keyword arguments:
        '''
        self.dialog = None

        super().__init__(
            tk_flowchart=tk_flowchart,
            node=node,
            canvas=canvas,
            x=x,
            y=y,
            w=w,
            h=h
        )

    def create_dialog(self):
        """Create the dialog!"""
        self.dialog = Pmw.Dialog(
            self.toplevel,
            buttons=('OK', 'Help', 'Cancel'),
            master=self.toplevel,
            title='Edit Custom Python',
            command=self.handle_dialog
        )
        self.dialog.withdraw()

        # self._widget, which is inherited from the base class, is
        # a place to store the pointers to the widgets so that we can access
        # them later. We'll set up a short hand 'w' just to keep lines short
        w = self._widget
        # frame = ttk.Frame(self.dialog.interior())
        # frame.pack(expand=tk.YES, fill=tk.BOTH)

        frame = self.dialog.interior()
        w['frame'] = frame

        # Put in the editor window
        textarea = custom_step.TextArea(frame)
        textarea.insert(1.0, self.node.script)
        textarea.pack(expand=tk.YES, fill=tk.BOTH)
        w['textarea'] = textarea

        # self.reset_dialog()

    def reset_dialog(self, widget=None):
        # set up our shorthand for the widgets
        w = self._widget

        # Remove any widgets previously packed
        frame = w['frame']
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        w['textarea'].grid(row=row, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
        row += 1

    def right_click(self, event):
        """Probably need to add our dialog...
        """

        super().right_click(event)
        self.popup_menu.add_command(label="Edit..", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def edit(self):
        """Present a dialog for editing the Custom input
        """
        if self.dialog is None:
            self.create_dialog()

        self.dialog.activate(geometry='centerscreenfirst')

    def handle_dialog(self, result):
        if result == 'Cancel':
            self.dialog.deactivate(result)
            return

        if result == 'Help':
            # display help!!!
            return

        if result != "OK":
            self.dialog.deactivate(result)
            raise RuntimeError(
                "Don't recognize dialog result '{}'".format(result)
            )

        self.dialog.deactivate(result)

        # set up our shorthand for the widgets
        w = self._widget

        # and get the script
        self.node.script = w['textarea'].get(1.0, tk.END)

    def handle_help(self):
        """Not implemented yet ... you'll need to fill this out!"""
        print('Help!')
