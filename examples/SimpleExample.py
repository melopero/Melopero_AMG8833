#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 18:19:16 2019

@author: leoli
"""
import time
import melopero-amg8833 as mp

sensor = mp.AMGGridEye()
sensor.set_fps_mode(mp.AMGGridEye.FPS_10_MODE)

while(True):
    #update and print temperature
    sensor.update_temperature()
    print(sensor.get_temperature()) 

    #update and print matrix
    sensor.update_pixels_matrix()
    print(sensor.get_pixel_temperature_matrix())
    
    #wait 0.1 seconds
    time.sleep(0.1)
