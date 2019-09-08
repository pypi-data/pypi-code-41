import os
import re
import sys
import curses


class Screen:

    '''
    Class: Screen

    Description: Generic screen using curses

    Args:
        - keypad: Enable keypad keys
        - cbreak: Enable cbreak mode
        - noecho: Enable noecho mode
        - (kw)?args: See parent class(es)
    '''

    def __init__(self, keypad=True, cbreak=True, noecho=True, *args, **kwargs):
        self.screen = curses.initscr()
        self.t_height, self.t_width = self.screen.getmaxyx()
        self.setup(keypad, cbreak, noecho)
        self.keyfuncs = {}
        self.spacing = 1

    def setup(self, keypad, cbreak, noecho):
        ''' Setup curses session '''
        if cbreak:
            curses.cbreak()
        if noecho:
            curses.noecho()
        self.screen.keypad(keypad)

    def run_command(self, key):
        ''' Run a command from .keyfuncs '''
        if key in self.keyfuncs:
            self.keyfuncs[key]()
        else:
            self.incorrect_command(key)

    def one_text_input(self, header, addit=''):
        ''' Recieve one line of text input from the bottom of the screen '''
        h = 1
        w = self.t_width - 1
        x = self.spacing
        y = self.t_height - self.spacing  # int((self.t_height - h) / 2)
        tmp_win = curses.newwin(h, w, y, x)
        tmp_win.keypad(1)
        txtbox = curses.textpad.Textbox(tmp_win)
        tmp_win.addstr(0, 0, header + addit)
        inp = txtbox.edit(self.handle_input_key)
        if len(inp) < len(header):
            return inp
        else:
            return inp[len(header):-1]

    def are_you_sure(self):
        ''' Asks the user yes/no '''
        header = 'Confirm [Yn]: '
        if re.match(r'[Nn].*', self.one_text_input(header)[len(header):-1]):
            return False
        return True

    def incorrect_command(self, key):
        ''' Handle incorrect command '''
        pass

    def terminate_input_on_all(self, ch):
        ''' Key handler: Continue on keypress '''
        return 7

    def handle_input_key(self, ch):
        ''' Key handler: Recognises CR as ^G and BS as ^H '''
        if ch == 127:  # BS
            return 263
        if ch == 10:  # CR
            return 7
        return ch

    def quit(self):
        ''' End curses session and exit program '''
        curses.endwin()
        sys.exit(0)
