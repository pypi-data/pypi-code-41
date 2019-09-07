#!/usr/bin/env python3
import pathlib
from datetime import datetime
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


# Helper functions #####################################################################################################
def _enlarge_spinbox_font(spinbox):
    """
    This function increases the font size of the provided spinbox by 400%.
    It is used by the hour and minute spinboxes
    """
    css = b'''spinbutton {font-size: 400%;}'''
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(css)
    spinbox_style_context = spinbox.get_style_context()
    spinbox_style_context.add_provider(style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def _show_leading_zeros(spin_button):
    """
    This function to the hour and minute spinboxes' "output" signal to add leading zeroes
    """
    adjustment = spin_button.get_adjustment()
    value = int(adjustment.get_value())
    spin_button.set_text(f'{value:02d}')
    return True


# DateTimePopover Class ################################################################################################
class DateTimePopover:
    """
    This class provides the logic for a gtk date/time popover widget.
    """
    def __init__(self, set_relative_to=None, connect_signals=None):
        # gtk builder setup
        glade_file_path = str(pathlib.Path(__file__).resolve().parent / "datetime_popover.glade")
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(glade_file_path)
        gtk_builder.connect_signals(self)
        # Widget Fetching
        self._popover = gtk_builder.get_object('popover')
        self._stack_switcher = gtk_builder.get_object('stack_switcher')
        self._stack = gtk_builder.get_object('stack')
        self._calendar = gtk_builder.get_object('calendar')
        self._current_date_button = gtk_builder.get_object('current_date_button')
        self._clear_date_button = gtk_builder.get_object('clear_date_button')
        self._hour_spinbox = gtk_builder.get_object('hour_spinbox')
        self._minute_spinbox = gtk_builder.get_object('minute_spinbox')
        self._clear_time_button = gtk_builder.get_object('clear_time_button')
        self._current_time_button = gtk_builder.get_object('current_time_button')
        # Spinbox setup
        for spinbox in [self._hour_spinbox, self._minute_spinbox]:
            _enlarge_spinbox_font(spinbox)
            spinbox.connect('output', _show_leading_zeros)
        # arg parsing
        if set_relative_to:
            self.set_relative_to(set_relative_to)
        if connect_signals:
            self.connect_signals(connect_signals)
        # date initialization
        self.datetime = None

    # changed handlers -------------------------------------------------------------------------------------------------
    def _on_calendar_day_selected(self, *_):
        self.update_clear_date_button()

    def _on_time_spinboxes_changed(self, *_):
        self.update_clear_time_button()

    # Button Handlers --------------------------------------------------------------------------------------------------
    def _on_current_date_button_clicked(self, *_):
        self.select_current_date()

    def _on_clear_date_button_clicked(self, *_):
        self.clear_date()

    def _on_current_time_button_clicked(self, *_):
        self.select_current_time()

    def _on_clear_time_button_clicked(self, *_):
        self.clear_time()

    # popover methods --------------------------------------------------------------------------------------------------
    def raise_popover(self):
        """This raises the popup"""
        self._popover.popup()

    def set_relative_to(self, widget):
        self._popover.set_relative_to(widget)

    def connect_signals(self, signals_dict):
        for signal, functions in signals_dict.items():
            for function in functions:
                self._popover.connect(signal, function)

    #  Update Methods --------------------------------------------------------------------------------------------------
    def update_clear_date_button(self):
        """This handler enables and disables the clear date button, depending on whether a day is selected or not"""
        self._clear_date_button.set_sensitive(True if self.day else False)

    def update_clear_time_button(self):
        """This method updates the clear time button depending on whether the hour and minute spinboxes are set to 0"""
        hour = self._hour_spinbox.get_value_as_int()
        minute = self._minute_spinbox.get_value_as_int()
        sensitive = True if hour or minute else False
        self._clear_time_button.set_sensitive(sensitive)

    #  Main Functions --------------------------------------------------------------------------------------------------
    def select_current_date(self):
        """Sets the calendar to the current date. The time picker is not affected"""
        current_date = datetime.now()
        self.year = current_date.year
        self.month = current_date.month
        self.day = current_date.day

    def clear_date(self):
        """This sets the day to 0, clearing the date for the gtk widget"""
        self.select_current_date()
        self.day = 0

    def select_current_time(self):
        """This handler sets the hour and minute spinboxes to the current time. The date is not affected"""
        current_time = datetime.now()
        self.hour = current_time.hour
        self.minute = current_time.minute

    def clear_time(self):
        """This handler clears the hour and minute spinboxes by setting both to 0. The date is not affected"""
        self.hour = 0
        self.minute = 0

    # datetime properties ----------------------------------------------------------------------------------------------
    @property
    def year(self):
        return self._calendar.get_date().year

    @year.setter
    def year(self, year):
        self._calendar.select_month(self.month - 1, year)

    @property
    def month(self):
        return self._calendar.get_date().month + 1

    @month.setter
    def month(self, month):
        self._calendar.select_month(month - 1, self.year)

    @property
    def day(self):
        return self._calendar.get_date().day

    @day.setter
    def day(self, day):
        self._calendar.select_day(day)
        self.update_clear_date_button()

    @property
    def hour(self):
        return self._hour_spinbox.get_value_as_int()

    @hour.setter
    def hour(self, hour):
        self._hour_spinbox.set_value(hour)
        self.update_clear_time_button()

    @property
    def minute(self):
        return self._minute_spinbox.get_value_as_int()

    @minute.setter
    def minute(self, minute):
        self._minute_spinbox.set_value(minute)
        self.update_clear_time_button()

    @property
    def datetime(self):
        if self._calendar.get_date().day:
            return datetime(self.year, self.month, self.day, self.hour, self.minute)

    @datetime.setter
    def datetime(self, datetime_object):
        if datetime_object:
            self.year = datetime_object.year
            self.month = datetime_object.month
            self.day = datetime_object.day
            self.hour = datetime_object.hour
            self.minute = datetime_object.minute
        else:
            self.clear_date()
            self.clear_time()


class DateTimeButton:
    def __init__(
            self, date_format_string='%Y-%m-%d', datetime_format_string='%Y-%m-%d at %H:%M',
            no_date_string='No Date Selected'):
        """
        :param date_format_string:
        :param datetime_format_string:
        :param no_date_string:
        """
        super().__init__()
        self.date_format_string = date_format_string
        self.datetime_format_string = datetime_format_string
        self.no_date_string = no_date_string
        self.button = Gtk.Button()
        self.popover = DateTimePopover()

        self.button.connect('clicked', self._on_button_clicked)
        self.popover.set_relative_to(self.button)
        self.popover.connect_signals({'closed': [self.on_popover_closed]})

    def _on_button_clicked(self, *_):
        self.popover.raise_popover()

    def on_popover_closed(self, *_):
        self.set_date_button_label()

    def set_date_button_label(self):
        if self.datetime:
            use_datetime_format_string = (self.datetime.minute or self.datetime.hour) and self.datetime_format_string
            format_string = self.datetime_format_string if use_datetime_format_string else self.date_format_string
            final_date_string = self.datetime.strftime(format_string)
            self.button.set_label(final_date_string)
        else:
            self.button.set_label(self.no_date_string)

    @property
    def year(self):
        return self.popover.year

    @year.setter
    def year(self, year):
        self.popover.year = year
        self.set_date_button_label()

    @property
    def month(self):
        return self.popover.month

    @month.setter
    def month(self, month):
        self.popover.month = month
        self.set_date_button_label()

    @property
    def day(self):
        return self.popover.day

    @day.setter
    def day(self, day):
        self.popover.day = day
        self.set_date_button_label()

    @property
    def hour(self):
        return self.popover.hour

    @hour.setter
    def hour(self, hour):
        self.popover.hour = hour
        self.set_date_button_label()

    @property
    def minute(self):
        return self.popover.minute

    @minute.setter
    def minute(self, minute):
        self.popover.minute = minute
        self.set_date_button_label()

    @property
    def datetime(self):
        return self.popover.datetime

    @datetime.setter
    def datetime(self, datetime_object):
        self.popover.datetime = datetime_object
        self.set_date_button_label()
