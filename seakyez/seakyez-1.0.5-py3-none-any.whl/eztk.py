from tkinter import *
from tkinter import messagebox, ttk
import time, threading

def getText(text):
    return text.get(1.0, END).strip()

def clearText(text):
    text.delete(1.0, END)

def setText(text, content):
    text.insert(1.0, content)

def setEntry(entry, text):
    entry.delete(0, END)
    entry.insert(0, text)

def clearEntry(entry):
    entry.delete(0, END)

def setEntryHint(entry, hint, hintTextColor = 'grey39'):
    def focusIn(event):
        clearEntry(entry)
        entry['fg'] = color
    def focusOut(event):
        if not entry.get():
            setEntry(entry, hint)
            entry['fg'] = hintTextColor
    color = entry['fg']
    entry.bind('<FocusIn>', focusIn)
    entry.bind('<FocusOut>', focusOut)
    setEntry(entry, hint)
    entry['fg'] = hintTextColor

class LoadDialog(Toplevel):
    '''A simple LoadDialog'''
    def __init__(self, master, load_message = 'Loading', maxDots = 6):
        assert isinstance(load_message, str) and isinstance(maxDots, int) and maxDots > 0
        Toplevel.__init__(self, master)
        self.transient(master)
        self.geometry(f"+{master.winfo_rootx() + 50}+{master.winfo_rooty() + 50}")
        self.title('Load Dialog')
        self.load_message = load_message
        self.maxDots = maxDots
        self.label = Label(self, text = load_message, width = 20)
        self.label.pack()
        self.protocol('WM_DELETE_WINDOW', self.dontClose)
        self.isClose = False
        threading.Thread(target = self.update).start()

    def setCloseEvent(self, target, args = ()):
        threading.Thread(target = self.__task, args = (target, args)).start()

    def __task(self, target, args):
        try:
            target(*args)
        finally:
            self.close()

    def dontClose(self):
        pass

    def update(self):
        dots = 0
        while not self.isClose:
            dots = (dots + 1) % (self.maxDots + 1)
            time.sleep(0.5)
            self.label['text'] = self.load_message + dots * '.'
        self.destroy()

    def close(self):
        self.isClose = True

class ProgressDialog(Toplevel):
    '''A simple ProgressDialog with progress from 0 to 100'''
    def __init__(self, master, load_message = 'Progress: 0%'):
        assert isinstance(load_message, str)
        Toplevel.__init__(self, master)
        self.master = master
        self.transient(master)
        self.geometry(f"+{master.winfo_rootx() + 50}+{master.winfo_rooty() + 50}")
        self.title('Progress Dialog')
        self.label = Label(self, text = load_message)
        self.label.pack(side = TOP, expand = True, fill = BOTH)
        self.progressbar = ttk.Progressbar(self, length = 300, maximum = 100, mode = 'determinate')
        self.progressbar.pack(side = BOTTOM, expand = True, fill = BOTH)
        self.progress = 0
        self.progressbar.start(0)
        threading.Thread(target = self.updateProgressbar).start()

    def updateProgressbar(self):
        while self.progress < 100:
            pass
        self.progressbar.stop()
        self.destroy()

    def update(self, value, text = ''):
        self.label['text'] = text or f'Progress: {value}%'
        self.progressbar['value'] = value
        self.progress = value
