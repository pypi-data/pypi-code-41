from tkinter import *
import tkinter as tk
import mysql.connector
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk
top=Tk()
top.title('UPDATE DETAILS HERE')
top.geometry('1000x550+200+50')
#===============================================database conectivity===========================================
def get():
    e1=ent1.get()
    if e1=='NAME':
        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))#.grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id=StringVar()
        name=StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson',font=('arial', 10, 'bold'), bg="powder blue").place(x=100,y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson',font=('arial', 10, 'bold'), bg="powder blue").place(x=350,y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW",textvariable=id, bd=7, fg='crimson',font=('arial', 15 ), bg="powder blue").place(x=100,y=80)
        entry = Entry(f2, text="ENTER CORRECT",textvariable=name, bd=7, fg='crimson',font=('arial', 15, ), bg="powder blue").place(x=350,y=80)
        def data():
            i=id.get()
            n=name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1="'"+n+"'"
            sql = f" update student set name ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "NAME UPDATE SUCCESSFULLY")
            mydb.commit()
        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300, y=200)
#================================================FATHER NAME===============================================================
    elif e1=='FATHER NAME':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))#.grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id=StringVar()
        name=StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson',font=('arial', 10, 'bold'), bg="powder blue").place(x=100,y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson',font=('arial', 10, 'bold'), bg="powder blue").place(x=350,y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW",textvariable=id, bd=7, fg='crimson',font=('arial', 15 ), bg="powder blue").place(x=100,y=80)
        entry = Entry(f2, text="ENTER CORRECT",textvariable=name, bd=7, fg='crimson',font=('arial', 15, ), bg="powder blue").place(x=350,y=80)
        def data():
            i=id.get()
            n=name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1="'"+n+"'"
            sql = f" update student set father_name ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "FATHER NAME UPDATE SUCCESSFULLY")
            mydb.commit()
        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300, y=200)





    elif e1=='MOTHER NAME':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))  # .grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id = StringVar()
        name = StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=100, y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=350, y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW", textvariable=id, bd=7, fg='crimson', font=('arial', 15),
                       bg="powder blue").place(x=100, y=80)
        entry = Entry(f2, text="ENTER CORRECT", textvariable=name, bd=7, fg='crimson', font=('arial', 15,),
                      bg="powder blue").place(x=350, y=80)

        def data():
            i = id.get()
            n = name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1 = "'" + n + "'"
            sql = f" update student set mother_name ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "MOTHER NAME UPDATE SUCCESSFULLY")
            mydb.commit()

        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300,
                                                                                                              y=200)

    elif e1=='MOBILE NO':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))  # .grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id = StringVar()
        name = StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=100, y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=350, y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW", textvariable=id, bd=7, fg='crimson', font=('arial', 15),
                       bg="powder blue").place(x=100, y=80)
        entry = Entry(f2, text="ENTER CORRECT", textvariable=name, bd=7, fg='crimson', font=('arial', 15,),
                      bg="powder blue").place(x=350, y=80)

        def data():
            i = id.get()
            n = name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1 = "'" + n + "'"
            sql = f" update student set mobile_no ={n} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "MOBILE NO UPDATE SUCCESSFULLY")
            mydb.commit()

        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300,
                                                                                                              y=200)

    elif e1=='EMAIL ID':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))  # .grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id = StringVar()
        name = StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=100, y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=350, y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW", textvariable=id, bd=7, fg='crimson', font=('arial', 15),
                       bg="powder blue").place(x=100, y=80)
        entry = Entry(f2, text="ENTER CORRECT", textvariable=name, bd=7, fg='crimson', font=('arial', 15,),
                      bg="powder blue").place(x=350, y=80)

        def data():
            i = id.get()
            n = name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1 = "'" + n + "'"
            sql = f" update student set email_id ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "EMAIL ID UPDATE SUCCESSFULLY")
            mydb.commit()

        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300,
                                                                                                              y=200)

    elif e1=='GENDER':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))  # .grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id = StringVar()
        name = StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=100, y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=350, y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW", textvariable=id, bd=7, fg='crimson', font=('arial', 15),
                       bg="powder blue").place(x=100, y=80)
        Radiobutton(f2, text='Male', value='Male', bg="powder blue", variable=name).place(x=350, y=80)
        Radiobutton(f2, text='Female', value='Female', bg="powder blue", variable=name).place(x=450, y=80)


        def data():
            i = id.get()
            n = name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1 = "'" + n + "'"
            sql = f" update student set gender ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "GENDER UPDATE SUCCESSFULLY")
            mydb.commit()

        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300,
                                                                                                              y=200)

    elif e1=='DATE OF BIRTH':

        ll = Label(f2, text="Kindly Fill This Details !", bd=7, fg='crimson', bg="powder blue",
                   font=('times new roman', 15, 'bold'))  # .grid(row=1, column=1, padx=20, pady=30)
        ll.pack(side=TOP)
        bt = Button(f1, text="UPDATE", command=get, font=('arial', 15, 'bold'), bg="pink", fg="black").grid(row=1,
                                                                                                            column=4,
                                                                                                            padx=20,
                                                                                                            pady=30)

        id = StringVar()
        name = StringVar()
        ll = Label(f2, text="ENTER YOUR ID BLOW", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=100, y=50)
        ll = Label(f2, text="ENTER CORRECT DETAILS", bd=7, fg='crimson', font=('arial', 10, 'bold'),
                   bg="powder blue").place(x=350, y=50)
        entry1 = Entry(f2, text="ENTER YOUR ID BLOW", textvariable=id, bd=7, fg='crimson', font=('arial', 15),
                       bg="powder blue").place(x=100, y=80)

        cal = DateEntry(f2, bd=5, fg='crimson', bg="powder blue", year=2000, font=('times new roman', 15, 'bold'),
                        date_pattern='dd/MM/yyyy', textvariable=name, width=19, height=100).place(x=350, y=80)



        def data():
            i = id.get()
            n = name.get()
            if i=='':
                messagebox.showinfo('EMAIL UPDATE','ENTER THE ID FIRST')
            mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                           database='student_management')
            mycursor = mydb.cursor()
            n1 = "'" + n + "'"
            sql = f" update student set dob ={n1} where id ={i}"
            mycursor.execute(sql)
            messagebox.showinfo("UPDATE", "DATE OF BIRTH UPDATE SUCCESSFULLY")
            mydb.commit()

        bt = Button(f2, text="UPDATE", command=data, font=('arial', 15, 'bold'), bg="pink", fg="black").place(x=300,
                                                                                                              y=200)

#===============================frame=====================================================

ent1=StringVar()


f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f1.place(x=100,y=30,width=800,height=100)
f2=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f2.place(x=100,y=200,width=800,height=300)
cb=ttk.Combobox(f1,width=20,textvariable=ent1,value=('NAME','FATHER NAME','MOTHER NAME','MOBILE NO','EMAIL ID','GENDER','DATE OF BIRTH'),state='readonly',font=('arial',10)).grid(row=1,column=2,padx=20,pady=30)
l5=Label(f1, text="Choose What you Want to Update !", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,column=1,padx=20,pady=30)
bt=Button(f1,text="UPDATE",command=get,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=1,column=4,padx=20,pady=30)
#e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=ent0,font=('arial',15,'bold')).grid(row=1,column=3,padx=20,pady=30)
#================================================================================================================================


top.mainloop()


