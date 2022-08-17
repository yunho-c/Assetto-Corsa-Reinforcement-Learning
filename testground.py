from pynput.keyboard import Key, Listener
import time

def on_press(key):
    print('{0} pressed'.format(key))
    # if key is space: 
    print('hooray') if key is Key.space else print('nope')
    # if key is virtual accel: 
    # elif key is virtual decel: 

# Key.space
# Key.left

def on_release(key):
    print('{0} release'.format(key))
    if key == Key.esc:
        return False

listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

while True:
    time.sleep(1)