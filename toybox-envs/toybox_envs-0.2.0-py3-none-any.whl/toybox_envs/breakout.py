from toybox_envs.base import ToyboxBaseEnv
from toybox_envs.constants import *
from toybox import Toybox, Input


class BreakoutEnv(ToyboxBaseEnv):
    def __init__(self, frameskip=(2, 5), repeat_action_probability=0., grayscale=True, alpha=False): 
        super().__init__(Toybox('breakout', grayscale), 
            frameskip, repeat_action_probability,
            grayscale=grayscale, 
            alpha=alpha)

