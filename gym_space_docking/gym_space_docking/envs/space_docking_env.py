from numpy.core.fromnumeric import shape
import pygame
from pygame import transform, math
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math as m
import sys, os, copy, time, random



from gym_space_docking.envs.space_objects import *

local_path = os.path.curdir


window_width, window_height = 1200, 640

SCREENFLAGS = pygame.RESIZABLE | pygame.SCALED | pygame.DOUBLEBUF

class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):

        self.camera_pos = math.Vector2(0,0)
        self.camera_scale = 0.2

        pygame.init()
        self.window = pygame.Surface((window_width, window_height))
        self.init_render()
        metadata = {'render.modes': ['human', 'rgb_array']}  
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(4*40, 4*40), dtype=np.uint8)
        
        self.action_space =  spaces.Discrete(7)

        
        
        
        #self.init_render()
        self.init_level()

    def init_render(self):
        
        self.window_display = pygame.display.set_mode(size=(window_width, window_height),flags= SCREENFLAGS)#, vsync=True)
        self.clock = pygame.time.Clock()
        self.init_level()
        

    def reset(self):
        # reset the environment to initial state
        self.init_level()
        return None #observation

    def step(self, action):

        #print('action',action)
        # action[0]: acceleration | action[1]: rotation action[2]: strafe_sideway
        self.handle_input(action)

        observation, reward, done, info =0., 0., False, {}

        #observation = self.get_observation()

        return observation, reward, done, info
    

    def render(self, mode='human', close=False):
        if mode == 'rgb_array':
            pass
        elif mode == 'human':
            self.window_display.fill((5,52,103))
            self.window.fill((5,52,103))
            
            self.camera_pos = self.player.pos - math.Vector2(window_width / 2 / self.camera_scale,window_height / 2 / self.camera_scale)

            for obj in self.objects:
                obj.scale = self.camera_scale
                obj.camera_pos = self.camera_pos #+ math.Vector2(window_width/2,window_height/2)
                obj.update()
                

                #self.window.blit(obj.surf, (obj.pos_x - obj.surf.get_rect().centerx, obj.pos_y - obj.surf.get_rect().centery))
            
            self.player.scale = self.camera_scale
            self.player.camera_pos = self.camera_pos
            self.player.update()

            self.check_for_player_collision()
            self.get_observation()
            self.draw_gui()
            
            #pygame.display.update()
            self.window_display.blit(self.window, (0,0))
            #pygame.display.flip()
            pygame.display.update()
        

    
    
    def get_observation(self):

        # needed observation 
        # ship pos, vel, rot, rot_vel
        # target pos
        # map 1, map 10, map 100
        

        map_10 = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_100 = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_1k = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_10k = np.ndarray(shape=(40,40), dtype=np.uint8)

        # calculate distance player to objects

        # scale: 2px = 1m
        nearest = 99999
        n_name = ''
        for item in self.objects:
            #print(self.player.pos)
            distance = self.player.pos.distance_to(item.pos)
            distance_vec = item.pos - self.player.pos 
            if distance < nearest:
                nearest = distance
                n_name = item.name
            #print(distance, distance_vec, item.name['name'])
        print(n_name, nearest)
        return np.random.randint(3)


    def get_reward(self):
        pass


# ----------- Handle Drawing


    def draw_gui(self):
        # draw orientation
        pygame.draw.circle(self.window, (0, 200, 200), (self.player.pos), 6)
        p1 = (self.player.pos.x - 10 * np.cos(m.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos.y + 10 * np.sin(m.radians(self.player.rot_angle) + 0.5 * np.pi))
        p2 = (self.player.pos.x + 15 * np.cos(m.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos.y - 15 * np.sin(m.radians(self.player.rot_angle) + 0.5 * np.pi))
        pygame.draw.line(self.window,(0,100,100),p1,p2,2)
        pass

# ----------- Handle Input -------------------------------------------


    def handle_input(self, action):
        self.player.handle_input(action)


# ----------- Simple Physics -----------------------------------------

    def check_for_player_collision(self) -> bool:

        player_mask = pygame.mask.from_surface(self.player.surf)
        for i in self.objects:
            if self.player.surf.get_rect().colliderect(i.surf.get_rect()):
                #print('player rect collide with ', i.name['name'])
                i_mask = pygame.mask.from_surface(i.surf)
                
                off = (i.pos * self.camera_scale - math.Vector2(i.surf.get_rect().center) * self.camera_scale) - (self.player.pos * self.camera_scale - math.Vector2(self.player.surf.get_rect().center) * self.camera_scale)
                
                col = player_mask.overlap(i_mask, off)
                if col != None:
                        print(col, i.name)
                        return True
        return False


# --------------------------- Level design ----------------------------

    def init_level(self):

            # create basic level 
            self.player = Ship(name='Player')
            self.player.pos = math.Vector2(600, 600)
            self.dock = DockingSpot(name='Docking_Spot')
            self.dock.pos = math.Vector2(100, 600)
            self.objects = pygame.sprite.Group()
            self.objects.add(self.dock)
            
            for i in range(300):
                size = 'med'
                if i % 40 == 0:
                    size = 'L0'
                if i % 80 == 0:
                    size = 'L1'
                astro = Asteroid(astrosize=size, name='astro_'+str(i), type='astro')
                coord = math.Vector2()
                while True:
                    coord.x = np.random.randint(-4000, 4000)
                    coord.y = np.random.randint(-4000, 4000)
                    if coord.distance_to(self.dock.pos) > 700:
                        break
                angle = np.random.randint(0, 360)
                rot_vel = np.random.uniform(-0.5,0.5)
                astro.pos = coord
                astro.rot_angle = angle
                astro.rot_vel = rot_vel
                self.objects.add(astro)
            #self.station = SpaceStation(name='Station')
            #self.station.rot_vel = -0.1
            #self.objects.add(self.station)
            
            for i in self.objects:
                i.camera_pos = self.camera_pos
                i.scale = self.camera_scale
                i.root_screen = self.window
            self.player.root_screen = self.window
            pass






