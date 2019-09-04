from lmf.dbv2 import db_command


def create_table(loc="aliyun"):
    if loc == "aliyun" or loc is None:
        long_ip_conp = ['postgres', 'since2015', '192.168.4.201', 'postgres', 'public']
    elif loc == "kunming":
        long_ip_conp = ['postgres', 'since2015', '192.168.169.89', 'postgres', 'public']
    else:
        long_ip_conp = loc

    sql1 = """
    create table if not exists %s.long_ip_cfg
    (
    ip text,
    ExpireTime text,
    create_time text,
    info text,
    primary key(ip)
    )
    """ % (long_ip_conp[4])

    db_command(sql1, dbtype="postgresql", conp=long_ip_conp)
