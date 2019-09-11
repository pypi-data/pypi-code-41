import pygame
from pygame.locals import *
from GameObject.Transform import Transform
from Engine.Engine import Engine
import pygame
class GameObject():
    def __init__(self, image: str, priority: int):
        self.id=id
        self.priority=priority
        self.transform=Transform(image)
        self.__activation=True
        Engine.drawlist[str(priority)]=self

        pass
    def Add(self,image: str):
        self.transform.Add(image)
        pass
    def Set(self, id: int):
        if id <= self.transform.drawId and id >= 0:
            self.transform.Set(id)
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