import io
from typing import Union, Optional, Tuple, TextIO, List
from warnings import warn

import pandas as pd
from pandas import DataFrame
from pandas import Series
from nezha.file import File
from nezha.ustring import clean_str


def read(file: Union[str, TextIO, io.StringIO],
         names: Optional[Tuple[str, ...]] = None,
         clean_item: bool = True,
         remove_chinese_comma: bool = True,
         skiprows: Union[int, Tuple[int, ...], None] = None,
         header: Union[int, List[int], None] = 0) -> DataFrame:
    """
    read file from xlsx or csv and return pd.DataFrame
    :param file:
    :param names: specified pd.DataFrame header
    :param clean_item: remove invisible char
    :param remove_chinese_comma: not work in xlsx, is suit for csv.
    :header
    指定行数用来作为列名，数据开始行数。
    如果文件中没有列名，则默认为0，否则设置为None。
    如果明确设定header=0 就会替换掉原来存在列名。
    header参数可以是一个list例如：[0,1,3]，这个list表示将文件中的这些行作为列标题（意味着每一列有多个标题），
    介于中间的行将被忽略掉（例如本例中的2；本例中的数据1,2,4行将被作为多级标题出现，第3行数据将被丢弃，dataframe的数据从第5行开始。）。
    :return:
    """
    if isinstance(file, str):
        if file.endswith('xlsx'):
            print(file, names, skiprows, header)
            df = pd.read_excel(file, names=names, skiprows=skiprows, header=header)
        else:
            if not file.endswith('csv'):
                warn(f"{file} treated as csv file")
            if remove_chinese_comma:
                file = File(file).remove_chinese_comma()
            if isinstance(file, io.StringIO):
                df = pd.read_csv(file, names=names, skiprows=skiprows, header=header)
                file.close()
            elif isinstance(file, str):
                df = pd.read_csv(file, names=names, encoding=File(file).encoding, skiprows=skiprows, header=header)
            else:
                raise NotImplementedError(f'file type {type(file)}')
        if not clean_item:
            return df
        frame = []
        for _, series in df.iterrows():
            new_series = {clean_str(k): clean_str(v, striped='"') for k, v in series.iteritems()}
            frame.append(new_series)
        return pd.DataFrame(frame)
    elif isinstance(file, io.StringIO):
        if remove_chinese_comma:
            file = File(file).remove_chinese_comma()
        df = pd.read_csv(file, names=names, skiprows=skiprows, header=header)
        if isinstance(file, io.StringIO):
            file.close()
        return df
    else:
        raise NotImplementedError(f'file type {type(file)}')


def to_excel(df: pd.DataFrame,
             output_name: str,
             index: bool = False,
             columns: Optional[Tuple[str, ...]] = None) -> None:
    df.to_excel(output_name, index=index, columns=columns)


def read_str_csv(s: str, sep: str = '\r\n') -> TextIO:
    """

    :param s:
    example: 'name,phone,idcard\r\n\r\n张**,1536**,14273219***\r\n\r\n韩**,1521**7881,370303**6110320'
    :return: stringIO. csv
    """
    invalid_lines = ('',)
    lines = (line.strip() + '\n' for line in s.split(sep) if line not in invalid_lines)
    io_text = io.StringIO()
    # even call writelines, \n must be added too. It's strange ...
    io_text.writelines(lines)
    io_text.seek(0)
    return io_text


class Excel:

    def __init__(self, file: Union[str, TextIO]):
        """
        as pandas doc, the file is io file-like object.
         you can refer pd.read_html()/pd.read_excel() ... first parameter
        :param file:
        """
        self.file: Union[str, TextIO] = file
        self.dataframe: DataFrame = DataFrame()

    def read(self, names: Optional[Tuple[str, ...]] = None, clean_item: bool = True,
             remove_chinese_comma: bool = True, skiprows: Union[int, Tuple[int, ...], None] = None,
             header: Union[int, List[int], None] = 0) -> 'Excel':
        """

        :param names: if name is not None and the file first row is column_name, skiprows should be 0.
            So the first row will be skipped.
        :param clean_item:
        :param remove_chinese_comma:
        :param skiprows: 需要忽略的行数（从文件开始处算起），或需要跳过的行号列表（从0开始)。
        :return:
        """
        self.dataframe = read(self.file, names=names, clean_item=clean_item, remove_chinese_comma=remove_chinese_comma,
                              skiprows=skiprows, header=header)
        return self

    @property
    def header(self) -> List[str]:
        return list(self.dataframe)

    @classmethod
    def prepare_file(cls, s: str, is_csv: bool = True, sep: str = '\r\n') -> 'Excel':
        if not is_csv:
            raise NotImplementedError()
        file = read_str_csv(s, sep=sep)
        return cls(file)

    def to_excel(self, output_name: str, index: bool = False, columns: Optional[Tuple[str, ...]] = None) -> None:
        print('self.dataframe', self.dataframe)
        to_excel(self.dataframe, output_name, index=index, columns=columns)

    def get_row(self, index: Union[str, int]) -> Series:
        return self.dataframe.loc[index]

    def read_html(self) -> 'Excel':
        self.dataframe = pd.read_html(self.file, encoding='utf-8')
        return self


def csv2xlsx(input: str, output: str, names: Optional[Tuple[str, ...]] = None) -> None:
    """
    usage:
        turn pure csv to xlsx because of scientific notation.
    :param input:
    :param output:
    :param names:
    :return:
    """
    Excel(input).read(names=names).to_excel(output, columns=names)

# if __name__ == '__main__':
#     s = '/Users/yutou/Downloads/sqlresult_4032539.csv'
#     w = Excel(s).read(names=('name', 'product', 'order_sn', 'price', 'create_at')).to_excel(
#         '/Users/yutou/shouxin/sxProject/pysubway/pysubway/gitignore/sqlresut_cy.xlsx',
#         columns=('name', 'product', 'order_sn', 'price', 'create_at'), index=False)
#     print(w)
