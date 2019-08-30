import pygame
import math


class Engine:
    def __init__(self, screen_width, screen_height, screen_name):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
#        self.screen.fill((0, 50, 100))
        
        pygame.display.flip()
        pygame.display.set_caption(screen_name)
        
        self.camx = 0
        self.camy = 0

        self.im_height = 0
        self.im_width = 0
        self.grid_width = 0
        self.grid_height = 0
        self.grid_visible = True

        self.screen_width = screen_width
        self.screen_height = screen_height

    def init_grid(self, grid_width, grid_height, imflat_width, imflat_height, angle_degrees,  visible):
        angle_radian = math.radians(angle_degrees)
        print(angle_radian)
        print(angle_degrees)
        im_height = imflat_height * math.sin(angle_radian)
        if im_height >= 5:
            im_height = math.ceil(im_height)
        else:
            im_height = math.floor(im_height)
        
        self.im_height = im_height
        self.im_width = imflat_width
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_visible = visible

        return im_height
    
    def draw_grid(self):
        for x in range(self.grid_width + 1):
            for y in range(self.grid_height):
                relx = self.im_width / 2 * x - self.im_width / 2 * y - self.camx
                rely = self.im_height / 2 * y + self.im_height / 2 * x - self.camy
                print(str(relx) + " " + str(rely))
                pygame.draw.line(self.screen, (0,255,0), (relx, rely), (relx - self.im_width / 2,
                                                                        rely + self.im_height / 2), 1)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width + 1):
                relx = self.im_width / 2 * y - self.im_width / 2 * x - self.camx
                rely = self.im_height / 2 * x + self.im_height / 2 * y - self. camy
                pygame.draw.line(self.screen, (255,255,0), (relx, rely), (relx + self.im_width / 2,
                                                                          rely + self.im_height / 2), 1)

    def set_cam(self, x, y):
        self.camx = x
        self.camy = y

    def move_cam(self, rel_x, rel_y):
        self.camx = self.camx + rel_x
        self.camy = self.camy + rel_y

    def zoom(self, factor):
        pass

    def place_tile(self, image, image_center_x, image_center_y, grid_x, grid_y, place_center_x, place_center_y):
        pass

    def mainloop_action(self):
        if self.grid_visible:
            self.draw_grid()




en = Engine(1500, 1000, "test")
width = en.init_grid(10, 5, 128, 128, 30, True)
print(width)
en.draw_grid()
en.zoom(2)
while True:
    pygame.display.flip()