import requests
import json

API = {"endpoint": "https://studiobitonti.appspot.com"}

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

def send(url,payload,printPayload = True,printResult = True):

    payload = {k: v for k, v in payload.items() if v!= '' and v != None } # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)

class adaptiveLattice:
    """
    This object of for lattices that conform their shape to volumes.
    """
    def __init__(self): #set global variables
        """
        Initialize
        """
        #URL is always this.
        self.urlGrid = "%s/adaptiveGrid" % API["endpoint"]
        self.urlPopulate = "%s/boxMorph" % API["endpoint"]
        self.urlImplicit = "%s/implicit_lattice" % API["endpoint"]        
        #variables that need to be set by the user.
        self.cellSize = None
        self.edges = None
        self.volume=None
        self.output=None
        self.component=None
        self.gridOutput='temp_grid.json'
        self.boxes=None
        self.attractorSet=[]
        self.EPSILON = None
        self.origin = None

    def setVolume(self,volume):
        self.volume = volume
    def setEdges(self,edges):
        self.edges = edges
    def setCellSize(self,cellSize):
        self.cellSize = cellSize
    def setOrigin(self,origin):
        self.origin = origin
    #(string) Component: Is the uploaded .Obj component to be arrayed.
    def setComponent(self,component):
        self.component=component
    #(string) Name of the .json file for export.
    def setGridOutput(self,gridOutput):#file name that you want to save out
        self.gridOutput=gridOutput
    #(string) Name of lattice file for export.
    def setOutput(self,output):#file name that you want to save out
        self.output=output
    def setEPSILON(self,EPSILON):
        self.EPSILON=EPSILON

    #add point attractor. For example:(component="cell_2.obj",point=[2.8,8,2.7],range=5)
    def addPointAttractor(self,component,point,range):
        self.attractorSet.append({"component":component,"attractor":{"point":point,"range":range}})
    #add plane attractor. For example:(component="cell_2.obj",plane=[0,1,0,-5],range=10)
    def addPlaneAttractor(self,component,plane,range):
        self.attractorSet.append({"component":component,"attractor":{"plane":plane,"range":range}})
    #add curve attractor. For example: (component="unit_1.obj",curve=[[2.8,8,2.7],[-3.3,8,2.7],[-3.3,14,6]],range=2)
    def addCurveAttractor(self,component,curve,range):
        self.attractorSet.append({"component":component,"attractor":{"curve":curve,"range":range}})


    def genGrid(self,token):
        """
        """
        payload = {
            "input":self.volume,
            "output":self.gridOutput,
            "cellSize":self.cellSize,
            "edges":self.edges,
            "origin": self.origin,
            "t":token
            }
        self.boxes=self.gridOutput

        return send(self.urlGrid,payload)

#Populate conformal lattice
    def populateLattice(self,token):#Lattice on one surface with a constant offset with attractors for blended lattice
        """
        The Populate modulus function populates a given component into a conformal grid structure. It fill the boxes of the conformal grid into the component defined in the input.

        Component: Is the uploaded .Obj component to be arrayed.
        Boxes: Is the name of uploaded box scaffold json name.
        File Name:  Name of the resultant file for the surface lattice.
        """
        #get attractor information

        payload = {"boxes":self.gridOutput,"component":self.component,"filename":self.output,"t":token,"blendTargets":self.attractorSet,"EPSILON":self.EPSILON}
        return send(self.urlPopulate,payload)

    def implicitLattice(self,function,token,resolution = None,unit_resolution = None,smooth = None):

        payload = {"grid":self.gridOutput,"output":self.output,"function": function,"resolution":resolution,"unit_resolution":unit_resolution,"smooth":smooth,"t":token}
        return send(self.urlImplicit,payload)