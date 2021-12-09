import gym
import gym_space_docking
from gym_space_docking.envs.space_objects import ACTION_MAIN, ACTION_NONE, ACTION_RETRO, ACTION_STRAFE_LEFT, ACTION_STRAFE_RIGHT, ACTION_TURN_LEFT, ACTION_TURN_RIGHT

import numpy as np

import pygame
from pygame.locals import *


env = gym.make('space_docking-v0')



def pressed_to_action(keytouple):
    
    action = ACTION_NONE

    if keytouple[K_DOWN] == 1 or keytouple[K_s] == 1:
        action = ACTION_RETRO
    if keytouple[K_UP] == 1 or keytouple[K_w] == 1:  # forward
        action = ACTION_MAIN
    if keytouple[K_LEFT] == 1 or keytouple[K_a] == 1:  # left  is -1
        action = ACTION_TURN_LEFT
    if keytouple[K_RIGHT] == 1 or keytouple[K_d] == 1:  # right is +1
        action = ACTION_TURN_RIGHT
    if keytouple[K_q] == 1:
        action = ACTION_STRAFE_LEFT
    if keytouple[K_e] == 1:
        action = ACTION_STRAFE_RIGHT
    
    return action


environment = env
environment.init_render()
run = True

environment.reset()

while run:
    # set game speed to 30 fps
    environment.clock.tick(30)
    # environment.clock.tick_busy_loop(30)
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
        if event.type == pygame.VIDEORESIZE:
            # There's some code to add back window content here.
            
            environment.window = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)
            
pygame.quit()