import requests
import base64
#TODO: throw more formal exceptions than base exception
#TODO: create a NOSConnectionError exception

class NOSClient:
    def __init__(self, host, provider=""):

        if provider == "aws":
            # host will equal CloudFormation stackID
            # do the things to set self.host -- from AWS perspective.
            pass
        elif provider == "gcp":
            pass
        elif provider == "azure":
            pass
        else:
            # self.host will be a URL to the NOS instance.
            self.host = host

        self._verify_host_is_reachable()

    def _verify_host_is_reachable(self):
        try:
            response = requests.get(self.host)
            if response.json()['status'] == 'ok':
                return True
            else: 
                raise Exception("NOSClient is was able to reach host %s. However, the status of this NOS instance is NOT OK. Please verify your NOS configuration and try again." % self.host)
        except Exception as err:
            if "Failed to establish a new connection:" in str(err):
                raise Exception("NOSClient is unable to reach host %s. Please verify your NOS configuration and try again." % self.host)
            raise Exception(err)

    def GetObjectByUUID(self, uuid):
        self.r = requests.get("%s/object/%s" % (self.host, uuid))
        if self.r.status_code == 200:
            data = self.r.json()
            if "_object" in data:
                obj = NOSObject(data["_object"])
                return obj
            else:
                raise Exception("NOSClient Error: No '_object' property was found. Invalid NOS API.")
        else:
            if "_error" in self.r.json():
                raise Exception("ERROR FROM NOS API Server: %s" % self.r.json()["_error"])
            else:
                raise Exception("Unknown Error: NOSClient was unable to get NOS object.")
    
    def DeleteObjectByUUID(self, uuid):
        self.r = requests.delete("%s/object/%s" % (self.host, uuid))
        data = self.r.json()
        if self.r.status_code == 200:
            return True
        else:
            if "_error" in data:
                raise Exception("ERROR FROM NOS API Server: %s" % data["_error"])
            else:
                raise Exception("Unknown Error: NOSClient was unable to find NOS objects.")
    
    def UpdateObjectByUUID(self, uuid, binaryData="", name="", tags={}):
        headers = {}
        if len(name) > 0 and name != "":
            headers['x-nos-object-name'] = name
        
        if type(tags) is dict:
            if len(tags) > 0:
                tagstr = ""
                for tag in tags:
                    tagstr += "%s:%s," % (tag, tags[tag])
                tagstr = tagstr.rstrip(',')
                headers['x-nos-object-tags'] = tagstr

        try:
            self.r = requests.put("%s/object/%s" % (self.host, uuid), data=binaryData, headers=headers)
            data = self.r.json()
            if self.r.status_code == 200:
                if "_object" in data:
                    obj = NOSObject(data['_object'])
                    return obj
            else:
                if '_error' in data:
                    raise Exception("UpdateObject Failed. Server said: %s" % (data['_error']))
                else:
                    raise Exception("UpdateObject Failed. Unknown error.")
        except Exception as err:
            print(str(err))
            pass

    def FindObjects(self, query, page = "0,10"):
        results = []
        headers = {}
        headers['x-nos-page'] = page
        self.r = requests.post("%s/object/find" % self.host, query, headers=headers)
        data = self.r.json()
        if self.r.status_code == 200:
            if "_results" in data:
                if data["_results"] is not None:
                    for result in data["_results"]:
                        obj = NOSObject(result)
                        results.append(obj)
                return results
            else:
                if "_error" in data:
                    raise Exception("ERROR FROM NOS API Server: %s" % data["_error"])
                else:
                    raise Exception("Unknown Error: NOSClient was unable to find NOS objects.")
        else:
            if "_error" in data:
                raise Exception("ERROR FROM NOS API Server: %s" % data["_error"])
            else:
                raise Exception("Unknown Error: NOSClient was unable to find NOS objects.")
    
    def CreateObject(self, binaryData, name="", tags={}):
        # verify that the binaryData is indeed binary...
        # TODO: add more verification for binaryData
        # can use regex to match binary pattern
        if type(binaryData) is not bytes:
            raise Exception("CreateObject expected binaryData argument to be of type 'bytes' but got %s instead." % (type(binaryData)))
        
        headers = {}
        if len(name) > 0 and name != "":
            headers['x-nos-object-name'] = name
        
        if type(tags) is dict:
            if len(tags) > 0:
                tagstr = ""
                for tag in tags:
                    tagstr += "%s:%s," % (tag, tags[tag])
                tagstr = tagstr.rstrip(',')
                headers['x-nos-object-tags'] = tagstr
        try:
            self.r = requests.post("%s/object" % (self.host), binaryData, headers=headers)
            data = self.r.json()
            if self.r.status_code == 201:
                if "_object" in data:
                    obj = NOSObject(data['_object'])
                    return obj
            else:
                if '_error' in data:
                    raise Exception("CreateObject Failed. Server said: %s" % (data['_error']))
                else:
                    raise Exception("CreateObject Failed. Unknown error.")
        except Exception as err:
            print(str(err))
            pass

class NOSObject:
    """ python representation of a NOS object. """
    # This class also has a few helper methods to make interacting
    # with NOS objects a little easier in python scripts/codebases.

    def __init__(self, props = {}):
        self.UUID = None
        self.ContentType = None
        self.Checksum = None
        self.Content = None
        self.DateCreated = None # TODO: add a python datetime value converter
        self.LastUpdated = None
        self.Name = None
        self.Path = None
        self.SizeInBytes = None
        self.Tags = {}

        for prop in props:
            self._set_prop(prop, props[prop])
    
    def _set_prop(self, prop, val):
        if hasattr(self, prop):
            # we add a special condition to deserialize our "Content" property back into bytes.
            if prop == 'Content':
                if len(val) > 0:
                    setattr(self, prop, base64.b64decode(val))
            else:
                setattr(self, prop, val)
        else:
            raise Exception("Invalid NOSObject Property %s" % (prop))