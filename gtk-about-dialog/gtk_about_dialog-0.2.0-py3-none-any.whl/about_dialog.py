#!/usr/bin/env python3
"""

"""
import pathlib
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


# About Dialog #########################################################################################################
class AboutDialog:
    def __init__(
            self, app_name='', app_version='', app_logo_file_path='', app_description='', app_copyright_string='',
            app_website='', app_author_list=(), dialog_parent=None):

        # GUI Setup
        path_to_glade_file = pathlib.Path(__file__).parent / 'about_dialog.glade'
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(str(path_to_glade_file.resolve()))
        gtk_builder.connect_signals(self)

        # dialog setup
        self._dialog = gtk_builder.get_object('dialog')
        self._dialog.set_license_type(Gtk.License.GPL_3_0)

        self.__logo_file_path = ''

        if app_name:
            self.app_name = app_name
        if app_version:
            self.app_version = app_version
        if app_logo_file_path:
            self.app_logo_file_path = app_logo_file_path
        if app_description:
            self.app_description = app_description
        if app_copyright_string:
            self.app_copyright_string = app_copyright_string
        if app_website:
            self.app_website = app_website
        if app_author_list:
            self.app_authors = app_author_list
        if dialog_parent:
            self.dialog_parent = dialog_parent

    # dialog parent ----------------------------------------------------------------------------------------------------
    @property
    def dialog_parent(self):
        return self._dialog.get_transient_for()

    @dialog_parent.setter
    def dialog_parent(self, dialog_parent):
        self._dialog.set_transient_for(dialog_parent)

    # app name ---------------------------------------------------------------------------------------------------------
    @property
    def app_name(self):
        return self._dialog.get_program_name()

    @app_name.setter
    def app_name(self, app_name):
        self._dialog.set_program_name(app_name)

    # app version ------------------------------------------------------------------------------------------------------
    @property
    def app_version(self):
        return self._dialog.get_version()

    @app_version.setter
    def app_version(self, app_version):
        self._dialog.set_version(app_version)

    # app logo file path -----------------------------------------------------------------------------------------------
    @property
    def app_logo_file_path(self):
        return self.__logo_file_path

    @app_logo_file_path.setter
    def app_logo_file_path(self, app_logo_file_path):
        self.__logo_file_path = app_logo_file_path
        self._dialog.set_logo(GdkPixbuf.Pixbuf().new_from_file(self.__logo_file_path))

    # app description --------------------------------------------------------------------------------------------------
    @property
    def app_description(self):
        return self._dialog.get_comments()

    @app_description.setter
    def app_description(self, app_description):
        self._dialog.set_comments(app_description)

    # app copyright string ---------------------------------------------------------------------------------------------
    @property
    def app_copyright_string(self):
        return self._dialog.get_copyright()

    @app_copyright_string.setter
    def app_copyright_string(self, copyright_string):
        self._dialog.set_copyright(copyright_string)

    # app website ------------------------------------------------------------------------------------------------------
    @property
    def app_website(self):
        return self._dialog.get_website()

    @app_website.setter
    def app_website(self, website):
        self._dialog.set_website(website)

    # app authors ------------------------------------------------------------------------------------------------------
    @property
    def app_authors(self):
        return self._dialog.get_authors()

    @app_authors.setter
    def app_authors(self, authors):
        self._dialog.set_authors(authors)

    # handlers ---------------------------------------------------------------------------------------------------------
    def _on_dialog_response(self, _, response_type):
        if response_type == Gtk.ResponseType.DELETE_EVENT:
            self._dialog.hide()

    # run method -------------------------------------------------------------------------------------------------------
    def run(self):
        self._dialog.show_now()
