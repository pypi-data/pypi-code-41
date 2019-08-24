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



def centerheader(text, window):
    textl = text.split('\n')
    height, width = window.getmaxyx()
    textcounter = 0
    for i in textl:
        window.addstr(int(height/2 - int(len(textl)/2) + textcounter),
                      int(width/2 - (len(i)/2)), i)
        textcounter += 1
    window.refresh()


def vcentertext(text, window):
    textl = text.split('\n')
    height, width = window.getmaxyx()
    textcounter = 0
    maxlen=len(max(textl, key=len))
    for i in textl:
        window.addstr(int(height/2 - int(len(textl)/2) + textcounter),
                      int(width/2 - (maxlen/2)), i)
        textcounter += 1
    window.refresh()


def animatetext(atext, window, textfunct):
    btext = ''
    for i in range(len(atext)):
        btext += atext[i]
        textfunct(btext, window)
        window.refresh()
        time.sleep(.05)


def chatbox(window):
    sub = window.subwin(1, 40, 3, 2)
    tb = curses.textpad.Textbox(sub)
    window.refresh()
    tb.edit()
