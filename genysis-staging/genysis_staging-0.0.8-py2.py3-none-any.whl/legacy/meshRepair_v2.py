import requests
import json

API = "https://studiobitonti.appspot.com"
# API = "http://104.196.49.174:3000"


class meshRepair_v2:
    """
    Second generation of mesh repair functionality. This will eventually phase out the original "v1" mesh repair operations.
    """
    def __init__(self,token): #set global variables
        """
        Initialize
        """
        self.url = "%s/meshRepair_v2" % API
        self.t = token
        self.input = ''
        self.output = ''

    def setInput(self,_input):
        self.input = _input

    def setOutput(self,output):
        self.output = output

    def auto_repair(self):
        """
        Will evaluate and repair mesh using our own algorithm.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/auto_repair',payload)

    def detect_edges(self, return_index = False):
        """
        Detect naked and nonManifold edges.
        """
        payload = {"input":self.input,"return_index":return_index,"t":self.t}
        return send(self.url+'/detect_edges',payload)

    def fill_holes(self, iteration = 1):
        """
        Fills holes in the mesh.
        """
        payload = {"input":self.input,"output":self.output,"iteration":iteration,"t":self.t}
        return send(self.url+'/fill_holes',payload)

    def filter_triangles(self, naked, nonManifold):
        """
        Fix nonManifold and naked edges.
        """
        payload = {"input":self.input,"output":self.output,"naked":naked,"nonManifold":nonManifold,"t":self.t}
        return send(self.url+'/filter_triangles',payload)

    def unify_mesh_normals(self):
        """
        Set all normals to face the same direction.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/unify_mesh_normals',payload)

    def detect_overlap_faces(self):
        """
        Detect and fix overlaping mesh faces.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/detect_overlap_faces',payload)

    def detect_separate_shells(self):
        """
        Detect if a mesh is composed of multiple shells. You will need to repair this issue using the mesh split function or the union shells.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/detect_separate_shells',payload)

    def round_up_vertices(self,digits):
        """
        Merge vertices within a specific tolerance. The digits field represents the number of decimal places that will be merged.
        For example, if you have two vertices (1.21 , 2.25, 3.32) and (1.24 , 2.26, 3.38) if you set digits to 1 both vertices will be at (1.2 , 2.2, 3.3)
        """
        payload = {"input":self.input,"output":self.output,"digits":digits,"t":self.t}
        return send(self.url+'/round_up_vertices',payload)

    def delete_degenerated_faces(self):
        """
        This function will remove degenerate traingels. A degenerate triangle is the "triangle" formed by three collinear points. It doesn't look like a triangle, it looks like a line segment.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/delete_degenerated_faces',payload)

    def union_shells(self):
        """
        Merge multiple shells into one unified mesh.
        """
        payload = {"input":self.input,"output":self.output,"t":self.t}
        return send(self.url+'/union_shells',payload)


def parseResponse(r,printResult = True, parseJSON = True):
    if r.status_code == 200:
        if printResult:
            print('response: ',r.text)
        if parseJSON:
            return json.loads(r.text)
        else:
            return
    else:
        raise RuntimeError(r.text)

def send(url,payload,printPayload = True,printResult = False):

    payload = {k: v for k, v in payload.items() if v!= ''} # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)
