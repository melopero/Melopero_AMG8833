#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: leoli
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
        self._fps = 10
        self._pixel_data = [[0]*8 for _ in range(8)]
        self._temperature = 0
        
    
    def set_fps_mode(self, fps_mode = 0):
        '''Sets how many times per second the pixels should update.\n
           Parameter : fps_mode (int) - can be 0 for 10 FPS or 1 for 1 FPS
        '''
        assert fps_mode == AMGGridEye.FPS_10_MODE or fps_mode == AMGGridEye.FPS_1_MODE, "FPS mode must be 0 (for 10 fps) or 1 (for 1 fps)!"
        self._fps = 10 if fps_mode == 0 else 1
        self._i2c.write_byte_data(self._i2c_address, _FRAME_RATE_REG_ADDR, fps_mode)
        
        
    def get_fps(self):
        ''' Returns the current FPS settings'''
        return self._fps
    
        
    def update_pixels_temperature(self):
        ''' Updates the pixels data\n
                    
            A pixel's data is stored like this:
            reg0 : b7 b6 b5 b4 b3  b2  b1 b0
            reg1 : -- -- -- -- b11 b10 b9 b8
        '''
        for i, reg_addr in enumerate(range(_FIRST_PIXEL_REG_ADDR,_LAST_PIXEL_REG_ADDR, 2)):
            bits_7to0 = self._i2c.read_byte_data(self._i2c_address, reg_addr)
            bits_11to8 = self._i2c.read_byte_data(self._i2c_address, reg_addr+1)
            
            bits = self._to_bit_list(bits_11to8, 4)
            bits.extend(self._to_bit_list(bits_7to0,8))
            
            self._pixel_data[i//8][i%8] = self._compute_pixel_temp(bits)
            
                
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
    
    def update_temperature(self):
        ''' thermistor's data is stored like this:
            reg0 : b7 b6 b5 b4 b3  b2  b1 b0
            reg1 : -- -- -- -- b11 b10 b9 b8
            
            the temperature is :
                b11      -> sign +1 or -1
                b10 - b4 -> integer part of temperature
                b3 - b0  -> fraction part of temperature: 1 / value(b3b2b1b0)
        '''
        bits_7to0  = self._i2c.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR)
        bits_11to8 = self._i2c.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR + 1)
        
        bits = self._to_bit_list(bits_11to8,4)
        bits.extend(self._to_bit_list(bits_7to0,8))
        
        sign = -1 if bits[0] else 1
        int_temp = self._to_unsigned_int(bits[1:8])
        frac_temp = self._to_unsigned_int(bits[8:])
        frac_temp = 0 if frac_temp==0 else 1 / frac_temp
        
        self._temperature = sign*(int_temp + frac_temp)   
    
    
    def get_temperature(self):
        return self._temperature
    
    def close(self):
        self._i2c.close()

    def _compute_pixel_temp(self, bits):
        ''' 
            The input list must be:
            [b11, b10, b9, b8, b7, b6, b5, b4, b3, b2, b1, b0]
            
            the temperature is obtained like this:
            temp = - b11 * 2**9 + b10 * 2**8 ... + b2 * 2**0 + (b1 * 2**1 + b0 * 2**0)*0.25
        '''
        #return - bits[0] * 2**9 + sum([bits[i] * 2**(11-i-2) for i in range(1, 10)]) + (bits[1] * 2 + bits[0])*0.25
        return self._to_signed_int(bits[0:10]) + (bits[1] * 2 + bits[0])*0.25

    def _to_unsigned_int(self, bitlist):
        val = 0
        for i, bit in enumerate(bitlist):
            val += bit * 2**(len(bitlist)-1-i)
        return val
    
    
    def _to_signed_int(self, bitlist):
        val = - bitlist[0] * 2**(len(bitlist) - 1)
        val += self._to_unsigned_int(bitlist[1:])
        return val


    def _to_bit_list(self, num, length = None):
        ret = []
        while(num != 0):
            ret.insert(0, num%2)
            num //= 2
            
        if length:
            if len(ret) < length:
                ret = [0]*(length - len(ret)) + ret
        return ret
