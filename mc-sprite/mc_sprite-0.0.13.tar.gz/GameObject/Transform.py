from GameObject.Vector2 import Vector
import pygame
from pygame.locals import *
from Engine.Engine import Engine
from Timer.Time import Time
class Transform(pygame.sprite.Sprite):
    def __init__(self, image: str):
        pygame.sprite.Sprite.__init__(self)
        self.__agl=0.0
        self.__scl=Vector(100.0,100.0)
        self.position=Vector()
        self.image=pygame.image.load(image)
        self.tempimage=pygame.image.load(image)
        self.drawId=0
        self.imageRect=self.image.get_rect()
        self.imageRect = self.imageRect.move((0,0))
        self.newRect=self.image.get_rect()
        self.newRect=self.newRect.move((900-self.newRect.width)/2,(600-self.newRect.height)/2)
        self.__drawL={}
        self.__drawL[self.drawId]=(self.image, self.tempimage)
        self.__wid=self.image.get_size()[0]
        self.__hgt=self.image.get_size()[1]
        pass
    def Add(self,image: str):
        self.drawId+=1
        self.__drawL[self.drawId]=(pygame.image.load(image), pygame.image.load(image))
        pass
    def Set(self,id: int):
        self.image=self.__drawL[id][0]
        self.tempimage=self.__drawL[id][1]
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
        self.image = pygame.transform.scale(self.image,(int(self.__wid*(self.__scl.x/100)),int(self.__hgt*(self.__scl.y/100))))
        pass
    @property
    def GetRect(self):
        return self.image.get_rect()
    def Rotate(self, angle: float):
        self.__agl+=angle
        if self.__agl>360:
            self.__agl-=360
        elif self.__agl<360:
            self.__agl+=360
        self.image = pygame.transform.rotate(self.tempimage,self.__agl)
        self.newRect = self.image.get_rect(center=self.tempimage.get_rect().center)
        pass
    def LookAt(self,obj):#亮向量夹角
        pass
    def LookAround(setf,obj):#向量间距离=r,圆周运动
        pass