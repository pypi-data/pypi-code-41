from lmf.dbv2 import db_write, db_command
import pandas as  pd
from collections import OrderedDict
from zlsrc.data import quyu_dict

from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN


def db(loc=None):
    if loc == "aliyun" or loc is None:
        conp = ['postgres', 'since2015', '192.168.4.201', 'postgres', 'public']
    elif loc == "kunming":
        conp = ['postgres', 'since2015', '192.168.169.89', 'postgres', 'public']
    else:
        conp = loc

    sql = """
    drop table if exists public.cfg;
    CREATE TABLE if not exists "public"."cfg" (
    "package" text,
    "quyu" text COLLATE "default", 
    "usr" text COLLATE "default" DEFAULT 'postgres'::text,
    "password" text COLLATE "default" DEFAULT 'since2015'::text,
    "host" text COLLATE "default",
    "db" text COLLATE "default",
    "schema" text COLLATE "default",
    "total" int4,
    "num" int4,
    "cdc_total" int4,
    "html_total" int4,
    "headless" boolean ,
    "pageloadstrategy" text COLLATE "default",
    "pageloadtimeout" int4,
    "ipNum" int4,
    "thread_retry" int4,
    "retry" int4,
    "add_ip_flag" boolean,
    "page_retry" int4,
    "image_show_gg" int4,
    "image_show_html" int4,
    "get_ip_url" text,
    "long_ip_url" text,
    "long_ip_num" int4,
    "long_ip" boolean,
    "info" text,

    primary key(quyu)
    )
    """
    db_command(sql, dbtype="postgresql", conp=conp)


def dbdata(host_dict):
    DB_A = ['anhui', 'beijing', 'chongqing', 'fujian', 'gansu', 'guangdong', 'guangxi', 'guizhou', 'hainan', 'hebei',
            'heilongjiang']
    DB_B = ['henan', 'hubei', 'hunan', 'jiangsu', 'jiangxi', 'jilin', 'liaoning']
    DB_C = ['neimenggu', 'ningxia', 'qinghai', 'shandong', 'shanghai', 'shanxi', 'shanxi1', 'sichuan', 'tianjin',
            'xinjiang', 'xizang', 'yunnan', 'zhejiang']
    DB_D = ['zlcommon', 'zlshenpi', 'zlsys', 'zljianzhu','yszz']

    all_quyus_dict = OrderedDict([("DB_A", DB_A), ("DB_B", DB_B), ("DB_C", DB_C), ("DB_D", DB_D)])

    data = []
    for k in all_quyus_dict.keys():

        quyus = []
        for sheng in all_quyus_dict[k]:
            tmp = quyu_dict[sheng]
            tmp = list(set(tmp))
            tmp.sort()
            quyus.extend(tmp)

        for quyu in quyus:
            db, schema = quyu.split("_")[0], quyu

            if "zljianzhu" in quyu:
                db, schema = "zljianzhu", "zljianzhu"

            tmp = ['zlsrc', quyu, 'postgres', 'since2015', host_dict[k], db, schema, None, None, 5, None, True,
                   'normal', 40, 5, 7, 10, False, 5, 2, 1, None, None, 20, False, None]
            data.append(tmp)

    columns = ['package', 'quyu', 'usr', 'password', 'host', 'db', 'schema', 'total', 'num', 'cdc_total', 'html_total',
               'headless', 'pageloadstrategy', 'pageloadtimeout', 'ipNum', 'thread_retry', 'retry', 'add_ip_flag',
               'page_retry',
               'image_show_gg', 'image_show_html', 'get_ip_url', "long_ip_url", "long_ip_num", "long_ip", 'info']

    df = pd.DataFrame(data=data, columns=columns)
    return df


def get_hosts(loc=None):
    if loc == "aliyun" or loc is None:
        conp = ['postgres', 'since2015', '192.168.4.201', 'postgres', 'public']
    elif loc == "kunming":
        conp = ['postgres', 'since2015', '192.168.169.89', 'postgres', 'public']
    else:
        conp = loc

    hosts_dict = {
        "192.168.4.201": {
            "DB_A": "192.168.4.198",
            "DB_B": "192.168.4.199",
            "DB_C": "192.168.4.200",
            "DB_D": "192.168.4.201"
        },
        "192.168.169.89": {
            "DB_A": "192.168.169.58",
            "DB_B": "192.168.169.59",
            "DB_C": "192.168.169.88",
            "DB_D": "192.168.169.89"
        }
    }
    host_dict = hosts_dict.get(conp[2])

    if host_dict == None:
        host_dict = {
            "DB_A": "127.0.0.1",
            "DB_B": "127.0.0.1",
            "DB_C": "127.0.0.1",
            "DB_D": "127.0.0.1"
        }
    return conp, host_dict


def todb(loc=None):
    conp1, hosts_dict = get_hosts(loc)
    df = dbdata(hosts_dict)

    db_write(df, 'cfg', dbtype="postgresql", if_exists='append', conp=conp1)


def append_db(loc=None):
    """
    增量更新 cfg 表
    :param conp:
    :return:
    """
    conp1, host_dict = get_hosts(loc)
    df = dbdata(host_dict)
    datadict = {"bd_key": BIGINT(), 'total': BIGINT(), 'num': BIGINT(), 'cdc_total': BIGINT(), 'html_total': BIGINT(),
                'pageloadtimeout': BIGINT(), 'ipNum': BIGINT(), 'thread_retry': BIGINT(), 'retry': BIGINT(),
                'add_ip_flag': BOOLEAN(), 'page_retry': BIGINT(), 'image_show_gg': BIGINT(),
                'image_show_html': BIGINT(),
                'long_ip_num': BIGINT(), "long_ip": BOOLEAN()}

    db_write(df, 'cfg_tmp', dbtype="postgresql", if_exists='replace', conp=conp1, datadict=datadict)

    sql = "insert into cfg select * from cfg_tmp where quyu not in(select quyu from cfg)"
    db_command(sql, dbtype="postgresql", conp=conp1)


def resetdb(loc=None):
    """
    重新生成 cfg 表
    :param loc: loc 区分代码环境位置 'aliyun' 'kunming' 'conp'
    :return:
    """
    db(loc)
    todb(loc)

# resetdb('kunming')

