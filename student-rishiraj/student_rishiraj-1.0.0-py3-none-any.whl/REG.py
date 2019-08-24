from tkinter import *
import mysql.connector
from tkinter import messagebox
from tkcalendar import DateEntry
top=Tk()
top.title('Resitration Form')
top.geometry('1200x700+0+0')
#===============================sql conectivity============================
def data():
    name1=name.get()
    fname1=fname.get()
    mname1=mname.get()
    mn1=(int)(mn.get())
    dob1=dob.get()
    email1=email.get()
    gen1=gen.get()
    #print(dob1)
    #print(name1,fname1,mname1,mn1,email1,gen1)

#l2 = Label(f3, text=('hello'+name1), bd=14, fg='crimson', bg="powder blue", font=('times new roman', 15)).grid(row=1,columnspan=1,pady=4, padx=10)
#================================== CREATE DATABASE ===========================================
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou')
    mycursor = mydb.cursor()
    mycursor.execute('CREATE DATABASE IF NOT EXISTS student_management')
# ============================================CREATE TABLE ==============================================================
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',database='student_management')
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS student(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,STUDENT_ID VARCHAR(20), NAME varchar(30),FATHER_NAME varchar(30),MOTHER_NAME varchar(30),MOBILE_NO BIGINT(12),EMAIL_ID varchar(50), GENDER varchar(10),DOB varchar(10))")
    mycursor.execute("ALTER TABLE student AUTO_INCREMENT=019787000")
#====================================execute value in table===================================================================
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',
                                   database='student_management')
    mycursor = mydb.cursor()
    sqlform = (
                "insert into student (NAME,FATHER_NAME,MOTHER_NAME,MOBILE_NO,EMAIL_ID,GENDER,DOB) values('%s','%s','%s','%s','%s','%s','%s')" % (name1,fname1,mname1,mn1,email1,gen1,dob1))

    mycursor.execute(sqlform)
    mydb.commit()
    messagebox.showinfo("Registration", 'YOUR DATA IS SUCCESSFULLY REGISTERED')
#========================================get id and generate student id ====================================================
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',database='student_management')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id FROM student ORDER BY id DESC LIMIT 1")
    l = mycursor.fetchone()
    s=str(l)
    s=s[:-2]
    s=s[1:]
    #print(s)
    l2 = Label(f3, text=("STUDENT ID: MMH" + s), bd=14, fg='crimson', bg="powder blue", font=('times new roman', 15)).grid(row=1,columnspan=1,pady=4, padx=10)
    l1 = Label(f3, text=("SR No.:" + s), bd=14, fg='crimson', bg="powder blue",
               font=('times new roman', 15)).grid(row=2, columnspan=1, pady=4, padx=10)

    #=============================================update student id=============================================================
    mydb = mysql.connector.connect(host="localhost", user='rishiraj', password='iloveyou',database='student_management')
    mycursor = mydb.cursor()
    st = "MMH" + s
    f="update student set STUDENT_ID=%s where id=%s"
    val=(st,s)
    mycursor.execute(f,val)
    mydb.commit()

#==========================variable diclearation==================
name=StringVar()
fname=StringVar()
mname=StringVar()
mn=StringVar()
email=StringVar()
gen=StringVar()
dob=StringVar()


#=====================heading==============================
label=Label(top,text='STUDENT  MANAGEMENT  SYSTEM',font=('arial',34,'bold'),bd=5,fg="blue",bg="powder blue")
label.grid(row=0,column=0,pady=40,padx=40)
#=================================frame===================
f1=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f1.place(x=50,y=150,width=500,height=500)
f2=Frame(f1,bg="powder blue",bd=5)
f2.place(x=240,y=270,width=200,height=50)
f3=Frame(top,bg="powder blue",bd=5,relief=RIDGE)
f3.place(x=600,y=150,width=450,height=500)
   #======================lable=============================
l1=Label(f1, text="NAME                     :",bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=0,columnspan=1,pady=4,padx=10)
l2=Label(f1, text="FATHER'S NAME :",bd=14,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=1,columnspan=1,pady=4,padx=10)
l3=Label(f1, text="MOTHER'S NAME :",bd=14,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=2,columnspan=1,pady=4,padx=10)
l4=Label(f1, text="MOBILE No.             :" ,bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=3,columnspan=1,pady=4,padx=10)
l5=Label(f1, text="EMAIL-ID                 :", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=4,columnspan=1,pady=4,padx=10)
l5=Label(f1, text="GENDER                   :", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=5,columnspan=1,pady=4,padx=10)
l5=Label(f1, text="DATE OF BIRTH     :", bd=7,fg='crimson',bg="powder blue",font=('times new roman',15,'bold')).grid(row=6,columnspan=1,pady=4,padx=10)


#=====================================text box =============================

e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=name,font=('times new roman',15,'bold')).grid(row=0,column=1,pady=4,padx=10)
e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=fname,font=('times new roman',15,'bold')).grid(row=1,column=1,pady=4,padx=10)
e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=mname,font=('times new roman',15,'bold')).grid(row=2,column=1,pady=4,padx=10)
e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=mn,font=('times new roman',15,'bold')).grid(row=3,column=1,pady=4,padx=10)
e1=Entry(f1,bd=5,fg='crimson',bg="powder blue",textvariable=email,font=('times new roman',15,'bold')).grid(row=4,column=1,pady=4,padx=10)
cal=DateEntry(f1,bd=5,fg='crimson',bg="powder blue",year=2000,font=('times new roman',15,'bold'),date_pattern='dd/MM/yyyy',textvariable=dob,width=19,height=100).grid(row=6,column=1,pady=4,padx=0)
#====================================bOTTOM========================

Radiobutton(f2,text='Male',value='Male',bg="powder blue",variable=gen).grid(row=5,column=0,pady=4,padx=10)
Radiobutton(f2,text='Female',value='Female',bg="powder blue",variable=gen).grid(row=5,column=1,pady=4,padx=10)
bt=Button(f1,text="Submit",font=('arial',25,'bold'),bg="pink",fg="black",command=data)
bt.place(x=180,y=400,width=150,height=50)


l1=Label(f3, text="               NOTE THE INFO",bd=7,fg='crimson',bg="powder blue",font=('times new roman',20,'bold')).grid(row=0,columnspan=1,pady=4,padx=10)

top.mainloop()