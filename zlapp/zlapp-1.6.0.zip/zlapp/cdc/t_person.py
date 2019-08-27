import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_t_person():
    sql="""
    CREATE TABLE if not exists "etl"."t_person" (
    "person_key" bigint primary key  ,
    "name" text COLLATE "default" NOT NULL,
    "zj_type" text COLLATE "default",
    "zjhm" text COLLATE "default" NOT NULL
    )
    distributed by (person_key)

    """

    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl'])



def et_t_person():
    sql="""
        drop external table if exists etl.et_t_person;
    create  external table etl.et_t_person(person_key bigint,    name text,  zj_type text,   zjhm  text )
        LOCATION ('pxf://public.t_person?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl'])



def update_t_person():
    et_t_person()
    est_t_person()
    sql="""
    truncate etl.t_person;
    insert into "etl".t_person(person_key,   name,   zj_type,    zjhm)


    select * from "etl".et_t_person 
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']

    db_command(sql,dbtype="postgresql",conp=conp)