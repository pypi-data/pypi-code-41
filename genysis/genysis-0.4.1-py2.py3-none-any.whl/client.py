import requests
import json
from time import time
from .legacy import download,upload,listFiles,visualize

def parseResponse(r,printResult = True):
    if r.status_code == 200:
        if printResult: print('response: ',r.text)
        try:
            return json.loads(r.text)
        except:
            return r.text
    else:
        raise RuntimeError(r.text)

def send(url,payload,printPayload = True,printResult = True):
    payload = {k: v for k, v in payload.items() if v!= '' and v != None }
    if printPayload: print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)

class client:
    
    def __init__(self, token = None,test=False):
        print("Connecting to Genysis")
        self.url = "https://studiobitonti.appspot.com/v1/"
        if test: 
            self.url = "https://studiobitonti.appspot.com/staging/"
            print("using testing server")
        self.token = token
        self.auth()
        
    def attach_token(self,body = None):
        if body == None: body = {}
        body['t'] = self.token
        return body
        
    def auth(self): 
        return send(self.url+'user', self.attach_token())
    
    def list_functions(self):
        return send(self.url+'list_functions', self.attach_token() )
    
    def run(self, function = None, parameters = None, print_time = False):
        
        start = time()
        result = send( self.url+function, self.attach_token(parameters) )
        end = time()
        if print_time: print('took: ', int(end-start),'s')
        
        return result
    
    def visualize(self,names):
        return visualize(names,self.token,True)
    
    def upload(self,src,dest=None):
        if dest == None: dest = src
        upload(src,dest,self.token)
        
    def download(self,src,dest=None):
        if dest == None: dest = src
        download(src,dest,self.token)
        
    def list_files(self):
        return listFiles(self.token)
        
    