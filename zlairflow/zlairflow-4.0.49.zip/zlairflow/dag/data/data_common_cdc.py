from collections import defaultdict
from pprint import pprint



para_dict={

 'fujian_nanan_ggzy':'minutes=360',
 'guangdong_guangdongsheng_1_zfcg':'minutes=480',
 'guangdong_zhanjiang_zfcg':'minutes=300',
 'zhejiang_hangzhou_gcjs':'minutes=480',
 'qycg_b2b_10086_cn':'minutes=480',

}




DB_A=['anhui','beijing','chongqing','fujian','gansu','guangdong','guangxi','guizhou','hainan','hebei','heilongjiang']
DB_B=['henan','hubei','hunan','jiangsu','jiangxi','jilin','liaoning']
DB_C=['neimenggu','ningxia','qinghai','shandong','shanghai','shanxi','shanxi1','sichuan','tianjin','xinjiang','xizang','yunnan','zhejiang']
DB_D=['zlcommon']

get_data_source = """

            
"""



def get_para(db_type,data_cdc_mode):
    """
    获取一个
    :param db_type:
    :param data_cdc_mode:
    :return:
    """
    get_data_source="from zlsrc.$$data$$ import quyu_dict as _quyu_dict_"
    get_data_str = get_data_source.replace("$$data$$", data_cdc_mode)
    exec(get_data_str)
    quyu_dict=locals().get("_quyu_dict_")

    para = []
    for sheng in db_type:
        quyu_list = quyu_dict.get(sheng)

        if quyu_list:
            for quyu in quyu_list:
                timeout = para_dict.get(quyu)
                if timeout:
                    quyu_cfg = [quyu, timeout]
                else:
                    quyu_cfg = [quyu, "minutes=240"]
                para.append(quyu_cfg)
    return para








