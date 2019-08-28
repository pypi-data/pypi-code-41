from simple_salesforce import Salesforce
from salesforce_reporting import Connection, ReportParser
from re import sub
import pandas as pd
import requests

class login:
    """Initiates Salseforce connection and is used for subsequent access methods"""
    
    def __init__(self,username,password,orgid,securitytoken='',sandbox=False):
        self.Username = username
        self.Password = password
        self.OrgId = orgid
        self.SecurityToken = securitytoken
        if sandbox==True:
            self.Sandbox = 'test'
        else:
            self.Sandbox = 'login'
        self.Org = Salesforce(username=self.Username, password=self.Password,
                              security_token=self.SecurityToken,organizationId=self.OrgId,
                             domain=self.Sandbox)

    def __expectString(self,val,argName=None):
        """Raises standard Exception message if passed value is not a string"""
        if argName == None:            
            if type(val) != str:
                raise Exception('Expected string, received {}'.format(type(val)))
        elif type(argName) != str:
            raise Exception('Expected string for argument \'argName\', received {}'.format(type(val)))
        else:
            if type(val) != str:
                raise Exception('Expected string for argument \'{}\', received {}'.format(argName,type(val)))
        
    def getdf(self,query):
        """Returns pandas dataframe from passed SOQL query"""
        self.__expectString(query)
        try:
            return pd.DataFrame(list(self.Org.query_all(query)['records'])).drop(columns=['attributes'])
        except (KeyError, NameError) as e:
            if str(e) == '"labels [\'attributes\'] not contained in axis"':
                raise Exception('No data found for query [{}]'.format(query))
            else:
                return e
            
    def getReport(self,reportId):
        """Returns pandas dataframe from passed Salesforce report Id (15 or 18 digit)"""
        self.__expectString(reportId)
        if len(reportId) != 15 and len(reportId) != 18:
            raise Exception('Expected 15 character or 18 character string, received {} character string'.format(len(reportId)))
        elif len(sub('[a-zA-z0-9]','',reportId)) > 0:
            raise Exception('Passed string cannot contain any special characters (i.e. "!","@","#")')
        with requests.session() as s:
            response = s.get("https://{}/{}?export".format(self.Org.sf_instance,reportId), headers=self.Org.headers, cookies={'sid': self.Org.session_id})
        
        def parseReponse(responseObject):
            # Separate trailing report data from regular data
            # then split remaining data by '\n'
            bigList = responseObject.text.split('\n\n\n')[0].split('\n')

            # Pull headers from first split group
            headers = bigList[0].split(',')

            #Crop off extra ""
            for i in range(0,len(headers)):
                headers[i] = headers[i][1:-1]

            # Initialize dictionary
            bigDict = {}
            for i in headers:
                bigDict[i] = []

            indexKeyMatcher = {}
            for i in range(0,len(headers)):
                indexKeyMatcher[i] = headers[i]

            # Separate header data from bigList
            bigList = bigList[1:]

            # Comma separate each sub-list
            # and add to dictionary
            for i in range(0,len(bigList)):
                data = bigList[i].split('",')
                #Crop off extra ""
                for subIndex in range(0,len(data)):
                    if subIndex == len(data)-1:
                        data[subIndex] = data[subIndex][1:-1]
                    else:
                        data[subIndex] = data[subIndex][1:]
                for col in range(0,len(data)):
                    bigDict[indexKeyMatcher[col]].append(data[col])
        #         bigDict[i] = data
            return bigDict
        
        return pd.DataFrame(parseReponse(response))

    def dml(self,obj='',uptype='',data=None):
        """Runs the specified bulk CRUD command with the passed data"""
        self.__expectString(obj,'obj')
        if self.checkObject(obj)['IsObject'] == False:
            raise Exception('\'{}\' is not a Salesforce object in this org'.format(obj))
        self.__expectString(uptype,'uptype')
        if uptype not in ['insert','update','delete','hard_delete','upsert']:
            raise Exception('No valid uptype selected. Please choose one of the folowing options: [insert, update, delete, hard_delete, upsert]')
        if type(data) != list:
            raise Exception('Expected list for argument \'data\', received {}'.format(type(data)))
        uptype = uptype.lower()
        return(eval(f'self.Org.bulk.{obj}.{uptype}(data)'))    

    def getObjectFields(self,obj):
        """Returns list of all field names in the passed Salesforce object name"""
        self.__expectString(obj)
        if self.checkObject(obj)['IsObject'] == False:
            raise Exception('Invalid Salesforce object name. If this is a custom object, make sure to append \'__c\' to the end of the object name')
        fields = getattr(self.Org,obj).describe()['fields']
        flist = [i['name'] for i in fields]
        return flist

    def getObjectFieldsDict(self,obj):
        """Returns all fields of passed Salesforce object name as {label:name} dictionary"""
        self.__expectString(obj)
        if self.checkObject(obj)['IsObject'] == False:
            raise Exception('Invalid Salesforce object name. If this is a custom object, make sure to append \'__c\' to the end of the object name')
        fields = getattr(self.Org,obj).describe()['fields']
        fdict = {}
        for i in fields:
            fdict[i['label']] = i['name']
        return fdict

    def checkObject(self,obj):
        """Accepts string argument. Returns dict {'isObject':True/False,'Records':count_of_records_in_object}"""
        self.__expectString(obj)
        try:
            eval('self.Org.{}.metadata()'.format(obj))['objectDescribe']['label']
            return {'IsObject':True,'Records':self.getdf('SELECT count(Id) FROM {}'.format(obj)).at[0,'expr0']}
        except:
            a = sys.exc_info()
            return {'IsObject':False,'Records':None}
