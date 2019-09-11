import json as js


def load_json(json_file_path):
    """
    读取json文件转dict or list(dict)
    :param json_file_path:
    :return:
    """
    with open(json_file_path, encoding='utf-8', mode='r') as f:
        return js.load(f, encoding='utf-8')
