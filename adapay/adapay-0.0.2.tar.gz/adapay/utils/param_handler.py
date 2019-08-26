"""
2019.8.1 create by jun.hu
参数处理
"""
import json

from adapay.adapay_obj import AdapayObject


def get_plain_text(all_params):
    temp_list = list()
    for (k, v) in sorted(all_params.items()):
        if not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        if not v:
            continue
        temp_list.append('{}={}'.format(str(k), str(v)))
    plain_text = '&'.join(temp_list)
    return plain_text


def read_pem(file_path):
    with open(file_path, 'r') as f:
        return f.read()


OBJECT_CLASSES = {}


def load_object_classes():
    from adapay import api

    global OBJECT_CLASSES

    OBJECT_CLASSES = {
        api.Charge.OBJECT_NAME: api.Charge,
        api.Refund.OBJECT_NAME: api.Refund
    }


def parse_to_adapay_object(info_obj):
    """
    将服务端返回的对象转为 adapay 业务类对象
    :return:
    """
    global OBJECT_CLASSES
    if len(OBJECT_CLASSES) == 0:
        load_object_classes()

    class_types = OBJECT_CLASSES.copy()

    if isinstance(info_obj, list):

        return [parse_to_adapay_object(i) for i in info_obj]
    elif isinstance(info_obj, dict):
        info_obj = info_obj.copy()
        class_name = info_obj.get('object')
        if isinstance(class_name, str):
            klass = class_types.get(class_name, AdapayObject)
        else:
            klass = AdapayObject

        return klass.construct_from(info_obj)
    else:
        return info_obj
