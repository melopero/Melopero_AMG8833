#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""
import time
import melopero_amg8833 as mp

high_threshold = 26
low_threshold = -10 #dont want it to fire

sensor = mp.AMGGridEye()
sensor.set_fps_mode(mp.AMGGridEye.FPS_1_MODE)
sensor.set_interrupt_thresholds(low_threshold, high_threshold)
sensor.enable_interrupt()

while(True):
    #update and print temperature
    print(sensor.get_thermistor_temperature()) 

    #update and print matrix
    sensor.update_pixel_temperature_matrix()
    print(sensor.get_pixel_temperature_matrix())
    
    status = sensor.get_status()
    for key, value in status.items():
        print(key, value)
    
    if status["Interrupt"]:
        sensor.update_interrupt_table()
        print(sensor.get_interrupt_table())
    
    sensor.reset_flags()
    
    #wait 1 seconds
    time.sleep(1)
