import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_t_person():
    sql="""
    CREATE TABLE if not exists "public"."t_person" (
    "person_key" bigint primary key  ,
    "name" text COLLATE "default" NOT NULL,
    "zj_type" text COLLATE "default",
    "zjhm" text COLLATE "default" NOT NULL
    )
    distributed by (person_key)

    """

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_t_person():
    est_t_person()
    sql="""
    truncate public.t_person;
    insert into "public".t_person(person_key,   name,   zj_type,    zjhm)


    select * from "public".et_t_person 
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])