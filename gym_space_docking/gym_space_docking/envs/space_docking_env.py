from numpy.core.fromnumeric import shape
import pygame
from pygame import transform, math
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math, sys, os, copy, time, random



from gym_space_docking.envs.space_objects import *

local_path = os.path.curdir


window_width, window_height = 800, 420#1200, 640

SCREENFLAGS = pygame.RESIZABLE | pygame.SCALED

class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):

        pygame.init()
        self.init_render()
        metadata = {'render.modes': ['human', 'rgb_array']}  
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(4*40, 4*40), dtype=np.uint8)
        #print(self.observation_space)
        self.action_space =  spaces.Discrete(7)

        print(self.action_space)
        self.window = None
        self.x = window_width/2
        self.y = window_height/2
        self.ang = 0.#0.5 * np.pi
        self.vel_x = 0.
        self.vel_y = 0.
        #self.init_render()
        self.init_level()

    def init_render(self):
        
        self.window = pygame.display.set_mode(size=(window_width, window_height),flags= SCREENFLAGS)#, vsync=True)
        self.clock = pygame.time.Clock()
        self.init_level()
        

    def reset(self):
        # reset the environment to initial state
        self.init_level()
        return None #observation

    def step(self, action=np.zeros((3),dtype=np.float32)):

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
            self.window.fill((0,0,70))
            
            for obj in self.objects:
                obj.update()
                #self.window.blit(obj.surf, (obj.pos_x - obj.surf.get_rect().centerx, obj.pos_y - obj.surf.get_rect().centery))
            self.player.update()

            self.check_for_player_collision()
            
            self.draw_gui()
            
            pygame.display.update()
        

    
    
    def get_observation(self):

        # needed observation 
        # ship pos, vel, rot, rot_vel
        # target pos
        # map 1, map 10, map 100
        player_pos = pygame.math.Vector2(self.player.pos_x, self.player.pos_y)
        player_vel = pygame.math.Vector2(self.player.vel_x, self.player.vel_y)
        target_pos = pygame.math.Vector2(self.dock.pos_x, self.dock.pos_y)
        target_vel = pygame.math.Vector2(self.dock.vel_x, self.dock.vel_y)
        

        map_10 = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_100 = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_1k = np.ndarray(shape=(40,40), dtype=np.uint8)
        map_10k = np.ndarray(shape=(40,40), dtype=np.uint8)

        for items in self.objects:
            pass
            


        return np.random.randint(3)


    def get_reward(self):
        pass


# ----------- Handle Drawing


    def draw_gui(self):
        # draw orientation
        pygame.draw.circle(self.window, (0, 200, 200), (int(self.player.pos_x), int(self.player.pos_y)), 6)
        p1 = (self.player.pos_x - 10 * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos_y + 10 * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi))
        p2 = (self.player.pos_x + 15 * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos_y - 15 * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi))
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
                off_x = (i.pos_x - i.surf.get_rect().centerx) - (self.player.pos_x - self.player.surf.get_rect().centerx)
                off_y = (i.pos_y - i.surf.get_rect().centery) - (self.player.pos_y - self.player.surf.get_rect().centery)
                col = player_mask.overlap(i_mask, (off_x, off_y))
                if col != None:
                        #print(col, i.name)
                        return True
        return False


# --------------------------- Level design ----------------------------

    def init_level(self):

            # create basic level 
            self.player = Ship(name='Player')
            self.astro = Asteroid(astrosize='L0', name='astro_0')
            self.astro_0 = Asteroid(astrosize='L1', name='astro_1')
            self.astro_0.rot_vel = -0.04
            self.astro_0.pos_x = 700
            self.astro_0.pos_y = 500
            self.astro.rot_vel = 0.05
            self.astro.pos_y = 100
            self.astro.pos_x = 200
            self.player.pos_x = 500
            self.player.pos_y = 500
            self.dock = DockingSpot(name='Docking_Spot')
            self.dock.pos_x = 100
            self.dock.pos_y = 600
            self.objects = pygame.sprite.Group()
            self.objects.add(self.astro)
            self.objects.add(self.astro_0)
            self.objects.add(self.dock)
            
            for i in self.objects:
                i.root_screen = self.window
            self.player.root_screen = self.window
            pass






