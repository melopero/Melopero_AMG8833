#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Leonardo La Rocca
"""

from smbus2 import SMBus

#=========== REGISTERS ADDRESSES ===========#
_MODE_REG_ADDR = 0x00
_RESET_REG_ADDR = 0x01
_FRAME_RATE_REG_ADDR = 0x02
_INTERRUPT_CONTROL_REG_ADDR = 0x03
_STATUS_REG_ADDR = 0x04
_CLEAR_STATUS_REG_ADDR = 0x05
_INT_THR_HIGH_L_REG_ADDRESS = 0x08
_INT_THR_HIGH_H_REG_ADDRESS = 0x09
_INT_THR_LOW_L_REG_ADDRESS = 0x0A
_INT_THR_LOW_H_REG_ADDRESS = 0x0B
_INT_HYSTERESIS_L_REG_ADDRESS = 0x0C
_INT_HYSTERESIS_H_REG_ADDRESS = 0x0D
_INT_TABLE_FIRST_ROW = 0x10
_INT_TABLE_LAST_ROW = 0x17
_FIRST_PIXEL_REG_ADDR = 0x80
_LAST_PIXEL_REG_ADDR = 0xFF
_TEMPERATURE_REG_ADDR = 0x0E

class AMGGridEye():
    ''' A class to easily handle the AMG8833 Grid Eye's functionalities'''
    
    NORMAL_MODE = 0x00
    SLEEP_MODE = 0x10
    STAND_BY_60_SEC_INTERMITTANCE_MODE = 0x20
    STAND_BY_10_SEC_INTERMITTANCE_MODE = 0x21
    
    INTERRUPT_DIFFERENCE_MODE = 0
    INTERRUPT_ABSOLUTE_VALUE_MODE = 1
    
    FPS_10_MODE = 0
    FPS_1_MODE = 1
    
    MIN_THR_TEMP = -2000
    MAX_THR_TEMP = 2000
    
    def __init__(self, i2c_addr = 0x69, i2c_bus = 1):
        self._i2c_address = i2c_addr
        self._i2c_bus = i2c_bus
        self._last_pixel_data = [[0]*8 for _ in range(8)] 
        self._last_interrupt_table = [[False]*8 for _ in range(8)]
        
    def read_byte(self, reg_address):
        with SMBus(self._i2c_bus) as bus:
            value = bus.read_byte_data(self._i2c_address, reg_address)
        return value
    
    def write_byte(self, reg_address, value):
        with SMBus(self._i2c_bus) as bus:
            bus.write_byte_data(self._i2c_address, reg_address, value)
        
    def set_mode(self, device_mode):
        '''Set's the device operating mode.\n
        :device_mode: must be one of NORMAL_MODE, SLEEP_MODE, 
            STAND_BY_N_INTERMITTANCE_MODE.\n
        Note:
            Writing operations in Sleep mode are not permitted. Just the set_mode to 
            NORMAL_MODE is permitted.
            Reading operations in Sleep mode are not permitted.
        '''
        if device_mode != 0x00 and device_mode != 0x10 and device_mode != 0x20 and device_mode != 0x21:
            raise ValueError("device_mode must be one of NORMAL_MODE, SLEEP_MODE, STAND_BY_N_INTERMITTANCE_MODE.")
        
        self.write_byte(_MODE_REG_ADDR, device_mode)
        
    def get_status(self):
        ''' Returns a dictionary containing information about the status of the device.'''
        status = dict()
        status_reg = self.read_byte(_STATUS_REG_ADDR)
        status["Thermistor temp. overflow"] = bool(status_reg & 0x08)
        status["Pixel temp. overflow"] = bool(status_reg & 0x04)
        status["Interrupt"] = bool(status_reg & 0x02)
        return status
    
    def clear_flags(self, interrupt_clear = True, pixel_temp_clear = True, therm_temp_clear = True):
        '''Clears the specified flags'''
        value = therm_temp_clear << 3 | pixel_temp_clear << 2 | interrupt_clear << 1
        self.write_byte(_CLEAR_STATUS_REG_ADDR, value)
            
    def reset_flags(self):
        '''Clears the Status Register, Interrupt Flag, and Interrupt Table.'''
        self.write_byte(_RESET_REG_ADDR, 0x30)
    
    def reset_flags_and_settings(self):
        '''Resets flags and returns to initial setting.'''
        self.write_byte(_RESET_REG_ADDR, 0x3F)
        
    def enable_interrupt(self, interrupt_enable = True, interrupt_mode = INTERRUPT_ABSOLUTE_VALUE_MODE):
        ''' Sets the interrupt mode.\n
        :interrupt_mode: must be INTERRUPT_DIFFERENCE_MODE or INTERRUPT_ABSOLUTE_VALUE_MODE.
        '''
        if interrupt_mode != 0 and interrupt_mode != 1:
            raise ValueError("interrupt_mode must be INTERRUPT_DIFFERENCE_MODE or INTERRUPT_ABSOLUTE_VALUE_MODE.")
        
        value = interrupt_mode << 1 | interrupt_enable
        self.write_byte(_INTERRUPT_CONTROL_REG_ADDR, value)

    def set_interrupt_thresholds(self, low_threshold, high_threshold, hysteresis_lvl = 0): 
        '''Set the low and high threshold values for the interrupt. The values 
        must be provided in Celsius degrees.
        '''
        def to_reg_format(temp):
            reg_format = int(abs(temp) * 4)
            if temp < 0:
                reg_format |= (1 << 12)
                reg_format = ~reg_format
                reg_format |= (1 << 12)
                reg_format += 1
            return reg_format
        
        if not (AMGGridEye.MIN_THR_TEMP < low_threshold < AMGGridEye.MAX_THR_TEMP
                and AMGGridEye.MIN_THR_TEMP < high_threshold < AMGGridEye.MAX_THR_TEMP):
            raise ValueError("low_threshold and high_threshold must be in range [MIN_THR_TEMP; MAX_THR_TEMP]")
        
        low_t_reg_value = to_reg_format(low_threshold)
        high_t_reg_value = to_reg_format(high_threshold)
        hyst_reg_value = to_reg_format(hysteresis_lvl)
        
        self.write_byte(_INT_THR_HIGH_L_REG_ADDRESS, high_t_reg_value & 0xFF)
        self.write_byte(_INT_THR_HIGH_H_REG_ADDRESS, (high_t_reg_value & 0xF00) >> 8)
        self.write_byte(_INT_THR_LOW_L_REG_ADDRESS, low_t_reg_value & 0xFF)
        self.write_byte(_INT_THR_LOW_H_REG_ADDRESS, (low_t_reg_value & 0xF00) >> 8)
        self.write_byte(_INT_HYSTERESIS_L_REG_ADDRESS, hyst_reg_value & 0xFF)
        self.write_byte(_INT_HYSTERESIS_H_REG_ADDRESS, (hyst_reg_value & 0xF00) >> 8)
        
    def update_interrupt_table(self):
        '''Updates the interrupt table. The int. table is an 8*8 matrix of booleans
        where if table[row][col] is True -> The pixel row col generated an interrupt.
        '''
        for row_index, row_address in enumerate(range(_INT_TABLE_FIRST_ROW, _INT_TABLE_LAST_ROW + 1)):
            row_reg = self.read_byte(row_address)
            for col_index in range(8):
                self._last_interrupt_table[row_index][col_index] = bool(row_reg & (1 << col_index))
    
    def get_interrupt_table(self):
        return self._last_interrupt_table
            
    def set_fps_mode(self, fps_mode = 0):
        '''Sets how many times per second the pixels should update.\n
           Parameter : fps_mode (int) - can be 0 for 10 FPS or 1 for 1 FPS
        '''
        if fps_mode != AMGGridEye.FPS_1_MODE and fps_mode != AMGGridEye.FPS_10_MODE:
            raise ValueError("fps_mode must be one of AMGGridEye.FPS_N_MODE")
        
        self.write_byte(_FRAME_RATE_REG_ADDR, fps_mode)
        
    def get_fps(self):
        ''' Returns the current FPS settings'''
        reg_data = self.read_byte(_FRAME_RATE_REG_ADDR)
        return 1 if reg_data else 10            
                
    def update_pixel_temperature_matrix(self):
        ''' Updates the 8*8 pixel temperature matrix containig the 
            the pixels temperature in Celsius\n
            Structure:\n
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
        def to_celsius_temperature(lsb_byte, msb_byte):
            unified_no_sign = ((msb_byte & 7) << 8) | lsb_byte
            value = 0 if (msb_byte & 8) == 0 else -(1 << 11)
            value += unified_no_sign
            return value / 4
        
        with SMBus(self._i2c_bus) as bus:
            for i, reg_addr in enumerate(range(_FIRST_PIXEL_REG_ADDR,_LAST_PIXEL_REG_ADDR, 2)):
                lsb = bus.read_byte_data(self._i2c_address, reg_addr)
                msb = bus.read_byte_data(self._i2c_address, reg_addr+1)
                self._last_pixel_data[i//8][i%8] = to_celsius_temperature(lsb, msb)
    
    def get_pixel_temperature_matrix(self):
        return self._last_pixel_data
    
    def get_pixel_temperature(self, x, y):
        return self._last_pixel_data[y][x]  
    
    def get_thermistor_temperature(self):
        #thermistor's data is stored like this:
        #    reg0 : b7 b6 b5 b4 b3  b2  b1 b0
        #    reg1 : -- -- -- -- b11 b10 b9 b8
        #    
        #    the temperature is :
        #        b11      -> sign +1 or -1
        #        b10 - b4 -> integer part of temperature
        #        b3 - b0  -> fraction part of temperature: 1 / value(b3b2b1b0)
        with SMBus(self._i2c_bus) as bus:
            lsb  = bus.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR)
            msb = bus.read_byte_data(self._i2c_address, _TEMPERATURE_REG_ADDR + 1)
        
        sign = -1 if msb & 0x08 > 0 else 1
        int_temp = ((msb & 0x07) << 4) | ((lsb & 0xF0) >> 4)
        frac = (lsb & 0x0F)
        frac_temp = 0 if frac == 0 else 1 / frac
        
        thermistor_temp = sign*(int_temp + frac_temp)
        return thermistor_temp
