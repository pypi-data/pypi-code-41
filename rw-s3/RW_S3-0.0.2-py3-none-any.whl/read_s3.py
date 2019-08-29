import pandas as pd
import boto3
from boto3.session import Session
import re

class read_s3(object):
    def __init__(self, s3_profile):
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')
        self.object_info = {}

    def ls(self, bucket, key="", last_modified_time=False):
        """
        bucketとkeyを指定したらその配下のオブジェクトを全てリストで返す
        """
        list_objects = self.__s3.list_objects(
            Bucket=bucket,
            Prefix=key
        )
        if "Contents" in list_objects:
            if last_modified_time == False:
                return [content["Key"] for content in list_objects["Contents"]]
            else:
                return {content["Key"]: content["LastModified"].strftime('%Y-%m-%d_%H:%M:%S')
                        for content in list_objects["Contents"]}
        else:
            return list_objects

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
        object_info_dic = self.ls(bucket=bucket, key=key, last_modified_time=True)
        print("object_info: %s" % object_info_dic)
        self.object_info.update(object_info_dic)
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
        object_info_dic = self.ls(bucket=bucket, key=key, last_modified_time=True)
        print("object_info: %s" % object_info_dic)
        self.object_info.update(object_info_dic)
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
        object_info_dic = self.ls(bucket=bucket, key=key, last_modified_time=True)
        print("object_info: %s" % object_info_dic)
        self.object_info.update(object_info_dic)
        return df