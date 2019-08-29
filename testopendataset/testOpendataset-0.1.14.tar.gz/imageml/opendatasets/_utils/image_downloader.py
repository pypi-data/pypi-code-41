# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from ..dataaccess._open_image_blob_info import OpenImageBlobInfo
from azure.storage.blob import BlockBlobService
from ..environ import RuntimeEnv, SparkEnv, PandasEnv
from multimethods import multimethod
import numpy as np
import os
import pandas as pd
import urllib
import cv2
import requests
from pyspark.sql import functions as F
from pyspark.sql.functions import udf
from pyspark.sql import SparkSession
import json

class ImageDownloader:
    """Open Image Dataset image downloader class."""

    @staticmethod
    def DownloadImages(elements, blobInfo, env, path):
        """
        Download images, used in GetImages function

        :param elements: each element is a tuple, it consists of (urlPrefix, subset/imageId, savePath)
         for example ('https://openimagestorage.blob.core.windows.net/openimagedataset/', 'validation/0001eeaf4aed83f9.jpg', 'tmp/')
        :type elements: iterator
        :param runType: local or spark
        :type runType: str
        """
        containerName = blobInfo.blob_container_name
        blobService = BlockBlobService(
            account_name=blobInfo.blob_account_name,
            sas_token=blobInfo.blob_sas_token.lstrip('?'))
        for relativePath in elements:
            if type(env) == SparkEnv:
                # save image in dbfs, path format : "/dbfs/tmp..." -> tmp folder at dbfs
                imagePath =  os.path.join("/dbfs", path, relativePath.split("/")[-1])
                blobService.get_blob_to_path(containerName, relativePath, imagePath)
            elif type(env) == PandasEnv:
                imagePath = os.path.join(path, relativePath.split("/")[-1])
                if not os.path.exists(imagePath):
                    blobService.get_blob_to_path(containerName, relativePath, imagePath)
            else:
                raise ValueError("Input is invalid")

    @multimethod(OpenImageBlobInfo, PdDataFrame, PdDataFrame, str, dict, str, str)
    def GetImages(self, blobInfo, bbox, urlTable, path, imageDict, storeType, tokens):
        """
        Download images (named by image ids) and a image attribute file (imageid, bb-info-list) into local path 
        or customer azure blob.

        :param urlPrefix: prefix of url
        :type urlPrefix: str
        :param bbox: pandans dataframe contains bounding box information
        :type bbox: PdDataFrame
        :param urlTable: pandas dataframe contains imageID and relative path on azure blob.
        :type urlTable: PdDataFrame
        :param path: download path
        :type path: str
        :param imageDict: dict of imageID and bounding boxID list
        :type imageDict: dict
        :param storeType: local or azureblob.
        :type storeType: str
        :param tokens: for authentication on azure blob.
        :type tokens: str

        """
        if not imageDict:
            raise ValueError("Input can not be empty.")

        imageSavePath = os.path.join(path, "image")
        if not os.path.exists(imageSavePath):
            os.makedirs(imageSavePath)
        imageIds = list(imageDict.keys())

        # annotation file
        bboxLists = [v for imageID in imageIds for v in imageDict.get(imageID)]
        bbox = bbox[bbox.index.isin(bboxLists)].copy()
        bbox.reset_index(inplace = True)
        bbox.loc[:,'BoxIDList'] = bbox.apply(lambda x: {'BoxID':x['BoxID'], 'XMin': x['XMin'],'XMax': x['XMax'],'YMin': x['YMin'],'YMax' : x['YMax'],
                                      'IsOccluded':x['IsOccluded'],'IsTruncated':x['IsTruncated'],'IsGroupOf':x['IsGroupOf'],
                                      'IsInside':x['IsInside'],'Category':x['Category']}, axis=1)
        df = bbox.groupby("ImageID", observed=True)['BoxIDList'].apply(list)
        with open(os.path.join(path, "annotation.json"), "w") as f:
            json.dump(df.reset_index().to_dict(orient='records'),f)

        # download images
        elements = []
        for imageId in imageIds:
            relativePath = urlTable.loc[imageId, "Subset"] + "/" + imageId + ".jpg"
            elements.append(relativePath)
        ImageDownloader.DownloadImages(elements, blobInfo, PandasEnv(), imageSavePath)

    @multimethod(OpenImageBlobInfo, SparkDataFrame, dict, str, dict, str, str)
    def GetImages(self, blobInfo, bbox, urlTable, path, imageDict, storeType, tokens):
        """
        Download images (named by image ids) and a image attribute file (imageid, categorylist, bb-info-list) into local path 
        or customer azure blob.

        :param urlPrefix: prefix of url
        :type urlPrefix: str
        :param bbox: spark dataframe contains bounding box information
        :type bbox: SparkDataFrame
        :param urlTable: dict contains imageID and relative path on azure blob.
        :type urlTable: dict
        :param path: download path
        :type path: str
        :param imageDict: dict of imageID and bounding boxID list
        :type imageDict: dict
        :param storeType: local or azureblob.
        :type storeType: str
        :param tokens: for authentication on azure blob.
        :type tokens: str

        """
        
        if not imageDict:
            raise ValueError("Input can not be null.")

        # validate input path, starting with / or dbfs: is both valid
        if path.startswith("dbfs:"):
            path = path.split(":")[1][1:]
        elif path.startswith("/"):
            path = path[1:]
        else:
            raise ValueError("The path is invalid")

        spark = SparkSession.builder.getOrCreate()
        # get image list and box list
        imageIds = list(imageDict.keys())
        bboxLists = [v for imageID in imageIds for v in imageDict.get(imageID)]

        # annotaiton file
        bboxListDF = spark.sparkContext.parallelize(bboxLists).map(lambda x : (x, )).toDF(["BoxID"])
        fileterDF = bboxListDF.join(bbox, ["BoxID"], "inner")
        fileterDF = fileterDF.withColumn("BoxList", F.struct(F.col("BoxID"), F.col("XMin"),F.col("XMax"),F.col("YMin"),F.col("YMax"),\
                                F.col("IsOccluded"),F.col("IsTruncated"),F.col("IsGroupOf"),F.col("IsInside"),F.col("Category")))
        fileterDF.groupBy("ImageID").agg(F.collect_list("BoxList").alias("BoxList")).write.json(os.path.join(path, "annoatation"))
                
        # download image
        urlList = []
        for imageId in imageIds:
            url = os.path.join(urlTable.get(imageId), imageId + ".jpg")
            urlList.append(url)
        func = ImageDownloader.DownloadImages
        spark.sparkContext.parallelize(urlList).foreachPartition(lambda x: func(x, blobInfo, SparkEnv(), path))

    @multimethod(PdDataFrame, str, int, list, int, str, str)
    def GetImagesByBatch(self, urlPrefix, imageInfoTable, df, path, partitionSize, imageIds, batchsize, storeType, tokens):
        """
        Return a list of images in image classes for training/testing 
        and at the same time a file described imageInstance list will be created in local or blob
        image class will contain:
        (1) image bits
        (2) image tensors in RGB format and will consider other type of format
        (3) image category list (may use number only, like 0 means car, 1 means human, ...)
        (4) image bb list (each element in the list will be like (xMin, yMin, bbcategory, isTruncated, isOcclued, ...))
        (5) ... 
        :param storeType: local or azureblob.
        :type: str
        :param path: download path.
        :type path: str
        :param tokens: for authentication on azure blob.
        :type tokens: str
        :param partitionSize: ...
        :type partitionSize: int
        :param imageIds: if None, means all images.
        :type imageIds: list
        :param batchsize: download images at the same time when training.
        :type batchsize: int   
        :return: a list of images in image classes for training/testing.
        :rtype: list
        """

        pass


    @multimethod(SparkDataFrame, str, int, list, int, str, str)
    def GetImagesByBatch(self, urlPrefix, imageInfoTable, df, path, partitionSize, imageIds, batchsize, storeType, tokens):
        """
        Return a list of images in image classes for training/testing 
        and at the same time a file described imageInstance list will be created in local or blob
        image class will contain:
        (1) image bits
        (2) image tensors in RGB format and will consider other type of format
        (3) image category list (may use number only, like 0 means car, 1 means human, ...)
        (4) image bb list (each element in the list will be like (xMin, yMin, bbcategory, isTruncated, isOcclued, ...))
        (5) ... 
        :param storeType: local or azureblob.
        :type: str
        :param path: download path.
        :type path: str
        :param tokens: for authentication on azure blob.
        :type tokens: str
        :param partitionSize: ...
        :type partitionSize: int
        :param imageIds: if None, means all images.
        :type imageIds: list
        :param batchsize: download images at the same time when training.
        :type batchsize: int   
        :return: a list of images in image classes for training/testing.
        :rtype: list
        """

        pass
     

