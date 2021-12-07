import pygame
from pygame import transform
from pygame.locals import *


class SpaceObject(pygame.sprite.Sprite):

    def __init__(self) -> None:
        super(SpaceObject, self).__init__()
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.rot_angle = 0.0
        self.rot_vel = 0.0
        self.image = None
        self.surf = None
        self.rect = None
    
    def set_offset(self):
        self.pos_x = int(self.surf.get_width()/2)
        self.pos_y = int(self.surf.get_height()/2)
        print(self.pos_x, self.pos_y)

    def rot_center(self):
        rot_sprite = pygame.transform.rotate(self.image, self.rot_angle)
        self.surf = rot_sprite
        
        
    
    def transform(self, direction):
        pass
    
    def update(self):
        self.rot_center()
        
        self.rot_angle += self.rot_vel
        pass


class Ship(SpaceObject):

    def __init__(self):
        super(Ship, self).__init__()
        self.image = pygame.image.load("assets/med_ship_01.png").convert_alpha()
        self.surf = self.image
        self.set_offset()
        #self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        #self.rect = self.surf.get_rect()


class Asteroid(SpaceObject):
    def __init__(self):
        super(Asteroid, self).__init__()
        self.image = pygame.image.load("assets/asteroid_large_0.png").convert_alpha()
        self.surf = self.image
        self.set_offset()
        #self.rect = self.surf.get_rect()
    


class DockingSpot(SpaceObject):
    pass



'''
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
'''