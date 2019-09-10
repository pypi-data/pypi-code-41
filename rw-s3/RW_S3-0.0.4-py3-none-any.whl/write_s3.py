import re
import pandas as pd
import logging
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError


class write_s3():
    def __init__(self, s3_profile='put_s3_lambda'):
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')

    def upload_file(self, src_data: str, bucket, key):
        """
        :param src_data: bytes of data or string reference to file spec
        :param bucket: bucket name
        :param key: key name
        :return: True if src_data was added to dest_bucket/dest_object, otherwise False
        """
        if isinstance(src_data, bytes):
            object_data = src_data
        elif isinstance(src_data, str):
            try:
                object_data = open(src_data, 'rb')
                # possible FileNotFoundError/IOError exception
            except Exception as e:
                logging.error(e)
                return False
        else:
            logging.error('Type of ' + str(type(src_data)) +
                          ' for the argument \'src_data\' is not supported.')
            return False
        try:
            self.__s3.put_object(Bucket=bucket, Key=key, Body=object_data)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return False
        finally:
            if isinstance(src_data, str):
                object_data.close()
        return True

    def to_csv(self, df: pd.DataFrame, bucket, key, index=True, encoding="utf_8"):
        """
        変数dfをbucketバケットのkeyパスに書き出す
            * df: pandasのデータフレーム
            * bucket: アップロードしたいバケット名
            * key: アップロードしたバケット内のファイルパス
        ※ 存在しないバケットにもアップロードできます
        """
        bytes_to_write = df.to_csv(
            None, index=index, encoding=encoding).encode(encoding)
        self.__s3.put_object(
            ACL='private', Body=bytes_to_write, Bucket=bucket, Key=key)

    def to_excel(self, df: pd.DataFrame, bucket, key, index=True, encoding="utf_8"):
        """
        変数dfをbucketバケットのkeyパスに書き出す
            * df: pandasのデータフレーム
            * bucket: アップロードしたいバケット名
            * key: アップロードしたバケット内のファイルパス
        ※ 存在しないバケットにもアップロードできます
        """
        bytes_to_write = df.to_excel(
            None, index=index, encoding=encoding).encode(encoding)
        self.__s3.put_object(
            ACL='private', Body=bytes_to_write, Bucket=bucket, Key=key)
