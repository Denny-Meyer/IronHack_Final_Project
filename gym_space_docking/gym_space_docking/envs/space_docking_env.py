import pygame
from pygame import transform
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math, sys, os, copy, time, random



from gym_space_docking.envs.space_objects import *

local_path = os.path.curdir


window_width, window_height = 1200, 640
rotation_max, acceleration_max, retro_max = 0.1, 0.08, 0.025
SCREENFLAGS = pygame.RESIZABLE #| pygame.OPENGL

class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):
        metadata = {'render.modes': ['human', 'rgb_array']}  
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(window_width, window_height), dtype=np.uint8)
        #print(self.observation_space)
        self.action_space =  spaces.Discrete(6)

        print(self.action_space)
        self.window = None
        self.x = window_width/2
        self.y = window_height/2
        self.ang = 0.#0.5 * np.pi
        self.vel_x = 0.
        self.vel_y = 0.

    def init_render(self):
        pygame.init()
        self.window = pygame.display.set_mode(size=(window_width, window_height),flags= SCREENFLAGS, vsync=True)
        self.clock = pygame.time.Clock()
        self.init_level()
        

    def reset(self):
        # reset the environment to initial state
        return observation

    def step(self, action=np.zeros((3),dtype=np.float32)):
        # action[0]: acceleration | action[1]: rotation action[2]: strafe_sideway
        
        # ─── APPLY ROTATION ──────────────────────────────────────────────
        self.player.rot_vel += action[1] * rotation_max

        # ─── APPLY ACCELERATION ──────────────────────────────────────────
        acceleration = action[0]
        # backwards acceleration at quarter thrust
        if acceleration == 1:
            self.player.set_thruster(True)
        else:
            self.player.set_thruster(False)
        if acceleration < 0:
            acceleration = acceleration * 0.5 
        self.player.vel_x = self.player.vel_x + acceleration_max * acceleration * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi)
        self.player.vel_y = self.player.vel_y - acceleration_max * acceleration * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi)
        
        # ––––––– APPLY STRAFE ACCELERATION ––––––––––––––––––––––––––––––––
        strafe = action[2]
        
        self.player.vel_x = self.player.vel_x + retro_max * strafe * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi)
        self.player.vel_y = self.player.vel_y + retro_max * strafe * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi)
        #print(action[2])
        
        # keep rocket on screen (optional)
        if self.x > window_width:
            self.x = self.x - window_width
        elif self.x < 0:
            self.x = self.x + window_width
        if self.y > window_height:
            self.y = self.y - window_height
        elif self.y < 0:
            self.y = self.y + window_height

        self.vel_x  = self.player.vel_x #= self.vel_x# - (self.player.surf.get_width()/2)
        self.vel_y = self.player.vel_y #= self.vel_y# - (self.player.surf.get_height()/2)
        #self.player.rot_angle = math.degrees(self.ang - 0.5 * np.pi)
        
        reward, done, info = 0., False, {}

        observation = self.get_observation()

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
            player_mask = pygame.mask.from_surface(self.player.surf)
            for i in self.objects:
                i_mask = pygame.mask.from_surface(i.surf)
                if self.player.surf.get_rect(center = (self.player.pos_x, self.player.pos_y)).colliderect(i.surf.get_rect(center=(i.pos_x, i.pos_y))):
                    #print(i)
                    off_x = self.player.surf.get_rect().centerx - i.surf.get_rect().centerx
                    off_y = self.player.surf.get_rect().centery - i.surf.get_rect().centery
                    print(player_mask.overlap(i_mask, (off_x, off_y)))
                else:
                    pass#print('no collision')
            #print(pygame.surfarray.pixels2d(self.window)[0][0])
            #print(self.window.unmap_rgb(4278190150))
            pygame.draw.circle(self.window, (0, 200, 200), (int(self.player.pos_x), int(self.player.pos_y)), 6)
            # draw orientation
            
            p1 = (self.player.pos_x - 10 * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos_y + 10 * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi))
            p2 = (self.player.pos_x + 15 * np.cos(math.radians(self.player.rot_angle) + 0.5 * np.pi),self.player.pos_y - 15 * np.sin(math.radians(self.player.rot_angle) + 0.5 * np.pi))
            pygame.draw.line(self.window,(0,100,100),p1,p2,2)
            pygame.display.update()
        

    def init_level(self):
        self.player = Ship()
        self.astro = Asteroid(astrosize='L0')
        self.astro_0 = Asteroid(astrosize='L1')
        self.astro_0.rot_vel = -0.05
        self.astro_0.pos_x = 700
        self.astro_0.pos_y = 500
        self.astro.rot_vel = 0.1
        self.astro.pos_y = 100
        self.astro.pos_x = 200
        self.player.pos_x = self.x
        self.player.pos_y = self.y
        self.dock = DockingSpot()
        self.dock.pos_x = 100
        self.dock.pos_y = 600
        self.objects = pygame.sprite.Group()
        self.objects.add(self.astro)
        self.objects.add(self.astro_0)
        self.objects.add(self.dock)
        #self.objects.add(self.player)
        for i in self.objects:
            i.root_screen = self.window
        self.player.root_screen = self.window
        pass

    
    def get_observation(self):
        return np.random.randint(3)


    def get_reward(self):
        pass
    

    def check_for_player_collision(self) -> bool:
        return False





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
    
    return np.array([action_acc, action_turn, action_strafe])


environment = Space_Docking_Env()
environment.init_render()
run = True


while run:
    # set game speed to 30 fps
    #environment.clock.tick(30)
    environment.clock.tick_busy_loop(30)
    # ─── CONTROLS ───────────────────────────────────────────────────────────────────
    # end while-loop when window is closed
    get_event = pygame.event.get()
    
    # get pressed keys, generate action
    get_pressed = pygame.key.get_pressed()
            
    action = pressed_to_action(get_pressed)
    # calculate one step
    environment.step(action)
    # render current state
    environment.render(mode='human')

    for event in get_event:
        if event.type == pygame.QUIT:
            pygame.display.quit()
            run = False
pygame.quit()



