"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

import numpy as np
import requests
import json

from .queryperiod import QueryPeriod
from .aggregatedetails import AggregateDetails
from .aggregatedetails import AggregateType
from .datavaluejson import DataValueJSON
from .annotationvaluejson import AnnotationValueJSON
from .itempathjson import ItemPathJSON
from .browsemodeljson import BrowseModelJSON
from .browseresultmodeljson import BrowseResultModelJSON
from .browseitemmodeljson import BrowseItemModelJSON
from .browseresultitemmodeljson import BrowseResultItemModelJSON
from .historyupdatedatamodeljson import HistoryUpdateDataModelJSON
from .historyupdatedataitemmodeljson import HistoryUpdateDataItemModelJSON
from .readitemmodeljson import ReadItemModelJSON
from .readmodeljson import ReadModelJSON
from .readresultitemmodeljson import ReadResultItemModelJSON
from .readresultmodeljson import ReadResultModelJSON
from .epmdataobject import EpmDataObject, EpmDataObjectPropertyNames, EpmDataObjectAttributeIds, getDiscreteValue, getDomainValue
from .epmobject import EpmObject
from .basicvariable import BasicVariable, BasicVariableAlreayExistsException, BasicVariableInvalidNameException
from .writeitemmodeljson import WriteItemModelJSON
from .writemodeljson import WriteModelJSON
from .itempathandcontinuationpointjson import ItemPathAndContinuationPointJSON
from .historyrawmodeljson import HistoryRawModelJSON
from .numpyextras import NumpyExtras
from .historyprocessedmodeljson import HistoryProcessedModelJSON
from .authorizationservice import AuthorizationService
from .querymodeljson import QueryModelJSON
from .queryresultmask import QueryResultMask
from .queryresultitemmodeljson import QueryResultItemModelJSON
from .diagnosticmodeljson import DiagnosticModelJSON
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .nodeclassmask import NodeClassMask
from .dataobjectsfilter import DataObjectsFilterType, DataObjectsFilter
from .domainfilter import DomainFilter
from .nodeattributes import NodeAttributes
from .portalresources import PortalResources
from .processorresources import ProcessorResources
from .historyupdatetype import HistoryUpdateType

import collections


