import pyautogui
import time

print("PyAutoGUI Failsafe: ", pyautogui.FAILSAFE) # enabling failsafe, at least during env setup, seems like a good idea.

'''
state table
0: nothing
1: content manager
2: AC loading
3: session overview
4: waiting for start signal
5: active race
-1: dysfunction (crash, damage, stuck, timeout, etc)
'''

'''
working setups: 
- 1600*900 @ 100% display scaling factor
- 1200*720 @ 100% display scaling factor <- main config
'''


state =  0


# open content manager
# NOTE: will not implement. 


# focus on the window
pyautogui.getWindowsWithTitle("Content Manager")[0].activate()
state = 1


# start a game
pyautogui.hotkey('alt', '1')  # alt+1 to run; enabled w/ CM quick switch feature
time.sleep(3)
pyautogui.getWindowsWithTitle("Assetto Corsa")[0].activate(); # window focus occurs automatically. if not, explicitize
# align AC window
# pyautogui.getWindowsWithTitle("Assetto Corsa")[0].move(0,0)
# pyautogui.moveTo(376,177); 
# pyautogui.mouseDown(x=376,y=177); pyautogui.dragTo(0, 0) # pyautogui.mouseUp(x=0,y=0)
# pyautogui.mouseDown(x=376,y=177); time.sleep(0.1); pyautogui.dragTo(0,0) # pyautogui.mouseUp()
pyautogui.mouseDown(376,177); time.sleep(0.1); pyautogui.moveTo(60,20); pyautogui.mouseUp()
state = 2


# 
while state == 2:
    coord = pyautogui.locateCenterOnScreen('./Assets/race_button.png', confidence=0.8)
    if coord: 
        pyautogui.click(coord) # 풀스크린 상태에서 클릭 안될지도
        state = 3


"""above is unmodified env_starter.py code"""

"""
1. Input testing
"""

# # from pynput import keyboard

# from pynput.keyboard import Key, Listener

# def on_press(key):
#     print('{0} pressed'.format(key))
#     # if key is space: 
#     # if key is virtual accel: 
#     # elif key is virtual decel: 


# def on_release(key):
#     print('{0} release'.format(key))
#     if key == Key.esc:
#         return False

# listener = Listener(on_press=on_press, on_release=on_release)
# listener.start()

# while True:
#     time.sleep(0.01) # flow control


# listener.finish()

"""
2. Observation Testing
"""
import numpy as np
from mss import mss

sct = mss.mss()

monitor = {"top": 35, "left": 5, "width": 1285, "height": 724}

game_screen = np.array(sct.grab(monitor))