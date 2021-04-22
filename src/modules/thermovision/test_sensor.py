import thermovision_sensor

"""It allows you to check the correctness of the configuration
and connection of the sensor.

The function returns 10 average temperature values for an object
with a temperature close to human temperature
"""
def main():
  thermal_sensor = thermovision_sensor.ThermovisionSensor()
    for i in range(10)
        print(thermal_sensor.get_temperature())
