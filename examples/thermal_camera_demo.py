#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 19:17:39 2019

@author: leoli

MIT license
"""



# imports
import pygame
import time
import melopero_amg8833.AMG8833 as mp
import numpy as np
import scipy.interpolate as interpolator


def main():
    # initialize pygame
    pygame.init()
    
    # screen globals
    
    resolution = 32
    rect_scale = 8
    game_screen = pygame.display.set_mode((resolution*rect_scale, resolution*rect_scale))
    pygame.display.set_caption('grid eye')
    
    #the default address is 0x69, solder the jumper on the back of the board to set 0x68
    eye = mp.AMGGridEye(0x69)
    eye.set_fps_mode(mp.AMGGridEye.FPS_10_MODE)
    
    #INTERPOLATION
    points = np.array([(i//8, i%8) for i in range(64)]).reshape(64,2)
    grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
    
    do_main = True
    while do_main:
        pressed = pygame.key.get_pressed()
        pygame.key.set_repeat()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                do_main = False
            
            if pressed[pygame.K_ESCAPE]:
                do_main = False
        
        game_screen.fill((0,0,0))
        
        eye.update_pixels_temperature()
        matrix = np.array(eye.get_pixel_temperature_matrix()).reshape(64)
        interpolated_grid = interpolator.griddata(points, matrix, (grid_x, grid_y), method='cubic')
        for i,row in enumerate(interpolated_grid):
            for j,temp in enumerate(row):
                pygame.draw.rect(game_screen, temp_to_color(temp), ((rect_scale*j, rect_scale*i),(rect_scale,rect_scale)))
                

                
        pygame.display.update()
        
        #time.sleep(0.1)
    
    pygame.quit()
    
blue = (0,0,255)
green = (0,255,0)
yellow = (255,255,0)
red = (255,0,0)

blue_temp = 22
green_temp = 24
yellow_temp = 26
red_temp = 28
    
def temp_to_color(temp):
    min_temp_col = blue
    max_temp_col = red
    min_temp = blue_temp
    max_temp = red_temp
    if temp < blue_temp:
        return blue
    elif temp < green_temp:
        max_temp = green_temp
        max_temp_col = green
    elif temp < yellow_temp:
        max_temp = yellow_temp
        max_temp_col = yellow
        min_temp = green_temp
        min_temp_col = green
    elif temp < red_temp:
        min_temp = yellow_temp
        min_temp_col = yellow
    else:
        return red

    val = (temp - min_temp) / (max_temp - min_temp) 
    return (1-val)*min_temp_col[0] + val*max_temp_col[0], (1-val)*min_temp_col[1] + val*max_temp_col[1], (1-val)*min_temp_col[2] + val*max_temp_col[2]

                


if __name__ == '__main__':
    main()
