import pyautogui
import time

print(pyautogui.FAILSAFE) # enabling failsafe, at least during env setup, seems like a good idea.

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

state =  0

# open content manager

# focus on the window
pyautogui.getWindowsWithTitle("Content Manager")[0].activate()
state = 1

# start a game
pyautogui.hotkey('alt', '1')  # alt+1 to run; enabled w/ CM quick switch feature
# window focus occurs automatically. if not, explicitize
state = 2

while state == 2:
    # time.sleep(1) # locateCenterOnScreen seems slow and blocking
    coord = pyautogui.locateCenterOnScreen('./Assets/race_button.png', confidence=0.8)
    if coord: 
        pyautogui.click(coord) # 이거 아무래도 풀스크린 상태에서 클릭 안될지도
        print(coord)
        state = 3
        

# a = time.time()
time.sleep(10)
