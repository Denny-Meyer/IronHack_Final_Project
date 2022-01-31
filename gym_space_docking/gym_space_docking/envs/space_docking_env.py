import re
from numpy.core.fromnumeric import shape
import pygame
from pygame import transform, math
from pygame import surface
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math as m
import sys, os, copy, time, random



from gym_space_docking.envs.space_objects import *
from pygame.sprite import collide_mask

local_path = os.path.curdir

SCALE = 0.3
window_width, window_height = 320, 200#1200, 640
#os.environ["SDL_VIDEODRIVER"] = "dummy"
SCREENFLAGS =  pygame.SCALED #| pygame.RESIZABLE 
# FULLSCREEN |
flags =  DOUBLEBUF | RESIZABLE #| SCALED
#SCREENFLAGS = 0

# reward table
# death -50
# increase distance -1
# decrease distance +1 
#



class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):
        metadata = {'render.modes': ['human', 'rgb_array']}
        self.camera_pos = math.Vector2(0,0)
        self.camera_scale = SCALE

        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.window = pygame.Surface((window_width, window_height))
        self.map_obs = pygame.Surface((88,80), pygame.SRCALPHA)
        self.map_1 = pygame.Surface((44,40), pygame.SRCALPHA)
        self.map_2 = pygame.Surface((44,40), pygame.SRCALPHA)
        self.map_3 = pygame.Surface((44,40), pygame.SRCALPHA)
        self.map_4 = pygame.Surface((44,40), pygame.SRCALPHA)
        self.init_render()

        self.init_level()
          
        self.observation_space = spaces.Box(low=0, high=255,
                                        shape=(88, 80), dtype=np.uint8)
        self.action_space =  spaces.Discrete(7)
        
        
        
        self.reward = 0
        self.last_distance = 0
        self.last_min_distance_step = 0
        self.is_in_docking_range = False
        self.docking_counter = 0
        self.collide_astro = False
        self.frame_counter = 0
        self.start_distance = 0
        self.player_old_rotation_speed = 0.0
        self.player_old_vel = 0
        self.rotation_penalty = 0



    def init_render(self):        
        self.window_display = pygame.display.set_mode(size=(window_width, window_height),flags= flags, depth=8)#, vsync=True)
        
        

    def reset(self):
        # reset the environment to initial state
        self.player.handle_input(0)
        self.player.set_main_thruster(False)
        self.player.set_retro_thruster(False)
        pygame.mixer.quit()
        
        self.init_level()
        return self.step(0)#None #observation

    def step(self, action):
        done = False
        
        # action[0]: acceleration | action[1]: rotation action[2]: strafe_sideway
        self.handle_input(action)
        
        
        

        self.render()
        self.map_obs = self.get_observation()
        
        if self.collide_astro:
            #print('collide')
            self.reward -= 100
            done = True
        #if self.reward < -50:
        #    done = True
        #    print('over limit')
        #if self.docking_counter > 10:
        #    self.reward += 5
        #
        #if self.docking_counter > 100:
        #    self.reward += 150
        #    print('finally docked')
        #    done = True
        if self.player.pos.distance_to(self.dock.pos) > self.last_min_distance_step + 0.9 * self.last_min_distance_step:
            done = True

        #if self.player.pos.distance_to(self.dock.pos) > 1.2 * self.start_distance:
            #self.reward -=50

        #    done = True
        #if self.frame_counter > 5000:
       #    done = True

        observation = pygame.surfarray.array3d(self.map_obs)
        self.reward += self.get_reward()
        observation.swapaxes(0,1)
        #print('reward', self.reward, self.frame_counter)
        info = {}

        self.frame_counter +=1
        return observation, self.reward, done, info
    

    def render(self, mode='human', close=False):
        
        
            self.window_display.fill((5,52,103))
            self.window.fill((5,52,103))

            self.camera_scale = SCALE
            
            #self.window.get_rect().center = self.player.pos
            
            #self.camera_pos = self.player.pos - self.window.get_rect
            self.camera_pos = self.player.pos - math.Vector2(int(window_width / 2 / self.camera_scale), int(window_height / 2 / self.camera_scale))

            for obj in self.objects:
                obj.root_screen = self.window
                obj.scale = self.camera_scale
                obj.camera_pos = self.camera_pos #+ math.Vector2(window_width/2,window_height/2)
                obj.update()
                

                #self.window.blit(obj.surf, (obj.pos_x - obj.surf.get_rect().centerx, obj.pos_y - obj.surf.get_rect().centery))
            #self.player.root_screen = self.window
            #self.player.scale = self.camera_scale
            #self.player.camera_pos = self.camera_pos
            #self.player.update()

            self.collide_astro = False
            if self.check_for_player_collision():
                self.player.handle_input(0)
                self.collide_astro = True
                self.player.destroy()
            #    self.init_level()
            
            self.get_observation()
            
            
            #pygame.display.update()
            self.window_display.blit(self.window, (0,0))
            self.window_display.blit(self.map_obs, (0,0))

            if mode == 'human':
                pygame.display.update()
            
            self.reward += self.get_reward()
            #print(self.reward, ' ', self.player.rot_vel, ' ', self.player_old_rotation_speed, ' ', self.rotation_penalty)
            #print(self.player.rot_vel)
        


    def render_scaled(self, surface: pygame.Surface, scale):
        surface.fill((0,0,0,0))
        #surface = pygame.Surface((80,80), pygame.SRCALPHA)
        self.camera_pos = self.player.pos - math.Vector2(surface.get_width() / 2 / scale, surface.get_height() / 2 / scale)
        for obj in self.objects:
            obj.root_screen = surface
            obj.scale = scale
            obj.camera_pos = self.camera_pos #+ math.Vector2(window_width/2,window_height/2)
            obj.update()
        
        #self.player.scale = scale
        #self.player.camera_pos = self.camera_pos
        #self.player.root_screen = surface
        #self.player.update()

        return surface
    
    
    
    def get_observation(self):
        
        map_old = self.map_obs.copy()
        back_ground = self.map_obs.copy()
        back_ground.fill((255,255,255))
        map_old.set_alpha(128)
        
        self.map_obs = pygame.Surface((88,80), pygame.SRCALPHA)
        self.map_1 = self.render_scaled(self.map_1, 0.08)
        self.map_2 = self.render_scaled(self.map_2, 0.01)
        self.map_3 = self.render_scaled(self.map_3, 0.005)
        self.map_4 = self.render_scaled(self.map_4, 0.0005)

        self.map_obs.blit(back_ground,(0,0))
        
        
        self.map_obs.blit(self.map_1, (0,0))
        self.map_obs.blit(self.map_2, (44, 0))
        self.map_obs.blit(self.map_3, (0, 40))
        self.map_obs.blit(self.map_4, (44, 40))
        
        #redraw old map over latest
        self.map_obs.blit(map_old, (0,0))
        
        
        return self.map_obs

