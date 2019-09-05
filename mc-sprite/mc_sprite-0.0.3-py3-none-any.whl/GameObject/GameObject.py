import pygame
from pygame.locals import *
from GameObject.Transform import Transform
from Engine.Engine import Engine
import pygame
class GameObject():
    def __init__(self, image: str, id: int):
        self.id=id
        self.transform=Transform(image)
        self.__activation=True
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