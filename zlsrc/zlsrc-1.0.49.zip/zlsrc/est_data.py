import os
import json
from collections import OrderedDict
from pprint import pprint
from zlsrc.data_old import quyu_dict as quyu_dict_old

dir_path = os.path.dirname(__file__)


def get_quyu_dict_diqu():
    dir_list = os.listdir(dir_path)
    quyu_dict=OrderedDict()
    dir_delete_list = ['zlshenpi', 'zljianzhu', 'zlcommon','zlsys', 'lib', 'util','beifenwenjian']
    file_delete_list = ['__init__.py', 'yzm_model.m']

    ndir_list = [x for x in dir_list if x not in dir_delete_list and os.path.isdir(os.path.join(dir_path,x))]

    for d in ndir_list:
        ndir = os.path.join(dir_path, d)
        file_list = os.listdir(ndir)
        nfile_list = [x for x in file_list if x not in file_delete_list]
        nfile_list = [x for x in nfile_list if x.endswith('.py')]
        fileList = [x.split('.py')[0] for x in nfile_list]
        quyu_dict[d]=fileList

    return quyu_dict


def get_quyu_dict_zlcommon():
    zlcommon_dir = os.path.join(dir_path, 'zlcommon')
    file_list = os.listdir(zlcommon_dir)
    quyu_dict=OrderedDict()
    file_delete_list = ['__init__.py']

    nfile_list = [x for x in file_list if x not in file_delete_list]
    nfile_list = [x for x in nfile_list if x.endswith('.py')]

    fileList = [x.split('.py')[0] for x in nfile_list]

    quyu_dict['zlcommon']=fileList
    return quyu_dict

def get_quyu_dict_zlshenpi():
    zlcommon_dir = os.path.join(dir_path, 'zlshenpi')
    file_list = os.listdir(zlcommon_dir)
    quyu_dict=OrderedDict()
    file_delete_list = ['__init__.py','default_path.txt','util_qgsp']

    nfile_list = [x for x in file_list if x not in file_delete_list]
    nfile_list = [x for x in nfile_list if x.endswith('.py')]

    fileList = [x.split('.py')[0] for x in nfile_list]

    quyu_dict['zlshenpi']=fileList
    return quyu_dict


def get_quyu_dict_zlsys():
    zlcommon_dir = os.path.join(dir_path, 'zlsys')
    file_list = os.listdir(zlcommon_dir)
    quyu_dict=OrderedDict()
    file_delete_list = ['__init__.py','db_task.py','download.py','src.py','t_gg.py','tohawq.py']

    nfile_list = [x for x in file_list if x not in file_delete_list]
    nfile_list = [x for x in nfile_list if x.endswith('.py')]

    fileList = [x.split('.py')[0] for x in nfile_list]

    quyu_dict['zlsys']=fileList
    return quyu_dict

def get_quyu_dict_zljianzhu():

    quyu_dict=OrderedDict()
    file_list=['zljianzhu_qiyexx','zljianzhu_renyuanxx','zljianzhu_xiangmuxx']
    fileList=[]
    for w in file_list:
        for flag in [0,1,2,3,4]:
            quyu='_'.join([w,str(flag)])
            fileList.append(quyu)
    fileList.append('zljianzhu_gg')
    quyu_dict['zljianzhu']=fileList
    return quyu_dict

def get_new_quyu_dict():
    quyu_dict=OrderedDict()

    diqu_dict=get_quyu_dict_diqu()
    common_dict=get_quyu_dict_zlcommon()
    shenpi_dict=get_quyu_dict_zlshenpi()
    sys_dict=get_quyu_dict_zlsys()
    jianzhu_dict=get_quyu_dict_zljianzhu()

    quyu_dict.update(diqu_dict)
    quyu_dict.update(common_dict)
    quyu_dict.update(shenpi_dict)
    quyu_dict.update(sys_dict)
    quyu_dict.update(jianzhu_dict)

    return quyu_dict


def get_cdc_data_dict():
    quyu_dict = OrderedDict()
    quyu_dict_new=get_new_quyu_dict()

    for quyu in quyu_dict_new.keys():
        quyu_list_new=quyu_dict_new.get(quyu)
        quyu_list_old=quyu_dict_old.get(quyu)

        quyu_list_cdc=set(quyu_list_new).difference(set(quyu_list_old))
        if quyu_list_cdc :
            quyu_dict[quyu]=quyu_list_cdc

    return quyu_dict

def create_data(quyu_dict,filename):

    h="quyu_dict={\n"
    ed="\n}"
    # shengs=list(quyu_dict.keys())
    # shengs.sort()

    sheng_union=[]
    for sf in quyu_dict.keys():
        sheng_prt1="""   "%s":[\n"""%sf
        sheng_prt2=',\n'.join(['''      "%s"'''%shi for shi in quyu_dict[sf]])+'\n   ]'
        sheng=sheng_prt1+sheng_prt2
        sheng_union.append(sheng)

    result=h+',\n'.join(sheng_union)+ed

    quyu_dict_str=result

    data_path=os.path.join(dir_path,filename)

    with open(data_path,'w',encoding='utf8') as f:
        f.write(quyu_dict_str)





def create_data_all():
    quyu_dict1=get_new_quyu_dict()
    create_data(quyu_dict1,filename='data.py')

def create_data_cdc():
    quyu_dict1=get_cdc_data_dict()
    create_data(quyu_dict1,filename='data_cdc.py')


# create_data_all()




