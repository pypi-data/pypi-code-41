import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC,TSVECTOR



def gg_all(conp_pg):
    sql="select * from etl.gg_all limit 5"
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    datadict={"html_key":BIGINT(),
    "price":NUMERIC(),'bd_key':BIGINT(),'fa_butime':TIMESTAMP(),'create_time':TIMESTAMP(),'ts_tile':TEXT()}
    def f(df):
        df['fabu_time']=df['fabu_time'].map(lambda x:x if str(x)<'2050-01-01' and str(x)>'1900-01-01' else '2050-01-01')
        return df 
    pg2pg(sql,'gg',conp_hawq,conp_pg,f=f,chunksize=10000,datadict=datadict)


#gg_all(['gpadmin','since2015','192.168.4.206','postgres','public'])