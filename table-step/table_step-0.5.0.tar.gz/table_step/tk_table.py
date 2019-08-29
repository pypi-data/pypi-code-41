# -*- coding: utf-8 -*-

"""The graphical part of a Table step"""

import seamm
import Pmw
import pprint  # noqa: F401
import table_step
import tkinter as tk
import tkinter.ttk as ttk


class TkTable(seamm.TkNode):
    """The node_class is the class of the 'real' node that this
    class is the Tk graphics partner for
    """

    node_class = table_step.Table

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
            defaultbutton='OK',
            master=self.toplevel,
            title='Edit Table step',
            command=self.handle_dialog
        )
        self.dialog.withdraw()

        # self._widget, which is inherited from the base class, is
        # a place to store the pointers to the widgets so that we can access
        # them later. We'll set up a short hand 'w' just to keep lines short

        w = self._widget
        frame = ttk.Frame(self.dialog.interior())
        frame.pack(expand=tk.YES, fill=tk.BOTH)
        w['frame'] = frame

        w['method_frame'] = ttk.Frame(frame)
        # Set the first parameter -- which will be exactly matched
        w['method_label'] = ttk.Label(w['method_frame'], text='Operation:')

        w['method'] = ttk.Combobox(
            w['method_frame'],
            state='readonly',
            values=table_step.methods,
            justify=tk.RIGHT,
            width=15
        )
        w['method'].set(self.node.method)

        # Name of table
        w['name_label'] = ttk.Label(w['method_frame'], text=' table named ')

        w['name'] = ttk.Entry(w['method_frame'], width=15)
        w['name'].insert(0, self.node.name)

        # Filename
        w['filename_label'] = ttk.Label(w['frame'], text=' from file:')

        w['filename'] = ttk.Entry(w['frame'], width=15)
        w['filename'].insert(0, self.node.filename)

        w['file_selector'] = ttk.Label(w['frame'], text='...')

        # Index column
        w['index_column_label'] = ttk.Label(w['frame'], text=' index column:')
        w['index_column'] = ttk.Entry(w['frame'], width=15)
        w['index_column'].insert(0, self.node.index_column)

        # area for columns
        w['columns'] = ttk.Frame(frame, height=300)

        # Information for getting and setting values
        w['row_index_label'] = ttk.Label(w['frame'], text=' row index:')
        w['row_index'] = ttk.Entry(w['frame'], width=15)
        w['row_index'].insert(0, self.node.row_index)

        w['column_index_label'] = ttk.Label(w['frame'], text=' column index:')
        w['column_index'] = ttk.Entry(w['frame'], width=15)
        w['column_index'].insert(0, self.node.column_index)

        w['value_label'] = ttk.Label(w['frame'], text=' value:')
        w['value'] = ttk.Entry(w['frame'], width=50)
        w['value'].insert(0, self.node.value)

        w['variable_name_label'] = ttk.Label(w['frame'], text=' variable:')
        w['variable_name'] = ttk.Entry(w['frame'], width=15)
        w['variable_name'].insert(0, self.node.variable_name)

        self.reset_dialog()

        w['method'].bind("<<ComboboxSelected>>", self.reset_dialog)

    def reset_dialog(self, widget=None):
        # set up our shorthand for the widgets
        w = self._widget

        # and get the method, which in this example controls
        # how the widgets are laid out.
        method = w['method'].get()

        # Remove any widgets previously packed
        frame = w['frame']
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        w['method_frame'].grid(row=row, column=0, columnspan=9, sticky=tk.W)
        w['method_label'].grid(row=row, column=0, sticky=tk.E)
        w['method'].grid(row=row, column=1, sticky=tk.W)
        w['name_label'].grid(row=row, column=2, sticky=tk.W)
        w['name'].grid(row=row, column=3, sticky=tk.W)

        if method == 'create':
            row += 1
            w['index_column_label'].grid(row=row, column=0, sticky=tk.E)
            w['index_column'].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            w['columns'].grid(row=row, column=0, sticky=tk.NSEW)
            self.layout_columns_for_editing(first=True)
        elif method == 'read':
            row += 1
            w['filename_label'].grid(row=row, column=0, sticky=tk.E)
            w['filename'].grid(row=row, column=1, sticky=tk.EW)
            w['file_selector'].grid(row=row, column=2, sticky=tk.W)
            row += 1
            w['index_column_label'].grid(row=row, column=0, sticky=tk.E)
            w['index_column'].grid(row=row, column=1, sticky=tk.EW)
        elif method == 'save':
            pass
        elif method == 'print':
            pass
        elif method == 'print current row':
            pass
        elif method == 'append row':
            row += 1
            w['columns'].grid(row=row, column=0, sticky=tk.NSEW)
            self.layout_columns_for_add_row(first=True)
        elif method == 'next row':
            pass
        elif method == 'add columns':
            row += 1
            w['columns'].grid(row=row, column=0, sticky=tk.NSEW)
            self.layout_columns_for_editing(first=True)
        elif method == 'get element':
            row += 1
            w['row_index_label'].grid(row=row, column=0, sticky=tk.E)
            w['row_index'].grid(row=row, column=1, sticky=tk.W)

            row += 1
            w['column_index_label'].grid(row=row, column=0, sticky=tk.E)
            w['column_index'].grid(row=row, column=1, sticky=tk.W)

            row += 1
            w['variable_name_label'].grid(row=row, column=0, sticky=tk.E)
            w['variable_name'].grid(row=row, column=1, sticky=tk.W)
        elif method == 'set element':
            row += 1
            w['row_index_label'].grid(row=row, column=0, sticky=tk.E)
            w['row_index'].grid(row=row, column=1, sticky=tk.W)

            row += 1
            w['column_index_label'].grid(row=row, column=0, sticky=tk.E)
            w['column_index'].grid(row=row, column=1, sticky=tk.W)

            row += 1
            w['value_label'].grid(row=row, column=0, sticky=tk.E)
            w['value'].grid(row=row, column=1, sticky=tk.W)
        else:
            raise RuntimeError(
                'The table method must be one of ' +
                ', '.join(table_step.methods) + ', not  "' + method + '"'
            )
        row += 1

    def right_click(self, event):
        """Probably need to add our dialog...
        """

        super().right_click(event)
        self.popup_menu.add_command(label="Edit...", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def edit(self):
        """Present a dialog for editing the Table input
        """
        if self.dialog is None:
            self.create_dialog()

        self.dialog.activate(geometry='centerscreenfirst')

    def handle_dialog(self, result):
        if result is None or result == 'Cancel':
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
        # and get the method, which in this example tells
        # whether to use the value directly or get it from
        # a variable in the flowchart

        method = w['method'].get()

        self.node.method = method
        self.node.name = w['name'].get()
        if method == 'create':
            self.save_column_data()
            self.node.index_column = w['index_column'].get()
        elif method == 'read':
            self.node.filename = w['filename'].get()
            self.node.index_column = w['index_column'].get()
        elif method == 'save':
            pass
        elif method == 'print':
            pass
        elif method == 'append row':
            self.save_column_data()
        elif method == 'next row':
            pass
        elif method == 'add columns':
            # Save any changes!
            self.save_column_data()
        elif method == 'get element':
            self.node.row_index = w['row_index'].get()
            self.node.column_index = w['column_index'].get()
            self.node.variable_name = w['variable_name'].get()
        elif method == 'set element':
            self.node.row_index = w['row_index'].get()
            self.node.column_index = w['column_index'].get()
            self.node.value = w['value'].get()
        else:
            raise RuntimeError(
                'The table method must be one of ' +
                ', '.join(table_step.methods) + ', not "' + method + '"'
            )

    def handle_help(self):
        """Not implemented yet ... you'll need to fill this out!"""
        print('Help!')

    def layout_columns_for_editing(self, first=False):
        """Layout the table of columns for adding, editing, etc.
        """

        w = self._widget
        frame = w['columns']

        # Save any changes!
        if not first:
            self.save_column_data()

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.destroy()

        row = 0
        w = ttk.Label(frame, text='Name')
        w.grid(row=row, column=1)
        w = ttk.Label(frame, text='Type')
        w.grid(row=row, column=2)
        w = ttk.Label(frame, text='Default')
        w.grid(row=row, column=3)

        for d in self.node.tmp_columns:
            row += 1
            widgets = d['widgets'] = {}

            col = 0
            # The button to remove a row...
            w = widgets['remove'] = ttk.Button(
                frame,
                text='-',
                width=5,
                command=lambda row=row: self.remove_column_for_add_row(row),
                takefocus=False,
            )
            w.grid(row=row, column=col, sticky=tk.W)
            col += 1
            widgets['remove'] = w

            # the name of the keyword
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d['name'])
            widgets['name'] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

            # the type of the column
            w = ttk.Combobox(
                frame,
                state='readonly',
                values=('string', 'boolean', 'integer', 'float')
            )
            if 'type' not in d:
                d['type'] = 'float'
            w.set(d['type'])
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1
            widgets['type'] = w

            # the default
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d['default'])
            widgets['default'] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

        # The button to add a row...
        row += 1
        w = self._widget['add column'] = ttk.Button(
            frame,
            text='+',
            width=5,
            command=self.add_column,
            takefocus=False,
        )
        w.grid(row=row, column=0, sticky=tk.W)

    def layout_columns_for_add_row(self, first=False):
        """Layout the table of columns for adding a row
        """

        w = self._widget
        frame = w['columns']

        # Save any changes!
        if not first:
            self.save_column_data()

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.destroy()

        row = 0
        w = ttk.Label(frame, text='Name')
        w.grid(row=row, column=1)
        w = ttk.Label(frame, text='Value')
        w.grid(row=row, column=2)

        for d in self.node.tmp_columns:
            row += 1
            widgets = d['widgets'] = {}

            col = 0
            # The button to remove a row...
            w = widgets['remove'] = ttk.Button(
                frame,
                text='-',
                width=5,
                command=lambda row=row: self.remove_column(row),
                takefocus=False,
            )
            w.grid(row=row, column=col, sticky=tk.W)
            col += 1
            widgets['remove'] = w

            # the name of the column
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d['name'])
            widgets['name'] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

            # the value
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d['value'])
            widgets['value'] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

        # The button to add a row...
        row += 1
        w = self._widget['add column'] = ttk.Button(
            frame,
            text='+',
            width=5,
            command=self.add_column_for_add_row,
            takefocus=False,
        )
        w.grid(row=row, column=0, sticky=tk.W)

    def remove_column(self, row=None):
        """Remove a column from the list of columns"""
        del self.node.tmp_columns[row]
        self.layout_columns_for_editing()

    def add_column(self):
        """Add entries for another column in the displayed table
        """
        self.node.tmp_columns.append(
            {
                'widgets': {},
                'type': 'float',
                'name': '',
                'default': ''
            }
        )
        self.layout_columns_for_editing()

    def remove_column_for_add_row(self, row=None):
        """Remove a column from the list of columns"""
        del self.node.tmp_columns[row]
        self.layout_columns_for_add_row()

    def add_column_for_add_row(self):
        """Add entries for another column in the displayed table
        """
        self.node.tmp_columns.append({'widgets': {}, 'name': '', 'value': ''})
        self.layout_columns_for_add_row()

    def save_column_data(self):
        """Get the data from the widgets when the table information is
        changed in the GUI.
        """
        for d in self.node.tmp_columns:
            w = d['widgets']
            if 'name' in w:
                d['name'] = w['name'].get()
            if 'type' in w:
                d['type'] = w['type'].get()
            if 'default' in w:
                d['default'] = w['default'].get()
            if 'value' in w:
                d['value'] = w['value'].get()
            del d['widgets']
