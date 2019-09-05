#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import pymysql
import sqlite3
import requests
from datetime import datetime

class mysqldb():
    def __init__(self,host='',port=3306,db='',user='',passwd='',charset='utf8'):
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd,charset=charset)
        self.cur = self.conn.cursor(cursor = pymysql.cursors.DictCursor)
            
    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

class sqlite(object):
    def __init__(self,sqlcmd,db_name,type='select'):
        self.sqlcmd = sqlcmd
        self.db_name = db_name

    def run(self):
        return self.sqlcommit()

    def sqlcommit(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            sqlex=cursor.execute(self.sqlcmd)
            sqlrc=cursor.rowcount
            sqlfa=cursor.fetchmany(200)
            cursor.close()
            conn.commit()
            conn.close()
            if self.sqlcmd.split(" ")[0]=='select':
                return sqlfa
            else:
                return sqlrc
        except Exception as error:
            return "sqlite数据库执行发生错误:"+str(error)

def  mysqlex(sqlcmd,host='',port=3306,db='',user='',passwd='',charset='utf8',args=[]):
    if host =='':
        with mysqldb() as db:
            try:
                if args!=[]:
                    db.executemany(sqlcmd,args)
                else:
                    db.execute(sqlcmd)
                if sqlcmd.split(" ")[0]=="select":
                    return db.fetchall()
                else:
                    return db.rowcount
            except Exception as error:
                return "mysql数据库执行发生错误:"+str(error)
    else:
        with mysqldb(host,port,db,user,passwd,charset) as db:
            try:
                if args!=[]:
                    db.executemany(sqlcmd,args)
                else:
                    db.execute(sqlcmd)
                if sqlcmd.split(" ")[0]=="select":
                    return db.fetchall()
                else:
                    return db.rowcount
            except Exception as error:
                return "mysql数据库执行发生错误:"+str(error)

def sendmsg(msgtitle='',msgtext=''):
    url='http://msg.mtoo.xyz/sendmsg'
    data="msgtitle="+str(msgtitle)+"&msgtext="+str(msgtext)
    r=requests.post(url,params=data,timeout=5) 
    return r.text

def mprint(string):
    print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+" "+str(string))

def formatcookie(MyCok):
    return eval('{"'+MyCok.replace('=','":"').replace(';','","').replace('":"":"','==').replace(" ","")+'"}')

def writestr(Str,File="./temp.log"):
    with open(File, 'a') as File:
        File.write(Str+"\n")
        print ("写入完成！")
    
def randomagent(UserAgentList):
    return UserAgentList[int(random.random()*len(UserAgentList))]

def timestamp(type=0):
    thistime=time.time()
    if type==0:
        return int(thistime)
    else:
        return int(round(thistime * 1000))