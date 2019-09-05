import _thread
from Timer.Time import Time
import pygame
import sys
class Engine(object):
    drawlist={}
    screen=None
    time=None
    @staticmethod
    def Start(screen):
        Engine.time=Time()
        Engine.screen=screen
        pass
    @staticmethod
    def A():
        pass
    @staticmethod
    def Draw():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        Engine.time.CalculationDeltaTime()
        for x in sorted(Engine.drawlist):
            temp=Engine.drawlist[x]
            if temp.active:
                Engine.screen.blit(temp.transform.image,temp.transform.position.value)
        pygame.display.update()