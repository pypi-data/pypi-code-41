#!/usr/bin/env python3
"""

"""
import pathlib
from gi.repository import Gtk


# FileChooser ##########################################################################################################
class FileChooser:
    """This class handles the logic for a GTK FileChooser Dialog. To use, call open_dialog()"""
    def __init__(self, dialog_parent=None):
        glade_file_path = str(pathlib.Path(__file__).resolve().parent / 'file_chooser.glade')
        builder = Gtk.Builder()
        builder.add_from_file(glade_file_path)
        builder.connect_signals(self)
        self.dialog = builder.get_object('dialog')
        self.save_button = builder.get_object('save_button')
        self.cancel_button = builder.get_object('cancel_button')
        if dialog_parent:
            self.dialog.set_transient_for(dialog_parent)

    # Dialog Control Handlers ------------------------------------------------------------------------------------------
    def on_cancel_button_clicked(self, _):
        self.dialog.response(Gtk.ResponseType.CANCEL)

    def on_save_button_clicked(self, _):
        self.dialog.response(Gtk.ResponseType.ACCEPT)

    # Open Dialog ------------------------------------------------------------------------------------------------------
    def open_dialog(self, file_name='', existing=False):
        if existing:
            self.dialog.set_action(Gtk.FileChooserAction.OPEN)
            self.dialog.set_filename(str(file_name))
            self.save_button.set_label('Open')
        else:
            self.dialog.set_action(Gtk.FileChooserAction.SAVE)
            self.dialog.set_current_name(str(file_name))
            self.save_button.set_label('Save')
        self.dialog.show()
        response = self.dialog.run()
        filename = self.dialog.get_filename()
        self.dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            return filename
        else:
            return None
