# Examples
Here are some instructions on how to run the examples. First connect the amg8833 sensor to your raspberry, to see if you have done everything right type `i2cdetect -y 1` on the command line. This command shows you the connected i2c devices, you should see the i2c address of your sensor on a grid.

## Temperature matrix

This demo prints out to the screen the `8*8` temperature matrix.
Simply download the file and run it with:
`python3 temperature_matrix.py`
Wow! you should see the matrix updating and printing out to the screen.

## Thermal camera demo

For this demo to work you will need to install numpy, scipy and pygame, numpy and pygame should already be installled in your raspberry. To install scipy type this command in a terminal:
`sudo apt-get install -y python3-scipy`

**Note:** installing scipy with `sudo pip3 install scipy` can cause problems!

Next download the demo and run it:
`python3 thermal_camera_demo.py`

