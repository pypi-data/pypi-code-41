#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
FileName    : common.py
Author      : ken
Date        : 2018-04-21
Describe    : common method for test
"""

import os
import xlrd
import basic

# proDir = basic.getdir()

def get_excel_value(excel_path, sheet_name):
    """
    get excel value by given excel_name and sheet_name
    :param excel_name:
    :param sheet_name:
    :return: cls
    """
    cls = []
    # excel_path = os.path.join(proDir, "test_data", excel_name)
    workbook = xlrd.open_workbook(excel_path)
    sheet = workbook.sheet_by_name(sheet_name)
    nrows = sheet.nrows

    for i in range(nrows):
        if sheet.row_values(i)[0] != "case_name":
            cls.append(sheet.row_values(i))
    return cls

def get_txt_value(txt_name):
    """
    get excel value by given excel_name and sheet_name
    :param excel_name:
    :param sheet_name:
    :return: cls
    """
    cls = []
    # excel_path = os.path.join(proDir, "test_data", txt_name)
    with open(txt_name, 'r') as file:
        for params in file:
            list=[]
            results = params.split(';;;')
            for result in results :
                list.append(unicode(result, 'utf-8'))
            cls.append(list)
    return cls
if __name__ == "__main__":

    test = get_txt_value(txt_name='json_data1.txt')
    test1= get_excel_value(excel_name='loginCase.xlsx', sheet_name='test')
    print(test)
    print (test1)