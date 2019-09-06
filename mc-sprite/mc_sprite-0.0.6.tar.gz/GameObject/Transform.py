from GameObject.Vector2 import Vector
import pygame
from pygame.locals import *
class Transform(object):
    def __init__(self, image: str):
        object.__init__(self)
        self.__agl=0.0
        self.__scl=Vector(100.0,100.0)
        self.position=Vector()
        self.image=pygame.image.load(image)
        self.__wid=self.image.get_size()[0]
        self.__hgt=self.image.get_size()[1]
        pass
    @property
    def width(self):
        return self.__wid*self.__scl.x/100
    @property
    def height(self):
        return self.__hgt*self.__scl.y/100
    @property
    def angle(self):
        return self.__agl
    @property
    def localScale(self):
        return Vector(self.__scl.x,self.__scl.y)
    def Translate(self,x: float,y: float):
        self.__scl.x=x
        self.__scl.y=y
        self.__UpdateLocalScale()
    def __UpdateLocalScale(self):
        print(int(self.__wid*(self.__scl.x/100)))
        print(self.image)
        self.image = pygame.transform.scale(self.image,(int(self.__wid*(self.__scl.x/100)),int(self.__hgt*(self.__scl.y/100))))
        pass
    def Rotate(angle: float):
        self.agl=angle
        pygame.transform.rotate(self.image,angle)
        pass
    def LookAt(self,obj):#亮向量夹角
        pass
    def LookAround(setf,obj):#向量间距离=r,圆周运动
        pass