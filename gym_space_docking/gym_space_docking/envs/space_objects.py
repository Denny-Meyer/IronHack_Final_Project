#from _typeshed import Self
import numpy as np
import pygame
from pygame import transform, mixer, math
from pygame import image
from pygame.locals import *
import os
import math as m

file_path = os.path.dirname(os.path.realpath(__file__))

PATH_SHIP_0 = '/assets/med_ship_01.png'
PATH_ASTRO_L0 = '/assets/asteroid_large_0.png'
PATH_ASTRO_L1 = '/assets/asteroid_large_1.png'
PATH_ASTRO_M0 = '/assets/asteroid_med_2.png'
PATH_LAND = '/assets/stationLandingSite.png'
PATH_STATION = '/assets/station_ring.png'
PATH_STATION_CENTER = '/assets/stationInnerRing.png'


PATH_THRUSTER_SOUND_MAIN = '/assets/thrusters.wav'
PATH_THRUSTER_SOUND_RETRO = '/assets/retro.wav'

PATH_THRUSTER_MAIN_IMG = '/assets/14x15.png'
PATH_tHRUSTER_RETRO_IMG = '/assets/1x5.png'

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

    def __init__(self, name='', type='',**kwargs) -> None:
        super().__init__( **kwargs)
        self.pos = math.Vector2(0,0)
        self.vel = math.Vector2(0,0)
        self.offset = math.Vector2(0,0)
        self.pivot = math.Vector2(0,0)
        self.type = type
        
        self.rot_angle = 0.
        self.rot_vel = 0.
        self.image = None
        self.surf = None
        self.name = name
        self.rect = None
        self.scale = 1.0

        self.camera_pos = math.Vector2(0,0)
        self.root_screen = None
        self.children = []
        
    
    def rotate(self, image, angle=0, pivot=math.Vector2(0,0), offset=math.Vector2(0,0), scale=1.0):

        """Rotate the surface around the pivot point.
        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = transform.rotozoom(image, angle, scale)  # Rotate the image.
        rotated_offset = self.offset.rotate(-angle) #* scale#/ offset.length()# * scale#/ scale # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center= (rotated_offset + self.pos))# * scale)# pivot + rotated_offset)
        return rotated_image, rect  # Return the rotated image and shifted rect.
            
    
   
    

    def update(self):
        # apply rotation
        self.rot_angle += self.rot_vel
        # apply movement to position
        self.pos = self.pos + self.vel

        #self.pivot = math.Vector2(self.image.get_rect().center)
        #self.offset = self.scale
        # calculate rotation and transformation
        self.surf, self.rect = self.rotate(image=self.image, angle=self.rot_angle, offset=self.offset, pivot=self.pos, scale=self.scale)
        

        # iterate over all children
        for child in self.children:
            child.root_screen = self.root_screen
            child.camera_pos = self.camera_pos
            child.rot_angle = self.rot_angle
            child.scale = self.scale
            child.pos = self.pos# + child.offset# self.scale
            child.update()
            
            if not child.root_screen:
                child.root_screen = self.root_screen
        #self.pos = self.pos
        # draw on root canvas
        if self.root_screen:
            pos_cam = self.rect
            pos_cam.x -= self.camera_pos.x #* self.scale
            pos_cam.y -= self.camera_pos.y #* self.scale
            pos_cam.x *= self.scale
            pos_cam.y *= self.scale
            self.root_screen.blit(self.surf, pos_cam)#self.rect)
        pass


class Ship(SpaceObject):

    def __init__(self, name='', type='', **kwargs):
        super().__init__(name = name, type=type, **kwargs)
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        
        self.image = pygame.image.load(file_path + PATH_SHIP_0).convert_alpha()
        self.surf = self.image
        self.thruster_main = mixer.Sound(file_path + PATH_THRUSTER_SOUND_MAIN)
        self.thruster_retro = mixer.Sound(file_path + PATH_THRUSTER_SOUND_RETRO)
        mixer.Sound.set_volume(self.thruster_main, 0.5)
        mixer.Sound.set_volume(self.thruster_retro, 0.3)
        mixer.Sound.fadeout(self.thruster_main, 10)

        self.main_thruster_active = False
        self.retro_thruster_active = False
        # ------------------- create thruster
        self.main_thruster_im = SpaceObject()
        self.main_thruster_im.image = pygame.image.load(file_path + PATH_THRUSTER_MAIN_IMG).convert_alpha()
        self.main_thruster_im.root_screen = self.root_screen
        self.main_thruster_im.pos = self.pos
        self.main_thruster_im.offset = math.Vector2(1, 56)
        self.children.append(self.main_thruster_im)
        FR = {'pos': (5,10), 'angle':(180)}
        FL = {'pos': (-5,10), 'angle':(180)}

        retro_pack = [FR, FL]
        for item in retro_pack:
            pass


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
    def __init__(self, name='', astrosize='L1', type='', **kwargs):
        super().__init__(name=name, type=type, **kwargs)
        im_path = ''
        if astrosize == 'L0':
            im_path = PATH_ASTRO_L0
        elif astrosize == 'L1':
            im_path = PATH_ASTRO_L1
        else:
            im_path = PATH_ASTRO_M0
        self.image = pygame.image.load(file_path + im_path).convert_alpha()
        self.surf = self.image
        #self.rect = self.surf.get_rect()
    


class DockingSpot(SpaceObject):
    
    def __init__(self, name='', type='', **kwargs) -> None:
        super().__init__(name=name, type=type, **kwargs)
        self.image = pygame.image.load(file_path + PATH_LAND).convert_alpha()
        self.surf = self.image
        pass



class SpaceStation(SpaceObject):

    def __init__(self, name='', **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.surf = pygame.Surface((10,10), pygame.SRCALPHA)
        self.image = self.surf
        r1 = Station_ring_part(name='ring')
        r1.pos = self.pos
        c1 = Station_center_part(name='center')
        c1.pos = self.pos
        #r1.offset = math.Vector2(-r1.surf.get_width()/2, -r1.surf.get_height()/2)
        
        #r2 = Station_ring_part(name='r_top_right')
        #r2.image = pygame.transform.flip(r2.image, True, False)
        #r2.pos = self.pos
        #r2.offset = math.Vector2(r2.surf.get_width()/2, -r2.surf.get_height() /2)

        '''
        c1 = Station_center_part('center_top_left')
        c1.pos = self.pos
        c1.offset = math.Vector2(-c1.surf.get_width()/2, -c1.surf.get_height()/2)
        
        c2 = Station_center_part('center_top_left')
        c2.image = pygame.transform.flip(c2.image, True, False)
        c2.pos = self.pos
        c2.offset = math.Vector2(c2.surf.get_width()/2, -c2.surf.get_height()/2)

        c3 = Station_center_part('center_top_left')
        c3.image = pygame.transform.flip(c3.image, True, True)
        c3.pos = self.pos
        c3.offset = math.Vector2(c3.surf.get_width()/2, c3.surf.get_height()/2)

        c4 = Station_center_part('center_top_left')
        c4.image = pygame.transform.flip(c4.image, False, True)
        c4.pos = self.pos
        c4.offset = math.Vector2(-c4.surf.get_width()/2, c4.surf.get_height()/2)
        
        self.children.append(c1)
        self.children.append(c2)
        self.children.append(c3)
        self.children.append(c4)


        
        #self.children.append(r2)
        '''
        self.children.append(c1)
        self.children.append(r1)


class Station_center_part(SpaceObject):

    def __init__(self, name='', **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.surf = pygame.Surface((400 ,400), pygame.SRCALPHA)
        self.image = self.surf

    def update(self):
        if self.root_screen:
            pygame.draw.ellipse(self.image, pygame.Color(129,58,0), (0, 0, 400, 400))
        return super().update()

class Station_ring_part(SpaceObject):

    def __init__(self, name='', **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.surf = pygame.Surface((2000,2000), pygame.SRCALPHA)
        self.image = self.surf


    def update(self):
        if self.root_screen:
            pygame.draw.ellipse(self.image, pygame.Color(129,58,0), (0,0,2000,2000), 250)#(self.pos.x - self.camera_pos.x -300, self.pos.y -self.camera_pos.y -300, 600, 600),60)

        return super().update()
