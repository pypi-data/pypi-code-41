"""
2019.8.1 create by jun.hu
参数处理
"""
import json


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
