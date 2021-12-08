import pygame
from pygame import transform
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math, sys, os, copy, time, random

from gym_space_docking.envs.space_objects import *

window_width, window_height = 1200, 640
rotation_max, acceleration_max, retro_max = 0.08, 0.05, 0.025
SCREENFLAGS = pygame.RESIZABLE #| pygame.OPENGL

class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):
        metadata = {'render.modes': ['human']}  
        # self.observation_space = gym.spaces.Box()
        # self.action_space = gym.spaces.Box()
        self.x = window_width/2
        self.y = window_height/2
        self.ang = 0.#0.5 * np.pi
        self.vel_x = 0.
        self.vel_y = 0.

    def init_render(self):
        pygame.init()
        self.window = pygame.display.set_mode(size=(window_width, window_height),flags= SCREENFLAGS, vsync=True)
        self.clock = pygame.time.Clock()
        self.clock.tick(30)
        self.player = Ship()
        self.astro = Asteroid()
        self.astro.rot_vel = 0.001
        self.astro.pos_y = 100
        self.astro.pos_x = 200
        self.player.pos_x = self.x
        self.player.pos_y = self.y
    def reset(self):
        # reset the environment to initial state
        return observation

    def step(self, action=np.zeros((3),dtype=np.float32)):
        # action[0]: acceleration | action[1]: rotation action[2]: strafe_sideway
        
        # ─── APPLY ROTATION ──────────────────────────────────────────────
        self.ang = self.ang + rotation_max * action[1]
        if self.ang > np.pi:
            self.ang = self.ang - 2 * np.pi
        if self.ang < -np.pi:
            self.ang = self.ang + 2 * np.pi
            
        # ─── APPLY ACCELERATION ──────────────────────────────────────────
        acceleration = action[0]
        # backwards acceleration at quarter thrust
        if acceleration < 0:
            acceleration = acceleration * 0.5 
        self.vel_x = self.vel_x + acceleration_max * acceleration * np.cos(self.ang)
        self.vel_y = self.vel_y - acceleration_max * acceleration * np.sin(self.ang)
        
        # ––––––– APPLY STRAFE ACCELERATION ––––––––––––––––––––––––––––––––
        strafe = action[2]
        
        self.vel_x = self.vel_x + retro_max * strafe * np.sin(self.ang)
        self.vel_y = self.vel_y + retro_max * strafe * np.cos(self.ang)
        #print(action[2])

        # move rocket
        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        
        # keep rocket on screen (optional)
        if self.x > window_width:
            self.x = self.x - window_width
        elif self.x < 0:
            self.x = self.x + window_width
        if self.y > window_height:
            self.y = self.y - window_height
        elif self.y < 0:
            self.y = self.y + window_height

        self.player.vel_x = self.vel_x# - (self.player.surf.get_width()/2)
        self.player.vel_y = self.vel_y# - (self.player.surf.get_height()/2)
        self.player.rot_angle = math.degrees(self.ang - 0.5 * np.pi)
        observation, reward, done, info = 0., 0., False, {}
        return observation, reward, done, info
    
    def render(self, mode='human', close=False):

        self.window.fill((0,0,90))
        
        self.player.update()
        self.window.blit(self.astro.surf, (self.astro.pos_x, self.astro.pos_y))
        self.window.blit(self.player.surf, (self.player.pos_x - self.player.surf.get_rect().centerx, self.player.pos_y -self.player.surf.get_rect().centery))
        #print(self.player.pos_x, self.player.pos_y)

        print(self.player.surf.get_rect().colliderect(self.astro.surf.get_rect()))
            #print('collision')

        pygame.draw.circle(self.window, (0, 200, 200), (int(self.x), int(self.y)), 6)
        # draw orientation
        
        p1 = (self.x - 10 * np.cos(self.ang),self.y + 10 * np.sin(self.ang))
        p2 = (self.x + 15 * np.cos(self.ang),self.y - 15 * np.sin(self.ang))
        pygame.draw.line(self.window,(0,100,100),p1,p2,2)
        pygame.display.update()
        
def pressed_to_action(keytouple):
    action_turn = 0.
    action_acc = 0.
    action_strafe = 0.

    if keytouple[K_DOWN] == 1 or keytouple[K_s] == 1:
        action_acc -= 1
    if keytouple[K_UP] == 1 or keytouple[K_w] == 1:  # forward
        action_acc += 1
    if keytouple[K_LEFT] == 1 or keytouple[K_a] == 1:  # left  is -1
        action_turn += 1
    if keytouple[K_RIGHT] == 1 or keytouple[K_d] == 1:  # right is +1
        action_turn -= 1
    if keytouple[K_q] == 1:
        action_strafe = -1
    if keytouple[K_e] == 1:
        action_strafe = 1
    # ─── KEY IDS ─────────
    # arrow forward   : 273
    # arrow backwards : 274
    # arrow left      : 276
    # arrow right     : 275
    return np.array([action_acc, action_turn, action_strafe])

'''
environment = Space_Docking_Env()
environment.init_render()
run = True


while run:
    # set game speed to 30 fps
    environment.clock.tick(30)
    # ─── CONTROLS ───────────────────────────────────────────────────────────────────
    # end while-loop when window is closed
    get_event = pygame.event.get()
    
    for event in get_event:
        if event.type == pygame.QUIT:
            run = False
    # get pressed keys, generate action
    get_pressed = pygame.key.get_pressed()
            
    action = pressed_to_action(get_pressed)
    # calculate one step
    environment.step(action)
    # render current state
    environment.render()
pygame.quit()



'''