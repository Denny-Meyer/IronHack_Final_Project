#from _typeshed import Self
import numpy as np
import pygame
from pygame import transform, mixer, math
from pygame.locals import *
import os
import math as m

file_path = os.path.dirname(os.path.realpath(__file__))

PATH_SHIP_0 = '/assets/med_ship_01.png'
PATH_ASTRO_L0 = '/assets/asteroid_large_0.png'
PATH_ASTRO_L1 = '/assets/asteroid_large_1.png'
PATH_ASTRO_M0 = '/assets/asteroid_med_2.png'
PATH_LAND = '/assets/stationLandingSite.png'

PATH_THRUSTER_SOUND_MAIN = '/assets/thrusters.wav'
PATH_THRUSTER_SOUND_RETRO = '/assets/retro.wav'

PATH_THRUSTER_MAIN_IMG = '/assets/14x15.png'


# ------------------ DISCRETE INPUT VALUES -----------------------
ACTION_NONE = 0
ACTION_MAIN = 1
ACTION_RETRO = 2
ACTION_TURN_RIGHT = 3
ACTION_TURN_LEFT = 4
ACTION_STRAFE_RIGHT = 5
ACTION_STRAFE_LEFT = 6


rotation_max, acceleration_max, retro_max = 0.1, 0.08, 0.025

print(file_path)
class SpaceObject(pygame.sprite.Sprite):

    def __init__(self, name='',**kwargs) -> None:
        super(SpaceObject, self).__init__(kwargs)
        self.pos = math.Vector2(0,0)
        self.vel = math.Vector2(0,0)
        self.offset = math.Vector2(0,0)
        self.pivot = math.Vector2(0,0)
        
        self.rot_angle = 0.
        self.rot_vel = 0.
        self.image = None
        self.surf = None
        self.name = name
        self.rect = None

        self.root_screen = None
        self.children = []
    
    def set_offset(self):
        #self.pos = self.pos + math.Vector2(self.surf.get_rect().center)
        #self.pos_x = int(self.surf.get_width()/2)
        #self.pos_y = int(self.surf.get_height()/2)
        #print(self.pos_x, self.pos_y)
        pass

        
    
    def rotate(self, angle=0, pivot=math.Vector2(0,0), offset=math.Vector2(0,0), scale=1):

        """Rotate the surface around the pivot point.
        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = transform.rotozoom(self.image, angle, scale)  # Rotate the image.
        rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center=pivot+rotated_offset)
        return rotated_image, rect  # Return the rotated image and shifted rect.
            
    
   
    

    def update(self):
        # apply rotation
        self.rot_angle += self.rot_vel
        # apply movement to position
        self.pos = self.pos + self.vel

        self.surf, self.rect = self.rotate(angle=self.rot_angle, offset=self.offset, pivot=self.pos)
        self.pivot = self.pos
        for child in self.children:
            child.rot_angle = self.rot_angle
            child.pos = self.pos
            child.update()
            if not child.root_screen:
                child.root_screen = self.root_screen
        if self.root_screen:
            self.root_screen.blit(self.surf, self.rect)
        pass


class Ship(SpaceObject):

    def __init__(self, **kwargs):
        super(Ship, self).__init__(kwargs)
        
        self.image = pygame.image.load(file_path + PATH_SHIP_0).convert_alpha()
        self.surf = self.image
        self.set_offset()
        self.thruster_main = mixer.Sound(file_path + PATH_THRUSTER_SOUND_MAIN)
        self.thruster_retro = mixer.Sound(file_path + PATH_THRUSTER_SOUND_RETRO)
        mixer.Sound.set_volume(self.thruster_main, 0.5)
        mixer.Sound.set_volume(self.thruster_retro, 0.3)
        mixer.Sound.fadeout(self.thruster_main, 10)

        self.main_thruster_active = False
        self.retro_thruster_active = False
        self.main_thruster_im = SpaceObject()
        self.main_thruster_im.image = pygame.image.load(file_path + PATH_THRUSTER_MAIN_IMG).convert_alpha()
        self.main_thruster_im.root_screen = self.root_screen

        self.main_thruster_im.pos = self.pos
        self.main_thruster_im.offset = math.Vector2(0, 50)
        self.children.append(self.main_thruster_im)

    def set_main_thruster(self, active):
        if self.main_thruster_active != active:
            self.main_thruster_active = active
            if self.main_thruster_active:
                mixer.Sound.play(self.thruster_main, -1)
            else:
                mixer.Sound.stop(self.thruster_main)
    
    def set_retro_thruster(self, active):
        if self.retro_thruster_active != active:
            self.retro_thruster_active = active
            if self.retro_thruster_active:
                mixer.Sound.play(self.thruster_retro, -1)
            else:
                mixer.Sound.stop(self.thruster_retro)
    
    def handle_input(self, action):

        if action == ACTION_NONE:
            self.set_retro_thruster(False)
            self.set_main_thruster(False)
            acceleration = 0
            strafe = 0
            rotation = 0
        
        elif action == ACTION_MAIN:
            self.set_main_thruster(True)
            acceleration = 1  
        
        elif action == ACTION_RETRO:
            self.set_main_thruster(False)
            self.set_retro_thruster(True)
            acceleration = -1
        
        elif action != ACTION_RETRO and action != ACTION_MAIN:
            self.set_retro_thruster(True)
            acceleration = 0
        
        elif action != ACTION_NONE and action != ACTION_MAIN:
            self.set_retro_thruster(True)
        
        if action == ACTION_RETRO:
            acceleration = -1
        
        if action == ACTION_TURN_LEFT:
            rotation = 1
        elif action == ACTION_TURN_RIGHT:
            rotation = -1
        else:
            rotation = 0
        
        if action == ACTION_STRAFE_LEFT:
            strafe = -1
        elif action == ACTION_STRAFE_RIGHT:
            strafe = 1
        else:
            strafe = 0
        # ─── APPLY ROTATION ──────────────────────────────────────────────
        
        self.rot_vel += rotation * rotation_max
        
        # ─── APPLY ACCELERATION ──────────────────────────────────────────
        
        # backwards acceleration at quarter thrust
        if acceleration < 0:
            acceleration = acceleration * 0.5 
        
        self.vel.x = self.vel.x + acceleration_max * acceleration * np.cos(m.radians(self.rot_angle) + 0.5 * np.pi)
        self.vel.y = self.vel.y - acceleration_max * acceleration * np.sin(m.radians(self.rot_angle) + 0.5 * np.pi)
        

        # ––––––– APPLY STRAFE ACCELERATION ––––––––––––––––––––––––––––––––
        self.vel.x = self.vel.x + retro_max * strafe * np.sin(m.radians(self.rot_angle) + 0.5 * np.pi)
        self.vel.y = self.vel.y + retro_max * strafe * np.cos(m.radians(self.rot_angle) + 0.5 * np.pi)
        



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