# ----------calculate Rewards------------------------------

    def get_reward(self):
        # check distance to target

        reward = 0
        distance = self.player.pos.distance_to(self.dock.pos)


        # set start distance
        if self.start_distance == 0:
            self.start_distance = distance
            self.last_min_distance_step = int(distance)

        # create distance rings to 20 steps
        ring_steps = int(self.start_distance / 2000)
        rot_vel_steps = 0.1

        if distance < (self.last_min_distance_step - ring_steps):
            reward += 1
            self.last_min_distance_step = self.last_min_distance_step - ring_steps
        elif distance > (self.last_min_distance_step + ring_steps) and distance < self.start_distance + 1:
            reward -= 1
            self.last_min_distance_step = self.last_min_distance_step + ring_steps
            

        rot_res = 0
        if self.player.rot_vel < -0.01:
            rot_res = int(self.player.rot_vel / rot_vel_steps)
            if -self.rotation_penalty != rot_res:
                reward -= -self.rotation_penalty - rot_res
                self.rotation_penalty = -rot_res
        elif self.player.rot_vel > 0.01:
            rot_res = -int(self.player.rot_vel / rot_vel_steps)
            if -self.rotation_penalty != rot_res:
                reward -= -self.rotation_penalty - rot_res
                self.rotation_penalty = -rot_res
        else:
            self.rotation_penalty = 0
        #print(self.player.vel.length())
        if self.player.vel.length() > self.player_old_vel:
            reward -= self.player.vel.length() #/ 2
        elif self.player.vel.length() < self.player_old_vel:
            reward += self.player_old_vel #/ 2
        self.player_old_vel = self.player.vel.length()


        #else:
        #    reward += 0.01
        reward -= 0.00001

        return reward


