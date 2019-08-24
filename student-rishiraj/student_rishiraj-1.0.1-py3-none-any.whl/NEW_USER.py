from tkinter import *
import tkinter as tk
import mysql.connector
from tkinter import messagebox
from tkinter.messagebox import *
from tkcalendar import DateEntry
from tkinter import ttk
top=Tk()
top.title('NEW USER')
top.geometry('1000x250+200+50')
def get():
    e0=ent0.get()
    mydb = mysql.connector.connect(host="localhost", user='root', password=e0)
    print(mydb)
    if (mydb):
        print('connection approved')
    else:
        print('connection loss')
    mycursor = mydb.cursor()
    sql1=("create user 'rishiraj'@'localhost' identified by 'iloveyou'")
    sql=("grant all privileges on *.* to 'rishiraj'@'localhost'")
    sql2=("flush privileges")
    sql3=('quit')
    mycursor.execute(sql1)
    mycursor.execute(   sql )
    mycursor.execute( sql2 )
    mycursor.execute( sql3)
    #messagebox.showinfo("DELETE", "DATA DELETE SUCCESSFULLY")
    #mydb.commit()







ent0=StringVar()
f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f1.place(x=100,y=30,width=800,height=200)
#cb=ttk.Combobox(f1,width=20,textvariable=ent1,value=('ID','NAME'),state='readonly',font=('arial',10)).grid(row=1,column=2,padx=20,pady=30)
l5=Label(f1, text="ENTER YOUR PASSWORD", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,column=1,padx=20,pady=30)
bt=Button(f1,text="RUN",command=get,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=2,column=4,padx=30,pady=30)
e1=Entry(f1,bd=5,fg='crimson',width=30,bg="powder blue",textvariable=ent0,font=('arial',15,'bold')).grid(row=2,column=1,padx=20,pady=30)
top.mainloop()