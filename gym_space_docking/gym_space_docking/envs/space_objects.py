from numpy import min_scalar_type
import pygame
from pygame import transform, mixer
from pygame.locals import *
import os
import math

file_path = os.path.dirname(os.path.realpath(__file__))

PATH_SHIP_0 = '/assets/med_ship_01.png'
PATH_ASTRO_L0 = '/assets/asteroid_large_0.png'
PATH_ASTRO_L1 = '/assets/asteroid_large_1.png'
PATH_ASTRO_M0 = '/assets/asteroid_med_2.png'
PATH_LAND = '/assets/stationLandingSite.png'

PATH_THRUSTER_SOUND_MAIN = '/assets/thrusters.wav'

PATH_THRUSTER_MAIN_IMG = '/assets/14x15.png'


print(file_path)
class SpaceObject(pygame.sprite.Sprite):

    def __init__(self, name='',**kwargs) -> None:
        super(SpaceObject, self).__init__(kwargs)
        self.pos_x = 0.
        self.pos_y = 0.
        self.vel_x = 0.
        self.vel_y = 0.
        self.rot_angle = 0.
        self.rot_vel = 0.
        self.image = None
        self.surf = None
        self.name = name
        #self.rect = None

        self.root_screen = None
        self.children = []
    
    def set_offset(self):
        self.pos_x = int(self.surf.get_width()/2)
        self.pos_y = int(self.surf.get_height()/2)
        #print(self.pos_x, self.pos_y)

    def rot_center(self):
        self.rot_angle += self.rot_vel
        #print(self.rot_angle)
        rot_sprite = pygame.transform.rotate(self.image, self.rot_angle)
        self.surf = rot_sprite
        self.rect = self.surf.get_rect().center
        #print(self.surf.get_rect().center)
    
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
        for child in self.children:
            child.rot_angle = self.rot_angle
            child.pos_x = self.pos_x
            child.pos_y = self.pos_y + 50
            child.update()
            if not child.root_screen:
                child.root_screen = self.root_screen
        if self.root_screen:
            #self.root_screen.blit(child.surf, (100,100))
            self.root_screen.blit(self.surf, (self.pos_x - self.surf.get_rect().centerx, self.pos_y - self.surf.get_rect().centery))
        #self.rot_angle += self.rot_vel
        pass


class Ship(SpaceObject):

    def __init__(self, **kwargs):
        super(Ship, self).__init__(kwargs)
        self.image = pygame.image.load(file_path + PATH_SHIP_0).convert_alpha()
        self.surf = self.image
        self.set_offset()
        self.thruster_main = mixer.Sound(file_path + PATH_THRUSTER_SOUND_MAIN)
        mixer.Sound.set_volume(self.thruster_main, 0.5)
        mixer.Sound.fadeout(self.thruster_main, 10)
        #self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        #self.rect = self.surf.get_rect()
        self.main_thruster_active = False
        self.main_thruster_im = SpaceObject()
        self.main_thruster_im.image = pygame.image.load(file_path + PATH_THRUSTER_MAIN_IMG).convert_alpha()
        self.main_thruster_im.root_screen = self.root_screen
        self.main_thruster_im.pos_x = 500
        self.main_thruster_im.pos_y = 200
        self.children.append(self.main_thruster_im)

    def set_thruster(self, active):
        if self.main_thruster_active != active:
            self.main_thruster_active = active
            if self.main_thruster_active:
                mixer.Sound.play(self.thruster_main, -1)
            else:
                mixer.Sound.stop(self.thruster_main)
    


class Asteroid(SpaceObject):
    def __init__(self, astrosize='L1', **kwargs):
        super(Asteroid, self).__init__(kwargs)
        im_path = ''
        if astrosize == 'L0':
            im_path = PATH_ASTRO_L0
        elif astrosize == 'L1':
            im_path = PATH_ASTRO_L1
        else:
            im_path = PATH_ASTRO_M0
        self.image = pygame.image.load(file_path + im_path).convert_alpha()
        self.surf = self.image
        self.set_offset()
        #self.rect = self.surf.get_rect()
    


class DockingSpot(SpaceObject):
    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs)
        self.image = pygame.image.load(file_path + PATH_LAND).convert_alpha()
        self.surf = self.image
        self.set_offset()
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