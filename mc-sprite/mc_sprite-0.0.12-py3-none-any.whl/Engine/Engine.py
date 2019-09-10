import _thread
from Timer.Time import Time
import pygame
import sys
import time as t

pygame.init()

class Engine(object):
    fps = 1/60
    drawlist={}
    screen=None
    time=None
    __isMouseDown_=False
    __isMouseUp_=True
    __isMouse=False
    @staticmethod
    def Start(screen=None):
        Engine.time=Time()
        _thread.start_new_thread(Engine.CheckEvent,())
        if not screen==None:
            Engine.screen=screen
        pass
    @staticmethod
    def isMouseDown():
        return Engine.__isMouseDown_
        pass
    @staticmethod
    def isMouseClicked():
        if Engine.__isMouseDown_:
            Engine.__isMouse=True
        if Engine.__isMouseUp_:
            if Engine.__isMouse:
                Engine.__isMouse=False
                return True
        pass
    @staticmethod
    def CheckEvent():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                Engine.__isMouseDown_=True
                Engine.__isMouseUp_=False
            elif event.type == pygame.MOUSEBUTTONUP:
                Engine.__isMouseDown_=False 
                Engine.__isMouseUp_=True
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
        Engine.time.CalculationDeltaTime()
        for x in Engine.drawlist:
            temp=Engine.drawlist[x]
            if temp.active:
                Engine.screen.blit(temp.transform.image,temp.transform.position.value)
        pygame.display.update()