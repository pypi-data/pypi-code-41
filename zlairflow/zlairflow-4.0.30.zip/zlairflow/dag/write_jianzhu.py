import sys
import os
from zlairflow.dag.data import data_zljianzhu

def write_dag(quyu, dirname, loc="aliyun",pool="abc_a",**krg):
    para = {
        "tag": "cdc",
        "start_date": "(2019,7,26)",
        "cron": "0 0/12 * * *",
        "timeout": 'minutes=240',

    }
    para.update(krg)
    tag = para["tag"]
    start_date = para["start_date"]

    cron = para["cron"]

    timeout = para["timeout"]



    filename = "%s_f.py" % quyu
    path1 = os.path.join(os.path.dirname(__file__), 'template', 'zljianzhu.txt')
    path2 = os.path.join(dirname, filename)

    with open(path1, 'r', encoding='utf8') as f:
        content = f.read()

    # from ##zlsrc.anqing## import ##task_anqing##

    content = content.replace("##task_anqing##", quyu)

    # tag='##cdc##'
    # datetime##(2019,4,27)##, }

    content = content.replace("##cdc##", tag)

    if 'flag' in krg.keys():
        flag=krg['flag']
        content = content.replace("##flag##", str(flag))
    else:
        content = content.replace('"flag":"##flag##"', '')

    if 'regions_index' in krg.keys():
        regions_index = krg['regions_index']
        content = content.replace("##regions_index##", str(regions_index))
    else:
        content = content.replace('"regions_index":"##regions_index##"', '')

    if 'delta' in krg.keys():
        delta=krg['delta']
        content = content.replace("##24##", str(delta))
    else:
        content = content.replace('+timedelta(hours=##24##)', '')


    content = content.replace("##(2019,1,1)##", start_date)

    content = content.replace("##quyuName##", "%s" % quyu)

    content = content.replace("##kunming##", "%s" % loc)

    content = content.replace("##0 0/12 * * *##", cron)
    content = content.replace("##abc_a##", pool)

    content = content.replace("##anqing_a1##", "%s_a1" % quyu)

    content = content.replace("##minutes=60##", timeout)

    content = content.replace("##anqing_b1##", "%s_b1" % quyu)

    content = content.replace("##anhui_anqing##", quyu)

    with open(path2, 'w', encoding='utf-8') as f:
        f.write(content)


# write_dag('anhui_bozhou',sys.path[0])



def write_dags_zljianzhu_gg(dirname, loc="aliyun",pool="abc_a7",regions_index="[0,3]", **krg):
    for w in data_zljianzhu.para[-8:]:

        quyu = w[0]
        timeout = w[1]
        krg.update({"timeout": timeout})
        regions_index1=quyu.split('_')[2]
        regions_index2=quyu.split('_')[3]
        regions_index="[%s,%s]"%(regions_index1,regions_index2)

        write_dag(quyu, dirname, loc,pool=pool,regions_index=regions_index, **krg)


def write_dags_zljianzhu_html(dirname, loc="aliyun",pool="abc_a7",daydelta=10, **krg):
    count = 1
    for w in data_zljianzhu.para[:-8]:
        quyu=w[0]
        flag=w[0].rsplit('_',maxsplit=1)[1]
        timeout = w[1]
        krg.update({"timeout": timeout})
        delta=(daydelta*24//15)*count
        count += 1
        write_dag(quyu, dirname, loc,pool=pool,delta=delta,flag=flag, **krg)




# write_dag('guandong_dongguan',r'C:\Users\jacky\Desktop\zhulongall\zlairflow\zlairflow\data',start_date='(2019,6,17)',tiemout='minutes=120')