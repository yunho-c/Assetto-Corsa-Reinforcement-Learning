# foundations
import gym
import numpy as np
# visual observation
import mss
import cv2
# observation, environment control
from ac_gsi import AC_GSI
from ac_interact import AC_Interact
# action pusher
import pyautogui
from pynput import keyboard



class AssettoCorsaEnv(gym.Env):
    def __init__(self):
        n_actions = (3, 3)
        self.action_space = gym.spaces.Discrete(np.prod(n_actions))
        # h, w = 724, 1285 # original
        # h, w = 720, 1280 # 
        self.h, self.w = 360, 640
        self.observation_space = gym.spaces.Box(low=0, high=255, shape=(self.h,self.w,3), dtype=np.uint8)
        self.sct = mss.mss()
        self.monitor = {"top": 35, "left": 5, "width": 1280, "height": 720}
        self.gsi = AC_GSI()
        self.interact = AC_Interact()

        self.initiate()

    def initiate(self):
        self.interact.initiate()

    def push(self, action):
        pyautogui.keyUp('w'); pyautogui. keyUp('s'); pyautogui.keyUp('a'); pyautogui.keyUp('d')
        if action // 3 == 0:
            pyautogui.keyDown('w')
            throttle = 'forward'
        elif action // 3 == 1:
            throttle = '---'
        elif action // 3 == 2:
            pyautogui.keyDown('s')
            throttle = 'backward'

        if action % 3 == 0:
            pyautogui.keyDown('a')
            steer = 'left'
        elif action % 3 == 1:
            steer = '---'
        elif action % 3 == 2:
            pyautogui.keyDown('d')
            steer = 'right'
        # print(action) # DEBUG
        print("Throttle:", throttle, "|", "Steer:", steer) # for fun

    def step(self, action):
        # perform action (& wait, maybe)
        self.push(action)

        # capture screen 
        game_screen = np.array(self.sct.grab(self.monitor), dtype=np.uint8)
        viz_obs = cv2.resize(game_screen[...,:3], (self.w, self.h))

        # other state
        self.gsi.update()
        velocity = self.gsi.velocity()
        print("velocity:", velocity, "km/h")

        # reward
        reward = self.gsi.reward()
        print("Reward:", round(reward, 5)) # for fun

        # race finish detection # TODO improve if needed
        done = int(self.gsi.reader.graphic['isInPit']) == 1 and self.gsi.total_time() > 10

        # misc.
        info = {}

        return viz_obs, reward, done, info
        # V2 TODO: Dict State https://stackoverflow.com/questions/58964267/how-to-create-an-openai-gym-observation-space-with-multiple-features

    def reset(self):
        self.interact.reset()
        self.gsi.reset()

        return self.observation_space.sample() # TODO: 이게 뭘까?

    # def render(self, mode='human'):
    #     pass

    # def close(self):
    #     pass