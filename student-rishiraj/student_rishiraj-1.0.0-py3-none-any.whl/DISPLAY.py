from tkinter import *
import tkinter as tk
import mysql.connector
from tkinter import messagebox
from tkinter.messagebox import *
from tkcalendar import DateEntry
from tkinter import ttk
top=Tk()
top.title('Display Data')
top.geometry('1000x250+200+50')
def get():
    e0=ent0.get()
    e1=e0.split()
    print(e1)
    e2=['insert','alter','update','insert','modify']
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                   database='student_management')
    mycursor = mydb.cursor()
    l=[]
    e3=([i for i in e1 if i in e2])
    if e3 != l:
        messagebox.showinfo("MySql","BEE IN LIMITE")
        exit()
    mycursor.execute(e0)
    for i in mycursor:
        print(i)
    #messagebox.showinfo("DELETE", "DATA DELETE SUCCESSFULLY")
    mydb.commit()







ent0=StringVar()

f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f1.place(x=100,y=30,width=800,height=200)
#cb=ttk.Combobox(f1,width=20,textvariable=ent1,value=('ID','NAME'),state='readonly',font=('arial',10)).grid(row=1,column=2,padx=20,pady=30)
l5=Label(f1, text="USE SQL COMMAND TO SHOW DATA:", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,column=1,padx=20,pady=30)
bt=Button(f1,text="RUN",command=get,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=2,column=4,padx=30,pady=30)
e1=Entry(f1,bd=5,fg='crimson',width=55,bg="powder blue",textvariable=ent0,font=('arial',15,'bold')).grid(row=2,column=1,padx=20,pady=30)
top.mainloop()