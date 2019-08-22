#!/usr/bin/env python3
import curses
import time
def setup():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    stdscr.keypad(True)
    return stdscr

def quit(stdscr):
    curses.echo()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()

def centertext(text, window):
    window.addstr(int(curses.LINES/2), int(curses.COLS/2), text)
    window.refresh()

def animatetext(atext, window):
    btext=''
    for i in range(len(atext)):
        btext+=atext[i]
        centertext(btext, window)
        window.refresh()
        time.sleep(.05)
