# Copyright (c) 2017-2019, BPMK LTD (BiSkilled) Tal Shany <tal.shany@biSkilled.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This file is part of dingDong
#
# dingDong is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dingDong is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dingDong.  If not, see <http://www.gnu.org/licenses/>.

import os
import io
import json

from collections import OrderedDict

from dingDong.misc.logger import p
from dingDong.misc.enumsJson import eJson, eConn, findProp
from dingDong.config      import config


#xx = [[{'s':}],[{'prop':{'pp':45}},{}],{'sql1':'', 's':xxx,'t':'dsdsdsd'},{''},{}]
# s : [obj] [conn,  obj],[conn. obj, filter]  {"conn":conn, "obj":obj, filter:"dddd"} // connection:"s":[]

class jsonParser (object):

    """ Create list of node to load and init all connection dictionary """
    def __init__ (self, dicObj=None, filePath=None,
                  dirData=None, includeFiles=None, notIncludeFiles=None, connDict=None, sqlFolder=None):

        if connDict and isinstance(connDict ,(dict, OrderedDict)):
            config.CONN_URL.update(connDict)

        self.connDict = config.CONN_URL
        self.sqlFolder= sqlFolder
        self.__initConnDict ()
        self.listObj    = []
        self.listFiles  = []
        self.jsonMapp   = []
        self.jsonName   = ''
        self.dirData    = None
        msg     = ""

        if dicObj:
            self.listObj.append (dicObj)
            msg+="loading data from dictioanry; "

        if filePath:
            if os.path.isfile (filePath):
                with io.open(filePath, encoding="utf-8") as jsonFile:  #
                    dicObj = json.load(jsonFile, object_pairs_hook=OrderedDict)
                    self.listObj.append (dicObj)
                    msg+="loading data from file"
            else:
                p("file %s is not exists " %(filePath),"e")

        if dirData:
            self.dirData = dirData
            if not os.path.isdir(dirData):
                p ("Folder not  exists : %s" % dirData, "e")
                return
            else:
                msg += "loading data from folder: %s" %dirData

                jsonFiles = [pos_json for pos_json in os.listdir(dirData) if pos_json.endswith('.json')]
                jsonFilesDic = {x.lower().replace(".json", ""): x for x in jsonFiles}

                if notIncludeFiles:
                    notIncludeDict = {x.lower().replace(".json", ""): x for x in notIncludeFiles}
                    for f in jsonFilesDic:
                        if f in notIncludeDict:
                            p('NOT INCLUDE: File:%s, file: NOT IN USED, REMOVED >>>>' % (str( os.path.join(dirData,f) ) ), "ii")
                            jsonFiles.remove(jsonFilesDic[f])
                    for f in notIncludeDict:
                        if f not in jsonFilesDic:
                            p('NOT INCLUDE: File: %s, NOT EXISTS.Ignoring>>>>>' % ( str(os.path.join(dirData, f))), "ii")

                if includeFiles:
                    includeDict = {x.lower().replace(".json", ""): x for x in includeFiles}
                    for f in jsonFilesDic:
                        if f not in includeDict and f in jsonFilesDic and jsonFilesDic[f] in jsonFiles:
                            p('INCLUDE: Folder:%s, file: %s NOT IN USED, REMOVED >>>>' % (str(dirData), f), "ii")
                            jsonFiles.remove(jsonFilesDic[f])
                    for f in includeDict:
                        if f not in jsonFilesDic:
                            p('INCLUDE: Folder: %s, file: %s not exists.. Ignoring >>>>' % (str(dirData), f), "ii")
                self.listFiles = jsonFiles

    def jsonMappings (self, destList = None):
        if self.listObj and len (self.listObj)>0:
            self.jsonMapp = list([])
            self.jsonName = ''
            self.__initMetaDict(listObj=self.listObj, destList=None)

            yield {self.jsonName:self.jsonMapp}
        elif self.listFiles and len (self.listFiles)>0:
            for index, js in enumerate(self.listFiles):
                self.jsonMapp = list([])
                self.jsonName = js
                with io.open(os.path.join(self.dirData, js), encoding="utf-8") as jsonFile:  #
                    jText = json.load(jsonFile, object_pairs_hook=OrderedDict)
                    self.__initMetaDict(listObj=jText, destList=None)
                    yield {self.jsonName:self.jsonMapp}

    def getAllConnection (self, pr=True):
        if pr:
            for x in self.connDict:
                p('TYPE: %s\t\t\tPROP: %s' %(str(x), str(self.connDict[x])), "ii")
            p ("====================================================" , "ii")
        return self.connDict

    """ MAIN KEYS : NAME (n) AND CONNENCTION TYPE (conn) """
    def __initConnDict (self):
        newConnDict =  {}
        for conn in self.connDict:
            dictProp = eJson.jValues.DIC.copy()
            dictProp[eJson.jValues.NAME] = conn
            dictProp[eJson.jValues.CONN] = conn

            if isinstance( self.connDict[conn], dict ):
                for k in self.connDict[conn]:
                    origK = findProp(prop=k, obj=eJson.jValues )
                    if origK:
                        dictProp[origK] = self.connDict[conn][k]
                    elif k.lower() in newConnDict:
                        dictProp[k.lower()] = self.connDict[conn][k]
                    else:
                        dictProp[k] = self.connDict[conn][k]

            elif isinstance( self.connDict[conn], str ):
                dictProp[eJson.jValues.URL] = self.connDict[conn]
            newConnDict[conn] = dictProp

            ### VALID CONNECTION TYPES
            errConn = []
            for conn in newConnDict:
                if not findProp(prop=newConnDict[conn][eJson.jValues.CONN], obj=eConn):
                    p("Remove Connection %s becouse prop: %s  is NOT VALID !!" %(str(conn), str(newConnDict[conn][eJson.jValues.CONN])), "e")
                    errConn.append (conn)
            for err in errConn:
                del newConnDict[err]
        self.connDict = newConnDict

    # parse Json file into internal Json format
    # Key can be name or internal dictionary
    def __initMetaDict (self, listObj,destList=None):
        for node in listObj:
            if isinstance(node ,list):
                self.__initMetaDict(listObj=node, destList=destList)
            elif isinstance(node, dict):
                stt     = OrderedDict()
                newDict = OrderedDict()

                for prop in node:
                    k =  findProp (prop=prop.lower(), obj=eJson.jKeys, dictProp=node[prop])
                    if k:
                        if eJson.jKeys.SOURCE  in newDict and k == eJson.jKeys.QUERY:
                            p("Source and Query exists - Will use Query", "ii")
                            del newDict[eJson.jKeys.SOURCE]
                        elif eJson.jKeys.QUERY in newDict and k == eJson.jKeys.SOURCE:
                            p("Query and Source exists - Will use Source", "ii")
                            del newDict[eJson.jKeys.QUERY]

                        if k == eJson.jKeys.STT or k == eJson.jKeys.STTONLY:
                            newSttL = {x.lower(): x for x in node[prop]}
                            sttL = {x.lower(): x for x in stt}
                            for s in stt:
                                if s.lower() in newSttL:
                                    stt[s].update(node[prop][newSttL[s.lower()]])

                            for s in newSttL:
                                if s not in sttL:
                                    stt[newSttL[s]] = node[prop][newSttL[s]]
                            newDict[k] =stt
                        # parse source / target / query
                        elif k == eJson.jKeys.SOURCE or k == eJson.jKeys.TARGET or k == eJson.jKeys.QUERY:
                            newDict[k] = self.__sourceOrTargetOrQueryConn(propFullName=prop, propVal=node[prop])
                        # parse merge
                        elif k == eJson.jKeys.MERGE:
                            newDict[k] = self.__mergeConn(existsNodes=newDict, propFullName=prop, propVal=node[prop])
                        # parse column data types
                        elif k == eJson.jKeys.COLUMNS:
                            stt = self.__sttAddColumns (stt=stt, propVal=node[prop])
                            newDict[eJson.jKeys.STTONLY] = stt

                            if eJson.jKeys.STT in newDict:
                                del newDict[eJson.jKeys.STT]

                        # parse column mapping
                        elif k == eJson.jKeys.MAP:
                            stt = self.__sttAddMappings(stt=stt, propVal=node[prop])
                            if eJson.jKeys.STT in newDict:
                                newDict[eJson.jKeys.STT] = stt
                            else:
                                newDict[eJson.jKeys.STTONLY] = stt
                        elif k == eJson.jKeys.INDEX:
                            index = self.__index(propVal=node[prop])
                            if index:
                                newDict[eJson.jKeys.INDEX] = index
                        else:
                            p ("%s not implemented !" %(k), "e")
                    else:
                        newDict[prop.lower()] = self.__uniqueProc(propVal=node[prop])

                self.jsonMapp.append ( newDict )
            else:
                p("jsonParser->__initMetaDict: Unknown node prop values: %s " %node)

    ### List option : [obj] [conn,  obj],[conn. obj, filter]  // connection Name defoult
    ### FINAL : {eJK.CONN:None, eJK.OBJ:None, eJK.FILTER:None, eJK.URL:None, eJK.URLPARAM:None}
    def __sourceOrTargetOrQueryConn(self, propFullName, propVal):
        ret = eJson.jValues.DIC.copy()
        if isinstance(propVal, str):
            ret[eJson.jValues.NAME] = propFullName
            ret[eJson.jValues.TYPE] = propFullName
            ret[eJson.jValues.OBJ]  = propVal
        elif isinstance(propVal, list):
            ret[eJson.jValues.NAME] = propFullName
            ret[eJson.jValues.TYPE] = propFullName
            if len(propVal) == 1:
                ret[eJson.jValues.CONN] = propFullName
                ret[eJson.jValues.OBJ] = propVal[0]
            elif len(propVal) == 2:
                ret[eJson.jValues.CONN] = propVal[0]
                ret[eJson.jValues.OBJ]  = propVal[1]
            elif len(propVal) == 3:
                ret[eJson.jValues.CONN]  = propVal[0]
                ret[eJson.jValues.OBJ]   = propVal[1]

                if str(propVal[2]).isdigit():
                    ret[eJson.jValues.UPDATE] =  self.__setUpdate (propVal[2])
                else:
                    ret[eJson.jValues.FILTER]= propVal[2]
            elif len(propVal) == 4:
                ret[eJson.jValues.CONN]     = propVal[0]
                ret[eJson.jValues.OBJ]      = propVal[1]
                ret[eJson.jValues.FILTER]   = propVal[2]
                ret[eJson.jValues.UPDATE]   = self.__setUpdate (propVal[3])

            else:
                p("%s: Not valid list valuues, must 1,2 or 3" % (str(propFullName)), "e")
        elif isinstance(propVal, dict):
            self.__notVaildProp(ret, propVal, propFullName)
        else:
            p("Not valid values: %s " %(propVal),"e")
            return {}

        if findProp (prop=ret[eJson.jValues.TYPE], obj=eJson.jKeys)  == eJson.jKeys.QUERY:
            ret[eJson.jValues.IS_SQL] = True
        return ret

    # Must have source / target / query in existing nodes
    # [obj], [obj, keys]
    def __mergeConn (self, existsNodes, propFullName, propVal):
        ret     = eJson.jMergeValues.DIC.copy()
        srcConn = None

        if eJson.jKeys.TARGET in existsNodes:
            srcConn = existsNodes[eJson.jKeys.TARGET]
        elif eJson.jKeys.SOURCE in existsNodes:
            srcConn = existsNodes[eJson.jKeys.SOURCE]
        elif eJson.jKeys.QUERY in existsNodes:
            srcConn = existsNodes[eJson.jKeys.QUERY]

        if not srcConn:
            p("There is no query/ source or target to merge with. quiting. val: %s " %(str(propVal)) ,"e")
            return {}

        ### Update values from Source connection
        ret[eJson.jMergeValues.SOURCE]  = srcConn[eJson.jValues.OBJ]
        ret[eJson.jValues.CONN]         = srcConn[eJson.jValues.CONN]
        ret[eJson.jValues.URL]          = srcConn[eJson.jValues.URL]
        ret[eJson.jValues.URLPARAM]     = srcConn[eJson.jValues.URLPARAM]
        ret[eJson.jValues.URL_FILE]     = srcConn[eJson.jValues.URL_FILE]

        if isinstance(propVal, str):
            ret[eJson.jValues.NAME]         = propFullName
            ret[eJson.jMergeValues.TARGET]  = propVal

        elif isinstance(propVal, list):
            ret[eJson.jValues.NAME] = propFullName
            if len(propVal) == 1:
                ret[eJson.jMergeValues.TARGET]  = propVal[0]
            elif len(propVal) == 2:
                ret[eJson.jMergeValues.TARGET] = propVal[0]
                if str(propVal[1]).isdigit():
                    ret[eJson.jValues.UPDATE] = self.__setUpdate(propVal[1])
                else:
                    ret[eJson.jMergeValues.MERGE]  = propVal[1]
            elif len(propVal) == 3:
                ret[eJson.jMergeValues.TARGET]  = propVal[0]
                ret[eJson.jMergeValues.MERGE]   = propVal[1]
                ret[eJson.jValues.UPDATE]       = self.__setUpdate (propVal[2])
            else:
                p("%s: Not valid merge valuues, must have obj and merge key..." % (str(propVal)), "e")
        elif isinstance(propVal, dict):
            self.__notVaildProp( ret, propVal, propFullName )
        else:
            p("Not valid values")

        ret[eJson.jValues.OBJ] = ret[eJson.jMergeValues.TARGET]

        return ret

    def __setUpdate (self, val):
        if str(val).isdigit():
            if findProp(prop=val, obj=eJson.jUpdate):
                return val
            else:
                p("THERE IS %s WHICH IS MAPPED TO UPDATE PROPERTY, MUST HAVE -1(drop), 1(UPDATE), 2(NO_UPDATE), USING -1 DROP--> CREATE METHOD ")
        return -1

    # Insert into STT Column mapping
    def __sttAddColumns(self, stt, propVal):
        if not isinstance(propVal, dict):
            p ("jsonParser->__sttAddColumns: Not valid prop %s, must be dictionary type" %(propVal),"e")
            return stt

        existsColumnsDict   = {x.lower():x for x in stt.keys()}


        for tar in propVal:
            if tar.lower() in existsColumnsDict:
                stt[ existsColumnsDict[tar.lower()] ][eJson.jSttValues.TYPE] = propVal[tar]
            else:
                stt[tar] = {eJson.jSttValues.TYPE:propVal[tar]}
        return stt

    # Insert / Add new column types
    def __sttAddMappings(selfself, stt, propVal):
        if not isinstance(propVal, dict):
            p ("jsonParser->__sttAddMappings: Not valid prop %s, must be dictionary type" %(propVal),"e")
            return stt
        existsColumnsDict = {x.lower(): x for x in stt.keys()}
        for tar in propVal:
            if tar.lower() in existsColumnsDict:
                stt[ existsColumnsDict[tar.lower()] ][eJson.jSttValues.SOURCE] = propVal[tar]
            else:
                stt[tar][eJson.jSttValues.SOURCE] = propVal[tar]
        return stt

    # Special connection execution
    # list - ]
    def __uniqueProc(self, propVal):
        ret= {}
        if isinstance(propVal ,list) and len(propVal)==2:
            ret[eJson.jValues.CONN]     = propVal[0]
            ret[eJson.jValues.OBJ]      = propVal[1]
            ret[eJson.jValues.FOLDER]   = self.sqlFolder

        elif isinstance(propVal ,dict) and eJson.jValues.CONN in propVal and eJson.jValues.OBJ in propVal:
            ret = propVal

        if eJson.jValues.OBJ in ret and ret[eJson.jValues.OBJ] is not None and '.sql' in ret[eJson.jValues.OBJ]:
            fileName = ret[eJson.jValues.OBJ]
            if os.path.isfile(fileName):
                ret[eJson.jValues.FILE] = fileName
            if eJson.jValues.FOLDER in ret and ret[eJson.jValues.FOLDER] is not None:
                folderPath = ret[eJson.jValues.FOLDER]
                if os.path.isfile( os.path.join(folderPath, fileName)):
                    ret[eJson.jValues.FILE] = os.path.join(folderPath, fileName)

        return ret

    def __index (self, propVal):
        ## propVal = [{col:[],'iu':True, 'ic':True},{}]
        if isinstance(propVal, (dict,OrderedDict)):
            propVal = [propVal]

        if not isinstance(propVal, list):
            p("INDEX VALUES MUST BE A DICTIONARY OR LIST OF DICTIOANRY, FORMAT {'C'':list_column_index, 'ic':is cluster (True/False), 'iu': is unique (True/False)}")
            return
        ret = []
        for indexDict in propVal:

            if not isinstance(indexDict, (dict, OrderedDict)):
                p("INDEX MUST BE DICTIOANY, FORMAT {'C'':list_column_index, 'ic':is cluster (True/False), 'iu': is unique (True/False)}")
                continue

            returnDict = {eJson.jValues.INDEX_COLUMS:[],eJson.jValues.INDEX_CLUSTER:True,eJson.jValues.INDEX_UNIQUE:False}
            for node in indexDict:
                k =  findProp (prop=node.lower(), obj=eJson.jValues, dictProp=indexDict[node])

                if not k:
                    p("INDEX VALUES IS NOT VALID: %s, IGNORE INDEX. VALID FORMAT: FORMAT {'C'':list_column_index, 'ic':is cluster (True/False), 'iu': is unique (True/False)}")
                    break

                if k == eJson.jValues.INDEX_COLUMS:
                    if isinstance(indexDict[node], list ):
                        returnDict[eJson.jValues.INDEX_COLUMS].extend(indexDict[node])
                    else:
                        returnDict[eJson.jValues.INDEX_COLUMS].append(indexDict[node])
                elif k == eJson.jValues.INDEX_CLUSTER:
                    if not indexDict[node]: returnDict[eJson.jValues.INDEX_CLUSTER] = False
                elif k == eJson.jValues.INDEX_UNIQUE:
                    if indexDict[node]: returnDict[eJson.jValues.INDEX_UNIQUE] = True
                else:
                    p("INDEX - UNRECOGNIZED KEY %s IN DICT:%s IGNORE. VALID FORMAT: FORMAT {'C'':list_column_index, 'ic':is cluster (True/False), 'iu': is unique (True/False)}" %(str(node),str(indexDict)), "e")
            ret.append(indexDict)
        return ret


    def __notVaildProp(self, propDic, newPropDic, propFullName):
        for k in newPropDic:
            if k not in propDic:
                p("baseParser->notValidProp: %s: not valid prop %s -> ignore" % (propFullName, k), "e")
                del newPropDic[k]
        return newPropDic