import requests
import json
import webbrowser
import os,sys
from .mesh import *
from .meshRepair import *
from .meshRepair_v2 import *
from .adaptiveLattice import *
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

API = {"endpoint": "https://studiobitonti.appspot.com"}
# API = {"endpoint": "http://localhost:3000"}

print('Welcome to GENYSIS')

def fileManager(token='',displayInLine = False,width=600, height=500):
    url = "%s/?t=%s" % (API["endpoint"],token)

    print(url)
    if displayInLine:
        from IPython.display import IFrame
        display(IFrame(url, width, height))
    else:
        webbrowser.open(url)
    return url

# internal function for response parsing and error handling
def parseResponse(r,printResult = True, parseJSON = True):
    if r.status_code == 200:
        if printResult:
            print('response: ',r.text)
        if parseJSON:
            return json.loads(r.text)
        else:
            return r.text
    else:
        raise RuntimeError(r.text)

def send(url,payload,printPayload = True,printResult = True):

    payload = {k: v for k, v in payload.items() if v!= '' and v != None } # clean None inputs
    if printPayload:
        print('request: ',json.dumps(payload))
    r = requests.post(url,json=payload)
    return parseResponse(r,printResult)

# File management functions
def download(src = '',dest = '',token = ''):
    """
    Download files from the genysis servers.
    src: location on the genysis servers.
    dest: local file name/path
    """
    url= "%s/storage/download?name=%s&t=%s" % (API["endpoint"],src,token)
    # r = requests.get(url, allow_redirects=True)
    # parseResponse(r,printResult = False,parseJSON = False) # just to check response status
    # open(dest, 'wb').write(r.content)
    # print('successfully downloaded to %s/%s' % (os.getcwd(),dest))
    # return

    with open(dest, "wb") as f:
        print("Downloading %s as %s" % (src,dest))
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                percentage = str(int(100 * dl / total_length))+'%'
                sys.stdout.write("\r[%s%s]%s" % ('=' * done, ' ' * (50-done),percentage) )
                sys.stdout.flush()

    print('\nsuccessfully downloaded to %s' % (dest))

