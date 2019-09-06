"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

from .itempathjson import ItemPathJSON
import datetime as dt
from .datavaluejson import DataValueJSON
from .epmvariable import EpmVariable
from .epmproperty import EpmProperty
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .basicvariablepropertymask import BasicVariablePropertyMask

from enum import Enum
import collections

class EpmDataObjectPropertyNames(Enum):
    Name = "4:Name"

    Description = "4:Description"

    EU = "0:EngineeringUnits"

    LowLimit = "4:RangeLow"

    HighLimit = "4:RangeHigh"

    Clamping = "4:RangeClamping"

    Domain = "4:Discrete"

    Annotations = "4:Annotations"


class EpmDataObjectAttributeIds(Enum):
    Name = 1

    Description = 2

    LowLimit = 15

    HighLimit = 16

    Clamping = 17

    Domain = 21

    EU = 22

    Annotations = 900

def getDiscreteValue(domain):
  if domain == 'Discrete':
    return True
  elif domain == 'Continuous':
    return False
  else:
    return None

def getDomainValue(discrete):
  if discrete == None:
    return None
  elif discrete:
    return 'Discrete'
  else:
    return 'Continuous'

class EpmDataObject(EpmVariable):
    """description of class"""

    def __init__(self, epmConnection, name, identity):
        super().__init__(epmConnection, name, '/DataObjects/' + name, identity)
        self._changeMask = BasicVariablePropertyMask.Unspecified.value
        self._identity = identity
        self._description = None
        self._eu = None
        self._highLimit = None
        self._lowLimit = None
        self._clamping = None
        self._domain = None

    ### Properties
    @property
    def description(self):
      return self._description

    @description.setter
    def description(self, value):
      if self._description == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Description.value
      self._description = value

    @property
    def eu(self):
      return self._eu

    @eu.setter
    def eu(self, value):
      if self._eu == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Eu.value
      self._eu = value

    @property
    def lowLimit(self):
      return self._lowLimit

    @lowLimit.setter
    def lowLimit(self, value):
      if self._lowLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.LowLimit.value
      self._lowLimit = value

    @property
    def highLimit(self):
      return self._lowLimit

    @highLimit.setter
    def highLimit(self, value):
      if self._highLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.HighLimit.value
      self._highLimit = value

    @property
    def clamping(self):
      return self._clamping

    @clamping.setter
    def clamping(self, value):
      if self._clamping == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Clamping.value
      self._clamping = value

    @property
    def domain(self):
      return self._domain

    @domain.setter
    def domain(self, value):
      if self._domain == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Domain.value
      self._domain = value

    ## Public Methods
    def readAnnotations(self, start, end):
      from .queryperiod import QueryPeriod
      queryPeriod = QueryPeriod(start, end)
      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      return self._epmConnection._historyReadAnnotation(queryPeriod, annotationPath)

    def deleteAnnotations(self, start, end, allUsers = False):
      userName = self._epmConnection._authorizationService._userName
      result = self.readAnnotations(start, end)
      deletedItems = []
      for index in range(len(result)):
        if allUsers or result[index][1] == userName:
          deletedItems.append(result[index])

      if len(deletedItems) == 0:
        return

      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      from .performupdatetype import PerformUpdateType
      self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Remove.value, deletedItems)

    def writeAnnotation(self, timestamp, message, override = True):
      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      userName = self._epmConnection._authorizationService._userName
      annotations = [ (timestamp, userName, message) ]
      from .performupdatetype import PerformUpdateType
      if override:
        results = self.readAnnotations(timestamp, timestamp + dt.timedelta(seconds=1))
        for index in range(len(results)):
          if results[index][1] == userName and self._compareDatetime(results[index][0], timestamp):
            return self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Update.value, annotations)
      return self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Insert.value, annotations)

    def readAttributes(self):
      self._epmConnection._fillDataObjectsAttributes([ self ], DataObjectAttributes.All)

    def enumProperties(self):
      result = self._epmConnection._browse([ self._itemPath ], EpmNodeIds.HasProperty.value).references()
      childProperties = collections.OrderedDict()
      for item in result[0]:
        childProperties[item._displayName] = EpmProperty(self._epmConnection, item._displayName, self._path + '/' + item._displayName, item._identity)
      return childProperties

    def _compareDatetime(self, datetime1, datetime2):
      return (datetime1.year == datetime2.year and
              datetime1.month == datetime2.month and
              datetime1.day == datetime2.day and
              datetime1.hour == datetime2.hour and
              datetime1.minute == datetime2.minute and
              datetime1.second == datetime2.second and
              datetime1.microsecond == datetime2.microsecond)

    def _setAttribute(self, attributeId, value):
      if attributeId == DataObjectAttributes.Description:
        self._description = value
      elif attributeId == DataObjectAttributes.EU:
        self._eu = value['displayName']
      elif attributeId == DataObjectAttributes.HighLimit:
        self._highLimit = value
      elif attributeId == DataObjectAttributes.LowLimit:
        self._lowLimit = value
      elif attributeId == DataObjectAttributes.Clamping:
        self._clamping = value
      elif attributeId == DataObjectAttributes.Domain:
        self._domain = 'Discrete' if value else 'Continuous'


    #Private Methods
    def _encodePropertyIdentity(self, propertyIdentity):

      nodeIdSplitted = self._identity.split(';')
      if len(nodeIdSplitted) != 2:
        raise Exception('Invalid nodeId format')
      matches = [x for x in nodeIdSplitted if x.startswith('i=')]
      if len(matches) != 1:
        raise Exception('Invalid nodeId type')

      objectIdentity = int(matches[0][2:])

      SignatureLSB = 0xFE;
      SignatureMSB = 0xCA;

      ret = [ 0 ] * 8

      ret[0] = ((propertyIdentity & 0x000000FF) >> (0 * 8));
      ret[1] = ((propertyIdentity & 0x0000FF00) >> (1 * 8));
      ret[2] = ((objectIdentity   & 0x000000FF) >> (0 * 8));
      ret[3] = ((objectIdentity   & 0x0000FF00) >> (1 * 8));
      ret[4] = ((objectIdentity   & 0x00FF0000) >> (2 * 8));
      ret[5] = ((objectIdentity   & 0xFF000000) >> (3 * 8));
      ret[6] = SignatureLSB;
      ret[7] = SignatureMSB;

      import base64

      return 'ns=1;b=' + base64.b64encode(bytes(ret)).decode("utf-8") 




