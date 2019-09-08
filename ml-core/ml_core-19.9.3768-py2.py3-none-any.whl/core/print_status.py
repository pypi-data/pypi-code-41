# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from .update_timer import UpdateTimer


def _dynamic_display(fp):
    return (hasattr(fp, 'isatty') and fp.isatty()) or 'ipykernel' in sys.modules


class PrintStatus(object):
    DEFAULT_STATIC_INTERVAL = 10

    def __init__(self, nl_on_clone=True, fp=sys.stdout, interval=None):
        if interval is None and not _dynamic_display(fp):
            interval = self.DEFAULT_STATIC_INTERVAL

        self.__update_timer = UpdateTimer(interval=interval)
        self.__first_status = True
        self.__last_printed_msg = None
        self.__last_msg = None
        self.__fp = fp
        self.__nl_on_close = nl_on_clone

    def close(self):
        if self.__last_msg is not None:
            if self.__last_msg != self.__last_printed_msg:
                self.__print_status(True, self.__last_msg)

            if self.__nl_on_close:
                self.__print_to_out('\n')

    def __get_formatted_message(self, msg, *args, **kwargs):
        formatted_msg = ''

        has_console = _dynamic_display(self.__fp)

        if self.__last_printed_msg and has_console:
            spaces = len(self.__last_printed_msg)
            formatted_msg += '\r' + (' ' * spaces) + '\r'

        formatted_msg += msg.format(*args, **kwargs)

        if self.__first_status or not has_console:
            formatted_msg = '\n' + formatted_msg

        return formatted_msg

    def __print_to_out(self, text):
        print(text, end='', file=self.__fp)
        self.__fp.flush()

    def __print_status(self, force, msg, *args, **kwargs):
        formatted_msg = self.__get_formatted_message(msg, *args, **kwargs)

        self.__last_msg = formatted_msg.strip()

        def do_update():
            self.__print_to_out(formatted_msg)
            self.__last_printed_msg = self.__last_msg

        if force:
            do_update()
        else:
            self.__update_timer.update_if_possible(do_update)

        return True

    def print_status(self, msg, *args, **kwargs):
        printed_status = self.__print_status(False, msg, *args, **kwargs)

        if self.__first_status and printed_status:
            self.__first_status = False
