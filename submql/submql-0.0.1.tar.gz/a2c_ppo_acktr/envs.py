import os

import gym
import numpy as np
import torch
from gym.spaces import Discrete
from gym.spaces.box import Box

import minerl
from a2c_ppo_acktr.wrap_env import FrameSkip, ObtainPoVWrapper, SerialDiscreteActionWrapper
from baselines import bench
from baselines.common.atari_wrappers import make_atari, wrap_deepmind
from baselines.common.atari_wrappers import make_atari, wrap_deepmind, EpisodicLifeEnv, WarpFrame, ScaledFloatFrame, ClipRewardEnv, FrameStack
from baselines.common.vec_env import VecEnvWrapper
from baselines.common.vec_env.dummy_vec_env import DummyVecEnv
from baselines.common.vec_env.shmem_vec_env import ShmemVecEnv
from baselines.common.vec_env.vec_normalize import \
    VecNormalize as VecNormalize_

try:
    import dm_control2gym
except ImportError:
    pass

try:
    import roboschool
except ImportError:
    pass

try:
    import pybullet_envs
except ImportError:
    pass
import cv2


class ImgPreprocessing:

    @staticmethod
    def greyscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def resize(img, height, width):
        return cv2.resize(img, (height, width), interpolation=cv2.INTER_AREA)

frame_skip = 4
always_keys = ['attack']
exclude_noop = True
exclude_keys = ['back', 'left', 'right', 'sneak', 'sprint', 'nearbyCraft', 'nearbySmelt', 'place', 'craft', 'equip']
reverse_keys = ['forward']

# class ActionSpaceWrapper(gym.ActionWrapper):
#
#     def __init__(self, env):
#         super(ActionSpaceWrapper, self).__init__(env)
#
#         self.action_map = []
#
#         self.action_map.append({"attack": 1, "back": 0, "camera": (0, 0), "forward": 1, "jump": 0, "left": 0, "right": 0, "sneak": 0, "sprint": 0})  # FORWARD
#         self.action_map.append({"attack": 0, "back": 0, "camera": (0, -11), "forward": 0, "jump": 0, "left": 0, "right": 0, "sneak": 0, "sprint": 0})  # LEFT 45 degrees
#         self.action_map.append({"attack": 0, "back": 0, "camera": (0, 11), "forward": 0, "jump": 0, "left": 0, "right": 0, "sneak": 0, "sprint": 0})  # RIGHT 45 degrees
#         self.action_map.append({"attack": 0, "back": 0, "camera": (0, 0), "forward": 1, "jump": 1, "left": 0, "right": 0, "sneak": 0, "sprint": 0})  # JUMP
#
#     def reset(self, **kwargs):
#         return self.env.reset(**kwargs)
#
#     def step(self, action):
#         return self.env.step(self.action(action))
#
#     def action(self, action):
#         return self.action_map[action]
#
#     def reverse_action(self, action):
#         raise NotImplementedError


class ObservationSpaceWrapper(gym.ObservationWrapper):

    def observation(self, observation):
        obs = observation['pov']
        obs = ImgPreprocessing.greyscale(obs)
        return np.array([obs], dtype=np.uint8)



class MineRLActionMapWrapper(gym.ActionWrapper):

    def __init__(self, env):
        self.original_action_space = env.action_space
        env.action_space = Discrete(4)
        self.env = env
        self.action_map = []

        self.action_map.append(
            {"attack": 1, "back": 0, "camera": (0, 0), "forward": 1, "jump": 0, "left": 0, "right": 0, "sneak": 0,
             "sprint": 0})  # FORWARD
        self.action_map.append(
            {"attack": 1, "back": 0, "camera": (0, -11), "forward": 0, "jump": 0, "left": 0, "right": 0, "sneak": 0,
             "sprint": 0})  # LEFT 45 degrees
        self.action_map.append(
            {"attack": 1, "back": 0, "camera": (0, 11), "forward": 0, "jump": 0, "left": 0, "right": 0, "sneak": 0,
             "sprint": 0})  # RIGHT 45 degrees
        self.action_map.append(
            {"attack": 1, "back": 0, "camera": (0, 0), "forward": 1, "jump": 1, "left": 0, "right": 0, "sneak": 0,
             "sprint": 0})  # JUMP
        super(MineRLActionMapWrapper, self).__init__(env)

        print(self.env.action_space)

    def action(self, action):
        return self.action_map[action[0]]


class MineRLObsWrapper(gym.ObservationWrapper):
    def __init__(self, env):
        super(MineRLObsWrapper, self).__init__(env)

    def observation(self, observation):

        if "pov" in observation:
            observation = observation['pov']
        else:
            observation = observation[0]['pov']
        return observation


