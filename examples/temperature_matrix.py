#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""
import time
import melopero_amg8833 as mp

sensor = mp.AMGGridEye()
sensor.set_fps_mode(mp.AMGGridEye.FPS_1_MODE)

while(True):
    #update and print temperature
    print(sensor.get_thermistor_temperature()) 

    #update and print matrix
    sensor.update_pixel_temperature_matrix()
    print(sensor.get_pixel_temperature_matrix())
    
    #wait 1 seconds
    time.sleep(1)
