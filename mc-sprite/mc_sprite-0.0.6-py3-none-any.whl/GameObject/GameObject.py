import pygame
from pygame.locals import *
from GameObject.Transform import Transform
from Engine.Engine import Engine
import pygame
class GameObject():
    def __init__(self, image: str, priority: int):
        self.id=id
        self.__drawId=0
        self.__drawL={}
        self.__drawL[str(self.__drawId)] = image
        self.transform=Transform(image)
        self.__activation=True
        Engine.drawlist[str(priority)]=self
        pass
    def Add(self,image: str):
        self.__drawId+=1
        self.__drawL[str(self.__drawId)] = image
        pass
    def Set(self, id):
        if id <= self.__drawId and id >= 0:
            self.Change(self.__drawL[str(id)])
        pass
    def Change(self,image: str):
        self.transform=Transform(image)
        Engine.drawlist[str(id)]=self
        pass
    @property
    def active(self):
        return self.__activation
        pass
    def SetActive(self, active: bool):
        self.__activation=active
        pass
    def Draw(self):
        pass
    def AddComponent(self):
        pass
    @staticmethod
    def Find(name):
        pass