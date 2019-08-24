from tkinter import *
import tkinter as tk
import mysql.connector
from tkinter import messagebox
from tkcalendar import DateEntry
from tkinter import ttk
top=Tk()
top.title('SEARCH')
top.geometry('1000x550+200+50')
#===============================================database conectivity===========================================
def get():
    e1=ent1.get()
    e0=ent0.get()


    if e1=="NAME":
        v=[]
        mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                       database='student_management')
        mycursor = mydb.cursor()
        e3="'"+ e0 +"'"
        sql=f"SELECT * FROM student where NAME={e3}"
        mycursor.execute(sql)
        l = mycursor.fetchall()
        for i in l:
            tree.insert('', 0, text="L1", values=(i))

    else:
        mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',database='student_management')
        mycursor = mydb.cursor()
        sql = f"SELECT * FROM student where id={e0}"
        mycursor.execute(sql)
        l = mycursor.fetchall()
        for i in l:
            tree.insert('', 0, text="L1", values=(i))



#===============================frame=====================================================
ent0=StringVar()
ent1=StringVar()


f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f1.place(x=100,y=30,width=800,height=100)
f2=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f2.place(x=100,y=200,width=800,height=300)
cb=ttk.Combobox(f1,width=20,textvariable=ent1,value=('ID','NAME'),state='readonly',font=('arial',10)).grid(row=1,column=2,padx=20,pady=30)
l5=Label(f1, text="SEARCH BY :", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,column=1,padx=20,pady=30)
bt=Button(f1,text="SEARCH",command=get,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=1,column=4,padx=20,pady=30)
#bt=Button(top,text="SEARCH",command=clear,font=('arial',15,'bold'),bg="pink",fg="black").grid(row=1,column=5,padx=20,pady=30)
e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=ent0,font=('arial',15,'bold')).grid(row=1,column=3,padx=20,pady=30)
#================================================================================================================================
tree=ttk.Treeview(f2,height=200,columns=('id','student id','name','father name','mother name','mobile no','email id','gender','dob'))

sx_x=ttk.Scrollbar(f2, orient=HORIZONTAL,command=tree.xview,).pack(side=BOTTOM,fill=X,)
sy_y=ttk.Scrollbar(f2, orient=VERTICAL,command=tree.yview).place(x=770+30+3,y=23,width=20,height=230+20)#.grid(row=5,column=5,sticky='ns')#.pack(side=RIGHT,fill=Y,)
# show1.configure(xscrollcommand=sx_x.set)
# show1.configure(yscrollcommand=sy_y.set)

# tree = ttk.Treeview(f2, columns=('id','student id','name','dob','father name','mother name','mobile no','email id','gender'),selectmode='browse')
# tree.place(x=30, y=95)
#
# vsb = ttk.Scrollbar(f2, orient="vertical", command=tree.xview)
# vsb.pack(side=BOTTOM,fill=Y)

tree.column("id", width=100)
tree.heading('id',text='ID')
tree.heading('student id',text='STUDENT ID')
tree.column("student id", width=100, anchor='c')
tree.heading('name',text='NAME')
tree.column("name", width=100, anchor='c')
tree.heading('dob',text='D.O.B')
tree.column("dob", width=100, anchor='c')
tree.heading('father name',text='FATHER NAME')
tree.column("father name", width=120, anchor='c')
tree.heading('mother name',text='MOTHER NAME')
tree.column("mother name", width=120, anchor='c')
tree.heading('mobile no',text='MOBILE NO')
tree.column("mobile no", width=100, anchor='c')
tree.heading('email id',text='EMAIL-ID')
tree.column("email id", width=100, anchor='c')
tree.heading('gender',text='GENDER')
tree.column("gender", width=100, anchor='c')
tree['show']='headings'




tree.pack()

top.mainloop()


