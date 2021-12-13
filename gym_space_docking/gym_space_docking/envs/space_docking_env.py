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

local_path = os.path.curdir

SCALE = 0.25
window_width, window_height = 320, 240#1200, 640
#os.environ["SDL_VIDEODRIVER"] = "dummy"
SCREENFLAGS =  pygame.SCALED | pygame.DOUBLEBUF #pygame.RESIZABLE |


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
        


    def init_render(self):        
        self.window_display = pygame.display.set_mode(size=(window_width, window_height),flags= SCREENFLAGS)#, vsync=True)
        
        

    def reset(self):
        # reset the environment to initial state
        self.player.handle_input(0)
        self.player.set_main_thruster(False)
        self.player.set_retro_thruster(False)
        pygame.mixer.quit()
        
        self.init_level()
        return None #observation

    def step(self, action):

        #print('action',action)
        # action[0]: acceleration | action[1]: rotation action[2]: strafe_sideway
        self.handle_input(action)
        self.render()
        observation = pygame.surfarray.array3d(self.map_obs)
        self.get_reward()
        #observation.swapaxes(0,1)
        reward, done, info = 0., False, {}


        return observation, reward, done, info
    

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

            if self.check_for_player_collision():
                self.init_level()
            
            self.get_observation()
            
            
            #pygame.display.update()
            self.window_display.blit(self.window, (0,0))
            self.window_display.blit(self.map_obs, (0,0))

            if mode == 'human':
                pygame.display.update()
        


    def render_scaled(self, surface: pygame.Surface, scale):
        surface.fill((255,255,255))
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
        
        self.map_obs.fill((0,0,0))
        #self.map_obs = pygame.Surface((80,80), pygame.SRCALPHA)
        self.map_1 = self.render_scaled(self.map_1, 0.05)
        self.map_2 = self.render_scaled(self.map_2, 0.005)
        self.map_3 = self.render_scaled(self.map_3, 0.001)
        self.map_4 = self.render_scaled(self.map_4, 0.00009)

        self.map_obs.blit(self.map_1, (0,0))
        self.map_obs.blit(self.map_2, (44, 0))
        self.map_obs.blit(self.map_3, (0, 40))
        self.map_obs.blit(self.map_4, (44, 40))
        
        return self.map_obs


    def get_reward(self):
        # check distance to target
        distance = self.player.pos.distance_to(self.dock.pos)
        print(distance/2)

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
                    if i.type == 'asteroid':
                        print(col, i.name)
                        return True
                    elif i.type == 'docking':
                        print('on docking field')
        return False


# --------------------------- Level design ----------------------------

    def init_level(self):

            # create basic level 

            self.objects = pygame.sprite.Group()
            

            self.player = Ship(name='Player', type='ship')
            self.player.pos = math.Vector2(0, 00)
            
            self.dock = DockingSpot(name='Docking_Spot', type='docking')
            self.dock.pos = math.Vector2(100, 600)
            self.objects.add(self.dock)
            
            for i in range(400):
                size = 'med'
                if i % 20 == 0:
                    size = 'L0'
                if i % 40 == 0:
                    size = 'L1'
                astro = Asteroid(astrosize=size, name='astro_'+str(i), type='asteroid')
                coord = math.Vector2()
                while True:
                    rn_angle = np.random.uniform(0, 2*m.pi)
                    dist = np.random.randint(-18000, 18000)
                    coord.x = dist * np.sin(rn_angle)
                    coord.y = dist * np.cos(rn_angle)
                    
                    if coord.distance_to(self.dock.pos) > 2500:
                        break
                angle = np.random.randint(0, 360)
                rot_vel = np.random.uniform(-0.1,0.1)
                astro.pos = coord
                astro.rot_angle = angle
                astro.rot_vel = rot_vel
                self.objects.add(astro)
            
            station = SpaceStation(name='Station 42', type='station')
            #station.rot_vel = -0.03
            self.objects.add(station)
            
            self.objects.add(self.player)
            
            for i in self.objects:
                i.camera_pos = self.camera_pos
                i.scale = self.camera_scale
                i.root_screen = self.window
            #self.player.root_screen = self.window
            pass






