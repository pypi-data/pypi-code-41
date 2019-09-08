import math
from Timer.Time import Time
class Vector(object):
    def __init__(self, x = 0, y = 0):
        object.__init__(self)
        self.x=x
        self.y=y
        pass
    def Set(self, x = 0, y =0):
        self.x=x
        self.y=y
    @property
    def value(self):
        return (self.x,self.y)
    @property
    def right():
        return Vector(1,0)
    @property
    def left():
        return Vector(-1,0)
    @property
    def down():
        return Vector(0,-1)
    @property
    def up():
        return Vector(0,1)
    @property
    def zero():
        return Vector(0,0)
    @property
    def one():
        return Vector(1,1)
    @property
    def magnitude(self):
        return math.sqrt(self.x*self.x+self.y*self.y)
    @staticmethod
    def MoveTowards(current, target, maxDistanceDelta):
        if current == target:
            return target
        else:
            return (target-current)*maxDistanceDelta*Time.deltaTime
    @staticmethod
    def Move(current,maxDistanceDelta,direction):
        if direction == Vector.right:
            return Vector(current.x+maxDistanceDelta*Time.deltaTime, current.y)
        if direction == Vector.left:
            return Vector(current.x-maxDistanceDelta*Time.deltaTime, current.y)
        if direction == Vector.up:
            return Vector(current.x, current.y-maxDistanceDelta*Time.deltaTime)
        if direction == Vector.down:
            return Vector(current.x, current.y+maxDistanceDelta*Time.deltaTime)
        pass
    def __getitem__(self, key):
        pass
    def __call__(self):
        return self
    def __eq__(self, other):
        if self.x == other[0] and self.y == other[1]:
            return True
        else:
            return False
    def __sub__(self, other):
        return Vector(self.x-other.x,self.y-other.y)
    def __add__(self, other):
        return Vector(self.x+other.x,self.y+other.y)
    def __mul__(self, other: int):
        return Vector(self.x*other,self.y*other)
        