#%matplotlib inline
import gym
from gym.wrappers import Monitor
import itertools
import numpy as np
import os
import random
import sys
import tensorflow as tf


from ale_py import ALEInterface

ale = ALEInterface()
from ale_py.roms import Breakout

ale.loadROM(Breakout)
if "../" not in sys.path:
  sys.path.append("../")
from plotting_lib import *

from collections import deque, namedtuple
env = gym.envs.make("Breakout-v0")
# Atari Actions: 0 (noop), 1 (fire), 2 (left) and 3 (right) are valid actions
#VALID_ACTIONS = [0, 1, 2, 3, 4,5 ,6 ]
# Atari Actions: 0 (noop), 1 (fire), 2 (left) and 3 (right) are valid actions
VALID_ACTIONS = [0, 1, 2, 3]
