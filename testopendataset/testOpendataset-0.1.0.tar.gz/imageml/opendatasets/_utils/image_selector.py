# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Image selector class."""

from pandas import DataFrame as PdDataFrame
from ..environ import SparkEnv, PandasEnv, RuntimeEnv
from .image_common_types import ImageAnalyzeResult
from collections import OrderedDict
from multimethods import multimethod
import logging
import cv2
import numpy as np
from urllib.request import urlopen
import os
from spacy.lang.en import English

from pyspark.sql.functions import udf,size,explode,concat_ws
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
import pyspark.sql.functions as F

class ImageSelector:
    """different kinds of selection to get the image info."""
    def __init__(self, env: RuntimeEnv):
        """
        Initializes an instance of the ImageSelector class.

        :param env: the runtime environment of the class.
        :type env: RuntimeEnv
        """

        self.env = env

    @staticmethod
    def __Numericfun(x: int, conditList: list):
        """
        convert Integer to String based on condition.

        :param x: Number to convert
        :type x: int 
        :param conditList: condition list
        :type conditList: list 
        """
        result = ''
        for item in conditList:
            if type(item) == int:
                if x == item:
                    result = str(item)
                    break
            else:
                if x >= item[0] and x <= item[1]:
                    result = str(item[0]) + '-' + str(item[1])
                    break
        return result

    @staticmethod
    def showBoxInImage(urlPrefix, path, elements):
        """
        draw bounding boxes on images of each partition, and save them.

        :param urlPrefix: the prefix of url
        :type urlPrefix: string
        :param path: save path
        :type path: string
        :param elements: each element contains: subset/imageId and boxList of the image
        :type elements: iterator
        """
        for element in elements:
            imageSubsetAndId = element[0]
            boxList = element[1]
            imageId = imageSubsetAndId.split("/")[1]
            url = urlPrefix + imageSubsetAndId + ".jpg"
            req = urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            for box in boxList:
                xmin = box["XMin"]
                xmax = box["XMax"]
                ymin = box["YMin"]
                ymax = box["YMax"]
                text = box["Category"]
                cv2.rectangle(img, (xmin, ymin), (xmax,ymax), (0,255,0), 2)
                cv2.putText(img, text, (xmin, max(ymin,10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            cv2.imwrite(os.path.join("/dbfs" + path, imageId + ".jpg"), img)

    def __GetSynonyms(self, nlp: English, categoryList: list, inputStrList: list, length: int=3) -> list: 
        """
        Get synonyms of the inputStrList.

        :param nlp: spacy model.
        :type nlp: spacy.lang.en.English
        :param categoryList: category list.
        :type categoryList: list
        :param inputStrList: input string list.
        :type inputStrList: list
        :param length: the length of the relevant category list.
        :type length: int
        :return: a category list.
        :rtype: list
        """
        tokens = nlp(' '.join(categoryList))
        result = []

        newCategoryList = [category.lower() for category in categoryList]
        for s in inputStrList:    
            s = s.strip().capitalize()

            if s.lower() in newCategoryList:
                result.append(categoryList[newCategoryList.index(s.lower())])
            else:         
                print('There is no category called "%s", will find relevant categories.' % s)
                if s != "":
                    relList = []
                    txt = nlp(s)
                    if txt and txt.vector_norm:
                        for token in tokens:
                            if(token and token.vector_norm):
                                score = token.similarity(txt)
                                if len(relList) >= length:
                                    index = 0 # in order to contrast 
                                    value = 1.0
                                    for i in range(0,len(relList)):
                                        if relList[i][1] < value:
                                            value = relList[i][1]
                                            index = i
                                    if value < score:
                                        relList[index] = [token.text, score]

                                else:
                                    relList.append([token.text, score])

                        nameList =[li[0] for li in relList]
                        for name in nameList:
                            result.extend([category for category in categoryList if name in category])
        return list(set(result))

    def __validateEDA(self, edaFilterList: dict, numericSelection: list=None, categorySelection: list=None, boolSelection: list=None) -> list:
        """
        The function to check the edaFilterList.

        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :param numericSelection: 'Area', 'Height', 'Width', 'LuminanceStd', 'LuminanceMean', 'BoxNumberPerImage', int or tuple with len=2 in every item in the list.
        :type numericSelection: list
        :param categorySelection: 'Category' and 'Mode', string every item in the list.
        :type categorySelection: list
        :param boolSelection: 'IsTruncated' and etc, bool every item in the list.
        :type boolSelection: list
        :return: a new eda filter list.
        :rtype: list
        """
        if numericSelection:
            numericSelectionLower = [s.lower() for s in numericSelection]   
        if categorySelection:
            categorySelectionLower = [s.lower() for s in categorySelection] 
        if boolSelection:
            boolSelectionLower = [s.lower() for s in boolSelection] 
        
        newEDAList = {}
        if not edaFilterList:
            return None

        if type(edaFilterList) != dict:
            raise ValueError("The edaFilterList must be a dict.")

        for edaName, conditList in edaFilterList.items():
            if type(edaName) != str:
                raise ValueError('The edaName must be a string.')    
            edaName = edaName.strip().lower()
        
            #if eda is luminance and for image, then add image prefix(only bbox has boolSelection)
            if boolSelection is None and edaName in ['luminancestd', 'luminancemean']:
                edaName = 'image'+ edaName
            
            if type(conditList) != list:
                raise ValueError('The filter condition must be a list.')

            if numericSelection and edaName in numericSelectionLower:
                edaName = numericSelection[numericSelectionLower.index(edaName)]
                for condit in conditList:
                    if type(condit) == int or (type(condit) == tuple and len(condit) == 2 and type(condit[0]) == int and type(condit[1]) == int):
                        continue
                    else:
                        raise ValueError("The numeric edaName '%s' condition's element must be int or tuple with len=2." % edaName)
                newEDAList[edaName] = conditList
            
            elif categorySelection and edaName in categorySelectionLower:
                edaName = categorySelection[categorySelectionLower.index(edaName)]
                for condit in conditList:
                    if type(condit) != str:
                        raise ValueError("The category edaName '%s' condition's elements must be string." % edaName)

                if edaName == 'Category':
                    #get category Synonyms
                    from .._open_image import OpenImage
                    categoryList = self.GetCategories(OpenImage._OpenImage__table_category)
                    newConditList = self.__GetSynonyms(OpenImage._OpenImage__model_spacy, categoryList, conditList)
                    newEDAList[edaName] = newConditList
                else:
                    newEDAList[edaName] = conditList
            
            elif boolSelection and edaName in boolSelectionLower:
                edaName = boolSelection[boolSelectionLower.index(edaName)]
                newConditList = []
                for condit in conditList:
                    if type(condit) != bool:
                        raise ValueError("The bool edaName '%s' condition's elements must be bool." % edaName)

                    condit = 1 if condit else 0
                    newConditList.append(condit)
                newEDAList[edaName] = newConditList
            else:
                raise ValueError("The edaName '%s' is invalid." % edaName)
            
        return newEDAList

   
    @multimethod(PdDataFrame, PdDataFrame, PdDataFrame, list, list, dict)
    def SearchImagesOnEDA(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterList):
        """
        The function to search images by the edaFilterList.

        :param imageInfoTable: image info table.
        :type imageInfoTable: PdDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param categoryTable: category table.
        :type categoryTable: PdDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all boxes).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: search result, eda name list, category list.
        :rtype: PdDataFrame, list, list
        """
        numericSelection = ['ImageLuminanceMean', 'ImageLuminanceStd', 'Width', 'Height', 'Area', 'BoxNumberPerImage']
        categorySelection = ['Mode', 'Category']
    
        #check the edaFilterList
        modifiedEdaFilterList = self.__validateEDA(edaFilterList, numericSelection, categorySelection)

        result = None
        edaNameList = None

        
        if imageIDList and boxIDList :
            result = imageInfoTable[imageInfoTable.index.isin(imageIDList)]
            logging.warning("the imageIDList and boxIDList shouldn't exist together.")
        elif imageIDList and not boxIDList:
            result = imageInfoTable[imageInfoTable.index.isin(imageIDList)]
        
        elif boxIDList and not imageIDList:
            imageIDListBox = bboxInfoTable[bboxInfoTable.index.isin(boxIDList)]['ImageID'].tolist()
            result = imageInfoTable[imageInfoTable.index.isin(imageIDListBox)]
        else:
            #This means user does not give any image ids or bbox ids then search on the imageInfoTable.
            result = imageInfoTable
        
        #add BoxNumber column
        result = result.assign(BoxNumberPerImage = result['BoxIDList'].map(lambda x: len(x)).values)
        #add Area column
        result.eval('Area = Width*Height', inplace=True)
    
        filtermask = ''
        imageIDListCate = []
        categoryList = None
        if modifiedEdaFilterList:
            edaNameList = [edaName for edaName in modifiedEdaFilterList.keys()]
        
            for edaName, condit in modifiedEdaFilterList.items():
                if edaName in numericSelection:
                    if len(condit) > 0:
                        filtermask += '('
                        for item in condit:
                            if type(item) == int:
                                filtermask += '{edaName} == {value} or '.format(edaName=edaName, value=item)
                            else:
                                filtermask += '({edaName} >= {left} and {edaName} <= {right}) or '.format(edaName=edaName, left=item[0], right=item[1])
                        filtermask = filtermask.rstrip('or ')
                        filtermask += ') and '
                elif edaName in categorySelection:
                    #Mode
                    if edaName == categorySelection[0]:
                        filtermask += '{edaName} in {conditList} and '.format(edaName=edaName, conditList=condit)
                    #Category
                    else:    
                        categoryList = condit.copy()
                        imageIDListsCate = categoryTable[categoryTable.index.isin(condit)]['ImageIDList'].tolist()
                        imageIDListCate = list(set().union(*imageIDListsCate))
                        filtermask += 'index in @imageIDListCate and '
                else:
                    raise ValueError('The edaName %s is invalid.' % edaName)
                
            #filteremask sample: Mode in ['RGB'] and (Width == 1024 or (Width >= 0 and Width <= 400)) and 
            #(Height == 1024 or (Height >= 0 and Height <= 400)) and ((BoxNumberPerImage >= 0 and BoxNumberPerImage <= 100)) 
            #and ((ImageLuminanceStd >= 0 and ImageLuminanceStd <= 200))
            filtermask = filtermask.rstrip('and ')
            result = result.query(filtermask)

            if result.shape[0] == 0:
                return result, edaNameList, categoryList
        
            if set(edaNameList)<= {'ImageLuminanceMean', 'ImageLuminanceStd'}:
                result = result[['ImageLuminanceMean', 'ImageLuminanceStd']]
            elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
                result = result[['Width', 'Height']]
            else:
                if categoryList:
                    result = result.assign(Category = result['CategoryList'].map(lambda x: ','.join(set([lis[0] for lis in x]))).values)
                    temp = result.drop(columns=['Category','CategoryList'],axis=1)
                    result = temp.join(result['Category'].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename('Category'))
                    result = result[result['Category'].isin(categoryList)]
                result = result[edaNameList]
                for edaName, condit in modifiedEdaFilterList.items():
                    if edaName in numericSelection:
                        result.loc[:, edaName] = result[edaName].map(lambda x: self.__Numericfun(x, condit))
    
        return result, edaNameList, categoryList
    
    @multimethod(SparkDataFrame, SparkDataFrame, SparkDataFrame, list, list, dict)
    def SearchImagesOnEDA(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterDict):
        """
        The function to search images by the edaFilterList.

        :param imageInfoTable: image info table.
        :type imageInfoTable: SparkDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param categoryTable: category table.
        :type categoryTable: SparkDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all boxes).
        :type boxIDList: list
        :param edaFilterDict: a dict of eda filters[(edaname, filtercondition)].
        :type edaFilterDict: dict
        :return: search result, eda name list, category list.
        :rtype: SparkDataFrame, list, list
        """
        numericSelection = ['ImageLuminanceMean', 'ImageLuminanceStd', 'Width', 'Height', 'Area', 'BoxNumberPerImage']
        categorySelection = ['Mode', 'Category']
        spark = SparkSession.builder.getOrCreate()
        #check the edaFilterList
    
        modifiedEdaFilterDict = self.__validateEDA(edaFilterDict, numericSelection, categorySelection)
        result = None
        edaNameList = None
    
        if imageIDList and boxIDList:
            temp = spark.sparkContext.parallelize(imageIDList).map(lambda x : (x, )).toDF(["ImageID"])
            result = temp.join(imageInfoTable, ["ImageID"], "inner")
            logging.warning("The imageIDList and boxIDList shouldn't exist together.")
        elif imageIDList and not boxIDList:
            temp = spark.sparkContext.parallelize(imageIDList).map(lambda x : (x, )).toDF(["ImageID"])
            result = temp.join(imageInfoTable, ["ImageID"], "inner")
        elif boxIDList and not imageIDList:
            temp = spark.sparkContext.parallelize(boxIDList).map(lambda x : (x, )).toDF(["BoxID"])
            boxTemp = temp.join(bboxInfoTable, ["BoxID"], "inner")
            result = boxTemp.join(imageInfoTable, ["ImageID"], "inner")
        else:
            result = imageInfoTable
            
        #add BoxNumber column
        result = result.withColumn('BoxNumberPerImage', size('BoxIDList'))
        #add Area column
        result = result.withColumn('Area', result["Height"] * result["Width"])
    
        filtermask = ''
        imageIDListCate = []
        categoryList = None
        func = ImageSelector.__Numericfun
        if modifiedEdaFilterDict:
            edaNameList = [edaName for edaName in modifiedEdaFilterDict.keys()]
            for edaName, condit in modifiedEdaFilterDict.items():
                if edaName in numericSelection:
                    if len(condit) > 0:
                        filtermask += '('
                        for item in condit:
                            if type(item) == int:
                                filtermask += '{edaName} == {value} or '.format(edaName=edaName, value=item)
                            else:
                                filtermask += '({edaName} >= {left} and {edaName} <= {right}) or '.format(edaName=edaName, left=item[0], right=item[1])
                        filtermask = filtermask.rstrip('or ')
                        filtermask += ') and '
                elif edaName in categorySelection:
                    #Mode
                    if edaName == categorySelection[0]:
                        if len(condit) == 1:
                            filtermask += "{edaName} == '{conditList}' and " .format(edaName=edaName, conditList=condit[0])
                        else:
                            filtermask += '{edaName} in {conditList} and '.format(edaName=edaName, conditList=tuple(condit))
                    #Category
                    else:
                        # filter operateion. Don't generate filtermask
                        # filter categoryTable with categoryList and flat imageIDList of it
                        # and then join result 
                        categoryList = condit.copy()
                        imageIDListDf = categoryTable[categoryTable.Category.isin(condit)]
                        imageIDListDf = imageIDListDf.withColumn("ImageID", explode(imageIDListDf.ImageIDList))
                        result = imageIDListDf.join(result, ["ImageID"], "inner")
                else:
                    raise ValueError('The edaName %s is invalid.' % edaName)

            filtermask = filtermask.rstrip('and ')
            result.createOrReplaceTempView("result")
            result = spark.sql("select * from result where " + filtermask)
            if set(edaNameList)<= {'ImageLuminanceMean', 'ImageLuminanceStd'}:
                result = result[['ImageID','ImageLuminanceMean', 'ImageLuminanceStd']]
            elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
                result = result[['ImageID','Width', 'Height']]
            else:
                result = result[edaNameList+['ImageID']]
                for edaName, condit in modifiedEdaFilterDict.items():
                    if edaName in numericSelection:
                        numUdf = udf(lambda x : func(x, condit))
                        result = result.withColumn(edaName, numUdf(result[edaName]))
        return result, edaNameList, categoryList

    @multimethod(PdDataFrame, list, dict)
    def SearchBoxesOnEDA(self, bboxInfoTable, boxIDList, edaFilterList):
        """
        The function to search boxes by the edaFilterList.

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param boxIDList: a list of boxIDs(if None, means all boxes).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: search result, eda name list.
        :rtype: PdDataFrame, list
        """
        numericSelection = ['Area', 'LuminanceMean', 'LuminanceStd', 'Width', 'Height']
        categorySelection = ['Category']
        boolSelection = ['IsOccluded', 'IsTruncated', 'IsGroupOf', 'IsDepiction', 'IsInside']
    
        #check the edaFilterList
        modifiedEdaFilterList = self.__validateEDA(edaFilterList, numericSelection, categorySelection, boolSelection)
    
        result = None
        edaNameList = None
        
        if boxIDList:
            result = bboxInfoTable[bboxInfoTable.index.isin(boxIDList)]
        else:
            #This means user does not give any box ids then search on the bboxInfoTable.
            result = bboxInfoTable
    
        #add Width, Height column
        result = result.eval('Width = XMax - XMin', inplace=False)
        result.eval('Height = YMax - YMin', inplace=True)
    
        filtermask = ''
        if modifiedEdaFilterList:
            edaNameList = [edaName for edaName in modifiedEdaFilterList.keys()]
        
            for edaName, condit in modifiedEdaFilterList.items():
                if edaName in numericSelection:
                    if len(condit) > 0:
                        filtermask += '('
                        for item in condit:
                            if type(item) == int:
                                filtermask += '{edaName} == {value} or '.format(edaName=edaName, value=item)
                            else:
                                filtermask += '({edaName} >= {left} and {edaName} <= {right}) or '.format(edaName=edaName, left=item[0], right=item[1])
                        filtermask = filtermask.rstrip('or ')
                        filtermask += ') and '
                elif edaName in (categorySelection + boolSelection):
                    filtermask += '{edaName} in {conditList} and '.format(edaName=edaName, conditList=condit)
                else:
                    raise ValueError('The edaName %s is invalid.' % edaName)
                
            filtermask = filtermask.rstrip('and ')
            result = result.query(filtermask)

            if set(edaNameList)<= {'LuminanceMean', 'LuminanceStd'}:
                result = result[['LuminanceMean', 'LuminanceStd']]
            elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
                result = result[['Width', 'Height']]
            else:
                result = result[edaNameList]
                for edaName, condit in modifiedEdaFilterList.items():
                    if edaName in numericSelection:
                        result.loc[:, edaName] = result[edaName].map(lambda x: self.__Numericfun(x, condit))
                    
        return result, edaNameList
    
    @multimethod(SparkDataFrame, list, dict)
    def SearchBoxesOnEDA(self, bboxInfoTable, boxIDList, edaFilterDict):
        """
        The function to search boxes by the edaFilterList.

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param boxIDList: a list of boxIDs(if None, means all boxes).
        :type boxIDList: list
        :param edaFilterDict: a dict of eda filters[(edaname, filtercondition)].
        :type edaFilterDict: dict
        :return: search result, eda name list.
        :rtype: SparkDataFrame, list
        """
        numericSelection = ['Area', 'LuminanceMean', 'LuminanceStd', 'Width', 'Height']
        categorySelection = ['Category']
        boolSelection = ['IsOccluded', 'IsTruncated', 'IsGroupOf', 'IsDepiction', 'IsInside']
        spark = SparkSession.builder.getOrCreate()
        #check the edaFilterList
        modifiedEdaFilterDict = self.__validateEDA(edaFilterDict, numericSelection, categorySelection, boolSelection)
    
        result = None
        edaNameList = None
        func = ImageSelector.__Numericfun
        if boxIDList:
            temp = spark.sparkContext.parallelize(boxIDList).map(lambda x : (x, )).toDF(["BoxID"])
            result = temp.join(bboxInfoTable, ["BoxID"], "inner")
        else:
            #This means user does not give any box ids then search on the bboxInfoTable.
            result = bboxInfoTable
      
        #add Width, Height column
        result = result.withColumn('Width', result["XMax"] - result["XMin"])
        result = result.withColumn('Height', result["YMax"] - result["YMin"])

        filtermask = ''
        if modifiedEdaFilterDict:
            edaNameList = [edaName for edaName in modifiedEdaFilterDict.keys()]

            for edaName, condit in modifiedEdaFilterDict.items():
                if edaName in numericSelection:
                    if len(condit) > 0:
                        filtermask += '('
                        for item in condit:
                            if type(item) == int:
                                filtermask += '{edaName} == {value} or '.format(edaName=edaName, value=item)
                            else:
                                filtermask += '({edaName} >= {left} and {edaName} <= {right}) or '.format(edaName=edaName, left=item[0], right=item[1])
                        filtermask = filtermask.rstrip('or ')
                        filtermask += ') and '
                elif edaName in (categorySelection + boolSelection):
                    if len(condit) == 1:
                        filtermask += "{edaName} == '{conditList}' and ".format(edaName=edaName, conditList=condit[0])
                    else:
                        filtermask += '{edaName} in {conditList} and '.format(edaName=edaName, conditList=tuple(condit))
                else:
                    raise ValueError('The edaName %s is invalid.' % edaName)
        
            filtermask = filtermask.rstrip('and ')
            result.createOrReplaceTempView("result")
            result = spark.sql("select * from result where " + filtermask)
        
            if set(edaNameList)<= {'LuminanceMean', 'LuminanceStd'}:
                result = result[['BoxID','LuminanceMean', 'LuminanceStd']]
            elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
                result = result[['BoxID','Width', 'Height']]
            else:
                result = result[edaNameList + ["BoxID"]]
                for edaName, condit in modifiedEdaFilterDict.items():
                    if edaName in numericSelection:
                        numUdf = udf(lambda x : func(x, condit))
                        result = result.withColumn(edaName, numUdf(result[edaName]))
        return result, edaNameList

    @multimethod(PdDataFrame, PdDataFrame, PdDataFrame, list, dict)
    def AnalyzeImages(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, edaFilterList):
        """
        Analyze images depending on EDA metrics and will return different kind of metrics:
        (1) Grayscale or color image distribution
        (2) Bounding boxes number distribution
        (3) Image size distribution
        (4) Image category distribution
        (5) Image luminance distribution
        (6) Image quality distribution (images with low night noise distribution)
        (7) ...

        :param imageInfoTable: image info table.
        :type imageInfoTable: PdDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param categoryTable: category table.
        :type categoryTable: PdDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """

        rdic = {}
        target = None
        result, edaNameList, _ = self.SearchImagesOnEDA(imageInfoTable, bboxInfoTable, categoryTable, imageIDList, [], edaFilterList)
    
        if result is None or result.shape[0] == 0 or not edaNameList:
            return ImageAnalyzeResult(self.env, rdic)
    
        result.reset_index(inplace=True)
        if set(edaNameList)<= {'ImageLuminanceMean', 'ImageLuminanceStd'}:
            #Luminance distribution 
            target = 'Luminance'
            rdic['Luminance'] = dict(zip(result['ImageLuminanceMean'].tolist(), result['ImageLuminanceStd'].tolist()))
        elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
            #Area distribution 
            target = 'Area'
            rdic['Area'] = dict(zip(result['Width'].tolist(), result['Height'].tolist()))
        else:   
            #combination distribution
            target = 'Distribution'
            series = result.groupby(edaNameList, observed=True)['ImageID'].count()
            series.sort_values(ascending=True, inplace=True)
            keyList = series.index.tolist()
            for i, row in enumerate(keyList):
                key = ''
                if type(row) == str:
                    key = row
                else:
                    key = ','.join(row)
                keyList[i] = key
            rdic['Distribution'] = OrderedDict(zip(keyList, series.tolist()))
    
        return ImageAnalyzeResult(self.env, rdic, target, edaNameList) 
    
    @multimethod(SparkDataFrame, SparkDataFrame, SparkDataFrame, list, dict)
    def AnalyzeImages(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, edaFilterDict):
        """
        Analyze images depending on EDA metrics and will return different kind of metrics:
        (1) Grayscale or color image distribution
        (2) Bounding boxes number distribution
        (3) Image size distribution
        (4) Image category distribution
        (5) Image luminance distribution
        (6) Image quality distribution (images with low night noise distribution)
        (7) ...

        :param imageInfoTable: image info table.
        :type imageInfoTable: SparkDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param categoryTable: category table.
        :type categoryTable: SparkDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param edaFilterDict: a dict of eda filters[(edaname, filtercondition)].
        :type edaFilterDict: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """
        rdic = {}
        target = None
        # result : imageInfoTable
        result, edaNameList, _ = self.SearchImagesOnEDA(imageInfoTable, bboxInfoTable, categoryTable, imageIDList, [], edaFilterDict)
        
        if result is None or result.count() == 0 or len(result.columns) == 0 or not edaNameList:
            return ImageAnalyzeResult(self.env, rdic)
        
        if set(edaNameList)<= {'ImageLuminanceMean', 'ImageLuminanceStd'}:
            #Luminance distribution
            resultCollect = result.select('ImageLuminanceMean', 'ImageLuminanceStd').collect()
            target = 'Luminance'
            rdic['Luminance'] = dict(zip([row["ImageLuminanceMean"] for row in resultCollect], [row["ImageLuminanceStd"] for row in resultCollect]))
        elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
            #Area distribution 
            resultCollect = result.select('Width', 'Height').collect()
            target = 'Area'
            rdic['Area'] = dict(zip([row["Width"] for row in resultCollect], [row["Height"] for row in resultCollect]))
        else:
            #combination distribution
            target = 'Distribution'
            df = result.groupby(edaNameList).count().sort("count")
            resultCollect = df.collect()
            keyList = []
            for row in resultCollect:
                element = ""
                for key in edaNameList:
                    element += str(row[key]) + ", "
                element = element.rstrip(", ")
                keyList.append(element)
            rdic['Distribution'] = OrderedDict(zip(keyList, [row["count"] for row in resultCollect]))
        return ImageAnalyzeResult(self.env, rdic, target, edaNameList) 

    @multimethod(PdDataFrame, list, dict)
    def AnalyzeImagesByBoundingBoxes(self, bboxInfoTable, boxIDList, edaFilterList):
        """
        Analyze bounding boxes depending on EDA metrics and will return different kind of metrics:
        (1) bb-level category distribution
        (2) bb-level attributes distribution like isOccluded bbs distribution, isTruncated bbs distribution, isGrouped bbs distribution, ...
        (3) bb size distribution
        (4) bb luminance distribution
        (5) ...

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """
        rdic = {}
        target = None
        result, edaNameList = self.SearchBoxesOnEDA(bboxInfoTable, boxIDList, edaFilterList)
      
        if result is None or result.shape[0] == 0 or not edaNameList:
            return ImageAnalyzeResult(self.env, rdic) 
    
        result.reset_index(inplace=True)
        if set(edaNameList)<= {'LuminanceMean', 'LuminanceStd'}:
            #Luminance distribution 
            target = 'Luminance'
            rdic['Luminance'] = dict(zip(result['LuminanceMean'].tolist(), result['LuminanceStd'].tolist()))
        elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
            #Area distribution 
            target = 'Area'
            rdic['Area'] = dict(zip(result['Width'].tolist(), result['Height'].tolist()))
        else:   
            #combination distribution
            target = 'Distribution'
            series = result.groupby(edaNameList, observed=True)['BoxID'].count()
            series.sort_values(ascending=True, inplace=True)
            keyList = series.index.tolist()
            for i, row in enumerate(keyList):
                key = ''
                if type(row) == str:
                    key = row
                elif type(row) == int:
                    key = str(row)
                else:
                    key = ','.join([str(el) for el in row])
                keyList[i] = key
            rdic['Distribution'] = OrderedDict(zip(keyList, series.tolist()))
    
        return ImageAnalyzeResult(self.env, rdic, target, edaNameList)   

    @multimethod(SparkDataFrame, list, dict)
    def AnalyzeImagesByBoundingBoxes(self, bboxInfoTable, boxIDList, edaFilterDict):
        """
        Analyze bounding boxes depending on EDA metrics and will return different kind of metrics:
        (1) bb-level category distribution
        (2) bb-level attributes distribution like isOccluded bbs distribution, isTruncated bbs distribution, isGrouped bbs distribution, ...
        (3) bb size distribution
        (4) bb luminance distribution
        (5) ...

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterDict: a dict of eda filters[(edaname, filtercondition)].
        :type edaFilterDict: dict
        :return: the analyze result.
        :rtype: ImageAnalyzeResult
        """
        rdic = {}
        target = None
        result, edaNameList = self.SearchBoxesOnEDA(bboxInfoTable, boxIDList, edaFilterDict)
    
        if result is None or result.count() == 0 or not edaNameList:
            return ImageAnalyzeResult(self.env, rdic) 
    
        if set(edaNameList)<= {'LuminanceMean', 'LuminanceStd'}:
            #Luminance distribution 
            resultCollect = result.select('LuminanceMean', 'LuminanceStd').collect()
            target = 'Luminance'
            rdic['Luminance'] = dict(zip([row["LuminanceMean"] for row in resultCollect], [row["LuminanceStd"] for row in resultCollect]))
        elif set(edaNameList) <= {'Width', 'Height', 'Area'}:
            #Area distribution 
            target = 'Area'
            resultCollect = result.select('Width', 'Height').collect()
            rdic['Area'] = dict(zip([row["Width"] for row in resultCollect], [row["Height"] for row in resultCollect]))
        else:
            #combination distribution
            target = 'Distribution'
            df = result.groupby(edaNameList).count().sort("count")
            resultCollect = df.collect()
            keyList = []
            for row in resultCollect:
                element = ""
                for key in edaNameList:
                    element += str(row[key]) + ", "
                element = element.rstrip(", ")
                keyList.append(element)
            rdic['Distribution'] = OrderedDict(zip(keyList, [row["count"] for row in resultCollect]))
        return ImageAnalyzeResult(self.env, rdic, target, edaNameList)
    
    @multimethod(PdDataFrame, PdDataFrame, PdDataFrame, list, list, dict)
    def SelectImages(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterList):
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

        :param imageInfoTable: image info table.
        :type imageInfoTable: PdDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param categoryTable: category table.
        :type categoryTable: PdDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: a dict like {ImageID: [bboxID1, bboxID2,...]}.
        :rtype: dict
        """
        result, _, categoryList = self.SearchImagesOnEDA(imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterList)
    
        if not categoryList and not boxIDList:
            result = imageInfoTable[imageInfoTable.index.isin(result.index.tolist())]
            return dict(zip(result.index.tolist(), result['BoxIDList'].tolist()))
        else:
            result = bboxInfoTable[bboxInfoTable['ImageID'].isin(result.index.tolist())]
            if categoryList:
                result = result[result['Category'].isin(categoryList)]
            if boxIDList:      
                 result = result[result.index.isin(boxIDList)]
        
            result = result.reset_index().groupby('ImageID', observed=True)['BoxID'].apply(list)
            return dict(zip(result.index.tolist(), result.tolist()))

    @multimethod(SparkDataFrame, SparkDataFrame, SparkDataFrame, list, list, dict)
    def SelectImages(self, imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterDict):
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

        :param imageInfoTable: image info table.
        :type imageInfoTable: SparkDataFrame
        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param categoryTable: category table.
        :type categoryTable: SparkDataFrame
        :param imageIDList: a list of imageIDs(if None, means all images).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterDict: a dict of eda filters[(edaname, filtercondition)].
        :type edaFilterDict: dict
        :return: a dict like {ImageID: [bboxID1, bboxID2,...]}.
        :rtype: dict
        """
        result, _, categoryList = self.SearchImagesOnEDA(imageInfoTable, bboxInfoTable, categoryTable, imageIDList, boxIDList, edaFilterDict)
        spark = SparkSession.builder.getOrCreate()
        if not categoryList and not boxIDList:
            temp = result.select("ImageID")
            result = temp.join(imageInfoTable,["ImageID"], "inner")
            return dict(zip(result.select("ImageID").rdd.map(lambda x : x[0]).collect(), result.select("BoxIDList").rdd.map(lambda x : x[0]).collect()))
        else:
            temp = result.select("ImageID")
            result = temp.join(bboxInfoTable,["ImageID"], "inner")
            if categoryList:
                result = result[result.Category.isin(categoryList)]
            if boxIDList:
                temp = spark.sparkContext.parallelize(boxIDList).map(lambda x : (x, )).toDF(["BoxID"])
                result = temp.join(result,["BoxID"], "inner")
            result = result.dropDuplicates().groupby('ImageID').agg(F.collect_list(F.col("BoxID")).alias("BoxList"))
            boxCollect = result.select("BoxList").rdd.map(lambda x : x[0]).collect()
            imageCollect = result.select("ImageID").rdd.map(lambda x : x[0]).collect()
            return dict(zip(imageCollect, boxCollect))

    @multimethod(PdDataFrame, list, dict)
    def SelectBboxs(self, bboxInfoTable, boxIDList, edaFilterList):
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

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterList: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterList: dict
        :return: a boxID list of the query results.
        :rtype: list
        """
        result, _ = self.SearchBoxesOnEDA(bboxInfoTable, boxIDList, edaFilterList)
        return result.index.tolist()

    @multimethod(SparkDataFrame, list, dict)
    def SelectBboxs(self, bboxInfoTable, boxIDList, edaFilterDict):
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

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param edaFilterDict: a dict of eda filters{edaname: filtercondition}.
        :type edaFilterDict: dict
        :return: a boxID list of the query results.
        :rtype: list
        """
        result, _ = self.SearchBoxesOnEDA(bboxInfoTable, boxIDList, edaFilterDict)
        return result.select("BoxID").rdd.map(lambda x : x[0]).collect()
        
    @multimethod(PdDataFrame)
    def GetCategories(self, categoryTable):
        """
        Get all categories.

        :param categoryTable: category table.
        :type categoryTable: PdDataFrame
        :return: a category list.
        :rtype: list
        """
        return categoryTable.index.tolist()

    @multimethod(SparkDataFrame)
    def GetCategories(self, categoryTable):
        """
        Get all categories.

        :param categoryTable: category table.
        :type categoryTable: SparkDataFrame
        :return: a category list.
        :rtype: list
        """
        return categoryTable.select("Category").rdd.map(lambda x : x[0]).collect()

    @multimethod(PdDataFrame, PdDataFrame, list, list, str, str, int)
    def ShowImages(self, bboxInfoTable, urlTable, imageIDList, boxIDList, urlPrefix, path, limitedNum):
        """
        Show bounding boxes in images and will download images with drawn bounding boxes to local path. 

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: PdDataFrame
        :param urlTable: image url table.
        :type urlTable: PdDataFrame
        :param imageIDList: a list of imageIDs(if None, select image id by boxIDList).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all bbox).
        :type boxIDList: list
        :param urlPrefix: the download url prefix.
        :type urlPrefix: str
        :param path: local save path.
        :type path: str
        :param limitedNum: the download image number.
        :type limitedNum: int
        """

        if not os.path.exists(path):
            os.makedirs(path)
        
        if not boxIDList and not imageIDList:
            raise ValueError("Input can not be empty.")  
            
        if boxIDList:
            bboxInfoTable = bboxInfoTable[bboxInfoTable.index.isin(boxIDList)]
        if not imageIDList:
            df = bboxInfoTable.drop_duplicates(subset = ["ImageID"])
            imageIDList = df["ImageID"].tolist()
    
        count = 0
        print('download start...')
        for imageId in imageIDList: 
            if count == limitedNum:
                break;
            url = urlPrefix + urlTable.loc[imageId, 'Subset'] + "/" + imageId + ".jpg"
            req = urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1)
            multiBox = bboxInfoTable[bboxInfoTable["ImageID"] == imageId]
            #if no box, continue
            if multiBox.shape[0]==0:
                continue
            labelLists = multiBox["Category"].tolist()
            xminLists = multiBox["XMin"].tolist()
            xmaxLists = multiBox["XMax"].tolist()
            yminLists = multiBox["YMin"].tolist()
            ymaxLists = multiBox["YMax"].tolist()
            for i in range(len(labelLists)):
                cv2.rectangle(img, (xminLists[i], yminLists[i]), (xmaxLists[i],ymaxLists[i]), (0,255,0), 2)
                text = labelLists[i]
                cv2.putText(img, text, (xminLists[i], max(yminLists[i],10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            cv2.imwrite(os.path.join(path, imageId + ".jpg"), img)
            count += 1

        print('finish.')

    @multimethod(SparkDataFrame, dict, list, list, str, str, int)
    def ShowImages(self, bboxInfoTable, urlDict, imageIDList, boxIDList, urlPrefix, path, limitedNum):
        """
        Show bounding boxes in images and will download images with drawn bounding boxes to dbfs path. 

        :param bboxInfoTable: bounding box info table.
        :type bboxInfoTable: SparkDataFrame
        :param urlDict: image url table.
        :type urlDict: dict
        :param imageIDList: a list of imageIDs(if None, select image id by boxIDList).
        :type imageIDList: list
        :param boxIDList: a list of boxIDs(if None, means all boxes).
        :type boxIDList: list
        :param urlPrefix: the download url prefix.
        :type urlPrefix: str
        :param path: dbfs save path.
        :type path: str
        :param limitedNum: the download image number.
        :type limitedNum: int
        """

        if not boxIDList and not imageIDList:
            raise ValueError("Input can not be empty.")
        if path.startswith("dbfs:"):
            path = path.split(":")[1]
        elif path.startswith("/"):
            path = path
        else:
            raise ValueError("The path is invalid")
        
        spark = SparkSession.builder.getOrCreate()
        if boxIDList:
            temp = spark.sparkContext.parallelize(boxIDList).map(lambda x : (x, )).toDF(["BoxID"])
            bboxInfoTable = temp.join(bboxInfoTable,["BoxID"], "inner")
        if imageIDList:
            temp = spark.sparkContext.parallelize(imageIDList).map(lambda x : (x, )).toDF(["ImageID"])
            bboxInfoTable = temp.join(bboxInfoTable,["ImageID"], "inner")
        func = ImageSelector.showBoxInImage
        result = bboxInfoTable.withColumn("BoxList", F.struct(F.col("XMin"),F.col("XMax"),F.col("YMin"),F.col("YMax"),F.col("Category")))
        result = result.groupBy("ImageID").agg(F.collect_list("BoxList").alias("BoxList")).select("ImageID", "BoxList")
        urlUdf = udf(lambda x : urlDict[x] + "/" + x)
        # result : "ImageID": subset/imageId.jpg, "BoxList" : ("XMin")
        result = result.withColumn("ImageID", urlUdf(result["ImageID"]))

        if not limitedNum:
            result = result.limit(limitedNum)
        result.rdd.foreachPartition(lambda x : func(urlPrefix,path,x))
    