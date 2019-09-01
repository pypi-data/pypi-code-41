#!python

import os
import tkinter as tk
import tkinter.filedialog

filename = None
type_of_file = None

def newFile():
    global filename
    filename = None
    text.delete(0.0, tk.END)
    statusbar.config(text="File type: {}".format(fileType()))
    

def saveFile():
    global filename
    if filename == None:
        filename = tk.filedialog.asksaveasfile(mode='w', defaultextension='.txt')
        statusbar.config(text="File type: {}".format(fileType()))
    if filename is not None:
        t = text.get(0.0, tk.END)
        filename.write(t)
        statusbar.config(text="File type: {}".format(fileType()))
        

def saveAs():
    f = tk.filedialog.asksaveasfile(mode='w', defaultextension='.txt')
    t = text.get(0.0, tk.END)
    f.write(t.rstrip())
    f.close()
    statusbar.config(text="File type: {}".format(fileType()))
    

def openFile():
    global filename
    filename = tk.filedialog.askopenfile(mode = 'r+')
    t = filename.read()
    text.delete(0.0, tk.END)
    text.insert(0.0, t)
    statusbar.config(text="File type: {}".format(fileType()))

def fileType():
    global filename
    global type_of_file
    if filename == None:
        type_of_file = "Undefined"
        return type_of_file
    else:
        fext = os.path.splitext(filename.name)
        if fext[1] == '.py':
            type_of_file = "Python"
            return type_of_file
        elif fext[1] == '.c':
            type_of_file = "C"
            return type_of_file
        elif fext[1] == '.h':
            type_of_file = "Header"
            return type_of_file
        elif fext[1] == '.txt':
            type_of_file = "Text"
            return type_of_file
        elif fext[1] == '.cpp':
            type_of_file = "C++"
            return type_of_file
        else:
            type_of_file = "Unknown"
            return type_of_file

root = tk.Tk()
root.title("Golmorich Text Editor | Version 1.1")
root.geometry('800x800')

text = tk.Text(root)
text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

statusbar = tk.Label(root, text="File type: {}".format(fileType()), bd=1, relief=tk.SUNKEN, anchor=tk.W)
statusbar.pack(side=tk.BOTTOM, fill=tk.X)

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar)
filemenu.add_command(label="New", command=newFile)
filemenu.add_command(label="Open", command=openFile)
filemenu.add_command(label= "Save", command=saveFile)
filemenu.add_command(label="Save As", command=saveAs)
filemenu.add_separator()
filemenu.add_command(label="Quit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)
root.mainloop()