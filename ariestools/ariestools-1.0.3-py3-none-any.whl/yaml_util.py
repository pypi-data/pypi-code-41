import yaml


def load_yaml(path):
    """
    读取一个yaml文件
    :param path: 文件路径
    :return:
    """
    with open(path, encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def write_yaml(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)
