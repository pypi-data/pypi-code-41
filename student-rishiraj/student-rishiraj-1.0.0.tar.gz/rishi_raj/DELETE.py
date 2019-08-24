def de():

    from tkinter import *
    import tkinter as tk
    import mysql.connector
    from tkinter import messagebox
    from tkinter.messagebox import *
    from tkcalendar import DateEntry
    from tkinter import ttk
    top=Tk()
    top.title('Delete')
    top.geometry('1000x250+200+50')
    def get():
        e0=ent0.get()
        mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                       database='student_management')
        mycursor = mydb.cursor()
        x=(askokcancel("DELETE DATA", f"ARE YOU SURE TO DELETE DATA OF ID={e0}"))
        if x==True:
            sql = f"delete from student where id ={e0}"
            mycursor.execute(sql)
            messagebox.showinfo("DELETE", "DATA DELETE SUCCESSFULLY")
            mydb.commit()
            e1.delete(0, 'end')

        else:
            messagebox.showinfo("DELETE", "DATA CAN BE DELETE")






    ent0=StringVar()

    f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
    f1.place(x=100,y=30,width=800,height=100)
    #cb=ttk.Combobox(f1,width=20,textvariable=ent1,value=('ID','NAME'),state='readonly',font=('arial',10)).grid(row=1,column=2,padx=20,pady=30)
    l5=Label(f1, text="DELETE  BY  ID  ONLY :", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,column=1,padx=20,pady=30)
    bt=Button(f1,text="DELETE",command=get,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=1,column=4,padx=20,pady=30)
    e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=ent0,font=('arial',15,'bold')).grid(row=1,column=3,padx=20,pady=30)
    top.mainloop()