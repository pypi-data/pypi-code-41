from itertools import product
from mcvapi.mcvbase import MCVBase

def combinations(iter1, iter2):
    size = len(iter1)
    a = [e for e in iter1]
    for i in range(size):
        res = []
        for j in range(size):
            res.append((a[j],iter2[j]))
        a = a[1:]+a[:1]
        yield list(res)


class OrderByPosition(MCVBase):
    """
    Order the blobs by position
    Return: Ordered blobs
    """

    IMPORT = "from mcvapi.blobs.order_by_position import OrderByPosition"
    
    def __init__(self, **kwargs):
        super(OrderByPosition, self).__init__(**kwargs)
        self._orderblobs_last_blobs = []
    
    def clear(self): self._orderblobs_last_blobs = []

    def process(self, blobs, **kwargs):
        # First time
        if len(self._orderblobs_last_blobs)==0 or len(self._orderblobs_last_blobs)<len(blobs): 
            self._orderblobs_last_blobs = blobs
            return blobs

        blobs = blobs + [None for i in range(len(self._orderblobs_last_blobs)-len(blobs))]

        #################### SELECT BLOBS BY POSITION ########################
        #### Blobs are identified by their distance to the previous position
        
        classifications = []
        for comb in combinations( blobs, self._orderblobs_last_blobs ):
            distances = []
            for b1,b2 in comb:
                if (b1!=None and b2!=None):
                    dist = b1.distance_to(b2)
                    distances.append(dist)

            classification = sum(distances)
            classifications.append([classification, [b1 for b1,b2 in comb]])

        if len(classifications)==0: 
            return [ None for i in range(len(self._orderblobs_last_blobs)) ]
        
        classifications = sorted(classifications, key=lambda x: x[0], reverse=False)
        
        r = classifications[0]

        for i in range(len(r[1])):
            if r[1][i] is not None:
                self._orderblobs_last_blobs[i] = r[1][i]

        return r[1]

    def processflow(self, blobs, **kwargs):
        blobs = super(OrderByPosition, self).processflow(blobs, **kwargs)
        return OrderByPosition.process(self, blobs, **kwargs)
