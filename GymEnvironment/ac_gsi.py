# game state integration
from acc_shm_reader import Reader
import time

import cv2
import numpy as np

track_coef = 2.5 # spa


# TODO:
# MSS를 이용한 image grab 및 처리 (RGB 채널 가공 및 커빙을 통한 SNR 향상)
# 를 acenv에 놔둘지, 여기에 가져둘지 고민해보자. Version-specific한 부분은 최대한 acenv에 놔두는 것으로. 

class AC_GSI:
    def __init__(self): 
        self.reader = Reader()
        self.current_time = None
        self.start_time = 0.0

        self.norm_pos_priori = 0.0
        self.penalty = 0

    def reset(self):
        self.start_time = time.time()
        self.penalty = 0

    def total_time(self):
        return round(time.time() - self.start_time, 3)

    def update(self):
        self.reader.update()

        self.current_time = int(self.reader.graphic['iCurrentTime'])/1000
        if self.current_time < 0.1: self.start_time = time.time() # very first start case
        self.norm_pos, self.comp_laps = self.reader.graphic['normalizedCarPosition'], self.reader.graphic['completedLaps']
        
        if self.norm_pos - self.norm_pos_priori > 0.8: self.penalty += 1 # reverse lap case
        self.norm_pos_priori = self.norm_pos

    # calculate reward
    def reward(self):
        r = (self.norm_pos + self.comp_laps - self.penalty) * track_coef - self.total_time()/100
        return r

    def velocity(self): 
        # return self.reader.physics['velocity'] # TODO: learn more about shared memory @ https://www.assettocorsa.net/forum/index.php?threads/acc-shared-memory-documentation.59965/page-20
        return round(self.reader.physics['speedKmh'])

    def action(self): pass
    # 요원 자기자신의 행동 또한 되먹임 되어야 하는가?


def main():
    s = AC_GSI()
    zerotime = time.time()
    while True:
        s.update()

        print("reward", s.reward())
        print("current_lap_time:", s.current_time)
        print("total_time:", s.total_time())

        time.sleep(1)

if __name__ == "__main__": main()

# normalizedCarPosition: starts at 0.98...
# currentTime: resets at lap change