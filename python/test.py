import gym
import gym_space_docking

import numpy as np

import pygame
from pygame.locals import *


env = gym.make('space_docking-v0')



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