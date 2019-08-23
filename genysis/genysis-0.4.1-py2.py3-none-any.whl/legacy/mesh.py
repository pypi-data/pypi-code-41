from .parse_request import send

API = {"endpoint": "https://studiobitonti.appspot.com"}

def union_shells(input=None,output=None,token=None):
    url ="%s/union_shells" % API["endpoint"]
    payload = {"input":input,"output":output,"t":token}
    return send(url,payload)

def auto_repair(input=None,output=None,token=None):
    url ="%s/auto_repair" % API["endpoint"]
    payload = {"input":input,"output":output,"t":token}
    return send(url,payload)

def mesh_reduction(input=None,output=None,ratio=0.5,token=None):
    url ="%s/mesh_reduction" % API["endpoint"]
    payload = {"input":input,"output":output,"ratio":ratio,"t":token}
    return send(url,payload)