import pandas as pd
import boto3
from boto3.session import Session
import re


class read_s3(object):
    def __init__(self, s3_profile):
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')

    def ls(self, bucket, key=""):
        return self.__get_all_keys(bucket, key)

    def __get_all_keys(self, bucket: str='', prefix: str='', keys: []=[], marker: str='') -> [str]:
        """
        指定した prefix のすべての key の配列を返す
        """
        response = self.__s3.list_objects(Bucket=bucket, Prefix=prefix, Marker=marker)
        if 'Contents' in response:  # 該当する key がないと response に 'Contents' が含まれない
            keys.extend([content['Key'] for content in response['Contents']])
            if 'IsTruncated' in response:
                return self.__get_all_keys(bucket=bucket, prefix=prefix, keys=keys, marker=keys[-1])
        return keys

    def read_file(self, bucket, key, encoding="utf_8") -> str:
        """
        拡張子を問わず，テキストファイルとして読み込む
        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=key)
        f = read_file["Body"].read().decode(encoding)
        return f

    def read_csv(self, bucket, key, encoding="utf_8", sep=',', header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        """
        csvの読み込み(pandasのread_csvとほぼ同じ)
            bucket: s3のバケット名
            key: バケット内のkey名
        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(read_file['Body'], encoding=encoding, sep=sep, header=header,
                         index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_excel(self, bucket, key, encoding="utf_8", sheet_name=0, header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        """
        excelの読み込み(pandasのread_excelとほぼ同じ)
            bucket: s3のバケット名
            key: バケット内のkey名
        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_excel(read_file['Body'], encoding=encoding, sheet_name=sheet_name,
                           header=header, index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_table(self, bucket, key, encoding="utf_8", sep="\t", header=0, index_col=None, usecols=None, na_values=None, nrows=None):
        """
        ※※※※ pandasではread_tableは非推奨扱いです ※※※※
        ※※※※ read_csv(sep='\t')を用いてください ※※※※
        csv, tsv, excel等の読み込み(pandasのread_tableとほぼ同じ)
            bucket: s3のバケット名
            key: バケット内のkey名
        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_table(read_file['Body'], encoding=encoding, header=header, sep=sep,
                           index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows)
        return df

if __name__ == '__main__':
    s3 = read_s3("read_s3")
    print(s3.ls("estiepro"))