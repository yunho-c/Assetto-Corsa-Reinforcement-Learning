# game state integration
from acc_shm_reader import Reader
import time

import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import struct
from map_decoder import TrackDetailNode, decode_track

import matplotlib.pyplot as plt # DEBUG

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

        self.map = None # variable shape, according to track scale, is attractive

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

    def create_map(self, track):
    # using point cloud data, create minimap. fill strategy: quads.

        self.map = np.zeros(shape=[500,500,3], dtype=np.uint8)
 
        fn = "./Assets/{}_fast_lane.ai".format(track)

        A = decode_track(fn)

        # fit map onto viewport shape
        x_min, x_max = A[0,:].min(), A[0,:].max()
        y_min, y_max = A[1,:].min(), A[1,:].max()

        x_diff = x_max - x_min
        y_diff = y_max - y_min

        if x_diff > y_diff:
            sr = x_diff / 500
        else: 
            sr = y_diff / 500

        # print("Size Ratio:", round(sr, 2))

        # align centers
        view_center = (250,250)
        map_center = ((x_min+x_max)/2/sr, (y_min+y_max)/2/sr)
        offset = (view_center[0]- map_center[0],view_center[1]- map_center[1]) # for addition

        for i in range(A.shape[1]//2):
            x, y = int(A[0,2*i]/sr+offset[0]), int(A[1,2*i]/sr+offset[1])
            x, y = max(x, 0), max(y, 0) # prevent wall portaling
            try: self.map[y, x] = [255, 255, 255]
            except Exception as e: print(e)
        

def imdpg(img):
    return img.astype(np.float32)/255


def main():
    s = AC_GSI()

    # s.create_map("monza_junior")
    s.create_map("spa")

    dpg.create_context()

    # texture registry
    with dpg.texture_registry(show=False): # show=True
        dpg.add_raw_texture(tag="minimap", width=s.map.shape[1], height=s.map.shape[0], default_value=imdpg(s.map), format=dpg.mvFormat_Float_rgb)

    with dpg.window(tag="primary_window"):
        dpg.add_image("minimap")
        dpg.add_text("Hello, world")
        dpg.add_button(label="Save")
        dpg.add_input_text(label="string", default_value="Quick brown fox")
        dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

    dpg.create_viewport(title='AC Game State Integration Visualizer', width=500, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("primary_window", True)

    while dpg.is_dearpygui_running():
        s.update()

        print("reward", s.reward())
        print("current_lap_time:", s.current_time)
        print("total_time:", s.total_time())

        dpg.render_dearpygui_frame()

        # time.sleep(1)

    dpg.destroy_context()

    # plt.imshow(s.map) # DEBUg
    # plt.show() # DEBUG


if __name__ == "__main__": main()

# normalizedCarPosition: starts at 0.98...
# currentTime: resets at lap change