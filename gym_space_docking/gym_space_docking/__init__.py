from gym.envs.registration import register
 
register(id='space_docking-v0', 
    entry_point='gym_space_docking.envs:Space_Docking_Env', 
)