#!/usr/bin/env python
# -*- coding: utf-8 -*-

#                                                           
# Copyright (C)2017 SenseDeal AI, Inc. All Rights Reserved  
#                                                           

"""                                                   
File: change_info.py
Author: lzl
E-mail: zll@sensedeal.ai
Last modified: 2019/8/20
Description:                                              
"""

from lxml import etree
import re


def get_change(content):
    """
    最终整理成 "姓名:XXX,职位:XXX;" 的格式
    :param content:
    :return:
    """
    if re.match(r'姓名:.+?;职位:.+?;姓名:', content):
        content = content.replace(';职位', ',职位').replace('董事,总经理', '总经理,董事')
        content_list = ['<td>' + text.strip() + '</td><br>' for text in content.split(';') if text]
        return content_list

    if re.match(r'姓名:.+?;职位:.+?姓名:', content):
        content = content.replace(';职位', ',职位').replace('姓名', ';姓名').replace('董事,总经理', '总经理,董事')
        content_list = ['<td>' + text.strip() + '</td><br>' for text in content.split(';') if text]
        return content_list

    if re.match(r'姓名:.+?职位:.+?;姓名:', content):
        # 姓名:杜越新职位:董事;
        content = content.replace('职位', ',职位').replace('董事,总经理', '总经理,董事')
        content_list = ['<td>' + text.strip() + '</td><br>' for text in content.split(';') if text]
        return content_list

    if re.match(r'.+?（.+?）、', content):
        # 杜越新（董事）、
        content = content.replace('）、', ';').replace('（', ',职位:') \
            .replace('）', '').replace('[退出]', '').replace('[新增]', '').replace('董事,总经理', '总经理,董事')
        content_list = ['<td>姓名:' + text.strip() + '</td><br>' for text in content.split(';') if text]
        return content_list

    if re.match(r'.+?（.+?）', content):
        # 邓子权（董事）
        content = content.replace('）', ';').replace('（', ',职位:') \
            .replace('）', '').replace('[退出]', '').replace('[新增]', '').replace('董事,总经理', '总经理,董事')
        content_list = ['<td>姓名:' + text.strip() + '</td><br>' for text in content.split(';') if text]
        return content_list

    # if re.match(r'.+?(董事|董事长|监事|总经理|监事会主席|董事兼总经理|董事长兼总经理);', content):
    #     content = content.replace('[退出]', '').replace('[新增]', '').replace('董事,总经理', '总经理,董事')
    #     content_list = []
    #     for text in content.split(';'):
    #         for position in ['董事', '董事长', '监事', '总经理', '监事会主席', '董事兼总经理', '董事长兼总经理']:
    #             pass
    #         content_list.append('<td>姓名:' + text.strip() + '</td><br>')
    #     content_list = ['<td>姓名:' + text.strip() + '</td><br>' for text in content.split(';') if text]
    #     return content_list

    return None


def fix_keyword(content):
    content = re.sub(r'证件号码:\s*.*?;', '', content)
    content = re.sub(r'证件名称:.*?;', '', content)
    content = re.sub(r'性别:\s*女性;', '', content)
    content = re.sub(r'性别:\s*男性;', '', content)
    content = re.sub(r'职务', '职位', content)
    content = re.sub(r'；', ';', content)
    content = re.sub(r'：', ':', content)
    content = re.sub(r'\s', '', content)
    return content


def reversed_map(content):
    """
    自定义职位排序
    :param content:
    :return:
    """
    position_1 = ['董事长', '总经理', '监事会主席']
    for i in range(len(position_1)):
        if position_1[i] in content and '职位:副' not in content:
            return i

    position_2 = ['副董事长', '副总经理']
    for i in range(len(position_2)):
        if position_2[i] in content:
            return i + len(position_1)

    position_3 = ['董事', '监事']
    for i in range(len(position_3)):
        if position_3[i] in content:
            return i + len(position_1) + len(position_2)

    return 100


