from acc_shm_reader import Reader
import numpy as np
import time

r = Reader()
r.update()

cn = 1

# print(np.array(r.graphic['carCoordinates']))

a = time.time()

while (time.time() - a) < 500:
    r.update() 
    # print(list(r.graphic['carCoordinates'][0]))
    # print(list(r.graphic['carCoordinates'][1]))
    # print(list(r.graphic['carCoordinates'][2]))
    # print(r.graphic['normalizedCarPosition']) # 허!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 요놈 물건일세
    print(r.graphic['completedLaps'])
    print(r.graphic['numberOfLaps'])
    print(r.physics['fuel'])
    print(r.physics['brakeBias'])
    print("speedKmh:", r.physics['speedKmh'])
    print("localVelocity:", r.physics['localVelocity'])
    print("velocity:", r.physics['velocity'])
    time.sleep(10)