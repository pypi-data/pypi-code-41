# -*- coding: utf-8 -*-

import json
from datetime import date
from datetime import datetime
from typing import Dict, Any, Union, Optional, List, Tuple

import pandas as pd
from nezha.uexcel import Excel, to_excel


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj: Union[date, datetime]) -> str:
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def dumps(py_ins: Any) -> str:
    u"""
    把 py_ins 转化为 json 字符串对象;
    这个封装方法的优势：
    + sort_keys=True，避免 dict 对象转化为 json str 时因位置不同导致 json 不同；
    + 支持 datatime 的转化；
    :param py_ins:
    :return:
    """
    return json.dumps(py_ins, sort_keys=True, cls=ComplexEncoder)


class Json2Excel:
    """
    template.xlsx content:
    + first row is chinese header
    + second row is json fields

    transform json to excel as the template.xlsx provided
    the transformation rule is:
    + model 'a' matches to json field "a" value
    + model 'a.b' matches to "b" in json field "a" values
    """

    def __init__(self, template_path: str):
        self.template_path: str = template_path
        self._template: Dict = dict()
        self._reversed_template: Dict = dict()

    @classmethod
    def get_recursively(cls, param_key: str, adict: Dict[str, Any]) -> Union[Dict[str, Any], str, None]:
        if isinstance(adict, dict):
            for k, v in adict.items():
                if k != param_key:
                    result = cls.get_recursively(param_key, v)
                    if result is not None:
                        return result
                else:
                    return v
        return None

    @classmethod
    def get_recursively_multi_nest(cls, multi_nest_key: str, data: Dict[str, Any]) -> Any:
        """

        :param multi_nest_key: like 'a.b.c'
        :param data:
        :return:
        """
        fields = multi_nest_key.split('.')
        not_contain_dot = 1
        if len(fields) == not_contain_dot:
            return cls.get_recursively(multi_nest_key, data)
        else:
            first_key, left_keys = fields[0], fields[1:]
            result = cls.get_recursively(first_key, data)
            if isinstance(result, dict):
                nest_key = '.'.join(left_keys)
                return cls.get_recursively_multi_nest(nest_key, result)
            else:
                return result

    def _get_result_val(self, key: str, resp_data: dict) -> str:
        result = self.get_recursively_multi_nest(key, resp_data)
        return result

    @property
    def template(self) -> Dict[str, str]:
        """
        read template.xlsx and transfer to dict.
        :return: dict[chinese, english],
        """
        if not self._template:
            self._template = Excel(self.template_path).read(header=0).dataframe.to_dict(orient='records')[0]
        return self._template

    @property
    def reversed_template(self) -> Dict[str, str]:
        """
        reverse template dict[chinese, english] to dict[chinese, english]
        :return: dict(english=[chinese])
        """
        if not self._reversed_template:
            self._reversed_template = {v: k for k, v in self.template.items()}
        return self._reversed_template

    def parse(self, input: Dict[str, Any], output: str = 'dataframe', index: Optional[List[int]] = None) -> Union[
        Dict[str, Any], pd.DataFrame]:
        """
        parse input by self.reversed_template
        call it like that: result = self.parse(input, output='dataframe', index=index)

        :param input: input data
        :param output: output type: dict/pd.DataFrame
        :param index: if output type is pd.DataFrame and dict value is scalar value, need index
        :return:
        """
        collections = {}
        for key_english, key_chinese in self.reversed_template.items():
            val = self.get_recursively_multi_nest(key_english, input)
            collections[key_chinese] = str(val)
        if output == 'dict':
            return collections
        elif output.lower() == 'dataframe':
            return pd.DataFrame(collections, index=index)
        else:
            raise NotImplementedError(f'output {output} is not support')

    @staticmethod
    def to_excel(df: pd.DataFrame, output: str, columns: Optional[Tuple[str, ...]] = None) -> None:
        """

        :param pf: need persist data
        :param output: output file name
        :param columns: specified the columns name in xlsx file
        :return:
        """
        if not output.endswith('xlsx'):
            raise ValueError(f'output {output} must be xlsx file')
        to_excel(df, output, columns=columns)


if __name__ == '__main__':
    from gitignore import huizu_resp

    xl = ''
    j = Json2Excel(xl)
    df = j.parse(huizu_resp, index=[0])
    j.to_excel(df, '')
