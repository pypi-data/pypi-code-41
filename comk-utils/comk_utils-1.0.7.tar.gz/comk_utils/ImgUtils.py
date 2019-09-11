import base64


def img_bytes_to_str(img_bytes):
    """
    将图片的bytes数据，转换为base64编码的字符串

    :param img_bytes:
    :return:
    """
    return base64.b64encode(img_bytes).decode('utf-8')  # 图片文件应该设置好格式


def img_str_to_bytes(img_str):
    """
    将图片的base64编码的字符串，转换为bytes数据


    :param img_str:
    :return:
    """
    return base64.b64decode(img_str)


def img_str_to_src_format(img_str):
    """
    将img的base64编码的字符串，增加数据，变为前端可以直接展示的src型字符串

    :param img_str:
    :return:
    """
    return 'data:image/jpeg;base64,' + img_str


def img_src_format_to_str(img_src_format):
    """
    src型字符串，去掉数据，变为纯粹的img的base64编码的字符串

    :param img_src_format:
    :return:
    """
    return img_src_format.replace('data:image/jpeg;base64,', '')
