# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Open Image Dataset."""

from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from .dataaccess._open_image_blob_info import OpenImageBlobInfo
from ._utils.image_downloader import ImageDownloader
from ._utils.image_selector import ImageSelector
from ._utils.image_common_types import ImageAnalyzeResult
from .environ import SparkEnv, PandasEnv, RuntimeEnv
from ._utils.image_annotation_table_loader import load_annotation_tables
from ._utils.telemetry_utils import get_opendatasets_logger
from azureml.telemetry.activity import ActivityType, log_activity
import spacy

class OpenImage:
    """Open Image Dataset class."""

    #load the spacy model
    try:
        print('loading the spacy model..')
        import en_core_web_md
        __model_spacy = en_core_web_md.load()
        print('finish.')
    except ModuleNotFoundError:
        print('Downloading language model for the spaCy POS tagger\n'
              "(don't worry, this will only happen once)")
        from spacy.cli import download
        download('en_core_web_md')
        import en_core_web_md
        __model_spacy  = en_core_web_md.load()
        print('finish.')

    __blobInfo = OpenImageBlobInfo()

    def __init__(
            self,
            env: str = 'pandas',
            enable_telemetry: bool = True):
        """
        Initializes an instance of the OpenImage class.

        :param env: the runtime environment of the class.
        :type env: str
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        env = env.lower()
        if env == 'pandas':
            self.env = PandasEnv()
        elif env == 'spark':
            self.env = SparkEnv()
        else:
            raise ValueError("Input must be 'pandas' or 'spark'")

        self.enable_telemetry = enable_telemetry
        if self.enable_telemetry:
            self.logger = get_opendatasets_logger(__name__)
            self.log_properties = self.get_common_log_properties()
            self.log_properties['env'] = env

        self.__selector = ImageSelector(self.env)
        self.__downLoader = ImageDownloader()

        #load the tables
        if not hasattr(OpenImage, '_OpenImage__table_imageUrl') or \
        (type(self.env) != PandasEnv and type(getattr(OpenImage, '_OpenImage__table_imageUrl')) == PdDataFrame) or \
        (type(self.env) != SparkEnv and type(getattr(OpenImage, '_OpenImage__table_imageUrl')) == SparkDataFrame):
            OpenImage.__table_bbox,  OpenImage.__table_category, OpenImage.__table_imageInfo,\
                OpenImage.__table_imageBoxNum, OpenImage.__table_imageUrl = load_annotation_tables(self.env, self.__blobInfo) 

    def get_common_log_properties(self):
        """Get common log properties."""
        return {}

    def AnalyzeImages(self, imageIDList: list=[], edaFilterList: dict={}) -> ImageAnalyzeResult:
        """
        Analyze images depending on EDA metrics and will return different kind of metrics:
        (1) Grayscale or color image distribution
        (2) Bounding boxes number distribution
        (3) Image size distribution
        (4) Image category distribution
        (5) Image luminance distribution
        (6) Image quality distribution (images with low night noise distribution)
        (7) ...

        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'AnalyzeImages',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.AnalyzeImages(OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_category, imageIDList, edaFilterList)
        else:
            return self.__selector.AnalyzeImages(OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_category, imageIDList, edaFilterList)

    def AnalyzeImagesByBoundingBoxes(self, boxIDList: list=[], edaFilterList: dict={}) -> ImageAnalyzeResult:
        """
        Analyze bounding boxes depending on EDA metrics and will return different kind of metrics:
        (1) bb-level category distribution
        (2) bb-level attributes distribution like isOccluded bbs distribution, isTruncated bbs distribution, isGrouped bbs distribution, ...
        (3) bb size distribution
        (4) bb luminance distribution
        (5) ...

        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'AnalyzeImagesByBoundingBoxes',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.AnalyzeImagesByBoundingBoxes(OpenImage._OpenImage__table_bbox, boxIDList, edaFilterList)
        else:
            return self.__selector.AnalyzeImagesByBoundingBoxes(OpenImage._OpenImage__table_bbox, boxIDList, edaFilterList)

    def SelectImages(self, imageIDList: list=[], boxIDList: list=[], edaFilterList: dict={}) -> dict:
        """
        Select images
        People can select images on different rules and return image id list:
        1. select images by ids, if none, select all images.
        2. select images by one or multiple combination of the following image level eda metrics: 
            (1) image-level category, 
            (2) image size, 
            (3) bounding box number, 
            (4) bounding box ids, 
            (5) image luminance
            (6) image quality (low night noise)
            (7) Grayscale or color image
            (8) ...

        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: a dict like {ImageID: [bboxID1, bboxID2,...]}.
        :rtype: dict
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'SelectImages',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.SelectImages(OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_category, imageIDList, boxIDList, edaFilterList)
        else:
            return self.__selector.SelectImages(OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_category, imageIDList, boxIDList, edaFilterList)

    def SelectBboxs(self, boxIDList: list=[], edaFilterList: dict={}) -> list:
        """
        Select bounding boxes (bbs)
        People can select bbs on different rules and bbs id list:
        1. select bbs by ids, if none, select all bbs
        2. select bbs by one or multiple combination of the following bb level eda metrics:
            (1) bb-level category
            (2) bb-level attributes like isOccluded, isTruncated, isGrouped, ...
            (3) bb size
            (4) bb luminace
            (5) ...

        :param box_data: bbox data.
        :type box_data: PdDataFrame
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: a boxID list of the query results.
        :rtype: list
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'SelectBboxs',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.SelectBboxs(OpenImage._OpenImage__table_bbox, boxIDList, edaFilterList)
        else:
            return self.__selector.SelectBboxs(OpenImage._OpenImage__table_bbox, boxIDList, edaFilterList)

    def GetCategories(self) -> list:
        """
        Get all categories.

        :return: a category list.
        :rtype: list
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'GetCategories',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.GetCategories(OpenImage._OpenImage__table_category)
        else:
            return self.__selector.GetCategories(OpenImage._OpenImage__table_category)

    def GetCategories(self) -> list:
        """
        Get all categories.

        :return: a category list.
        :rtype: list
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'GetCategories',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.GetCategories(OpenImage.__table_category)
        else:
            return self.__selector.GetCategories(OpenImage.__table_category)

    def ShowImages(self, path: str, imageIDList: list=[], boxIDList: list=[], limitedNum: int=100):
        """
        Show bounding boxes in images and will download images with drawn bounding boxes to local path. 

        :param path: local save path.
        :type path: str
        :param imageIDList: a list of imageIDs(if None, select image id by boxIDList).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param urlPrefix: the download url prefix.
        :type urlPrefix: str
        :param limitedNum: the download image number.
        :type limitedNum: int
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'ShowImages',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__selector.ShowImages(OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_imageUrl, imageIDList, boxIDList, self.__blobInfo.url_prefix, path, limitedNum)
        else:
            return self.__selector.ShowImages(OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_imageUrl, imageIDList, boxIDList, self.__blobInfo.url_prefix, path, limitedNum)

    def GetImages(self, path: str, imageDict: dict = None, storeType: str = "", tokens: str = ""):
        """
        Download images (named by image ids) and a image attribute file (imageid, categorylist, bb-info-list) into local path 
        or customer azure blob.
        :param storeType: local or azureblob.
        :type storeType: str
        :param path: download path.
        :type path: str
        :param tokens: for authentication on azure blob.
        :type tokens: str
        :param imageIds: image id list you want to download.
        :type imageIds: list
        :param imageLimtationNumberWhenNoIds: to avoid download all images unless customer manually give a None here.
        :type imageLimtationNumberWhenNoIds: int
        :param includeAttributedFile: to download only images or both.
        :type includeAttributedFile: bool
        """
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'GetImages',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__downLoader.GetImages(self.__blobInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_imageUrl, path, imageDict, storeType, tokens)
        else:
            return self.__downLoader.GetImages(self.__blobInfo, OpenImage._OpenImage__table_bbox, OpenImage._OpenImage__table_imageUrl, path, imageDict, storeType, tokens)
    
    def GetImagesByBatch(self, storeType: str, path: str, tokens: str, partitionSize: int, imageIds: list = None, batchsize: int = 100) -> list:
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
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'GetImagesByBatch',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                return self.__downLoader.GetImagesByBatch(OpenImage.__blobInfo.url_prefix, OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_imageUrl, storeType, path, tokens, partitionSize, imageIds, batchsize)
        else:
            return self.__downLoader.GetImagesByBatch(OpenImage.__blobInfo.url_prefix, OpenImage._OpenImage__table_imageInfo, OpenImage._OpenImage__table_imageUrl, storeType, path, tokens, partitionSize, imageIds, batchsize)