def upload(src ,dest = '',token = ''):
    """
    Upload files from the genysis servers.
    src: local file name/path
    """
    url= "%s/storage/upload" % API["endpoint"]

    if dest == '':
        dest = src

    file_size = os.path.getsize(src)
    print ('uploading file size:',(file_size//1000)/1000.0,'MB')

    if (file_size >= 32 * 1000 * 1000):
        print('file is larger than 32MB, using compute node for uploading')
        r = requests.get( "%s/compute/getNode?t=%s" % (API["endpoint"],token), allow_redirects=True)
        computeNode = parseResponse(r,False,False)
        url= "%s/storage/upload" % computeNode
        print('compute node found')

    # files = {'upload_file': open(src,'rb')}
    # values = {'t': token}
    # r = requests.post(url, files=files, data=values)
    # parseResponse(r,printResult = False,parseJSON = False) # just to check response status

    def my_callback(monitor):
    # Your callback function
        progress = monitor.bytes_read
        done = int(50 * progress / file_size)
        percentage = str(int(100 * progress / file_size)) + '%'
        sys.stdout.write("\r[%s%s]%s" % ('=' * done, ' ' * (50-done), percentage ))
        sys.stdout.flush()

    e = MultipartEncoder(
        fields={'t': token,
                'dest': dest,
                'file': (src, open(src, 'rb'), 'text/plain')}
        )
    m = MultipartEncoderMonitor(e, my_callback)
    r = requests.post(url, data=m, headers={'Content-Type': m.content_type})

    print('\nsuccessfully uploaded %s as %s' % (src,dest))
    return parseResponse(r,printResult=False)

def listFiles(token):
    url="%s/storage/list?t=%s" % (API["endpoint"],token)
    r = requests.get(url, allow_redirects=True)
    return parseResponse(r,printResult=False)

def visualize(name,token,displayInLine=False,width=800, height=600):
    """
    open a default browser window to visualize a geometry file given its name and user token
    """
    if isinstance(name, list):
        name = ','.join(name)
    url = '%s/apps/visualize?name=%s&t=%s'%(API["endpoint"],name,token)
    print(url)
    if displayInLine:
        from IPython.display import IFrame
        display(IFrame(url, width, height))
    else:
        webbrowser.open(url)
    return url

def latticeUnitDesign(name='',token='',displayInLine=False,width=800, height=600):
    """
    open a default browser window to for the lattice unit design app
    """
    url = '%s/apps/visualize/latticeUnit.html?name=%s&t=%s'%(API["endpoint"],name,token)
    print(url)
    if displayInLine:
        from IPython.display import IFrame
        display(IFrame(url, width, height))
    else:
        webbrowser.open(url)
    return url

def cylindricalProjection(target,resolution,height,output,token,center='',range='',startDir='',rotateAxis='',project_object='',project_height='',project_offset=''):
    """
    The cylindrical projection function wraps a cylindrical mesh around the input mesh. It can used to shrink wrap the mesh and create a new cleaner and refined mesh. The target and resolution can basic inputs required, whereas advance inputs include defining a center, and axis for the projection. This projection is made using a cylindrical base.

    Target: (string) The uploaded .Obj target to be projected on.
    Resolution: (int) Is the number cells in U and V direction.
    Height:(float)  Height of cylinder to be projected.
    File Name:(string)  Name of the resultant file for the surface lattice.

    OPTIONAL:
    to be added

    """
    url ="%s/cylindricalProjection" % API["endpoint"]
    payload = {"target":target,"center":center,"resolution":resolution,"range":range,"rotate_axis":rotateAxis,"start_dir":startDir,"height":height,"filename":output,"t":token,"project_object":project_object,"project_height":project_height,"project_offset":project_offset}
    return send(url,payload)

def sphericalProjection(target,resolution,output,token,center='',range='',startDir='',rotateAxis='',project_object='',project_height='',project_offset=''):
    """
    The spherical projection function works by wraps a given mesh with a sphere either partially or whole in order to create a clean base surface from the input. The target and resolution can basic inputs required, whereas advance inputs include defining a center, and axis for the projection. This projection is made using a spherical base.

    Target:(String) The uploaded .Obj target to be projected on.
    Resolution: (int) Is the number cells in U and V direction.
    File Name:(string)  Name of the resultant file for the surface lattice.

    OPTIONAL:
    to be added
    """
    url ="%s/sphericalProjection" % API["endpoint"]
    payload = {"target":target,"center":center,"resolution":resolution,"range":range,"rotate_axis":rotateAxis,"start_dir":startDir,"filename":output,"t":token,"project_object":project_object,"project_height":project_height,"project_offset":project_offset}
    return send(url,payload)

def planarProjection(target,center,direction,size,resolution,output,token,project_object='',project_height='',project_offset=''):
    """
    The plane projection function wraps a given mesh input by projecting a place on to it from the specified direction. This function can be used to patch holes, create a new draped mesh over multiple objects, etc. The required inputs include the target file name, center of the object, direction of projection, size of the plane and its resolution.

    Target:(String) The uploaded .Obj target to be projected on.
    Center:(array) 3D coordinate of projection center, by default [0,0,0].
    Direction:(vector) 3D vector defining, the direction where projection starts, by default [1,0,0].
    Size:(2D vector)  Is the [U,V] input defining the size of the projected plane.
    Resolution:(int) Is the number cells in U and V direction.
    File Name:(string)  Name of the resultant file for the surface lattice.
    """
    url ="%s/planeProjection" % API["endpoint"]
    payload = {"target":target,"center":center,"direction": direction,"size":size,"resolution":resolution,"filename":output,"t":token,"project_object":project_object,"project_height":project_height,"project_offset":project_offset}
    return send(url,payload)

def boolean(input1,input2,output,operation,token,engine='carve',vxsize=''): #operations are Union, Interset and Difference
    """
    This is the Doc stings located at the top of the file.

    Input1:(string) Name of first .obj component file uploaded to storage.
    Input2:(string) Name of second .obj component file uploaded to storage.
    Output:(string) Result file name for the boolean operation in .obj format.
    Operation:(string) Choose one from union,difference and intersection.
    """
    if engine == 'voxel':
        url ="%s/voxel_boolean" % API["endpoint"]
    else:
        url ="%s/boolean" % API["endpoint"]
    payload = {"input1":input1,"input2":input2,"operation":operation,"output":output,"t":token, "engine":engine,'vxsize': vxsize}
    return send(url,payload)

def convexHull(points,token):
    """
    The convex hull function creates a boundary around the outermost laying points. It is used to get a sense of size of the point cloud field.
    Input is an array
    """
    url ="%s/convexHull" % API["endpoint"]
    payload = {"points":points,"t":token}
    return send(url,payload)

def voronoi(points,token):
    """
    The voronoi function creates partitions based on distance between the input points.
    Input is an array
    """
    url ="%s/voronoi" % API["endpoint"]
    payload = {"points":points,"t":token}
    return send(url,payload)

def delaunay(points,token):
    """
    The delaunay triangulation function creates triangular connections in 2D and 3D. The input is a point cloud array in any dimensions.
    Input is an array
    """
    url ="%s/delaunay" % API["endpoint"]
    payload = {"points":points,"t":token}
    return send(url,payload)

def blend(compA,compB,value,output,token):
    """
    The blend function takes two mesh objects with same topology and different vertices locations, then output a blended geometry given a value between 0 and 1.

    compA:(string)  name of component A obj file uploaded to storage
    compB:(String)  name of component B obj file uploaded to storage
    filename:(string) target output file name
    value:(float)  float between 0 and 1, the blend position between compA and compB
    """
    url ="%s/blend" % API["endpoint"]
    payload = {"compA":compA,"compB":compB,"value":value,"filename":output,"t":token}
    return send(url,payload)

def meshSplit(target,output,token):
    """
    The split mesh function breaks down the given mesh input into its component mesh parts.

    Target:(string)  Name of input .obj/.stl file uploaded to storage
    Filename:(string) Target output file name
    """
    url ="%s/meshSplit" % API["endpoint"]
    payload = {"target":target,"filename":output,"t":token}
    return send(url,payload)

def meshReduce(target,output,portion,token):
    """
    Reduce the number of faces of a mesh.

    target:(string) the name of the mesh you want to reduce
    output:(string) the name of the new mesh after reduction.
    portion:(float) the percentage you wish to reduce the mesh.
    """
    url ="%s/meshreduction" % API["endpoint"]
    payload = {"target":target,"portion":portion,"filename":output,"t":token}
    return send(url,payload)

def genLatticeUnit(case,chamfer,centerChamfer,bendIn,cBendIn,connectPt,output,token):
    """
    Case:(Integer) Is an integer value between 0 - 7,  defining different type of lattice units.
    Chamfer:(float) Is a float value between 0 to 0.5 defining the angle of chamfer of the corners.
    Center Chamfer:(float) Is a float value between 0 to 0.5 defining the angle of chamfer from the center.
    Bendln:(float) Is a float value between 0 and 1, defining angle bend of the lines.
    cBendln:(float)  Is a float value between 0 and 1,defining the central bend of the lines.
    Connect Pt:(float)  Is a float value between 0 and 1, defining the connection points.
    """
    url = "%s/latticeUnit" % API["endpoint"]
    payload = {"case":case,"chamfer":chamfer,"centerChamfer":centerChamfer,"bendIn":bendIn,"cBendIn":cBendIn,"connectPt":connectPt,"filename":output,"t":token}
    return send(url,payload)

def marchingCube(lines,resolution,memberThickness,filename,token,preview='',blendTargets=None):
    """
    The marching cubes function is used to create a mesh from the given line input. Is it used to create a thickness that can be defined by the user, as well as the resolution.

    Lines:(string) Is the uploaded .obj file containing lines to be meshed by Marching Cubes algorithm.
    Resolution:(int)  Is the integer value between from 64 to 600, defining the resolution of the meshing operation. Lower value gives a more coarse result, whereas a higher value gives out a more refined result.
    Member Thickness:(float)  Is a float value defining the radius of the line members being meshed.
    Filename:(string) Name of the resultant file of the meshed object.
    """
    url = "%s/marchingCube" % API["endpoint"]
    payload = {"lines":lines,"resolution":resolution,"memberThickness":memberThickness,"filename":filename,"t":token,"preview":preview,'blendTargets':blendTargets}
    return send(url,payload)

class volumeLattice:
    """
    This is for lattices that conform to volumes but do not change the shape of the lattice units.
    """
    def __init__(self): #set global variables
        #URL is always this.
        self.url = "%s/volumeLattice" % API["endpoint"]
        self.urlStochastic = "%s/stochasticLattice" % API["endpoint"]
        #variables that need to be set by the user.
        self.poreSize=""
        self.volume=""
        self.output=""
        self.component=""
        self.componentSize=""
        self.attractorSet=[]

#functions for seting key variables
    #(string) Set the file name for the exported lattice structure
    def setOutput(self,output):#file name that you want to save out
        self.output=output
    #(String) set the volume you want to fill with the lattice
    def setVolume(self,volume):#base surface
        self.volume=volume
    #(float) For stochastic lattices only. This will be the miniumum pore size for the stochastic lasttice.
    def setPoreSize(self,pore):#pore size for stochastic Lattice
        self.poreSize=pore
    #(float) This is the size of the lattice grid. For one unit.
    def setComponentSize(self,cellHeight):#size of componet in a static or graded grid
        self.componentSize=cellHeight
    #(string) Set the file name for the component to be populated to lattice structure
    def setComponent(self,component):
        self.component=component

    #add point attractor. For example:(component="cell_2.obj",point=[2.8,8,2.7],range=5)
    def addPointAttractor(self,component,point,range):
        self.attractorSet.append({"component":component,"attractor":{"point":point,"range":range}})
    #add plane attractor. For example:(component="cell_2.obj",plane=[0,1,0,-5],range=10)
    def addPlaneAttractor(self,component,plane,range):
        self.attractorSet.append({"component":component,"attractor":{"plane":plane,"range":range}})
    #add curve attractor. For example: (component="unit_1.obj",curve=[[2.8,8,2.7],[-3.3,8,2.7],[-3.3,14,6]],range=2)
    def addCurveAttractor(self,component,curve,range):
        self.attractorSet.append({"component":component,"attractor":{"curve":curve,"range":range}})

#lattice generation functions

    def runStochastic(self,token):
        """
        once all the variables are set you will run this function to generate a stochastic lattice.
        """
        payload = {"volume":self.volume,"poreSize":self.poreSize,"filename":self.output,"t":token}
        return send(self.urlStochastic,payload)

    def run(self,token):
        """
        once all the variables are set you will run this function to generate the lattice.
        """
        payload = {"component":self.component,"volume":self.volume,"componentSize":self.componentSize,"filename":self.output,"t":token,"blendTargets": self.attractorSet}
        return send(self.url,payload)

class surfaceLattice:
    """
    This class is for lattice that form their shapes to surfaces
    """
    def __init__(self): #set global variables
        """
        Initialize
        """
        #URL is always this.
        self.url = "%s/surfaceLattice"%(API["endpoint"])
        self.gridUrl = "%s/surfaceGrid"%(API["endpoint"])
        self.urlPopulate = "%s/boxMorph" % API["endpoint"]
        self.urlImplicit = "%s/implicit_lattice" % API["endpoint"]
        self.EPSILON=0.01
        #variables that need to be set by the user.
        self.output = None
        self.attractorSet=[]
        self.component=None
        self.gridOutput = 'temp.json'
        self.div_U = None
        self.div_V = None
        self.div_W = None
        self.height = None

#functions for seting key variables

    #(float) Epsilon is used to determin tolerances that define when two lattice cells are considered touching.
    def setEPSILON(self,EPSILON):
        self.EPSILON=EPSILON
    #(string) this is the name of the file that the function will output after it is computed.
    def setOutput(self,output):#file name that you want to save out
        self.output=output
    #(string) Define the base surface to populat lattices on. This will be a mesh with all 4 sided faces.
    def setSurfaces(self,surfaces):
        self.surfaces=surfaces
    #(float) If you do not define a top surface you will need to define a constant height to offset the lattice units.
    def setHeight(self,height):#if no top surface is defined set a cell height. Else it will be set to 1
        self.height=height

    def setDivision(self, u = None, v = None, w = None):
        self.div_U = u
        self.div_V = v
        self.div_W = w

    def setGridOutput(self,output):#file name that you want to save out
        self.gridOutput=output

    def genGrid(self,token):
        payload = {
            "surfaces": self.surfaces,
            "div_U": self.div_U,
            "div_V": self.div_V,
            "div_W": self.div_W,
            "output": self.gridOutput,
            "height": self.height,
            "t": token
        }

        return send(self.gridUrl,payload)

    def setComponent(self,component):
        self.component=component
    #add point attractor. For example:(component="cell_2.obj",point=[2.8,8,2.7],range=5)
    def addPointAttractor(self,component,point,range):
        self.attractorSet.append({"component":component,"attractor":{"point":point,"range":range}})
    #add plane attractor. For example:(component="cell_2.obj",plane=[0,1,0,-5],range=10)
    def addPlaneAttractor(self,component,plane,range):
        self.attractorSet.append({"component":component,"attractor":{"plane":plane,"range":range}})
    #add curve attractor. For example: (component="unit_1.obj",curve=[[2.8,8,2.7],[-3.3,8,2.7],[-3.3,14,6]],range=2)
    def addCurveAttractor(self,component,curve,range):
        self.attractorSet.append({"component":component,"attractor":{"curve":curve,"range":range}})

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


class conformalLattice:
    """
    This object of for lattices that conform their shape to volumes.
    """
    def __init__(self): #set global variables
        """
        Initialize
        """
        #URL is always this.
        self.urlGrid = "%s/conformalGrid" % API["endpoint"]
        self.urlPopulate = "%s/boxMorph" % API["endpoint"]
        self.urlImplicit = "%s/implicit_lattice" % API["endpoint"]        
        #variables that need to be set by the user.
        self.u=''
        self.v=''
        self.w=''
        self.unitize=''
        self.output=''
        self.component=''
        self.surfaces=''
        self.gridOutput='temp_grid.json'
        self.boxes=""
        self.attractorSet=[]
        self.EPSILON = 0.01
        self.merges = []

#functions for seting key variables
    def setUVW(self,u,v,w):
        """
        U: Input the number of grid cells in u direction.
        V: Input number of grid cells in v direction.
        W: Input number of grid cells in w direction.
        """
        self.u=u
        self.v=v
        self.w=w
    #(boolean) The input of true or false,defines whether to redivide the surface in unitized way.
    def setUnitize(self,unitize):
        self.unitize=unitize
    #(string) Component: Is the uploaded .Obj component to be arrayed.
    def setComponent(self,component):
        self.component=component
    #(string) Name of the uploaded .json file of surface grid representations.
    def setSurfaces(self,surfaces=None,top=None,bottom=None,side1=None,side2=None):
        self.surfaces=surfaces
        self.top = top
        self.bottom = bottom
        self.side1 = side1
        self.side2 = side2
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


    def addMerge(self,merge_object):
        self.merges.append(merge_object)


#Generate conformalGrid
    def designGrid(self,token,displayInLine=False,width=800, height=600):

        url = '%s/apps/visualize/gridDesign.html?surfaces=%s&t=%s&filename=%s'%(API["endpoint"],self.surfaces,token,self.gridOutput)
        print(url)
        if displayInLine:
            from IPython.display import IFrame
            display(IFrame(url, width, height))
        else:
            webbrowser.open(url)
        return url


    def genGrid(self,token):
        """
        The conformal grid function generates a grid structure inside a given mesh input. The U,V,W are variables for the number of the grid cells.

        U: Input the number of grid cells in u direction.
        V: Input number of grid cells in v direction.
        W: Input number of grid cells in w direction.
        Surface: Name of the uploaded .json file of surface grid representations.
        Filename: Name of the resultant file for the lattice unit.
        """
        payload = {
            "u":self.u,"v":self.v,"w":self.w,
            "unitize":self.unitize,
            "surfaces":self.surfaces,
            "top":self.top,"bottom":self.bottom,"side1":self.side1,"side2":self.side2,
            "filename":self.gridOutput,
            "merges": self.merges,
            "t":token
            }
        self.boxes=self.gridOutput

        if self.top and self.bottom and self.side1 and self.side2 :
            payload['output'] = payload['filename']
            return send(self.urlGrid+'_v2',payload)
        else:
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



class fea:

    def __init__(self): 

        self.url = "%s/fea" % API["endpoint"]
        self.setting = {'load_conditions':[],'support_conditions':[],'material':{},'remesh':{'detail':'normal','fast':False}}

    def setVolume(self,volume=None):
        self.volume = self.setting['input']  = volume

    def setOutput(self,output = None):
        self.output = self.setting['output'] = output

    def setMaterial(self,elastic_modulus = 100,poisson_ratio = 0.4):
        self.setting['material']['elastic_modulus'] = elastic_modulus
        self.setting['material']['poisson_ratio'] = poisson_ratio

    def addLoad(self,condition=None,load=None,file=None):

        if file != None:
            condition = {'file':file}

        self.setting['load_conditions'].append({
            'type': 'cload',
            'load': load,
            'condition':condition
        })

    def addSupport(self,condition=None,axis=None,file=None):

        if file != None:
            condition = {'file':file}

        self.setting['support_conditions'].append({
            'axis': axis,
            'condition':condition
        })

    def setRemesh(self,detail='normal',fast=False):
        self.setting['remesh']['detail'] = detail
        self.setting['remesh']['fast'] = fast


    def run(self,token):

        inputs = [self.volume]
        loads = []
        for load in self.setting['load_conditions']:
            if 'file' in load['condition']:
                loads.append(load['condition']['file'])
        supports = []
        for support in self.setting['support_conditions']:
            if 'file' in support['condition']:
                supports.append(support['condition']['file'])
        inputs = inputs + loads + supports

        payload = {"input":inputs,"output":self.output,'setting':self.setting,'t':token}
        return send(self.url,payload)


class surfaceRoughness:

    def __init__(self): 
        self.url = "%s/surfaceRoughness" % API["endpoint"]
        self.roughness_size = None
        self.radius = None

    def setInput(self,input=None):
        self.input = input

    def setOutput(self,output = None):
        self.output = output

    def setRoughnessSize(self,size):
        self.roughness_size = size

    def setRadius(self,radius):
        self.radius = radius

    def run(self,token):
        payload = {"input":self.input,"output":self.output,'roughness_size':self.roughness_size,'radius':self.radius,'t':token}
        return send(self.url,payload)