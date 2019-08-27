# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import subprocess
import os
import platform
import numpy as np
from multimethods import multimethod
from pandas import read_csv
from azure.storage.blob import BlockBlobService
from pyspark.sql import SparkSession
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from ..environ import SparkEnv, PandasEnv, RuntimeEnv
from ..dataaccess._open_image_blob_info import OpenImageBlobInfo
from pyspark.sql.functions import udf

def GetListFromStr(s:str) -> list:
    """A function to parse str into list.

    :param s: column list str.
    :type s: str.
    :return: the convert result.
    :rtype: list
    """
    return s.strip("[]").replace("'","").split(", ")

def GetCategoryList(str1:str) -> list:
    """A function to parse str into category list.

    :param str1: category list str.
    :type str1: str.
    :return: the convert result.
    :rtype: list
    """
    result = []
    str1 = str1.replace("'","")
    if(len(str1)>2):
        str1 = str1[1:len(str1)-1]
        list1 = str1.split("], ")
        for str2 in list1:
            list2 = str2.strip("[]").split(", ")
            result.append(list2)
    return result

@multimethod(PandasEnv, OpenImageBlobInfo)
def load_annotation_tables(env, blobInfo):
    """
    Load the open image dataset tables.

    :param env: runtime environment.
    :type env: PandasEnv
    :param blobInfo: blob info.
    :type blobInfo: OpenImageBlobInfo
    """

    blob_service = BlockBlobService(
        account_name=blobInfo.blob_account_name,
        sas_token=blobInfo.blob_sas_token.lstrip('?'))

    if platform.system() == 'Windows': 
        azcopy_path = blobInfo.azcopy_win_path
    else:
        azcopy_path = blobInfo.azcopy_linux_path
        
    azcopyFileName = azcopy_path.split('/')[-1]
    
    print('Loading the azcopy executable file...')
    tempPath = os.path.join(os.getcwd(), azcopyFileName)
    blob_service.get_blob_to_path(blobInfo.blob_container_name, azcopy_path.lstrip('/'), tempPath)
    print('finish.')
    
    if platform.system() == 'Linux': 
        prog = subprocess.Popen('chmod +x ./azcopy', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
        prog.wait()  
        if prog.returncode: 
            raise Exception('fail to Grant execute authority on the azcopy.')

    print('Loading the tables...')
    table_bbox = load_table_bbox_local(blobInfo.url_prefix, blobInfo.table_bbox_path)
    table_category = load_table_category_local(blobInfo.url_prefix, blobInfo.table_category_path)
    table_imageInfo = load_table_imageInfo_local(blobInfo.url_prefix, blobInfo.table_imageInfo_path)
    table_imageBoxNum = load_table_imageBoxNum_local(blobInfo.url_prefix, blobInfo.table_imageBoxNum_path)
    table_imageUrl = load_table_imageUrl_local(blobInfo.url_prefix, blobInfo.table_imageUrl_path)
    print('Table loading finish.')
    
    #delete the temp file
    os.remove(tempPath)

    return table_bbox, table_category, table_imageInfo, table_imageBoxNum, table_imageUrl

@multimethod(SparkEnv, OpenImageBlobInfo)
def load_annotation_tables(env, blobInfo):
    """
    Load the open image dataset tables.

    :param env: runtime environment.
    :type env: SparkEnv
    :param blobInfo: blob info.
    :type blobInfo: OpenImageBlobInfo
    """
    blob_prefix = 'wasbs://%s@%s.blob.core.windows.net/' % (blobInfo.blob_container_name,blobInfo.blob_account_name)
    spark = SparkSession.builder.getOrCreate()
    spark.conf.set('fs.azure.sas.%s.%s.blob.core.windows.net' % (blobInfo.blob_container_name, blobInfo.blob_account_name),
                   blobInfo.blob_sas_token)

    table_bbox = load_table_bbox_spark(spark, blob_prefix, blobInfo.table_bbox_path)
    table_category = load_table_category_spark(spark, blob_prefix, blobInfo.table_category_path)
    table_imageInfo = load_table_imageInfo_spark(spark, blob_prefix, blobInfo.table_imageInfo_path)
    table_imageBoxNum = load_table_imageBoxNum_spark(spark, blob_prefix, blobInfo.table_imageBoxNum_path)
    table_imageUrl = load_table_imageUrl_spark(spark, blob_prefix, blobInfo.table_imageUrl_path)

    return table_bbox, table_category, table_imageInfo, table_imageBoxNum, table_imageUrl


def load_table_bbox_local(url_prefix: str, table_relative_path: str)-> PdDataFrame:
    """
    Load the bounding box table in local(use azcopy).

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: PdDataFrame
    """

    tableName = table_relative_path.split('/')[-1]
    print('Loading the table {0}...'.format(tableName))
    tempPath = os.path.join(os.getcwd(), tableName)
    url = url_prefix + table_relative_path.lstrip('/')
    if platform.system() == 'Windows':
        cmd = 'azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    else:
        cmd = './azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    #use azcopy to download the table to temp path
    prog = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    prog.wait()  
    if prog.returncode: 
        raise Exception('fail to load the table: {0}'.format(tableName))
        
    df = read_csv(tempPath, index_col=0, dtype={'BoxID': object, 'ImageID': 'category', 'XMin': np.uint16, 'YMin': np.uint16, 'XMax': np.uint16, 
                                                'YMax': np.uint16, 'Area': np.uint32, 'IsOccluded': np.int8, 'IsTruncated': np.int8, 
                                                'IsGroupOf': np.int8, 'IsDepiction': np.int8, 'IsInside': np.int8, 
                                                'LuminanceMean': np.uint16, 'LuminanceStd': np.uint16, 'Category': 'category'})
    #delete the temp file
    os.remove(tempPath)
    print('finish.')
    return df

def load_table_bbox_spark(spark: SparkSession, blob_prefix: str, table_relative_path: str)-> SparkDataFrame:
    """
    Load the bounding box table in spark.

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: SparkDataFrame
    """
    return spark.read.csv(blob_prefix + table_relative_path.lstrip('/'), header=True, inferSchema=True)

def load_table_category_local(url_prefix: str, table_relative_path: str)-> PdDataFrame:
    """
    Load the category table in local(use azcopy).

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: PdDataFrame
    """

    tableName = table_relative_path.split('/')[-1]
    print('Loading the table {0}...'.format(tableName))
    tempPath = os.path.join(os.getcwd(), tableName)
    url = url_prefix + table_relative_path.lstrip('/')
    if platform.system() == 'Windows':
        cmd = 'azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    else:
        cmd = './azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    #use azcopy to download the table to temp path
    prog = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    prog.wait()  
    if prog.returncode: 
        raise Exception('fail to load the table: {0}'.format(tableName))

    df = read_csv(tempPath, index_col=0, converters={"BoxIDList": GetListFromStr, "ImageIDList": GetListFromStr}, dtype={'Category': object})
    #delete the temp file
    os.remove(tempPath)
    print('finish.')
    return df

def load_table_category_spark(spark: SparkSession, blob_prefix: str, table_relative_path: str)-> SparkDataFrame:
    """
    Load the category table in spark.

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: SparkDataFrame
    """

    category = spark.read.csv(blob_prefix + table_relative_path.lstrip('/'), header=True, inferSchema=True)
    listUdf = udf(lambda x : GetListFromStr(x), 'array<string>') 
    nestListUdf = udf(lambda x: GetString2List(x), 'array<array<string>>')
    category = category.withColumn("BoxIDList", listUdf(category["BoxIDList"]))
    category = category.withColumn("ImageIDList", listUdf(category["ImageIDList"]))
    return category

def load_table_imageInfo_local(url_prefix: str, table_relative_path: str)-> PdDataFrame:
    """
    Load the image info table in local(use azcopy).

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: PdDataFrame
    """

    tableName = table_relative_path.split('/')[-1]
    print('Loading the table {0}...'.format(tableName))
    tempPath = os.path.join(os.getcwd(), tableName)
    url = url_prefix + table_relative_path.lstrip('/')
    if platform.system() == 'Windows':
        cmd = 'azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    else:
        cmd = './azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    #use azcopy to download the table to temp path
    prog = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    prog.wait()  
    if prog.returncode: 
        raise Exception('fail to load the table: {0}'.format(tableName))

    df = read_csv(tempPath, index_col=0, converters={"BoxIDList": GetListFromStr, 'CategoryList': GetCategoryList}, 
                  dtype={'ImageID': object, 'ImageQualityMean': np.uint16, 'ImageQualityStd': np.uint16,
                        'Mode': 'category', 'Width': np.uint16, 'Height': np.uint16,
                        'ImageLuminanceMean': np.uint16, 'ImageLuminanceStd': np.uint16})
    #delete the temp file
    os.remove(tempPath)
    print('finish.')
    return df

def load_table_imageInfo_spark(spark: SparkSession, blob_prefix: str, table_relative_path: str)-> SparkDataFrame:
    """
    Load the image info table in spark.

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: SparkDataFrame
    """
    imageInfoTable = spark.read.csv(blob_prefix + table_relative_path.lstrip('/'), header=True, inferSchema=True)
    listUdf = udf(lambda x : GetListFromStr(x), 'array<string>') 
    nestListUdf = udf(lambda x: GetString2List(x), 'array<array<string>>')
    imageInfoTable = imageInfoTable.withColumn("BoxIDList", listUdf(imageInfoTable["BoxIDList"]))
    imageInfoTable = imageInfoTable.withColumn("CategoryList", nestListUdf(imageInfoTable["CategoryList"]))
    return imageInfoTable

def load_table_imageBoxNum_local(url_prefix: str, table_relative_path: str)-> PdDataFrame:
    """
    Load the imageBoxNum table in local(use azcopy).

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: PdDataFrame
    """

    tableName = table_relative_path.split('/')[-1]
    print('Loading the table {0}...'.format(tableName))
    tempPath = os.path.join(os.getcwd(), tableName)
    url = url_prefix + table_relative_path.lstrip('/')
    if platform.system() == 'Windows':
        cmd = 'azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    else:
        cmd = './azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    #use azcopy to download the table to temp path
    prog = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    prog.wait()  
    if prog.returncode: 
        raise Exception('fail to load the table: {0}'.format(tableName))

    df = read_csv(tempPath, index_col=0, converters={"ImageIDList": GetListFromStr}, dtype={'NumofboundingBox': np.uint16})
    #delete the temp file
    os.remove(tempPath)
    print('finish.')
    return df

def load_table_imageBoxNum_spark(spark: SparkSession, blob_prefix: str, table_relative_path: str)-> SparkDataFrame:
    """
    Load the imageBoxNum table in spark.

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: SparkDataFrame
    """
    imageBoxNum = spark.read.csv(blob_prefix + table_relative_path.lstrip('/'), header=True, inferSchema=True)
    listUdf = udf(lambda x : GetListFromStr(x), 'array<string>') 
    imageBoxNum = imageBoxNum.withColumn("ImageIDList", listUdf(imageBoxNum["ImageIDList"]))
    return imageBoxNum

def load_table_imageUrl_local(url_prefix: str, table_relative_path: str)-> PdDataFrame:
    """
    Load the imageUrl table in local(use azcopy).

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: PdDataFrame
    """

    tableName = table_relative_path.split('/')[-1]
    print('Loading the table {0}...'.format(tableName))
    tempPath = os.path.join(os.getcwd(), tableName)
    url = url_prefix + table_relative_path.lstrip('/')
    if platform.system() == 'Windows':
        cmd = 'azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    else:
        cmd = './azcopy copy "{source}" "{dest}"'.format(source=url, dest=tempPath)
    #use azcopy to download the table to temp path
    prog = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    prog.wait()  
    if prog.returncode: 
        raise Exception('fail to load the table: {0}'.format(tableName))

    df = read_csv(tempPath, index_col=0, dtype={'ImageID': object, 'Subset': 'category'})
    #delete the temp file
    os.remove(tempPath)
    print('finish.')
    return df

def load_table_imageUrl_spark(spark: SparkSession, blob_prefix: str, table_relative_path: str)-> dict:
    """
    Load the imageUrl table in spark, and convert it to dict

    :param url_prefix: url prefix.
    :type url_prefix: str
    :param table_relative_path: table relative path.
    :type table_relative_path: str
    :return: the table.
    :rtype: dict
    """
    df = spark.read.csv(blob_prefix + table_relative_path.lstrip('/'), header=True, inferSchema=True)
    return df.rdd.map(lambda row : (row[0], row[1])).collectAsMap()
