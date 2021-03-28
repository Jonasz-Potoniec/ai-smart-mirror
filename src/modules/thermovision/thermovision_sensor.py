#!/usr/bin/env python3

# Import required Python libraries
import seeed_mlx9064x
import numpy as np
import math
import argparse
import zmq
import xdrlib

class ThermovisionSensor:
    def __init__(self):
        self.mlx = seeed_mlx9064x.grove_mxl90641()
        self.mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_8_HZ
        self.size_x = 16
        self.size_y = 12

    def getFrame(self):
        try:
            frame = [0]*192
            self.mlx.getFrame(frame)
            return frame
        except ValueError:
            return -1

    def getTemperature(self):
        measurement_points = self.getFrame()

        if measurement_points == -1:
            return np.nan
        measurement_points = list(filter(lambda temp: 32 < float(temp) < 40, measurement_points))
        return np.average(measurement_points)
    
        

def main(parser):
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
    # while(True):
    # trigger
    # send temp


def test():
    thermal_sensor = ThermovisionSensor()
    for i in range(10)
        print(thermal_sensor.getTemperature())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Thermovision sensor')
    parser.add_argument('-t', help='Test thermovision sensor connection', default=False, action='store_true')
    init_args = parser.parse_args()

    if init_args.t:
        test()
    else
        main(parser)