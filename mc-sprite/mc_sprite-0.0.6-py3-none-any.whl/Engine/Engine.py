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
    @staticmethod
    def Start(screen=None):
        Engine.time=Time()
        if not screen==None:
            Engine.screen=screen
        pass
    @staticmethod
    def isMouseDown():
        if Engine.__isMouseDown_:
            Engine.__isMouseDown_=False
            return not Engine.__isMouseDown_
        else:
            return Engine.__isMouseDown_
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
            elif event.type == pygame.MOUSEBUTTONUP:
                Engine.__isMouseDown_=False     
        Engine.time.CalculationDeltaTime()
        for x in sorted(Engine.drawlist):
            temp=Engine.drawlist[x]
            if temp.active:
                Engine.screen.blit(temp.transform.image,temp.transform.position.value)
        pygame.display.update()