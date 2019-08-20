from MAYA.VIA import uuid,uform,repos
r = repos.Repository('localhost:6200')

import sys
sys.path.append('/Users/widdows/svn/components/C/r2')
import vvf
from MAYA.VIA import vsmf

MAX_LEN = 6000

### if there are more than 2 points you can set a simple projection here
def projection( point ):
    return( (point[0], point[1]) )

def getMinMax( point_lists ):
    min = list(point_lists[0][0])
    max = list(point_lists[0][0])
    for polyline in point_lists:
	for point in polyline:
	    for i in range(len(point)):
		if point[i] < min[i]:
		    min[i] = point[i]
		if point[i] > max[i]:
		    max[i] = point[i]
    return (min, max)

def drawPolylineImage( r, uu, polylines, point_objects=[] ): 
    (min, max) = getMinMax(polylines)
    
    max_scale = 0
    for i in range(len(min)):
	if max[i]-min[i] > max_scale:
	    max_scale = max[i]-min[i]
    DIVISOR = max_scale/MAX_LEN

    x1,y1,x2,y2 = 0, 0, (max[0]-min[0])/DIVISOR, (max[1]-min[1])/DIVISOR
    print 'x1=%d, y1=%d, x2=%d, y2=%d' % (x1,y1,x2,y2)
    w = x2-x1
    h = y2-y1

    r.setAttr(uu,'image_width',w)
    r.setAttr(uu,'image_height',h)


    vp = vvf.VVFpath()
    vp.set_fillstroke(1,0,1)
    for points in polylines:
	point = points[0]
	vp.moveto(int((point[0]-min[0])/DIVISOR), int((max[1]-point[1])/DIVISOR))
	for point in points[1:]:
	    if len(point)>2:
		point = projection(point)
	    point = map(int, [ (point[0]-min[0])/DIVISOR, (max[1]-point[1])/DIVISOR ])
	    vp.lineto(point[0], point[1])

    p = vvf.VVFpict()
    p.ctx_width(20)
    p.ctx_stroke(128,64,128,64)
    p.add_path(vp)

    # now do something for point objects
    vp2 = vvf.VVFpath()
    vp2.set_fillstroke(1,0,1)
    for point in point_objects:
	vp2.moveto(int((point[0]-min[0])/DIVISOR-w/80), int((max[1]-point[1])/DIVISOR))
	vp2.lineto(int((point[0]-min[0])/DIVISOR+w/80), int((max[1]-point[1])/DIVISOR))
	vp2.moveto(int((point[0]-min[0])/DIVISOR), int((max[1]-point[1])/DIVISOR-h/80))
	vp2.lineto(int((point[0]-min[0])/DIVISOR), int((max[1]-point[1])/DIVISOR+h/80))
    p.ctx_width(10)
    p.ctx_stroke(128,128,0,0)
    p.add_path(vp2)

    vs = p.serialize()
    mv = vsmf.MimeVal('image/vvf',vs)
    r.setAttr(uu,'image_data',mv)

    #print vs
    #x1,y1,x2,y2 = vvf.bounds_from_buffer(vs)

def test():
    from MAYA.utils.geometry import simplify, drawShape
    #uu = uuid._('~013f9c4ed669e211dbb75327a02f6d5f23') # recursive
    uu = uuid._('~01ef259e706adf11db93bf4b741029604e') # linear
    #uu = uuid._('~01e676a9866c8311db93bf1ca226197b99') #projection
    (point_lists, point_objects) = simplify.test2()
    drawPolylineImage(r, uu, point_lists, point_objects)
    my_picture = drawShape.makePicture( point_lists, y_invert=1 )
    my_picture.save('rcoast.gif')

if __name__ == '__main__':
    test()