def wrap_env(env, test):
    # wrap env: time limit...
    # if isinstance(env, gym.wrappers.TimeLimit):
    #     logger.info('Detected `gym.wrappers.TimeLimit`! Unwrap it and re-wrap our own time limit.')
    #     env = env.env
    #     max_episode_steps = env.spec.max_episode_steps
    #     env = ContinuingTimeLimit(env, max_episode_steps=max_episode_steps)

    # wrap env: observation...
    # NOTE: wrapping order matters!

    # if test and args.monitor:
    #     env = ContinuingTimeLimitMonitor(
    #         env, os.path.join(args.outdir, 'monitor'),
    #         mode='evaluation' if test else 'training', video_callable=lambda episode_id: True)
    if frame_skip is not None:
        env = FrameSkip(env, skip=frame_skip)
    # if args.gray_scale:
    #     env = GrayScaleWrapper(env, dict_space_key='pov')
    # if args.env.startswith('MineRLNavigate'):
    #     env = PoVWithCompassAngleWrapper(env)
    # env = ObtainPoVWrapper(env)
    # env = MoveAxisWrapper(env, source=-1, destination=0)  # convert hwc -> chw as Chainer requires.
    # env = ScaledFloatFrame(env)

    # if args.frame_stack is not None and args.frame_stack > 0:
    #     env = FrameStack(env, args.frame_stack, channel_order='chw')

    # wrap env: action...
    # env = SerialDiscreteActionWrapper(
    #         env,
    #         always_keys=always_keys,
    #         reverse_keys=reverse_keys,
    #         exclude_keys=exclude_keys,
    #         exclude_noop=exclude_noop)
    # else:
    #     env = CombineActionWrapper(env)
    #     env = SerialDiscreteCombineActionWrapper(env)

    # env_seed = test_seed if test else train_seed
    # env.seed(int(env_seed))  # TODO: not supported yet
    return env

def wrap_deepmind(env, episode_life=True, clip_rewards=False, frame_stack=False, scale=False):
    """Configure environment for DeepMind-style Atari.
    """

    env.observation_space = env.observation_space["pov"]

    # Q: Seems like the wrap_env of serial keys is not combinable with cuda; hope to find out

    env = MineRLObsWrapper(env)
    env = FrameSkip(env, skip=frame_skip)
    env = MineRLActionMapWrapper(env)

    # if episode_life:
    # env = EpisodicLifeEnv(env)

    env = WarpFrame(env)
    if scale:
        env = ScaledFloatFrame(env)
    if clip_rewards:
        env = ClipRewardEnv(env)
    if frame_stack:
        env = FrameStack(env, 4)

    return env


def make_env(env_id, seed, rank, log_dir, allow_early_resets):
    def _thunk():
        if env_id.startswith("dm"):
            _, domain, task = env_id.split('.')
            env = dm_control2gym.make(domain_name=domain, task_name=task)
        else:
            env = gym.make(env_id)

        is_atari = hasattr(gym.envs, 'atari') and isinstance(
            env.unwrapped, gym.envs.atari.atari_env.AtariEnv)
        if is_atari:
            env = make_atari(env_id)

        env.seed(seed + rank)

        obs_shape = env.observation_space.shape

        if str(env.__class__.__name__).find('TimeLimit') >= 0:
            env = TimeLimitMask(env)

        if log_dir is not None:
            env = bench.Monitor(
                env,
                os.path.join(log_dir, str(rank)),
                allow_early_resets=allow_early_resets)

        env = wrap_deepmind(env)

        # If the input has shape (W,H,3), wrap for PyTorch convolutions
        obs_shape = env.observation_space.shape
        if len(obs_shape) == 3 and obs_shape[2] in [1, 3]:
            env = TransposeImage(env, op=[2, 0, 1])

        return env

    return _thunk


def make_vec_envs(env_name,
                  seed,
                  num_processes,
                  gamma,
                  log_dir,
                  device,
                  allow_early_resets,
                  num_frame_stack=None):
    envs = [
        make_env(env_name, seed, i, log_dir, allow_early_resets)
        for i in range(num_processes)
    ]

    if len(envs) > 1:
        envs = ShmemVecEnv(envs, context='fork')
    else:
        envs = DummyVecEnv(envs)

    if len(envs.observation_space.shape) == 1:
        if gamma is None:
            envs = VecNormalize(envs, ret=False)
        else:
            envs = VecNormalize(envs, gamma=gamma)

    envs = VecPyTorch(envs, device)

    if num_frame_stack is not None:
        envs = VecPyTorchFrameStack(envs, num_frame_stack, device)
    elif len(envs.observation_space.shape) == 3:
        envs = VecPyTorchFrameStack(envs, 4, device)

    return envs


