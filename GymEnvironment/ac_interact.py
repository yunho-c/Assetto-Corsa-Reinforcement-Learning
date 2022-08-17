import pyautogui
import time


class AC_Interact():
    def __init__(self):
        pass
    
    def initiate(self):
        # activate Content Manager window
        pyautogui.getWindowsWithTitle("Content Manager")[0].activate()
        
        # start a game
        pyautogui.hotkey('alt', '1')  # alt+1 to run; enabled w/ CM quick switch feature

        # activate Assetto Corsa window
        time.sleep(3)
        pyautogui.getWindowsWithTitle("Assetto Corsa")[0].activate()
        
        # align AC window
        pyautogui.mouseDown(376,177); time.sleep(0.1); pyautogui.moveTo(60,20); pyautogui.mouseUp()

        # click on race start button
        while True:
            coord = pyautogui.locateCenterOnScreen('./Assets/race_button.png', confidence=0.8)
            if coord: pyautogui.click(coord); break

    def reset(self):
        time.sleep(1)
        print("Resetting")
        with pyautogui.hold('ctrl'):
            pyautogui.press("O")
        time.sleep(1)
        # click on race start button
        while True:
            coord = pyautogui.locateCenterOnScreen('./Assets/race_button.png', confidence=0.8)
            if coord: 
                pyautogui.click(coord)
                time.sleep(1)
                pyautogui.click(coord) # occcasional failures without this.
                break