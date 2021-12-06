import math, pygame, sys, os, copy, time, random
import pygame.gfxdraw
from pygame import transform
from pygame.locals import *

pygame.init()




class Ship(pygame.sprite.Sprite):

    def __init__(self):
        super(Ship, self).__init__()
        self.surf = pygame.image.load("assets/med_ship_01.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
    
    def update(self):
        self.rect = self.rect.move(1,0)



class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super(Asteroid, self).__init__()
        self.surf = pygame.image.load("assets/asteroid_large_0.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rotation_angle = 0
    
    def update(self):
        self.image = transform.rotate(self.surf, self.rotation_angle)
        print(self.image)
        self.rect = self.image.get_rect()
        self.surf = self.image
        self.rotation_angle += 0.001
        pass


class DockingSpot(pygame.sprite.Sprite):
    pass




class Game:

    def __init__(self) -> None:
        self.running = True
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))


    def create_level(self):
        pass

    def run_gameloop(self):
        player = Ship()
        astro = Asteroid()

        while self.running:
            # Look at every event in the queue
            for event in pygame.event.get():
                # Did the user hit a key?
                if event.type == KEYDOWN:
                    # Was it the Escape key? If so, stop the loop.
                    if event.key == K_ESCAPE:
                        self.running = False

                # Did the user click the window close button? If so, stop the loop.
                elif event.type == QUIT:
                    self.running = False
            
            self.screen.fill((0,0,0))

            self.screen.blit(astro.surf, astro.rect)
            astro.update()
            player.update()
            self.screen.blit(player.surf, player.rect)

            pygame.display.flip()
            


if __name__ == "__main__":
    Game().run_gameloop()
    print('run file')