# Checks whether done was caused my timit limits or not
class TimeLimitMask(gym.Wrapper):
    def step(self, action):
        obs, rew, done, info = self.env.step(action)
        if done and self.env._max_episode_steps == self.env._elapsed_steps:
            info['bad_transition'] = True

        return obs, rew, done, info

    def reset(self, **kwargs):
        return self.env.reset(**kwargs)


# Can be used to test recurrent policies for Reacher-v2
class MaskGoal(gym.ObservationWrapper):
    def observation(self, observation):
        if self.env._elapsed_steps > 0:
            observation[-2:] = 0
        return observation


class TransposeObs(gym.ObservationWrapper):
    def __init__(self, env=None):
        """
        Transpose observation space (base class)
        """
        super(TransposeObs, self).__init__(env)


class TransposeImage(TransposeObs):
    def __init__(self, env=None, op=[2, 0, 1]):
        """
        Transpose observation space for images
        """
        super(TransposeImage, self).__init__(env)
        assert len(op) == 3, f"Error: Operation, {str(op)}, must be dim3"
        self.op = op
        obs_shape = self.observation_space.shape
        self.observation_space = Box(
            self.observation_space.low[0, 0, 0],
            self.observation_space.high[0, 0, 0], [
                obs_shape[self.op[0]], obs_shape[self.op[1]],
                obs_shape[self.op[2]]
            ],
            dtype=self.observation_space.dtype)

    def observation(self, ob):
        return ob.transpose(self.op[0], self.op[1], self.op[2])


class VecPyTorch(VecEnvWrapper):
    def __init__(self, venv, device):
        """Return only every `skip`-th frame"""
        super(VecPyTorch, self).__init__(venv)
        self.device = device
        # TODO: Fix data types

    def reset(self):
        obs = self.venv.reset()
        obs = torch.from_numpy(obs).float().to(self.device)
        return obs

    def step_async(self, actions):
        if isinstance(actions, torch.LongTensor):
            # Squeeze the dimension for discrete actions
            actions = actions.squeeze(1)
        actions = actions.cpu().numpy()
        self.venv.step_async(actions)

    def step_wait(self):
        obs, reward, done, info = self.venv.step_wait()
        obs = torch.from_numpy(obs).float().to(self.device)
        reward = torch.from_numpy(reward).unsqueeze(dim=1).float()
        return obs, reward, done, info


class VecNormalize(VecNormalize_):
    def __init__(self, *args, **kwargs):
        super(VecNormalize, self).__init__(*args, **kwargs)
        self.training = True

    def _obfilt(self, obs, update=True):
        if self.ob_rms:
            if self.training and update:
                self.ob_rms.update(obs)
            obs = np.clip((obs - self.ob_rms.mean) /
                          np.sqrt(self.ob_rms.var + self.epsilon),
                          -self.clipob, self.clipob)
            return obs
        else:
            return obs

    def train(self):
        self.training = True

    def eval(self):
        self.training = False


# Derived from
# https://github.com/openai/baselines/blob/master/baselines/common/vec_env/vec_frame_stack.py
class VecPyTorchFrameStack(VecEnvWrapper):
    def __init__(self, venv, nstack, device=None):
        self.venv = venv
        self.nstack = nstack

        wos = venv.observation_space  # wrapped ob space
        self.shape_dim0 = wos.shape[0]

        low = np.repeat(wos.low, self.nstack, axis=0)
        high = np.repeat(wos.high, self.nstack, axis=0)

        if device is None:
            device = torch.device('cpu')
        self.stacked_obs = torch.zeros((venv.num_envs, ) +
                                       low.shape).to(device)

        observation_space = gym.spaces.Box(
            low=low, high=high, dtype=venv.observation_space.dtype)
        VecEnvWrapper.__init__(self, venv, observation_space=observation_space)

    def step_wait(self):
        obs, rews, news, infos = self.venv.step_wait()
        self.stacked_obs[:, :-self.shape_dim0] = \
            self.stacked_obs[:, self.shape_dim0:]
        for (i, new) in enumerate(news):
            if new:
                self.stacked_obs[i] = 0
        self.stacked_obs[:, -self.shape_dim0:] = obs
        return self.stacked_obs, rews, news, infos

    def reset(self):
        obs = self.venv.reset()
        if torch.backends.cudnn.deterministic:
            self.stacked_obs = torch.zeros(self.stacked_obs.shape)
        else:
            self.stacked_obs.zero_()
        self.stacked_obs[:, -self.shape_dim0:] = obs
        return self.stacked_obs

    def close(self):
        self.venv.close()
