#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 18:19:16 2019

@author: leoli

MIT license
"""
import time
import melopero_amg8833.AMG8833 as mp

#the default address is 0x69, solder the jumper on the back of the board to set 0x68
sensor = mp.AMGGridEye(0x69)
sensor.set_fps_mode(mp.AMGGridEye.FPS_1_MODE)

while(True):
    #update and print temperature
    sensor.update_temperature()
    print(sensor.get_temperature()) 

    #update and print matrix
    sensor.update_pixels_temperature()
    print(sensor.get_pixel_temperature_matrix())
    
    #wait 1 seconds
    time.sleep(1)
