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
#!/usr/bin/env python
#
# routines for computing the area and centroid of a polygon given by a
# list of coodinates of its vertices.

# so far I'm not bothering to convert from latitude/longitude, I'm
# just assuming an orthonormal coordinate system

# area function: takes a list of 2-tuples and computes the area they enclose
def area( parallel_list ) :
    polygon = zip( parallel_list['x'], parallel_list['y'] )
    # if it's not a closed polygon wrap it round so that it is
    if polygon[0] != polygon[len(polygon)-1] :
        polygon.append(polygon[0])

    area = 0
    for i in range(1, len(polygon)-1 ):
        area += (polygon[i][0]*polygon[i-1][1])-(polygon[i-1][0]*polygon[i][1])

    return area/2

# centroids function: takes a list of 2-tuples and computes the
# coordinates of their centre of gravity
# this is pretty similar to the area function
def centroid( path ) :
    # this is not a good hack to make the function take different sorts of arguments
    if type(path)==type([]):
        points = path
        path = {}
        path['x'] = []
        path['y'] = []
        for point in points:
            path['x'].append(point[0])
            path['y'].append(point[1])

    X = path['x']
    Y = path['y']

    if len(X) != len(Y) :
        print "Ill-formed point lists passed to centroid function."
        return -1

    # if it's not a closed polygon wrap it round so that it is
#    if ( X[len(X)-1], Y[len(Y)-1] ) != (X[0], Y[0]) :
    X.append(X[0])
    Y.append(Y[0])

    x_ave = 0.0
    y_ave = 0.0
    area = 0.0
    for i in range(0, len(X)-2 ):
        chunk = X[i+1]*Y[i] - X[i]*Y[i+1] 
        area += chunk
        x_ave += (X[i+1] + X[i]) * chunk
        y_ave += (Y[i+1] + Y[i]) * chunk

    x_ave = (x_ave/area)/3.0
    y_ave = (y_ave/area)/3.0

    return (x_ave, y_ave)


####
def makeParallel( points ):
    dict ={}
    dict['x'] = []
    dict['y'] = []
    for point in points:
        dict['x'].append(point[0])
        dict['y'].append(point[1])
    return dict

########
def Test():
    path= { 'x' : [0, -1, -2, 0], 'y' : [0, 0, -2, -1] }
    print centroid(path)

if __name__ == '__main__' :
    Test()


    

