"""`spatial_sites.volumes.py`

Module defining geometric regions of space that can be filled with Sites.

"""


class Box(object):

    def __init__(self, edge_vectors, origin=None):

        self.origin = origin
        self.edge_vectors = edge_vectors

    def fill(self, sites_obj, face_conditions):
        pass
