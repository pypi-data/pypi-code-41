#!/usr/bin/env python
# coding: utf-8
from collections import OrderedDict
from .utils.exceptions import HeaderNotDefine, HeaderAndRowLenNotMatch


class UiTable(object):
    def __init__(self):
        self.__table = OrderedDict({})
        self.__header_len = 0
        self.__row_len = 0
        self.__max_row_len = 0
        self.__header_list = []
        self.filed_spacing = 4

    def __reset(self):
        self.__table = OrderedDict({})
        self.__header_len = 0
        self.__row_len = 0
        self.__max_row_len = 0
        self.__header_list = []

    def add_header(self, *args):
        self.__reset()
        self.__header_len = len(args)
        self.__header_list = args
        for item in args:
            self.__table[item] = []

    def get_max_len(self, arg_list):
        max_len = 0
        for item in arg_list:
            if len(str(item)) > max_len:
                max_len = len(str(item))
        return max_len

    def gen_format_str(self, i):
        str_len = self.__max_row_len + self.filed_spacing
        return i + " " * (str_len - len(i))

    def add_row(self, *args):
        if not self.__header_list:
            raise HeaderNotDefine("Header not define!!!")
        max_len = self.get_max_len(args)
        if max_len > self.__max_row_len:
            self.__max_row_len = max_len

        if len(args) != self.__header_len:
            raise HeaderAndRowLenNotMatch("Header's len not equal Row's len")
        else:
            self.__row_len += 1
            for item in self.__header_list:
                self.__table[item].append(str(args[self.__header_list.index(item)]))

    def __str__(self):
        table_lines = []
        table_lines.append(
            "".join([self.gen_format_str(item) for item in self.__header_list])
        )
        for item in range(self.__row_len):
            line = []
            for header in self.__header_list:
                line.append(self.__table[header][item])
            table_lines.append("".join([self.gen_format_str(item) for item in line]))
        return "\n".join(table_lines)

    def __repr__(self):
        table_lines = []
        table_lines.append(
            "".join([self.gen_format_str(item) for item in self.__header_list])
        )
        for item in range(self.__row_len):
            line = []
            for header in self.__header_list:
                line.append(self.__table[header][item])
            table_lines.append("".join([self.gen_format_str(item) for item in line]))
        return "\n".join(table_lines)
