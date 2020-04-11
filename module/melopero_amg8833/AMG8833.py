#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""
'''
   TODO: write better documentation 
   TODO: implement missing features
   TODO: clean up code 
'''

from smbus2 import SMBus

#=========== REGISTERS ADDRESSES ===========#
_FRAME_RATE_REG_ADDR = 0x02
_FIRST_PIXEL_REG_ADDR = 0x80
_LAST_PIXEL_REG_ADDR = 0xFF
_TEMPERATURE_REG_ADDR = 0x0E

class AMGGridEye():
    ''' A class to easily handle the AMG8833 Grid Eye's funtionalities'''
    
    FPS_10_MODE = 0
    FPS_1_MODE = 1
    
    def __init__(self, i2c_addr = 0x69, i2c_bus = 1):
        self._i2c_address = i2c_addr
        self._i2c_bus = i2c_bus
        self._i2c = SMBus(i2c_bus)
        self._pixel_data = [[0]*8 for _ in range(8)]
        self._thermistor_temp = 0
        
    
    def set_fps_mode(self, fps_mode = 0):
        '''Sets how many times per second the pixels should update.\n
           Parameter : fps_mode (int) - can be 0 for 10 FPS or 1 for 1 FPS
        '''
        if fps_mode != AMGGridEye.FPS_1_MODE and fps_mode != AMGGridEye.FPS_10_MODE:
            raise ValueError("fps_mode must be one of AMGGridEye.FPS_N_MODE")
        self._i2c.write_byte_data(self._i2c_address, _FRAME_RATE_REG_ADDR, fps_mode)
        
        
    def get_fps(self):
        ''' Returns the current FPS settings'''
        reg_data = self._i2c.read_byte_data(self._i2c_address, _FRAME_RATE_REG_ADDR)
        return 1 if reg_data else 10
    
        
    def update_pixels_temperature(self):
        ''' Updates the pixels data\n
                    
            A pixel's data is stored like this:
            reg0 : b7 b6 b5 b4 b3  b2  b1 b0
            reg1 : -- -- -- -- b11 b10 b9 b8
        '''
        for i, reg_addr in enumerate(range(_FIRST_PIXEL_REG_ADDR,_LAST_PIXEL_REG_ADDR, 2)):
            lsb = self._i2c.read_byte_data(self._i2c_address, reg_addr)
            msb = self._i2c.read_byte_data(self._i2c_address, reg_addr+1)
            
            self._pixel_data[i//8][i%8] = self._compute_pixel_temp(lsb, msb)
            
                
    def get_pixel_temperature_matrix(self):
        ''' Returns a matrix 8*8 (list of lists with 8 elements) containig the 
            the pixels temperature in Celsius\n
            Example:\n
            [
                 [00, 01, 02, 03, 04, 05, 06, 07],\n
                 [08, 09, 10, 11, 12, 13, 14, 15],\n
                 [16, 17, 18, 19, 20, 21, 22, 23],\n
                 [24, 25, 26, 27, 28, 29, 30, 31],\n
                 [32, 33, 34, 35, 36, 37, 38, 39],\n
                 [40, 41, 42, 43, 44, 45, 46, 47],\n
                 [48, 49, 50, 51, 52, 53, 54, 55],\n
                 [56, 57, 58, 59, 60, 61, 62, 63]\n
            ]
        '''
        return self._pixel_data
    
    def get_pixel_temperature(self, x, y):
        return self._pixel_data[y][x]  
    
    def update_thermistor_temperature(self):
        ''' thermistor's data is stored like this:
            reg0 : b7 b6 b5 b4 b3  b2  b1 b0
            reg1 : -- -- -- -- b11 b10 b9 b8
            
            the temperature is :
                b11      -> sign +1 or -1
                b10 - b4 -> integer part of temperature
                b3 - b0  -> fraction part of temperature: 1 / value(b3b2b1b0)
        '''
        lsb  = self._i2c.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR)
        msb = self._i2c.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR + 1)
        
        sign = -1 if msb & 0x08 > 0 else 1
        int_temp = ((msb & 0x07) << 4) | (lsb & 0xF0)
        frac = (lsb & 0x0F)
        frac_temp = 0 if frac == 0 else 1 / frac
        
        self._thermistor_temp = sign*(int_temp + frac_temp)   
    
    
    def get_thermistor_temperature(self):
        return self._thermistor_temp
    
    def close(self):
        self._i2c.close()

    def _compute_pixel_temp(self, lsb, msb):
        unified_no_sign = ((msb & 7) << 8) | lsb
        value = 0 if (msb & 8) == 0 else -(1 << 11)
        value += unified_no_sign
        return value / 4
