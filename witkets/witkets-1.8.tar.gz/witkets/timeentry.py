#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *
from witkets.spin import Spin


class TimeEntry(Frame):
    """Entry for inputting time (hours, minutes and seconds)
    
    Convenient widget that combines 3 spins and 2 labels to compose an entry
    suitable for inputting time.
    
    Options:
       - seconds --- Whether to show the seconds spin (constructor only)
       - All :code:`Frame` widget options
    """

    def __init__(self, master=None, seconds=True, **kw):
        Frame.__init__(self, master, **kw)
        self.spinHours = Spin(self, to=23, orientation=VERTICAL)
        self.spinHours['numberformat'] = '%02d'
        self.spinHours['circular'] = True
        self.spinHours.entry['width'] = 2
        self.spinHours.pack(side=LEFT)
        self.label1 = Label(self, text=':')
        self.label1.pack(side=LEFT)
        self.spinMinutes = Spin(self, to=59, orientation=VERTICAL)
        self.spinMinutes['numberformat'] = '%02d'
        self.spinMinutes['circular'] = True
        self.spinMinutes.entry['width'] = 2
        self.spinMinutes.pack(side=LEFT)
        self.label2 = Label(self, text=':')
        self.spinSeconds = Spin(self, to=59, orientation=VERTICAL)
        self.spinSeconds['numberformat'] = '%02d'
        self.spinSeconds['circular'] = True
        self.spinSeconds.entry['width'] = 2
        if seconds:
            self.label2.pack(side=LEFT)
            self.spinSeconds.pack(side=LEFT)

    def get(self):
        """Gets the time stored in the widget as a tuple (hours, mins, secs)"""
        hours = int(self.spinHours.get())
        minutes = int(self.spinMinutes.get())
        seconds = int(self.spinSeconds.get())
        return (hours, minutes, seconds)

    def set(self, hours, minutes, seconds):
        """Sets the time stored in the widget"""
        self.spinHours.set(hours)
        self.spinMinutes.set(minutes)
        self.spinSeconds.set(seconds)


if __name__ == '__main__':
    root = Tk()
    timeEntry = TimeEntry(root)
    timeEntry.pack(expand=0)
    timeEntry.set(23, 48, 36)
    print(timeEntry.get())
    root.mainloop()
