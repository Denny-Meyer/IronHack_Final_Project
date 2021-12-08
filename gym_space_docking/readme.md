### description

Enviroment based on OpenAI gym template

***contain***
- controllable SpaceShip

- obs
    > map coordinates are given as 0.5m per pixel
    - ship:
        - position -> float [pos_x, pos_y]
        - velocity -> float [vel_x, vel_y]
        - rotation -> float [angle in degree]
        - rotation velocity -> float [angle in radian]
    - target:
        - position -> float[pos_x, pos_y]
        - rotation -> float[angle in degree]
    - map array 
        - size 30x30 -> scale 1
    - map array 
        - size 30x30 -> scale 10
    - map array 
        - size 30x30 -> scale 100
    > map values are integers
    >
    > 1. interger holds number of asteroids n*10e1
    > 2. interger holds number of ships n*10e2
    > 3. interger hold target n*10e3
    >
    > example: 
    >
    > [.., 134, ..]
    > 
    > the cell has:
    >
    > 1 target, 3 ships and 4 asteroids

### install 

```py
pip install -e .

# if from other folder
!pip install -e <path>
```
usage in script:
```python
import gym
import gym_space_docking
env = gym.make('space_docking-v0')
```