def change_format(item, before, after):
    key_words = ['高级管理人员备案', '负责人变更', '董事成员', '监事成员', '主要人员备案', '董事备案', '监事备案', '经理备案', '组织机构变更']
    if any(key in item for key in key_words):
        before_div = before
        after_div = after
        before = etree.HTML(before_div)
        after = etree.HTML(after_div)

        # 去除标签
        before = ''.join(before.xpath("//text()"))
        after = ''.join(after.xpath("//text()"))
        before = fix_keyword(before)
        after = fix_keyword(after)
        before_list = get_change(before)
        after_list = get_change(after)

        if before_list is None or after_list is None:
            return before_div.replace('；', ';<br>'), after_div.replace('；', ';<br>')

        # 对 before_list 加灰
        for i in range(len(before_list)):
            if before_list[i] in ''.join(after_list):
                continue
            info = re.search(r'姓名:(.*?),职位:(.*?)<', before_list[i])
            if not info:
                continue
            name = info.group(1)
            position = info.group(2)

            if name in ''.join(after_list):
                if position:
                    before_list[i] = before_list[i] \
                        .replace(position, '<font color="#C0C0C0">' + position + '</font>')
            else:
                if name:
                    before_list[i] = before_list[i].replace(name, '<font color="#C0C0C0">' + name + '</font>')

        # 对 after_list 加红
        for i in range(len(after_list)):
            if after_list[i] in ''.join(before_list):
                continue
            info = re.search(r'姓名:(.*?),职位:(.*?)<', after_list[i])
            if not info:
                continue
            name = info.group(1)
            position = info.group(2)
            if name in ''.join(before_list):
                if position:
                    after_list[i] = after_list[i] \
                        .replace(position, '<font color="#EF5644">' + position + '</font>')
            else:
                if name:
                    after_list[i] = after_list[i].replace(name, '<font color="#EF5644">' + name + '</font>')

        before_list = sorted(before_list, key=lambda x: reversed_map(x))
        after_list = sorted(after_list, key=lambda x: reversed_map(x))
        # print('\n'.join(before_list))
        # print('\n'.join(after_list))
        return ''.join(before_list), ''.join(after_list)
    return before, after


if __name__ == '__main__':
    before = """<td><div class="change-text select-none link-warp">姓名: <a  target="_blank">边海峰</a>; 证件名称: ; 证件号码: ********; 性别: 女性; 职务: 监事<font color="#EF5644"> </font>姓名: <a  target="_blank">陈东东</a>; 证件名称: ; 证件号码: ********; 性别: 女性; 职务: 董事<font color="#EF5644"> </font>姓名: <font color="#EF5644">戴肇辉</font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <font color="#EF5644">何江良</font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <font color="#EF5644">金利国; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 监事 姓名: <a  target="_blank">潘刚升</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <font color="#EF5644"><a  target="_blank">谭道义</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <a  target="_blank">王爱明</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <a  target="_blank">王维安</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <a  target="_blank">闻掌华</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事长<font color="#EF5644"> </font>姓名: <a  target="_blank">翁永堂</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事<font color="#EF5644"> </font>姓名: <font color="#EF5644"><a  target="_blank">翁永堂</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: <font color="#EF5644">董</font>事<font color="#EF5644"> </font>姓名: <font color="#EF5644"><a  target="_blank">张卫平</a></font>; 证件名称: ; 证件号码: ********; 性别: <font color="#EF5644">男</font>性; 职务: 监事</div></td>"""
    after = """<td><div class="change-text select-none link-warp">姓名: <a  target="_blank">边海峰</a>; 证件名称: ; 证件号码: ********; 性别: 女性; 职务: 监事姓名: <a  target="_blank">陈东东</a>; 证件名称: ; 证件号码: ********; 性别: 女性; 职务: 董事姓名: <font color="#EF5644"><a  target="_blank">潘刚升</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <font color="#EF5644"><a  target="_blank">戚金松</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <font color="#EF5644"><a  target="_blank">谭道义</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <font color="#EF5644"><a  target="_blank">唐国华</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <a  target="_blank">王爱明</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <a  target="_blank">王维安</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <a  target="_blank">闻掌华</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事长姓名: <a  target="_blank">翁永堂</a>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: 董事姓名: <font color="#EF5644"><a  target="_blank">张卫平</a></font>; 证件名称: ; 证件号码: ********; 性别: 男性; 职务: <font color="#EF5644">监</font>事姓名: <font color="#EF5644"><a  target="_blank">赵安安</a></font>; 证件名称: ; 证件号码: ********; 性别: <font color="#EF5644">女</font>性; 职务: 监事</div></td>"""
    item = '组织机构变更'
    change_format(item, before, after)