# ----------- Handle Input -------------------------------------------


    def handle_input(self, action):
        self.player.handle_input(action)


# ----------- Simple Physics -----------------------------------------

    def check_for_player_collision(self) -> bool:

        for i in self.objects:
            if self.player.pos.distance_to(i.pos) < 800:
                col = collide_mask(self.player, i)
                if col != None:
                    if i.type == 'asteroid':
                        #print(col, i.name)
                        self.collide_astro = True
                        return True
                    elif i.type == 'docking':
                        #print('on docking field')
                        self.is_in_docking_range = True
                        self.docking_counter += 1
                    else:
                        self.is_in_docking_range = False
                        self.docking_counter = 0
        return False


# --------------------------- Level design ----------------------------

    def init_level(self):

            # create basic level 

            self.objects = pygame.sprite.Group()
            

            self.player = Ship(name='Player', type='ship')
            self.player.pos = math.Vector2(1000, 300)
            
            self.dock = DockingSpot(name='Docking_Spot', type='docking')
            self.dock.pos = math.Vector2(0, 1285)

            self.reward = 0
            self.last_distance = 0
            self.last_min_distance_step = 0
            self.is_in_docking_range = False
            self.docking_counter = 0
            self.collide_astro = False
            self.frame_counter = 0
            self.start_distance = 0

            self.map_obs = pygame.Surface((88,80), pygame.SRCALPHA)
            
            station = SpaceStation(name='Station 42', type='station')


            for i in range(0):
                size = 'med'
                if i % 10 == 0:
                    size = 'L1'
                if i % 20 == 0:
                    size = 'L0'
                astro = Asteroid(astrosize=size, name='astro_'+str(i), type='asteroid')
                coord = math.Vector2()
                while True:
                    rn_angle = np.random.uniform(0, 2*m.pi)
                    dist = np.random.randint(-10000, 10000)
                    coord.x = dist * np.sin(rn_angle)
                    coord.y = dist * np.cos(rn_angle)
                    
                    if coord.distance_to(station.pos) > 3200:
                        break
                angle = np.random.randint(0, 360)
                rot_vel = np.random.uniform(-0.1,0.1)
                astro.pos = coord
                astro.rot_angle = angle
                astro.rot_vel = rot_vel
                self.objects.add(astro)
            
            
            #station.rot_vel = -0.03
            self.objects.add(station)
            self.objects.add(self.dock)
            
            self.objects.add(self.player)
            
            for i in self.objects:
                i.camera_pos = self.camera_pos
                i.scale = self.camera_scale
                i.root_screen = self.window
            #self.player.root_screen = self.window

            # random player position
            while True:
                    rn_angle = np.random.uniform(0, 2*m.pi)
                    dist = np.random.randint(10000)#, 2000)
                    self.player.pos.x = dist * np.sin(rn_angle)
                    self.player.pos.y = dist * np.cos(rn_angle)
                    
                    if self.player.pos.distance_to(self.dock.pos) > 1000 and self.player.pos.distance_to(self.dock.pos) < 100000:
                        break 


            self.last_distance = self.player.pos.distance_to(self.dock.pos)

            pass






