# Melopero AMG8833
![melopero logo](images/sensor.jpg?raw=true)

## Getting Started
### Prerequisites
You will need:
- a python3 version, which you can get here: [download python3](https://www.python.org/downloads/)
- the AMG8833 grid eye sensor: [buy here](https://www.melopero.com/en/shop/sensori/melopero-amg8833-grid-eye-ir-array-breakout/)

### Installing
You can install the melopero-amg8833 module by typing this line in the terminal:
```python
sudo pip3 install melopero-amg8833
```

## Module description
The module contains a class to easily access the AMG8833's sensor functions.

### Usage
First you need to import the module in your file:
```python
import melopero_amg8833 as mp
```
Then you can create a simple amg8833 object and access it's methods, the sensor object will be initialized with the i2c address set to `0x69` and the i2c bus to `1` alias `(dev/i2c-1)` which is the standard i2c bus in a Raspberry pi.
```python
sensor = mp.AMGGridEye()
```
Alternatively you can modify it's parameters by typing
```python
sensor = mp.AMGGridEye(i2c_addr = myaddress, i2c_bus = mybus)
```

The sensor has the following methods
```python
sensor.set_fps_mode(fps_mode) #sets the fps mode there are only two options: AMGGridEye.FPS_10_MODE or AMGGridEye.FPS_1_MODE
sensor.get_fps() #returns the current fps 10 or 1
sensor.update_pixel_temperature_matrix() #updates the pixels matrix
sensor.get_pixel_temperature_matrix() #returns the last updated pixel matrix
sensor.get_pixel_temperature(x, y) #returns the spicified pixel's temperature
sensor.get_thermistor_temperature() #returns the temperature of the thermistor
```

## Example
The following example will print out the temperature and the pixel temperature matrix every 0.1 seconds (10 fps)
```python
import time
import melopero_amg8833 as mp

sensor = mp.AMGGridEye()
sensor.set_fps_mode(mp.AMGGridEye.FPS_10_MODE)

while(True):
    #update and print temperature
    print(sensor.get__thermistor_temperature())

    #update and print matrix
    sensor.update_pixel_temperature_matrix()
    print(sensor.get_pixel_temperature_matrix())

    #wait 0.1 seconds
    time.sleep(0.1)
```

### Attention:

The module is written in python3 and by now supports only python3, remember to use always `pip3` when you install the module and `python3` when you run the code.
