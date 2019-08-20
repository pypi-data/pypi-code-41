#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

import Image, ImageDraw, ImageColor, math
from MAYA.VIA import uuid, repos
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils import signing
from MAYA.utils.geometry import vectors, utils, shape_tree

r = repos.Repository('localhost:6200')
signing.enableSignatureReads(r)

RED   = "#ff0000"
YELLOW = "#ffff00"
WHITE = "#ffffff"
BLACK = "#000000"
GREY =  "#808080"
GREEN =  "#00ff00"
BLUE = "#0000ff"

red = ImageColor.getrgb(RED)
yellow = ImageColor.getrgb(YELLOW)
green = ImageColor.getrgb(GREEN)
blue = ImageColor.getrgb(BLUE)
white = ImageColor.getrgb(WHITE)
black = ImageColor.getrgb(BLACK)

### if there are more than 2 points you can set a simple projection here
def projection( point ):
#    if type(point) == type( null_vector ):
#        point = point.coords.tolist()
    return( (point[0], point[1]) )

###
# simple library routine to draw a (polygonal) shape from a list of
# coordinates (vertices) and (optionally) a bounding box.
# If the bounding box isn't specified then it's calculated

###
# arguments: components is a list of arrays of x,y tuples
#            colors is a parallel array of colors for these tuples
#            waypoints is a list of points that should be rendered as individuals
def makePicture ( components, colors=[], solo_points=[], scale=100, bbox=None, padding=10, y_invert=0 ):
    
    tly = bry = 0

    # get height and width from bbox if available
    try :
        (tlx, tly) = bbox[0]
        (brx, bry) = bbox[1]
    except :
        try :
            (tlx, tly, brx, bry) = bbox[0]
        # otherwise try to calculate from coordinates of points to be plotted
        except :
            first_point = components[0][0]
            (x, y) = projection(first_point)
            tlx = brx = x
            tly = bry = y

            for path in components :
                for point in path :
                    (x, y) = projection(point)
                    if x < tlx :
                        tlx = x
                    if x > brx :
                        brx = x
                    if y < tly :
                        tly = y
                    if y > bry :
                        bry = y
                   
    # calculate height and width from bounding box
    width = int(scale*(brx-tlx))
    height = int(scale*(bry-tly))

    # bound this if it's too big
    if (height>750 or width>1000) or (height<40 or width<50):
        if 4*width > 5*height : # in this case width is the biggest concern
            scale=1000/(brx-tlx)
        else :         # in this case height is the biggest concern
            scale=750/(bry-tly)

        width = int(scale*(brx-tlx))
        height = int(scale*(bry-tly))

#    print "width, height: ", width, height
    # create image object
    img = Image.new('RGB', [width + 2*padding , height + 2*padding], white)
    my_picture = ImageDraw.Draw(img)

    # if there are colors then we'll pop them off one by one
    if len(colors) > 0:
        colors.reverse()

    # translate points to fit within bounding box
    for path in components :
        translated_pts = []
        for point in path :
            (x, y) = projection(point)
            translated_x = int(round(scale*(x-tlx)))
            translated_y = int(round(scale*(y-tly)))

            if y_invert == 1 :
                translated_y = height - translated_y

            translated_point = (translated_x+padding, translated_y+padding)
            translated_pts.append(translated_point)

        if len(colors)>0:
            this_color = colors.pop()
        else:
            this_color = black

        my_picture.line(translated_pts, fill=this_color)


    ## add in waypoints if there are any
    if len(solo_points) > 0:
        boxsize = width/4000.0
        for solo_point in solo_points:
            solo_point_shape = [(solo_point[0]-boxsize,solo_point[1]-boxsize),
                              (solo_point[0]+boxsize,solo_point[1]-boxsize),
                              (solo_point[0]+boxsize,solo_point[1]+boxsize),
                              (solo_point[0]-boxsize,solo_point[1]+boxsize),
                              (solo_point[0]-boxsize,solo_point[1]-boxsize)]
            # this is a sloppy code repeat
            translated_pts = []
            for point in solo_point_shape :
                (x, y) = projection(point)
                translated_x = int(round(scale*(x-tlx)))
                translated_y = int(round(scale*(y-tly)))
                if y_invert == 1 :
                    translated_y = height - translated_y
                translated_point = (translated_x+padding, translated_y+padding)
                translated_pts.append(translated_point)
            my_picture.line(translated_pts, fill=black)
                        
    return img

###
def picturePath(r, path_uu):
    path_tree = shape_tree.readShapeFromUForm(r, path_uu)
    point_lists = path_tree.getAllPoints()
    my_picture = makePicture( point_lists, y_invert=1 )
    name = r.getAttr(path_uu, 'name') or "Test_picture"
    name = name.replace(' ', '_')
    filename = name + ".gif"
    my_picture.save(filename)

####
def TestUForms():
    tri_and_sq = uuid._ ( '~01d671db20830711daba8724ab1e2343ab' )
    nc_shape = uuid._('~01c9e3f81c312b11da98c1570524e54e7a')
    la_shape = uuid._('~011593a7c2214711da8cc10350131644d9')
    #minor_streets_shape = uuid._('~01e5a25b68935d11daa0c1092b07ef5706') # baseline
    minor_streets_shape = uuid._ ( '~01ef32ce8c973211dab2d8576908807aa0' ) # recursive
    #major_streets_shape = uuid._('~0141acc238935711dab6ab795a280e192a') # baseline
    major_streets_shape = uuid._('~01c13e4cbe935d11daa0c16c1a71e2785d') # recursive
    world = uuid._('~01444b7f50978211daa56763f614364132')
    picturePath(r, world)

####
# testing routines
def Test ():
    #my_picture = makePicture( [[(20,20),(80,60)],[(10,10),(10,200)]], colors=[red, green], solo_points=[(50,50)], scale=1)
    #my_picture.save("foo.gif")
    TestUForms()
    
if __name__ == "__main__":
    Test()
