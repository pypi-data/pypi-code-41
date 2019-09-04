from pprint import pprint

from lmf.dbv2 import db_query,db_command
from zlsrc.data import quyu_dict

def get_conp1(quyu,loc=None):

    if loc == "aliyun" or loc is None:
        conp = ['postgres', 'since2015', '192.168.4.201', 'postgres', 'public']
    elif loc == "kunming":
        conp = ['postgres', 'since2015', '192.168.169.89', 'postgres', 'public']
    else:
        conp=loc

    sql="select * from public.cfg where quyu ~ '^%s' limit 1"%(quyu)
    df=db_query(sql,dbtype="postgresql",conp=conp)

    conp1=[df.at[0,'usr'],df.at[0,'password'],df.at[0,'host'],df.at[0,'db'],'public']

    return conp1



def create_schema(quyu,loc):

    conp1=get_conp1(quyu,loc)
    if quyu=='qycg':
        schemas=[x for x in quyu_dict['zlcommon'] if x.startswith('qycg')]
    elif quyu == 'qg':
        schemas=[x for x in quyu_dict['zlcommon'] if x.startswith('qg')]
    elif quyu == 'daili':
        schemas = [x for x in quyu_dict['zlcommon'] if x.startswith('daili')]
    elif quyu == 'zljianzhu':
        schemas=['zljianzhu',]
    else:
        schemas=quyu_dict[quyu]

    print(schemas)

    for w in schemas:
        sql = "create schema if not exists %s"%w
        db_command(sql, dbtype="postgresql", conp=conp1)

def create_all_schema(loc):
    quyu_d=quyu_dict.copy()
    quyu_d.pop('zlcommon')
    ts={"qycg":1,"qg":1,"daili":1,"zljianzhu":1}
    quyu_d.update(ts)

    for quyu in quyu_d.keys():
        create_schema(quyu,loc)

    print('over')


def update_schema(quyu_list,loc, drop_html=False):
    '''
        :param schema_list: 一个包含多个schema的列表; list 格式
        :param drop_html: False 不删除gg_html;True 删除gg_html;just 只删除gg_html
        :return:
    '''
    conp1=get_conp1(quyu_list[0],loc)
    sql1 = '''select schemaname,tablename from pg_tables;'''
    tables = db_query(sql1, dbtype='postgresql', conp=conp1)
    for table in tables.values:

        if drop_html == 'just':
            if (table[0] in quyu_list) and ('gg_html' in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp1)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        elif not drop_html:

            if (table[0] in quyu_list) and ('gg_html' not in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp1)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        else:
            if table[0] in quyu_list:
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp1)
                print('已删除 %s.%s 表' % (table[0], table[1]))
    return 'over'




