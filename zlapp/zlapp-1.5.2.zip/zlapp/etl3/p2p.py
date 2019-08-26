import os 
from lmf.dbv2 import db_command ,db_query

#os.system("ipconfig")
def tb_dmp(tbname):
    os.system("(set PGPASSWORD=since2015) & d:\\postgresql\\data1\\bin\\pg_dump.exe -U postgres -d bid -t public.%s -F c -f D:\\webroot\\bstdata\\biaost\\%s.dmp  "%(tbname,tbname))
    conp=['postgres','since2015','192.168.4.207','biaost','public']
    sql="drop table if exists public.%s;"%tbname
    db_command(sql,dbtype="postgresql",conp=conp)
    os.system("(set PGPASSWORD=since2015) & d:\\postgresql\\data1\\bin\\pg_restore.exe -U postgres -d biaost -h 192.168.4.207 D:\\webroot\\bstdata\\biaost\\%s.dmp  "%tbname)

def tb_all():
    tbnames=['bd','bd_dt','qy_zz','qy_zcry','qy_base','qy_zhongbiao','gg_zhongbiao'
    ,'t_person','t_bd_xflv','t_gg_ent_bridge'
    ,'app_gg_zhongbiao','app_qy_zz','app_qy_zcry'
    ,'gg','gg_html']
    for tbname in tbnames[:-2]:
        print(tbname)
        tb_dmp(tbname)




def tb1(tbname):
    os.system("(set PGPASSWORD=since2015) & d:\\postgresql\\data1\\bin\\pg_dump.exe -U postgres -d biaost -h 192.168.4.174 -t public.%s -F c -f D:\\webroot\\bstdata\\biaost\\%s.dmp  "%(tbname,tbname))
    conp=['postgres','since2015','192.168.4.207','biaost','public']
    sql="drop table if exists public.%s;"%tbname
    db_command(sql,dbtype="postgresql",conp=conp)
    os.system("(set PGPASSWORD=since2015) & d:\\postgresql\\data1\\bin\\pg_restore.exe -U postgres -d biaost -h 192.168.4.207 D:\\webroot\\bstdata\\biaost\\%s.dmp  "%tbname)


def tb_sys():
    conp=['postgres','since2015','192.168.4.174','biaost','public']
    sql="""
    select tablename from pg_tables where schemaname='public' and tablename~'^lmbj|^sys|^xxgl'

    order by tablename"""

    df=db_query(sql,dbtype="postgresql",conp=conp)

    arr=df['tablename']
    for table  in arr:
        print(table)
        tb1(table)



def tb2_dmp(tbname):
    os.system("""(set PGPASSWORD=since2015) & d:\\postgresql\\data1\\bin\\pg_dump.exe -U postgres -d biaost -h 192.168.4.207 -t public.%s -F c -f D:\\webroot\\bstdata\\biaost\\%s.dmp  """%(tbname,tbname))

def tb2_all():
    tbnames=['bd','bd_dt','qy_zz','qy_zcry','qy_base','qy_zhongbiao','gg_zhongbiao'
    ,'t_person','t_bd_xflv','t_gg_ent_bridge'
    ,'app_gg_zhongbiao','app_qy_zz','app_qy_zcry'
    #,'gg','gg_html'
    ]
    for tbname in tbnames:
        print(tbname)
        tb2_dmp(tbname)
