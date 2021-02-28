#!/usr/bin/env python3

# Import required Python libraries
import seeed_mlx9064x
import numpy as np
import math

class ThermovisionSensor:
    def __init__(self):
        self.mlx = seeed_mlx9064x.grove_mxl90641()
        self.mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_2_HZ
        self.size_x = 16
        self.size_y = 12

    def getFrame(self):
        try:
            frame = [0]*192
            self.mlx.getFrame(frame)
            return frame
        except ValueError:
            return -1

    def getAvgTemperature(self):
        return np.average(self.getFrame())

    # def getTemperature(self, frame, percent_x, percent_y):
    #     frame_2d = np.resize(frame, (self.size_y, self.size_x))
    #     return frame_2d


def main():
    thermal_sensor = ThermovisionSensor()
    while(True):
        print(thermal_sensor.getAvgTemperature())


if __name__ == '__main__':
    main()