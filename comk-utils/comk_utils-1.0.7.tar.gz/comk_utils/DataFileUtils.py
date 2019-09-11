import csv

import xlrd
import xlwt


class DataFileUtils():
    '''
    data-file转换工具
    '''

    def __init__(self, encoding='utf-8'):
        self._encoding = encoding
        self._wbook = xlwt.Workbook(encoding=encoding)
        self._style = xlwt.easyxf('align:vertical center,horizontal center')  # 设置文字的 style
        # self.style = xlwt.XFStyle()  # 设置文字的 style

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    def wbook(self):
        return self._wbook

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if isinstance(value, xlwt.Style.XFStyle):
            self._style = value
        else:
            raise Exception('style must be XFStyle')

    ################################################################
    ## excel 相关功能
    ################################################################
    def excel_save(self, target):
        '''
        保存数据

        :param target: 保存数据的目标，可以是 文件，也可以是 httpresponse
        :return:
        '''
        self.wbook.save(target)

    def excel_to_list(self, excel_name, index=0):
        '''
        读取一个excel为list

        :param excel_name: 文件名
        :param index: 第index个工作表
        :return:
        '''
        l = []
        book = xlrd.open_workbook(excel_name)
        sheet = book.sheet_by_index(index)  # 按索引获取工作表
        nrows = sheet.nrows  # 获取行数
        for row in range(nrows):
            l.append(sheet.row_values(row))
        return l

    def add_a_sheet(self, sheet_name='sheet'):
        '''
        创建一张工作表

        :param sheet_name:
        :return:
        '''
        wsheet = self.wbook.add_sheet(sheet_name)  # 创建工作表，并为其命名
        return wsheet

    def save_at_cache(self, sheet_name='sheet', data=None, header=None):
        '''
        暂时把数据存放到内存中的表中
        由于本人才疏学浅，暂时做不到往内存中的同一个表中续写数据，只能新加一张表，新添数据，所以建议把数据整理好后一次性写入。

        :param excel_name:
        :param data:
        :return:
        '''
        wsheet = self.add_a_sheet(sheet_name)  # 获得一张表

        if header and isinstance(header, (list, tuple)):
            data.insert(0, header)

        y = 0
        for l in data:
            x = 0
            for cell in l:
                wsheet.write(y, x, cell, self.style)  # 向单元格内写数据
                x += 1
            y += 1

    def save_to_excel_file(self, excel_name):
        '''
        只将内存中的数据写入文件中

        :param excel_name:
        :return:
        '''
        self.excel_save('{}.xls'.format(excel_name))

    def list_to_excel_file(self, excel_name='excel', sheet_name='sheet', data=None, header=None):
        '''
        data 是一个list，list中包含list，将数据写入excel文件中

        :param excel_name:
        :param data:
        :return:
        '''
        if not data:
            return -1
        self.save_at_cache(sheet_name, data, header)
        self.save_to_excel_file(excel_name)

    ################################################################
    ## web服务，下载生成 excel文件
    ################################################################
    def save_to_excel_httpresponse(self, httpresponse):
        '''
        只将内存中的数据写入httpresponse中

        :param httpresponse:
        :return:
        '''
        self.excel_save(httpresponse)

    def list_to_excel_httesponse(self, httpresponse, sheet_name='sheet', data=None, header=None):
        '''
        data 是一个list，list中包含list，以excel文件的方式，写入httpresponse中

        :param httpresponse:
        :param data:
        :return:
        '''
        if not data:
            return -1
        self.save_at_cache(sheet_name, data, header)
        self.save_to_excel_httpresponse(httpresponse)

    ################################################################
    ## csv 相关功能
    ################################################################
    def csv_to_list(self, csv_name):
        '''
        将csv转换成一个list，该list中的元素是list

        :param csv_name: 文件名
        :param encoding:
        :return:
        '''
        l = []
        with open('{}.csv'.format(csv_name), 'r', encoding=self.encoding)as f:
            for line in f.readlines():
                line = line.strip().split(',')
                l.append(line)
        return l

    def list_to_csv_file(self, csv_name, data=None, header=None):
        '''
        将list转换成一个csv，该list中的元素是list

        :param csv_name: 文件名
        :param data:
        :param encoding:
        :return:
        '''
        if header and isinstance(header, (list, tuple)):
            data.insert(0, header)

        with open('{}.csv'.format(csv_name), 'w', encoding=self.encoding)as f:
            writer = csv.writer(f)
            for l in data:
                writer.writerow(l)

    def list_to_csv_httpresponse(self, httpresponse, data=None, header=None):
        '''
        data 是一个list，list中包含list，以csv文件的方式，写入httpresponse中


        :param httpresponse:
        :param data:
        :param header:
        :return:
        '''
        if header and isinstance(header, (list, tuple)):
            data.insert(0, header)
        writer = csv.writer(httpresponse)
        for l in data:
            writer.writerow(l)

    def csv_to_execl(self, csv_name, header=None):
        '''
        将csv文件保存为同名的Excel文件

        :param csv_name:
        :param encoding:
        :return:
        '''
        csv_data = self.csv_to_list(csv_name)
        self.list_to_excel_file(excel_name=csv_name, data=csv_data, header=header)


if __name__ == '__main__':
    '''
    测试

    '''
    l = [[1, 2, 3], [4, 5, 6]]
    eu = DataFileUtils()
    eu.list_to_excel_file(sheet_name='1', data=l)
    eu.list_to_excel_file(sheet_name='2', data=l)
