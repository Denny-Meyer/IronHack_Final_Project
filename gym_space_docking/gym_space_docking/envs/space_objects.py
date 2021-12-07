import pygame
from pygame import transform
from pygame import math
from pygame.locals import *
import math

class SpaceObject(pygame.sprite.Sprite):

    def __init__(self) -> None:
        super(SpaceObject, self).__init__()
        self.pos_x = 0.
        self.pos_y = 0.
        self.vel_x = 0.
        self.vel_y = 0.
        self.rot_angle = 0.
        self.rot_vel = 0.
        self.image = None
        self.surf = None
        self.rect = None
    
    def set_offset(self):
        self.pos_x = int(self.surf.get_width()/2)
        self.pos_y = int(self.surf.get_height()/2)
        #print(self.pos_x, self.pos_y)

    def rot_center(self):
        rot_sprite = pygame.transform.rotate(self.image, self.rot_angle)
        self.surf = rot_sprite
    
    def rotate(surface, angle, pivot, offset):

        """Rotate the surface around the pivot point.
        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = transform.rotozoom(surface, -angle, 1)  # Rotate the image.
        rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect  # Return the rotated image and shifted rect.
            
    
    def transform(self):
        self.pos_x = self.pos_x + self.vel_x# - (self.surf.get_width()/2)
        self.pos_y = self.pos_y + self.vel_y# - (self.surf.get_height()/2)
        pass
    
    def update(self):
        #self.surf,self.rect = self.rotate(self.image, self.rot_angle, self.rect)
        self.rot_center()
        self.transform()
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