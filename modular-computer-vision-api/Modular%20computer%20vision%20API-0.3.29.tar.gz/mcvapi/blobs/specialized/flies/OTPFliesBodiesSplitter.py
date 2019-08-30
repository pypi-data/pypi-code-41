from OTPBase import OTPBase
from Blob import Blob
import numpy as np, cv2
import pyforms.Utils.ImageBlobTools as blobTools



class OTPFliesBodiesSplitter(OTPBase):

    _wings_threshold = 105

    def __init__(self, **kwargs):
        super(OTPFliesBodiesSplitter, self).__init__(**kwargs)
        self._kernel = np.ones((5,5),np.uint8)

    def __wings_image(self, image):
        #_,wings = cv2.threshold(image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        _,wings = cv2.threshold(image,self._wings_threshold,255,cv2.THRESH_BINARY)
        return wings

    def __bodies_image(self, image, wings):
        not_wings = 255-wings
        body = cv2.bitwise_and(image, not_wings)
        body[body > 0] = 255
        return body

    def __bodies_contours(self, pos, bodies, howmany=1):
        contours = blobTools.getBiggestContour(bodies, howmany)
       
        for contour in contours:
            for i in range(len(contour)):
                contour[i][0][0] += pos[0]
                contour[i][0][1] += pos[1]
        return contours

    def __unmerged_flies(self, blob, bodies_contours, wings, body):
        objectsFound = []
        for cnt in bodies_contours:
            m = cv2.moments(cnt); m00 = m['m00']
            if m00 > self._param_min_area and m00 < self._param_max_area:
                if m00!=0: centroid = ( int(round(m['m10']/m00) ), int(round(m['m01']/m00)) )
                else: centroid = (0,0)

                p1, p2 = blob._bounding

                obj = Blob()
                obj._contour = cnt
                obj._full_contour = blob._contour
                obj._bounding = (p1, p2)
                obj._area = m00
                obj._centroid = centroid
                obj._oimage = blob._oimage
                obj._image = blob._image
                obj._image_mask = blob._image_mask
                obj._wings_image = wings
                obj._body_image  = body

                objectsFound.append( obj )
        return objectsFound

    def __merged_flies(self, blob, bodies_contours):
        pass

    def compute(self, blobs):
        self._flies_bodies_split = 0

        if len(blobs)==1:
            b = blobs[0]
            image = b._image
            p1, p2 = b._bounding
            if len(image.shape)>2: image = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)

            wings = self.__wings_image(image)
            bodies = self.__bodies_image(image, wings)
            bodies_contours = self.__bodies_contours( p1, bodies, 2)
            if len(bodies_contours)==2:
                self._flies_bodies_split = 1
                return self.__unmerged_flies(b, bodies_contours, wings, bodies)
            else:
                self._flies_bodies_split = 2
                return blobs

        else:
            for i, b in enumerate(blobs):
                image = b._image
                if len(image.shape)>2: image = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)

                p1, p2          = b._bounding
                wings           = self.__wings_image(image)
                body            = self.__bodies_image(image, wings)
                body_contour    = self.__bodies_contours(p1, body)[0]

                b._full_contour = b._contour
                b._contour      = body_contour
                b._wings_image  = wings
                b._body_image   = body

                # window_title = 'Fly {}: body'.format(i)
                # cv2.imshow(window_title, body)
                # window_title = 'Fly {}: wings'.format(i)
                # cv2.imshow(window_title, wings)
                # cv2.waitKey(1)

            return blobs

    def process(self, blobs):
        blobs = super(OTPFliesBodiesSplitter, self).process(blobs)

        return OTPFliesBodiesSplitter.compute(self, blobs)
