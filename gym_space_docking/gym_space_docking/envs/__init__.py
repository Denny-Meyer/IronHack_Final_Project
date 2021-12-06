from gym.envs.registration import register
 
register(id='Space_Docking-v0', 
    entry_point='gym_space_docking.envs:SpaceDockingEnv', 
)