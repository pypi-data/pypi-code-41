import os
import curses
import curses.textpad

from util.screen import Screen
from util import util


class ListScreen(Screen):

    '''
    Inheritence: ListScreen -> Screen

    Description: Generic TUI screen for a list of text

    Args:
        - fn: Config file to load
        - keypad: Enable keypad keys
        - cbreak: Enable cbreak mode
        - noecho: Enable noecho mode
        - on_color: Provide a main fg color
        - off_color: Provide a main bg color
        - (kw)?args: See parent class(es)
    '''

    ON_COLOR = None
    OFF_COLOR = None
    UP = -1
    DOWN = 1

    def __init__(self, fn, keypad=True, cbreak=True, noecho=True,
                 off_color=curses.COLOR_CYAN, on_color=curses.COLOR_BLACK,
                 *args, **kwargs):
        super().__init__(keypad, cbreak, noecho, *args, **kwargs)
        self.fn = fn
        self.set_list_functions()
        self.init_colors(off_color, on_color)
        self.cur_list_idx = 0
        self.cur_item_idx = 0
        self.top_of_screen = 0
        self.bottom_of_screen = 0
        self.item_list = [[]]
        self.parents = []
        self.config = None

    def init_colors(self, off_color, on_color):
        ''' Create color pairs (fg, bg) '''
        curses.start_color()
        curses.init_pair(1, on_color, off_color)
        curses.init_pair(2, off_color, on_color)
        self.ON_COLOR = curses.color_pair(1)
        self.OFF_COLOR = curses.color_pair(2)

    def read_config(self):
        ''' Read the (Yaml) config from .fn '''
        try:
            self.todo = util.read_yaml(self.fn)
        except FileNotFoundError as e:
            raise e
        return True

    def cur_list(self):
        return self.item_list[self.cur_list_idx]

    def cur_item(self):
        return self.cur_list()[self.cur_item_idx]

    def write_config(self):
        ''' Write the (Yaml) config to .fn '''
        l = []
        for i in self.item_list[0]:
            l.append(i.serialize())
        util.write_yaml(self.fn, {
            'config': self.config,
            'list': l
        })

    def scroll(self, direction):
        ''' Scrolls the list by the specified number of Items '''
        bound = self.cur_item_idx + direction
        if bound in range(len(self.cur_list())):
            self.cur_item_idx += direction
        if self.bottom_of_screen <= self.cur_item_idx and direction == self.DOWN:
            if self.top_of_screen <= len(self.cur_list()) and self.bottom_of_screen != len(self.cur_list()) - 1:
                self.top_of_screen += 1
        elif self.top_of_screen - 1 == self.cur_item_idx and self.UP:
            if self.top_of_screen >= 0:
                self.top_of_screen -= 1

    def cmd_down(self):
        ''' Scroll the List down '''
        self.scroll(self.DOWN)

    def cmd_up(self):
        ''' Scroll the List up '''
        self.scroll(self.UP)

    def set_list_functions(self):
        ''' Sets the functions specific to List '''
        self.keyfuncs['j'] = self.cmd_down
        self.keyfuncs['k'] = self.cmd_up
        self.keyfuncs[curses.KEY_DOWN] = self.cmd_down
        self.keyfuncs[curses.KEY_UP] = self.cmd_up
