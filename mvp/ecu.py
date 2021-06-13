from threading import Thread

import time

from distance_sensor import measure_distance
from distance_sensor import DistanceSensor
from camera import ActiveCamera
from camera import make_snap
# from detector import detect_mask


if __name__ == "__main__":
    # PREPARAION
    # Prepare distance sensor
    trigger_pin = 7
    echo_pin = 11
    sleep_time = 0.1
    sensor_settle_time = 0.3
    threshold_distance = 80

    distance_sensor = DistanceSensor(trigger_pin, echo_pin)
    time.sleep(sensor_settle_time)  # Allow module to settle

    # Prepare camera
    image_width = 1024
    image_height = 768
    image_format = 'jpg'
    pic_directory = '/tmp/'
    snap_name_container = ['']

    camera = ActiveCamera(
        width=image_width,
        height=image_height,
    )

    # START

    while True:
        # Measure distance
        distance = measure_distance(distance_sensor)

        if distance < threshold_distance:
            print(f'DISTANCE: {distance}')

            # Taking a picture
            snap_name = make_snap(camera, image_format, pic_directory)
            print(f'Camera took snap at: {snap_name}')

            # Detect mask
            time.sleep(3)
