import re

ul_pattern =  '</?ul.*?>'
span_pattern = '</?span.*?>'
li_pattern = '</?li.*?>'
p_pattern = '</?p.*?>'
label_pattern = '<.*?>'
space_pattern = r'\s+'

def clear_html(src):
    '''
    正则清除HTML标签
    :param src_html:原文本
    :return: 清除后的文本
    '''
    content = re.sub(label_pattern, "", src) # 去除标签
    # content = re.sub(r"&nbsp;", "", content)
    dst = re.sub(space_pattern, "", content)  # 去除空白字符
    return dst

def clear_ul(src):
    return re.sub(ul_pattern, '', src)

def clear_span(src):
    return re.sub(span_pattern, '', src)

def clear_li(src):
    return re.sub(li_pattern, '', src)

def clear_p(src):
    return re.sub(p_pattern, '', src)

def clear_space(src):
    return re.sub(space_pattern, '', src)

def clear_label(src):
    return re.sub(label_pattern, '', src)