import _thread
from Timer.Time import Time
import pygame
import sys

pygame.init()

class Engine(object):
    drawlist={}
    screen=None
    time=None
    __isMouseDown_=False
    __isMouseUp_=True
    __isMouse=False
    @staticmethod
    def Start(screen=None):
        Engine.time=Time()
        if not screen==None:
            Engine.screen=screen
        pass
    @staticmethod
    def isMouseDown():
        return Engine.__isMouseDown_
        pass
    @staticmethod
    def isMouse():
        if Engine.__isMouseDown_:
            Engine.__isMouse=True
        if Engine.__isMouseUp_:
            if Engine.__isMouse:
                Engine.__isMouse=False
                return True
        pass
    @staticmethod
    def isMouseUp():
        return Engine.__isMouseUp_
        pass
    @staticmethod
    def A():
        pass
    @staticmethod
    def SetMode(resolution=(0,0),flags=0,depth=0):
        Engine.screen=pygame.display.set_mode(resolution,flags,depth)
    @staticmethod
    def SetCaption(title: str, icontitle = None):
        if icontitle==None:
            pygame.display.set_caption(title)
        else:
            pygame.display.set_caption(title,icontitle)
    @staticmethod
    def Draw():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                Engine.__isMouseDown_=True
                Engine.__isMouseUp_=False
            elif event.type == pygame.MOUSEBUTTONUP:
                Engine.__isMouseDown_=False 
                Engine.__isMouseUp_=True
        Engine.time.CalculationDeltaTime()
        for x in sorted(Engine.drawlist):
            temp=Engine.drawlist[x]
            if temp.active:
                Engine.screen.blit(temp.transform.image,temp.transform.position.value)
        pygame.display.update()