class EpmConnection(object):
    """description of class"""

    def __init__(self, authServer, webApi, userName, password, clientId = 'EpmRestApiClient', programId = 'B39C3503-C374-3227-83FE-EEA7A9BD1FDC'):
        self._webApi = webApi
        self._authorizationService = AuthorizationService(authServer, clientId, programId, userName, password)

    # Public Methods
    def getPortalResourcesManager(self):
      return PortalResources(self._authorizationService, self._webApi)

    def getProcessorResourcesManager(self):
      return ProcessorResources(self._authorizationService, self._webApi)

    def getDataObjects(self, names = None, attributes = DataObjectAttributes.Unspecified):
      if names == None:
        return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent)
      else:
        return self._getDataObjects(names, attributes)

    def getBasicVariables(self, names = None, attributes = DataObjectAttributes.Unspecified):
      if names == None:
        return self._getAllDataObjects(attributes, EpmNodeIds.HasTags, '/1:BasicVariables')
      else:
        return self._getDataObjects(names, attributes, '/1:BasicVariables')

    def getExpressionVariables(self, names = None, attributes = DataObjectAttributes.Unspecified):
      if names == None:
        return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent, '/1:ExpressionVariables')
      else:
        return self._getDataObjects(names, attributes, '/1:ExpressionVariables')

    def createBasicVariable(self, name, description=None, tagType = None, realTimeEnabled = None, deadBandFilter = None, deadBandUnit = None, 
            eu = None, lowLimit = None, highLimit = None, scaleEnable = None, inputLowLimit = None, inputHighLimit = None, clamping = None, 
            domain = None, interface = None, ioTagAddress = None, processingEnabled = None, isRecording = None, isCompressing = None, 
            storeMillisecondsEnabled = None, storageSet = None):

      token = self._authorizationService.getToken()
      url = self._webApi + '/epm/v1/BV'
      header = {'Authorization': 'Bearer {}'.format(token)}

      discrete = getDiscreteValue(domain)

      jsonRequest = { 'Items' : [ { 'name' : name, 'description' : description if description != None else '', 
                                   'tagType' : tagType, 'realTimeEnabled' : realTimeEnabled, 
                                   'eu' : eu, 'lowLimit' : lowLimit, 'highLimit' : highLimit, 'scaleEnable' : scaleEnable, 
                                   'inputLowLimit' : inputLowLimit, 'inputHighLimit' : inputHighLimit, 'rangeClamping' : clamping, 
                                   'discrete' : discrete, 'interface' : interface, 'ioTagAddress' : ioTagAddress, 'processingEnabled' : processingEnabled, 
                                   'isRecording' : isRecording, 'isCompressing' : isCompressing, 'storeMillisecondsEnabled' : storeMillisecondsEnabled, 
                                   'storageSet' : storageSet, 'deadBandFilter' : deadBandFilter, 'deadBandUnit' : deadBandUnit } ] }

      response = requests.post(url, headers=header, json=jsonRequest, verify=False)
      if response.status_code != 200:
        if response.status_code == 400:
          if 'EpmErrorTagAlreadyExists' in response.text:
            raise BasicVariableAlreayExistsException('BasicVariable ' + name + ' already exists')
          if 'Invalid format Name' in response.text:
            raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
          if 'Invalid StorageSet name' in response.text:
            raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
          if 'Invalid Interface name' in response.text:
            raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
        raise Exception("CreateBasicVariable call error + '" +  str(response.status_code) + "'. Reason: " + response.reason)

      json_result = json.loads(response.text)

      bvInfo = json_result['items'][0]

      identity = 'ns=1;i=' + str(bvInfo['id'])

      bv = BasicVariable(self, identity, name = bvInfo['name'], description = bvInfo['description'],
                deadBandFilter = bvInfo['deadBandFilter'], deadBandUnit = bvInfo['deadBandUnit'],
                eu = bvInfo['eu'], lowLimit = bvInfo['lowLimit'], highLimit = bvInfo['highLimit'],
                tagType = bvInfo['tagType'], realTimeEnabled = bvInfo['realTimeEnabled'], scaleEnable = bvInfo['scaleEnable'], 
                inputLowLimit = bvInfo['inputLowLimit'], inputHighLimit = bvInfo['inputHighLimit'], clamping = bvInfo['rangeClamping'], 
                domain = getDomainValue(bvInfo['discrete']), interface = bvInfo['interface'], ioTagAddress = bvInfo['ioTagAddress'], 
                processingEnabled = bvInfo['processingEnabled'], isRecording = bvInfo['isRecording'], isCompressing = bvInfo['isCompressing'], 
                storeMillisecondsEnabled = bvInfo['storeMillisecondsEnabled'], storageSet = bvInfo['storageSet'])

      return bv

    def updateBasicVariable(self, name, newName = None, description=None, tagType = None, realTimeEnabled = None, deadBandFilter = None, deadBandUnit = None, 
            eu = None, lowLimit = None, highLimit = None, scaleEnable = None, inputLowLimit = None, inputHighLimit = None, clamping = None, 
            domain = None, interface = None, ioTagAddress = None, processingEnabled = None, isRecording = None, isCompressing = None, 
            storeMillisecondsEnabled = None, storageSet = None):

      token = self._authorizationService.getToken()
      url = self._webApi + '/epm/v1/BV'
      header = {'Authorization': 'Bearer {}'.format(token)}

      discrete = getDiscreteValue(domain)

      jsonRequest = { 'Items' : [ { 'name' : name, 'newName' : newName, 'description' : description, 
                                   'tagType' : tagType, 'realTimeEnabled' : realTimeEnabled, 
                                   'eu' : eu, 'lowLimit' : lowLimit, 'highLimit' : highLimit, 'scaleEnable' : scaleEnable, 
                                   'inputLowLimit' : inputLowLimit, 'inputHighLimit' : inputHighLimit, 'rangeClamping' : clamping, 
                                   'discrete' : discrete, 'interface' : interface, 'ioTagAddress' : ioTagAddress, 'processingEnabled' : processingEnabled, 
                                   'isRecording' : isRecording, 'isCompressing' : isCompressing, 'storeMillisecondsEnabled' : storeMillisecondsEnabled, 
                                   'storageSet' : storageSet, 'deadBandFilter' : deadBandFilter, 'deadBandUnit' : deadBandUnit } ] }

      response = requests.patch(url, headers=header, json=jsonRequest, verify=False)
      if response.status_code != 200:
        if response.status_code == 400:
          if 'EpmErrorTagAlreadyExists' in response.text:
            raise BasicVariableAlreayExistsException('BasicVariable ' + name + ' already exists')
          if 'Invalid format Name' in response.text:
            raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
          if 'Invalid StorageSet name' in response.text:
            raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
          if 'Invalid Interface name' in response.text:
            raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
        raise Exception("CreateBasicVariable call error + '" +  str(response.status_code) + "'. Reason: " + response.reason)


    def deleteBasicVariable(self, names):

      token = self._authorizationService.getToken()
      url = self._webApi + '/epm/v1/BV'
      header = {'Authorization': 'Bearer {}'.format(token)}

      jsonRequest = { 'Items' : names }

      response = requests.delete(url, headers=header, json=jsonRequest, verify=False)
      if response.status_code != 200:
        raise Exception("DeleteBasicVariable call error + '" +  str(response.status_code) + "'. Reason: " + response.reason)

      json_result = json.loads(response.text)

      #[ItemPathJSON('OPCUA.NodeId', '', item['identity']) for item in json_result['items']]
      if 'diagnostics' in json_result:
        return [True if item == 1 else False for item in json_result['diagnostics']]
      else:
        return True


    def filterDataObjects(self, filter = None, attributes = DataObjectAttributes.Unspecified):

      if filter == None:
        filter = DataObjectsFilter()

      typesFilter = []
      if DataObjectsFilterType.BasicVariable in filter.type:
        typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.BasicVariableType.value))
      if DataObjectsFilterType.ExpressionVariable in filter.type:
        typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.ExpressionVariableType.value))

      dataObjects = self._query(filter.name, filter.description, filter.eu, filter.domain, typesFilter)

      self._fillDataObjectsAttributes(list(dataObjects.values()), attributes)

      return dataObjects

    def getObjects(self, objectsPaths):

      paths = []
      browsePaths = []

      if type(objectsPaths) is str:
        paths.append(objectsPaths)
        browsePath = self._translatePathToBrowsePath(objectsPaths)
        browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
      else:
        for path in objectsPaths:
          paths.append(path)
          browsePath = self._translatePathToBrowsePath(path)
          browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

      # Verifica se todos os itens existem
      results = self._read(browsePaths, [ NodeAttributes.NodeId.value ] * len(browsePaths)).items()

      objs = collections.OrderedDict()
      for index in range(0, len(paths)):
        if results[index][1].code == 0:
          objs[paths[index]] = EpmObject(self, results[index][0]._identity, paths[index], paths[index].split('/')[-1])
        else:
          objs[paths[index]] = None

      return objs

    def close(self):
        self._authorizationService.close()

    def open(self):
        self._authorizationService.restart()

    def historyUpdate(self, variables, numpyArrays):
      self._historyUpdate(HistoryUpdateType.Update.value, [variable._itemPath for variable in variables], numpyArrays)
      return

    #region Private Methods

    def _historyUpdate(self, updateType, itemPaths, numpyArrays):
      if len(itemPaths) != len(numpyArrays):
        raise Exception('Invalid number of item in numpyArrays')

      #updateType = 3 # Update
      blockSize = 80000
      totalValues = 0

      historyUpdateRequests = []

      for index in range(len(itemPaths)):
        valuesCount = len(numpyArrays[index])
        if (valuesCount == 0):
            continue

        if (not numpyArrays[index].dtype.names == ('Value', 'Timestamp', 'Quality')):
          raise Exception('Invalid array definition')

        if valuesCount > blockSize:
          if len(historyUpdateRequests) > 0:
            self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
            historyUpdateRequests.clear()
          # Prepare big call
          chunks = [numpyArrays[index][x:x+blockSize] for x in range(0, len(numpyArrays[index]), blockSize)]
          for chunk in chunks:
            dataValueArray = []
            for i in iter(range(0, len(chunk))):
              dataValueArray.append(DataValueJSON((chunk['Value'][i]).item(), (chunk['Quality'][i]).item(), chunk['Timestamp'][i]))
            historyUpdateRequest = HistoryUpdateDataModelJSON([ HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray) ])
            self._historyUpdateCall(historyUpdateRequest)
          totalValues = 0
        else:
          dataValueArray = []
          for i in range(len(numpyArrays[index])):
            dataValueArray.append(DataValueJSON((numpyArrays[index]['Value'][i]).item(), (numpyArrays[index]['Quality'][i]).item(), numpyArrays[index]['Timestamp'][i]))
          historyUpdateRequests.append(HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray))
          if totalValues + valuesCount > blockSize:
            self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
            historyUpdateRequests.clear()
            totalValues = 0
          else:
            totalValues = totalValues + valuesCount
      if len(historyUpdateRequests) > 0:
        self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
      return 

    def _historyUpdateCall(self, historyUpdateRequest):
      token = self._authorizationService.getToken()
      url = self._webApi + '/opcua/v1/history/update/data'
      header = {'Authorization': 'Bearer {}'.format(token)}

      jsonRequest = historyUpdateRequest.toDict()

      response = requests.post(url, headers=header, json=jsonRequest, verify=False)
      if response.status_code != 200:
          raise Exception("HistoryUpdate call error + '" +  str(response.status_code) + "'. Reason: " + response.reason)

      json_result = json.loads(response.text)
      if json_result['diagnostics'][0]['code'] != 0:
        raise Exception("HistoryUpdate call error. Reason: " + str(json_result['diagnostics'][0]['code']))

      return json_result

    def _historyUpdateAnnotation(self, annotationPath, updateType, annotations):

      blockSize = 1000
      totalValues = 0

      historyUpdateRequests = []

      valuesCount = len(annotations)
      if (valuesCount == 0):
        return

      import datetime

      dataValueArray = []

      for i in range(len(annotations)):
        dataValueArray.append(AnnotationValueJSON(annotations[i][2], annotations[i][1], annotations[i][0]))

      annotationType = ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.AnnotationType.value)
      historyUpdateRequest = HistoryUpdateDataModelJSON([ HistoryUpdateDataItemModelJSON(annotationPath, updateType, dataValueArray, annotationType) ])
      self._historyUpdateCall(historyUpdateRequest)

      return 


    def _write(self, paths, attributeIds, values):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/write'
        header = {'Authorization': 'Bearer {}'.format(token)}

        writeItems = []
        for x in range(0, len(paths)):
          writeItems.append(WriteItemModelJSON(paths[x], attributeIds[x], values[x]))

        request = WriteModelJSON(writeItems)
        jsonRequest = request.toDict()
        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            print(response.reason)
            raise Exception("Write service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
        json_result = json.loads(response.text)
        if json_result == None:
            raise Exception("Write Failed no result")
        elif len(json_result['diagnostics']) != len(writeItems):
            raise Exception("Write Failed with error '" + str(json_result['diagnostics'][0]) + "'")
        elif json_result['diagnostics'][0]['code'] != 0:
            raise Exception("Write Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(json_result['diagnostics'][0]['message']) + "'")
        return

    def _read(self, paths, attributeIds):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/read'
        header = {'Authorization': 'Bearer {}'.format(token)}

        readItems = []
        for x in range(0, len(paths)):
          readItems.append(ReadItemModelJSON(paths[x], attributeIds[x]))

        continuationPoint = None
        
        resultItems = []
        diagnostics = []

        while True:
            request = ReadModelJSON(readItems, continuationPoint)
            jsonRequest = request.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception("Read service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("Read Failed no result")
            elif len(json_result['diagnostics']) != len(readItems):
                raise Exception("Read Failed with error '" + str(json_result['diagnostics'][0]) + "'")

            for diagnostic, item  in zip(json_result['diagnostics'], json_result['items']):
              diagnostics.append(DiagnosticModelJSON(diagnostic['code']))
              if diagnostic['code'] == 0:
                readItem = ReadResultItemModelJSON(item['identity'], DataValueJSON(item['value']['value'], item['value']['quality'], item['value']['timestamp']))
              else:
                readItem = None
              resultItems.append(readItem)

            #for item in json_result['items']:
            #  readItem = ReadResultItemModelJSON(item['identity'], DataValueJSON(item['value']['value'], item['value']['quality'], item['value']['timestamp']))
            #  resultItems.append(readItem)

            continuationPoint = json_result['continuationPoint']
            if continuationPoint == None:
                break

        return ReadResultModelJSON(resultItems, diagnostics)

    def _browse(self, paths, referenceType, nodeClassMask = NodeClassMask.Unspecified):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/browse'
        header = {'Authorization': 'Bearer {}'.format(token)}

        itemsModels = []

        for item in paths:
          itemsModels.append(BrowseItemModelJSON(item, nodeClassMask.value, [ referenceType ]))

        continuationPoint = None
        
        requestResults = []
        diagnostics = []

        while True:
            request = BrowseModelJSON(itemsModels, continuationPoint)
            jsonRequest = request.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception("Browse service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("Browse Failed no result")
            elif len(json_result['diagnostics']) != len(paths):
                raise Exception("Invalid browse result items!")

            for json_item, json_diags in zip(json_result['items'], json_result['diagnostics']):
              diagnostics.append(DiagnosticModelJSON(json_diags['code']))
              if json_diags['code'] == 0:
                resultItems = []
                for item in json_item:
                  browseItem = BrowseResultItemModelJSON(item['identity'], item['displayName'], item['relativePath'], item['type'], item['nodeClass'])
                  resultItems.append(browseItem)
                requestResults.append(resultItems)
              else:
                requestResults.append(None)
            continuationPoint = json_result['continuationPoint']
            if continuationPoint == None:
                break

        return BrowseResultModelJSON(requestResults, diagnostics)

    def _historyReadAggregate(self, aggregateType, queryPeriod, itemPath):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/processed'
        header = {'Authorization': 'Bearer {}'.format(token)}

        basePath = "/Server/ServerCapabilities/AggregateFunctions/"
        aggregatePath = ItemPathJSON('OPCUA.BrowsePath', '', basePath + aggregateType.type)
        #itemPath = ItemPathJSON('OPCUA.BrowsePath', '', variablePath)
        continuationPoint = None
        dataValues = []

        processingInterval = aggregateType.interval.total_seconds() * 1000

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryProcessedModelJSON(aggregatePath, processingInterval, queryPeriod.start, queryPeriod.end, [ itemPathAndCP ])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception("Service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadAggregate Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAggregate Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAggregate Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(json_result['diagnostics'][0]['message']) + "'")
            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues)
        return numpyArray

    def _historyReadAnnotation(self, queryPeriod, annotationPath):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/raw'
        header = {'Authorization': 'Bearer {}'.format(token)}

        continuationPoint = None
        annotations = []

        import dateutil.parser

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(annotationPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, False, [ itemPathAndCP ])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception("Service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadAnnotation Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAnnotation Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAnnotation Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(json_result['diagnostics'][0]['message']) + "'")

            for value in json_result['dataValues'][0]['dataValues']:
              if ('userName' in value['value'] and 
                  'annotationTime' in value['value'] and
                  'message' in value['value']):
                annotationTime = dateutil.parser.parse(value['value']['annotationTime'])
                annotations.append((annotationTime, value['value']['userName'],
                                    value['value']['message']))
            #dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break

        return annotations


    def _historyReadRaw(self, queryPeriod, itemPath, bounds = False):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/raw'
        header = {'Authorization': 'Bearer {}'.format(token)}

        #itemPath = ItemPathJSON('OPCUA.BrowsePath', '', variablePath)
        continuationPoint = None
        dataValues = []

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, bounds, [ itemPathAndCP ])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception("Service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadRaw Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadRaw Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadRaw Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(json_result['diagnostics'][0]['message']) + "'")

            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues)
        return numpyArray

    def _query(self, browseNameFilter, descriptionFilter, euNameFilter, domainFilter, typeFilter):
      token = self._authorizationService.getToken()
      url = self._webApi + '/epm/v1/query'
      header = {'Authorization': 'Bearer {}'.format(token)}

      continuationPoint = None

      items = collections.OrderedDict()

      while True:
          model = QueryModelJSON(continuationPoint, False, QueryResultMask.Name.value | QueryResultMask.Identity.value, browseNameFilter, descriptionFilter, euNameFilter, typeFilter, domainFilter.value)
          jsonRequest = model.toDict()
          response = requests.post(url, headers=header, json=jsonRequest, verify=False)
          if response.status_code != 200:
              print(response.reason)
              raise Exception("Service call http error '" +  str(response.status_code) + "'. Reason: " + response.reason)
          json_result = json.loads(response.text)
          if json_result == None:
              raise Exception("Query Failed no result")
          elif json_result['diagnostic']['code'] != 0:
              raise Exception("query Failed with error code: " + str(json_result['diagnostic']['code']) + " and message: '" + str(json_result['diagnostic']['message']) + "'")
          continuationPoint = json_result['continuationPoint']

          resultTypes = self._browse([ItemPathJSON('OPCUA.NodeId', '', item['identity']) for item in json_result['items']], EpmNodeIds.HasTypeDefinition.value).references()

          index = 0
          for item in json_result['items']:
            if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
              dataObject = BasicVariable(self, item['identity'], item['name'])
            else:
              dataObject = EpmDataObject(self, item['name'], item['identity'])
            items[item['name']] = dataObject
            index = index + 1
          if continuationPoint == None:
              break
      return items

    def _getAllDataObjects(self, attributes, reference, rootNode = '/1:DataObjects'):

      itemPath = ItemPathJSON('OPCUA.BrowsePath', '', rootNode)
      browseResult = self._browse([ itemPath ], reference.value, NodeClassMask.Variable).references()
      if len(browseResult) < 1:
        return []

      epmVariables = collections.OrderedDict()

      for item in browseResult[0]:
        if item._type == EpmNodeIds.BasicVariableType.value:
          epmVariables[item._displayName] = BasicVariable(self, item._identity, item._displayName)
        else:
          epmVariables[item._displayName] = EpmDataObject(self, item._displayName, item._identity)

      self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

      return epmVariables

    def _getDataObjects(self, doNames, attributes, rootNode = '/1:DataObjects'):
        names = []
        paths = []
        if type(doNames) is str:
          names.append(doNames)
          paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + doNames))
        else:
          names = doNames
          for item in doNames:
            paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + item))

        # Verifica se todos os itens existem
        resultIds = self._read(paths, [ NodeAttributes.NodeId.value] * len(paths)).items()
        resultTypes = self._browse(paths, EpmNodeIds.HasTypeDefinition.value).references()

        readProperties = []

        epmVariables = collections.OrderedDict()
        for index in range(0, len(names)):
          if resultIds[index][1].code == 0:
            if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
              epmVariables[names[index]] = BasicVariable(self, resultIds[index][0]._identity, names[index])
            else:
              epmVariables[names[index]] = EpmDataObject(self, names[index], resultIds[index][0]._identity)
          else:
            epmVariables[names[index]] = None

        self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

        return epmVariables

    def _fillDataObjectsAttributes(self, dataObjects, attributes):

      propertyPaths = []
      if attributes == DataObjectAttributes.Unspecified.value:
        return dataObjects

      for index in range(0, len(dataObjects)):
        #for item in dataObjects:
        variable = dataObjects[index]
        if variable == None:
          continue
        if DataObjectAttributes.Name in attributes:
          propertyPaths.append((variable, DataObjectAttributes.Name, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.Name.value))))
        if DataObjectAttributes.Description in attributes:
          propertyPaths.append((variable, DataObjectAttributes.Description, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.Description.value))))
        if DataObjectAttributes.EU in attributes:
          propertyPaths.append((variable, DataObjectAttributes.EU, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.EU.value))))
        if DataObjectAttributes.LowLimit in attributes:
          propertyPaths.append((variable, DataObjectAttributes.LowLimit, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.LowLimit.value))))
        if DataObjectAttributes.HighLimit in attributes:
          propertyPaths.append((variable, DataObjectAttributes.HighLimit, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.HighLimit.value))))
        if DataObjectAttributes.Clamping in attributes:
          propertyPaths.append((variable, DataObjectAttributes.Clamping, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.Clamping.value))))
        if DataObjectAttributes.Domain in attributes:
          propertyPaths.append((variable, DataObjectAttributes.Domain, ItemPathJSON('OPCUA.NodeId', None, variable._encodePropertyIdentity(EpmDataObjectAttributeIds.Domain.value))))

      chunks = [propertyPaths[x:x+1000] for x in range(0, len(propertyPaths), 1000)]

      for chunk in chunks:
        if len(chunk) > 0:
          readResults = self._read(list(zip(*chunk))[2], [13] * len(chunk)).items()
          for index in range(0, len(readResults)):
            dataObject = chunk[index][0]
            attributeId = chunk[index][1]
            if readResults[index][1].code == 0:
              dataObject._setAttribute(attributeId, readResults[index][0].value.value)

        # Private Methods
    def _translatePathToBrowsePath(self, path):
      if len(path) == 0:
        return ''
      if path[0] == '/':
        path = path[1:]

      browsePath = ''
      splittedPath = path.split('/')
      for relativePath in splittedPath:

        splittedRelativePath = relativePath.split(':')
        currentPath = relativePath
        if len(splittedRelativePath) == 1:
          currentPath = '1:' + relativePath
        browsePath = browsePath + '/' + currentPath

      return browsePath

    def logout(self):
        if (self._token == None):
          return
        post_data = { "token" : self._token }
        client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
        auth_url = self._authServer + '/connect/revocation'
        response = requests.post(auth_url,
                                 auth=client_auth,
                                 data=post_data, verify=False)

    def _getToken(self):
        if (self._token != None):
            return self._token
        client_auth = requests.auth.HTTPBasicAuth(self._clientId, self._programId)
        post_data = {"grant_type": "password", 
                     "username": self._userName,
                     "password": self._password,
                     "scope": "offline_access openid profile email opcua_browse opcua_read opcua_subscription opcua_history EpmWebApi"} #EpmProcessor #openid profile email opcua_browse opcua_read opcua_subscription 
        auth_url = self._authServer + '/connect/token'
        response = requests.post(auth_url,
                                 auth=client_auth,
                                 data=post_data, verify=False)
        respose_json = response.json()

        if response.status_code != 200:
            raise Exception("GetToken() call http error '" +  str(response.status_code) + "'. Reason: " + respose_json["error"])

        #post_data = {"grant_type": "refresh_token", 
        #             "refresh_token": respose_json['refresh_token'] }
        #auth_url = self._authServer + '/connect/token'
        #response = requests.post(auth_url,
        #                         auth=client_auth,
        #                         data=post_data)
        #respose_json = response.json()
     
        self._token = respose_json["access_token"]
        return self._token



