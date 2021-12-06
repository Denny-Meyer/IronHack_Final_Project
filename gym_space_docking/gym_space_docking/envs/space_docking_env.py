import pygame
import numpy as np
import gym

window_width, window_height = 1000, 500
rotation_max, acceleration_max = 0.08, 0.5

class Space_Docking_Env(gym.Env):
    def __init__(self,env_config={}):
        # self.observation_space = gym.spaces.Box()
        # self.action_space = gym.spaces.Box()
        self.x = window_width/2
        self.y = window_height/2
        self.ang = 0.
        self.vel_x = 0.
        self.vel_y = 0.

    def init_render(self):
        import pygame
        pygame.init()
        self.window = pygame.display.set_mode((window_width, window_height))
        self.clock = pygame.time.Clock()

    def reset(self):
        # reset the environment to initial state
        return observation

    def step(self, action=np.zeros((2),dtype=np.float)):
        # action[0]: acceleration | action[1]: rotation
        
        # ─── APPLY ROTATION ──────────────────────────────────────────────
        self.ang = self.ang + rotation_max * action[1]
        if self.ang > np.pi:
            self.ang = self.ang - 2 * np.pi
        if self.ang < -np.pi:
            self.ang = self.ang + 2 * np.pi
            
        # ─── APPLY ACCELERATION ──────────────────────────────────────────
        acceleration = action[0]
        # backwards acceleration at half thrust
        if acceleration < 0:
            acceleration = acceleration * 0.5
        self.vel_x = self.vel_x + acceleration_max * acceleration * np.cos(self.ang)
        self.vel_y = self.vel_y - acceleration_max * acceleration * np.sin(self.ang)
        
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
            
        observation, reward, done, info = 0., 0., False, {}
        return observation, reward, done, info
    
    def render(self):
        self.window.fill((0,0,0))
        pygame.draw.circle(self.window, (0, 200, 200), (int(self.x), int(self.y)), 6)
        # draw orientation
        p1 = (self.x - 10 * np.cos(self.ang),self.y + 10 * np.sin(self.ang))
        p2 = (self.x + 15 * np.cos(self.ang),self.y - 15 * np.sin(self.ang))
        pygame.draw.line(self.window,(0,100,100),p1,p2,2)
        pygame.display.update()
        
def pressed_to_action(keytouple):
    action_turn = 0.
    action_acc = 0.
    if keytouple[274] == 1:  # back
        action_acc -= 1
    if keytouple[273] == 1:  # forward
        action_acc += 1
    if keytouple[276] == 1:  # left  is -1
        action_turn += 1
    if keytouple[275] == 1:  # right is +1
        action_turn -= 1
    # ─── KEY IDS ─────────
    # arrow forward   : 273
    # arrow backwards : 274
    # arrow left      : 276
    # arrow right     : 275
    return np.array([action_acc, action_turn])

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







import math, pygame, sys, os, copy, time, random
from pygame import transform
from pygame.locals import *

import gym
from gym import error, spaces, utils
from gym.utils import seeding

pygame.init()


class SpaceObject(pygame.sprite.Sprite):

    def __init__(self) -> None:
        super(SpaceObject, self).__init__()
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.rot_angle = 0.0
        self.rot_mov = 0.0
    
    def rot_center(self, image, angle):
    
        loc = image.get_rect().center  #rot_image is not defined 
        rot_sprite = pygame.transform.rotate(image, angle)
        rot_sprite.get_rect().center = loc
        return rot_sprite


class Ship(SpaceObject):

    def __init__(self):
        super(Ship, self).__init__()
        self.surf = pygame.image.load("assets/med_ship_01.png").convert_alpha()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
    
    def update(self):
        self.rect = self.rect.move(1, 0)


class Asteroid(SpaceObject):
    def __init__(self):
        super(Asteroid, self).__init__()
        self.image = pygame.image.load("assets/asteroid_large_0.png").convert_alpha()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect()
        self.rotation_angle = 0
        self.surf = transform.rotate(self.image, self.rotation_angle)
        self.coord = self.rect
        #print(self.coord)
    
    def update(self):
        self.surf = self.rot_center(self.image, self.rotation_angle)
        #self.surf = transform.rotate(self.image, self.rotation_angle)
        #self.rect = self.image.get_rect()
        self.rotation_angle += 0.1
        pass


class DockingSpot(SpaceObject):
    pass




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
            
            


#if __name__ == "__main__":
#    Game().run_gameloop()
#    print('run file')