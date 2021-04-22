#!/usr/bin/env python3

# Import required Python libraries
import seeed_mlx9064x
import numpy as np
import math
import argparse
import zmq
import xdrlib

class ThermovisionSensor:
    """The class that supports a thermal imaging camera sensor

    For the configuration of the raspberry pi and the mxl90641 sensor,
    the maximum value of the sensor refresh is 8 HZ.

    Attributes:
        size_x(int): sensor resolution in horizontal pixels
        size_y(int): sensor resolution in vertical pixels
    """
    def __init__(self):
        self.mlx = seeed_mlx9064x.grove_mxl90641()
        self.mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_8_HZ
        self.horizontal_size = 16
        self.vertical_size = 12

    """Returns a list of temperature values for each pixel"""
    def get_frame(self):
        try:
            frame = [0] * self.horizontal_size * self.vertical_size
            self.mlx.getFrame(frame)
            return frame
        except ValueError:
            return None

    """Returns the average temperature for human temperature measurement
    at a very close distance of max 10 cm
    
    In the event that the measured surface does not use all pixels,
    we filter values in the range of 32-40 degrees Celsius to increase the accuracy.
    """
    def get_temperature(self):
        measurement_points = self.get_frame()

        if measurement_points == None:
            return np.nan
        measurement_points = list(filter(lambda temp: 32 < float(temp) < 40, measurement_points))
        return np.average(measurement_points)
    

"""The function determines the sensor and connects to the event bus.

Upon receiving a query on port XYZ,
it will return the temperature of the object on port XYZ
"""  
def main():
    parser = argparse.ArgumentParser(description='Thermovision sensor')
    parser.add_argument('--hostname', default="127.0.0.1", help='Hostname to which connect to')
    parser.add_argument('--port', default="5555", help='Port to which connect to')
    parser.add_argument('--topic', type=int, default=20001, help='Event bus topic for the thermovision sensor')

    init_args = parser.parse_args()
    hostname = init_args.hostname
    port = init_args.port
    topic = init_args.topic

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://%s:%s" % (hostname, port))
    data_packer = xdrlib.Packer()


    thermal_sensor = ThermovisionSensor()
    

if __name__ == '__main__':
    main()
