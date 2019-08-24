import os
from tkinter import *
top=Tk()
top.title('Menu')
top.geometry('800x500')
label=Label(top,text='STUDENT  MANAGEMENT  SYSTEM',font=('arial',34,'bold'),bd=5,fg="blue",bg="powder blue")
label.grid(row=0,column=0,)

def reg():
    os.system('python REG.py')
def search():
    os.system('python SEARCH.py')
def delete():
    os.system('python DELETE.py')
def update():
    os.system('python UPDATE.py')
def display():
    os.system('python DISPLAY.py')
def new():
    os.system('python NEW_USER.py')


f1=Frame(top,width=500,height=40,bg="powder blue",bd=5,relief=SUNKEN)
f1.grid(row=1,column=0,pady=40)
bt=Button(top,text="FOR NEW USER ONLY",width=25,height=3,bg="red",fg="black",command=new)
bt.place(x=300,y=200)

bt=Button(f1,text="REGISTRATION",width=15,height=3,bg="red",fg="black",command=reg)
bt.grid(column=0,row=0)
bt=Button(f1,text="UPDATE",width=10,height=3,bg="red",fg="black",command=update)
bt.grid(column=1,row=0)
bt=Button(f1,text="DELETE",width=10,height=3,bg="red",fg="black",command=delete)
bt.grid(column=2,row=0)
bt=Button(f1,text="SEARCH",width=10,height=3,bg="red",fg="black",command=search)
bt.grid(column=3,row=0)
bt=Button(f1,text="DISPLAY",width=10,height=3,bg="red",fg="black",command=display)
bt.grid(column=4,row=0)
top.mainloop()

