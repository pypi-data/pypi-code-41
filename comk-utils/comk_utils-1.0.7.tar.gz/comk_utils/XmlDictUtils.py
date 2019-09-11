import json

import xmltodict

'''
xml与dict互相转换的工具

'''


def xml_to_dict(xmlstr):
    '''
    xml转dict的函数
    parse是的xml解析器

    :param xmlstr:
    :return:
    '''
    xmlparse = xmltodict.parse(xmlstr)  # 不是很直观
    return json.loads(json.dumps(xmlparse))  # 经过这个方法改造后，就直观了


def dict_to_xml(data_dict, encoding='utf-8'):
    '''
    dict转xml函数

    :param data_dict:
    :return:
    '''
    xmlstr = xmltodict.unparse(data_dict, encoding=encoding, full_document=False)
    return xmlstr


if __name__ == '__main__':
    '''
    测试
    '''

    xml = """
       <student>
           <stid>10213</stid>
           <信息>
               <name>name</name>
               <sex>male</sex>
           </信息>
           <course>
               <name>math</name>
               <score>90</score>
           </course>
       </student>
           """
    result = xml_to_dict(xml)
    print(result)
    print(dict_to_xml(result))
