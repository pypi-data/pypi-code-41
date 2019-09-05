import math
from Timer.Time import Time
class Vector2(object):
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
        return Vector2(1,0)
    @property
    def left():
        return Vector2(-1,0)
    @property
    def down():
        return Vector2(0,-1)
    @property
    def up():
        return Vector2(0,1)
    @property
    def zero():
        return Vector2(0,0)
    @property
    def one():
        return Vector2(1,1)
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
        if direction == Vector2.right:
            return Vector2(current.x+maxDistanceDelta*Time.deltaTime, current.y)
        if direction == Vector2.left:
            return Vector2(current.x-maxDistanceDelta*Time.deltaTime, current.y)
        if direction == Vector2.up:
            return Vector2(current.x, current.y-maxDistanceDelta*Time.deltaTime)
        if direction == Vector2.down:
            return Vector2(current.x, current.y+maxDistanceDelta*Time.deltaTime)
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
        return Vector2(self.x-other.x,self.y-other.y)
    def __add__(self, other):
        return Vector2(self.x+other.x,self.y+other.y)
    def __mul__(self, other: int):
        return Vector2(self.x*other,self.y*other)
        