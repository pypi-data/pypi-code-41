from .bbox import BBox


class MultiBBox(object):

    def clone(self):
        res = []
        for bbox in self.arr:
            res.append(bbox.clone())
        return res

    def __add__(self, other):
        if isinstance(other, MultiBBox):
            res = self.clone()
            for bbox in other.arr:
                res = res.__add__(bbox)
            return res

        if not isinstance(other, BBox):
            raise TypeError("Argument should be of either of type BBox or MultiBBox")
        if other.empty():
            return self.clone()
        res = [other]
        for bbox in self.arr:
            res += bbox.subtract(other)
        return MultiBBox(res)

    def __sub__(self, other):
        if isinstance(other, MultiBBox):
            res = self.clone()
            for bbox in other.arr:
                res = res.__sub__(bbox)
            return res

        if not isinstance(other, BBox):
            raise TypeError("Bounding box should be of type BBox")
        if other.empty():
            return self.clone()
        res = []
        for bbox in self.arr:
            res += bbox.subtract(other)
        return MultiBBox(res)

    def add_bbox(self, other):
        self.arr = self.__add__(other).arr

    def remove_bbox(self, other):
        self.arr = self.__sub__(other).arr

    def __init__(self, arr=None):
        self.arr = []
        if not arr:
            return
        if isinstance(arr, BBox):
            self.arr.append(arr)
            return
        if isinstance(arr, MultiBBox):
            self.arr = arr.arr.copy()
            return
        if not isinstance(arr, list) and not isinstance(arr, tuple):
            raise TypeError("invalid bounding boxes")
        if arr:
            for bbox in arr:
                if not isinstance(bbox, BBox):
                    raise TypeError("Bounding boxes should be of type BBox")
                self.add_bbox(bbox)

    def to_json(self):
        return {"type": "MultiBBox", "coords": [list(bbox.arr) for bbox in self.arr]}

    @staticmethod
    def from_json(obj):
        if not isinstance(obj, dict) or obj.get("type") != "MultiBBox" or not obj.get("coords"):
            raise ValueError("Invalid multi-bbox json")
        res = []
        for coords in obj["coords"]:
            res.append(BBox(coords))
        return MultiBBox(res)

    def __str__(self):
        return "MultiBBox([{}])".format(",".join([bbox.__str__() for bbox in self.arr]))
