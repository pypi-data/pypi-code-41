###############################################################
#### Written By: SATYAKI DE                                ####
#### Written On: 08-Sep-2019                               ####
####                                                       ####
#### Objective: This scripts has multiple                  ####
#### features. This scripts has the following              ####
#### functions ->                                          ####
####                                                       ####
#### 1. Distinct features based on the supplied JSON.      ####
#### 2. Null check features substitute with dummy value.   ####
#### 3. Partition By equivalent on JSON.                   ####
#### 4. Regular expression features on JSON                ####
####                                                       ####
#### All these functions are use to facilitate JML i.e.    ####
#### JSON Manipulation Language for Python.                ####
#### Supported Version: Python 3.6 & 3.7                   ####
###############################################################
import re
import json
import pandas as p
import numpy as np


class clsDnpr:
    def __init__(self):
        pass

    def distinct(self, inputJson):
        try:
            res_json = ''
            dfSrc = p.DataFrame()

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])

            # Getting unique record
            newDF = dfSrc.drop_duplicates()

            # Converting back to JSON
            data = newDF.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return res_json

        except Exception as e:
            x = str(e)
            res_json = {'error':400, 'error_desc': x}

            return res_json

    def replace(self, row, def_val):
        try:
            str_colVal = str(row['processedCol']).strip()
            len_colVal = len(str_colVal)

            if (len_colVal != 0):
                res_val = str_colVal
            else:
                res_val = def_val

            return res_val

        except Exception as e:
            res_val = ''

            return res_val


    def nvl(self, inputJson, srcColName, srcDefVal):
        try:
            res_json = ''
            dfSrc = p.DataFrame()
            newDF = p.DataFrame()
            df_Publish = p.DataFrame()

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])

            # Getting unique record
            newDF = dfSrc.drop_duplicates()
            newDF.rename(columns={srcColName:'processedCol'}, inplace=True)

            # Getting the header info only
            hdr_list = list(dfSrc.head())

            # Applying NVL function
            newDF[srcColName] = newDF.apply(lambda row: self.replace(row, srcDefVal), axis=1)
            newDF.drop(['processedCol'], axis=1, inplace=True)

            # Ordering previous column order
            df_Publish = newDF.reindex(hdr_list, axis=1)

            # Converting back to JSON
            data = df_Publish.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return  res_json

        except Exception as e:
            dfError = p.DataFrame()

            return dfError


    def partitionBy(self, inputJson, GrpByList, GrpOperation, CandidateColNm, OutputColNm=''):
        try:
            res_json = ''
            targetColName = ''
            deftargetColName = 'processedCol1'
            GrpOp = ''
            flag = 'N'

            newDF = p.DataFrame()
            dfSrc = p.DataFrame()
            df_Publish = p.DataFrame()
            df_temp = p.DataFrame()
            dfPartitionBy = p.DataFrame()

            len_OutputColNm = len(str(OutputColNm.strip()))

            # Choosing the final output of the aggregated column name
            if (len_OutputColNm != 0):
                targetColName = OutputColNm
            else:
                targetColName = CandidateColNm

            GrpOp = str(GrpOperation)
            GrpList = GrpByList

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])

            print('Target Column Name: ', targetColName)

            if GrpOp.upper() == 'MAX':
                grouped = dfSrc.groupby(GrpList)
                dfSrc = grouped[CandidateColNm].agg([np.max])
                dfSrc.rename(columns={'amax': targetColName}, inplace=True)

            elif GrpOp.upper() == 'MIN':
                grouped = dfSrc.groupby(GrpList)
                dfSrc = grouped[CandidateColNm].agg([np.min])
                dfSrc.rename(columns={'amin': targetColName}, inplace=True)

            elif GrpOp.upper() == 'AVG':
                grouped = dfSrc.groupby(GrpList)
                dfSrc = grouped[CandidateColNm].agg([np.average])
                dfSrc.rename(columns={'amin': targetColName}, inplace=True)

            elif GrpOp.upper() == 'SUM':
                grouped = dfSrc.groupby(GrpList)
                dfSrc = grouped[CandidateColNm].agg([np.sum])
                dfSrc.rename(columns={'amin': targetColName}, inplace=True)

            else:
                raise ValueError

            # Getting unique record
            df_Publish = dfSrc.drop_duplicates()
            df_Publish.reset_index(inplace=True)

            # Converting back to JSON
            data = df_Publish.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return res_json

        except ValueError:
            x = 'Invalid Aggregate Method! Please provide the correct method name i.e. MAX/MIN/SUM/AVG'
            res_json = {'error': 400, 'error_desc': x}

            return res_json

        except Exception as e:
            x = str(e)
            res_json = {'error': 400, 'error_desc': x}

            return res_json

    def likeJson(self, row, targetColumn, inputPattern):
        try:
            str_val = ''
            res = ''

            str_dummy_val = row[targetColumn]
            str_val = re.search(inputPattern, str_dummy_val)
            len_str_val = len(str_val.string)

            if len_str_val > 0:
                res = 'Y'
            else:
                res = 'N'

            return res
        except:
            res = 'N'

            return res

    def regex_like(self, inputJson, targetColumn, inputPattern):
        try:
            dfSrc = p.DataFrame()
            df_lkp = p.DataFrame()
            dummyCol = 'Flag'

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])
            dfSrc[dummyCol] = dfSrc.apply(lambda row: self.likeJson(row, targetColumn, inputPattern), axis=1)

            # Filtering records with flag = 'Y'
            df_lkp = dfSrc[(dfSrc['Flag'] == 'Y')]

            # Dropping the flag column
            df_lkp.drop([dummyCol], axis=1, inplace=True)

            # Converting back to JSON
            data = df_lkp.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return res_json

        except Exception as e:
            x = str(e)
            res_json = {'error': 400, 'error_desc': x}

            return res_json

    def replaceJson(self, row, targetColumn, inputPattern, replaceString):
        try:
            str_val = ''
            res = ''

            str_dummy_val = row[targetColumn]
            str_val = re.sub(inputPattern, replaceString, str_dummy_val)
            len_str_val = len(str_val)

            if len_str_val > 0:
                res = str_val
            else:
                res = str_dummy_val

            return res
        except:
            res = ''

            return res

    def regex_replace(self, inputJson, targetColumn, inputPattern, replaceString):
        try:
            dfSrc = p.DataFrame()
            df_lkp = p.DataFrame()
            dummyCol = 'replacedColumn'

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])

            # Getting the header info only
            hdr_list = list(dfSrc.head())

            # Applying the replace function
            dfSrc[dummyCol] = dfSrc.apply(lambda row: self.replaceJson(row, targetColumn, inputPattern, replaceString), axis=1)

            # Dropping the flag column
            dfSrc.drop([targetColumn], axis=1, inplace=True)

            # Renaming the new column back to the old column
            dfSrc.rename(columns={dummyCol: targetColumn}, inplace=True)

            # Setting the correct order
            df_Publish = dfSrc.reindex(hdr_list, axis=1)

            # Converting back to JSON
            data = df_Publish.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return res_json
        except Exception as e:
            x = str(e)
            res_json = {'error': 400, 'error_desc': x}

            return res_json

    def substrJson(self, row, targetColumn, inputPattern, replaceString):
        try:
            str_val = ''
            res = ''

            str_dummy_val = row[targetColumn]
            str_val = re.sub(inputPattern, replaceString, str_dummy_val)
            len_str_val = len(str_val)

            if len_str_val > 0:
                res = str_val
            else:
                res = str_dummy_val

            return res
        except:
            res = ''

            return res

    def regex_substr(self, inputJson, targetColumn, inputPattern):
        try:
            dfSrc = p.DataFrame()
            df_lkp = p.DataFrame()
            dummyCol = 'substrColumn'
            replaceString = ''

            # Normalizing JSON
            dfSrc = p.io.json.json_normalize(inputJson)
            dfSrc.columns = dfSrc.columns.map(lambda x: x.split(".")[-1])

            # Getting the header info only
            hdr_list = list(dfSrc.head())

            # Applying the replace function
            dfSrc[dummyCol] = dfSrc.apply(lambda row: self.substrJson(row, targetColumn, inputPattern, replaceString), axis=1)

            # Dropping the flag column
            dfSrc.drop([targetColumn], axis=1, inplace=True)

            # Renaming the new column back to the old column
            dfSrc.rename(columns={dummyCol: targetColumn}, inplace=True)

            # Setting the correct order
            df_Publish = dfSrc.reindex(hdr_list, axis=1)

            # Converting back to JSON
            data = df_Publish.to_dict(orient='records')
            jdata = json.dumps(data)
            res_json = json.loads(jdata)

            return res_json
        except Exception as e:
            x = str(e)
            res_json = {'error': 400, 'error_desc': x}

            return res_json

