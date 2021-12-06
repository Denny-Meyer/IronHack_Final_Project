import math, pygame, sys, os, copy, time, random
from pygame import transform
from pygame.locals import *

pygame.init()


class SpaceObject(pygame.sprite.Sprite):

    def __init__(self) -> None:
        super(SpaceObject, self).__init__()
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.rot_angle = 0.0
        self.rot_mov = 0.0
    
    def rot_center(self, image, angle):
    
        loc = image.get_rect().center  #rot_image is not defined 
        rot_sprite = pygame.transform.rotate(image, angle)
        rot_sprite.get_rect().center = loc
        return rot_sprite


class Ship(SpaceObject):

    def __init__(self):
        super(Ship, self).__init__()
        self.surf = pygame.image.load("assets/med_ship_01.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
    
    def update(self):
        self.rect = self.rect.move(1, 0)


class Asteroid(SpaceObject):
    def __init__(self):
        super(Asteroid, self).__init__()
        self.image = pygame.image.load("assets/asteroid_large_0.png").convert_alpha()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect()
        self.rotation_angle = 0
        self.surf = transform.rotate(self.image, self.rotation_angle)
        self.coord = self.rect
        #print(self.coord)
    
    def update(self):
        self.surf = self.rot_center(self.image, self.rotation_angle)
        #self.surf = transform.rotate(self.image, self.rotation_angle)
        #self.rect = self.image.get_rect()
        self.rotation_angle += 0.1
        pass


class DockingSpot(SpaceObject):
    pass




class Game:

    def __init__(self) -> None:
        self.running = True
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.delta = 0.0


    def create_level(self):
        pass

    def run_gameloop(self):
        player = Ship()
        astro = Asteroid()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(astro)
        all_sprites.add(player)

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

            for elem in all_sprites:
                elem.update()
                print(elem.pos_x)


            self.screen.blit(astro.surf, astro.rect)
            self.screen.blit(player.surf, player.rect)

            pygame.display.flip()

            self.clock.tick(60)
            
            


if __name__ == "__main__":
    Game().run_gameloop()
    print('run file')