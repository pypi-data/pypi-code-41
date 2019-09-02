from .consts import EMPTY_BBOX


class BBox(object):
    def __init__(self, arr=None):
        if isinstance(arr, BBox):
            self.arr = arr.arr.copy()
            return
        if not arr:
            arr = list(EMPTY_BBOX)
        if not isinstance(arr, list) and not isinstance(arr, tuple):
            raise TypeError("invalid coordinates")
        if len(arr) != 4:
            raise ValueError("invalid coordinates")
        if arr[0] > arr[2] or arr[1] > arr[3]:
            arr = list(EMPTY_BBOX)
        self.arr = []
        for obj in arr:
            item = float(obj)
            self.arr.append(item)

    def clone(self):
        if self.empty():
            return BBox()
        return BBox(self.arr.copy())

    def empty(self):
        return self.arr[0] >= self.arr[2] or self.arr[1] >= self.arr[3]

    def intersect(self, other):
        if not isinstance(other, BBox):
            raise TypeError("invalid bbox")
        return BBox((max(self.arr[0], other.arr[0]), max(self.arr[1], other.arr[1]),
                     min(self.arr[2], other.arr[2]), min(self.arr[3], other.arr[3])))

    def union(self, other):
        if not isinstance(other, BBox):
            raise TypeError("invalid bbox")
        return BBox((min(self.arr[0], other.arr[0]), min(self.arr[1], other.arr[1]),
                     max(self.arr[2], other.arr[2]), max(self.arr[3], other.arr[3])))

    def contains(self, other):
        if not isinstance(other, BBox):
            raise TypeError("invalid bbox")
        return self.arr[0] <= other.arr[0] and self.arr[1] <= other.arr[1] and other.arr[2] <= self.arr[2] and \
               other.arr[3] <= self.arr[3]

    def subtract(self, other):
        if not isinstance(other, BBox):
            raise TypeError("invalid bbox")
        if self.empty():
            return []
        if other.empty():
            return [self.clone()]
        if other.contains(self):
            return []
        if not self.contains(other):
            return self.subtract(self.intersect(other))
        res = []
        if self.arr[0] < other.arr[0]:
            res.append(BBox((self.arr[0], self.arr[1], other.arr[0], self.arr[3])))
        if other.arr[2] < self.arr[2]:
            res.append(BBox((other.arr[2], self.arr[1], self.arr[2], self.arr[3])))
        if self.arr[1] < other.arr[1] and other.arr[0] < other.arr[2]:
            res.append(BBox((other.arr[0], self.arr[1], other.arr[2], other.arr[1])))
        if other.arr[3] < self.arr[3] and other.arr[0] < other.arr[2]:
            res.append(BBox((other.arr[0], other.arr[3], other.arr[2], self.arr[3])))
        return res

    def to_json(self):
        return {"type": "BBox", "coords": list(self.arr)}

    @staticmethod
    def from_json(obj):
        if not isinstance(obj, dict) or obj.get("type") != "BBox" or not obj.get("coords"):
            raise ValueError("Invalid bbox json")
        return BBox(obj["coords"])

    def __str__(self):
        return "BBox({})".format(self.arr)

    def equals(self, other):
        if not isinstance(other, BBox):
            raise TypeError("invalid bbox")
        return not self.subtract(other) and not other.subtract(self)
