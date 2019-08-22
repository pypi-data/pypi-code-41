import json
import traceback

from zlparse.parse_time.common import *
from zlparse.parse_time.conf import *
from zlparse.parse_time.exec_func_f import exec_func


# exec_func = {
#     'extimefbsj': extimefbsj,
#     'extime_xxsj': extime_xxsj,
#     'strptime_transfrom_yunan': strptime_transfrom_yunan,
#     'strptime_transfrom_yue_r_n': strptime_transfrom_yue_r_n,
#     'extime': extime,
#     'extime_v2': extime_v2,
#     'extimefbsj_v2': extimefbsj_v2,
#     'extime_xxsj_v2': extime_xxsj_v2,
#     'strptime_transfromgg_guangdong_guangdongsheng': strptime_transfromgg_guangdong_guangdongsheng,
# }


def extime_all(page, ggstart_time, quyu, conp=False):
    if conp:
        methed = select(quyu, conp)
    else:
        o_path = os.path.dirname(__file__)
        file_path = os.path.join(o_path, 'quyu_time_func.json')
        with open(file_path, encoding='utf-8') as f:
            dict_a = json.load(f)
        methed = dict_a.get(quyu, None)
    ggstart_time = ext_from_ggtime(ggstart_time if ggstart_time is not None else '')
    if not methed or methed == []:
        res = ggstart_time
    else:
        if methed == 'None':
            res = None
        else:
            res = exec_func[methed](ggstart_time, page)
    res = ext_from_ggtime(res if res is not None else '')
    if not res: return None
    page_time = pd.to_datetime(res, format='%Y-%m-%d', errors='ignore')
    curent_time = pd.to_datetime(datetime.datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d', errors='ignore')

    if not isinstance(page_time, str):
        if page_time <= curent_time:

            return page_time
        else:
            return None
    else:

        page_time = pd.to_datetime(res[:-1], format='%Y-%m-%d', errors='ignore')
        if isinstance(page_time, str):
            print('%s 仍为不规范日期。返回 None' % res)
            return None
            # raise ValueError('page_time still is Class "str".')
        if page_time <= curent_time:
            return ext_from_ggtime(res[:-1])
        else:
            return None


if __name__ == '__main__':
    '''
    时间解析函数主入口：
    extime_all(page, ggstart_time, quyu, conp=False)
    如果有传conp参数则读取数据库中的数据，否则读本地json文件。
    '''

    conp = ["postgres", "since2015", "192.168.3.171", "anbang", "parse_project_code"]

    # file_to_db(conp)
    # insert('xinjiang_atushi_gcjs111111','xxxxxxxxxxxxxxwerwerx',conp)
    # with open('quyu_time_func.json', encoding='utf-8') as f:
    # cotent_json = json.load(f)
    print(extime_all('20', '2017-04-00', 'xxxxx'))

