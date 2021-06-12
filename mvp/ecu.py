from threading import Thread

from distance_sensor import start_measuring_distance
from camera import ActiveCamera
from camera import take_snap
from detector import detect_mask


if __name__ == "__main__":
    # PREPARAION
    # Prepare distance sensor
    distance = 0
    distance_thread = Thread(target=start_measuring_distance, args=(distance,))

    # Prepare camera
    image_width = 1024
    image_height = 768
    image_format = 'jpg'
    pic_directory = '/tmp/'

    camera = ActiveCamera(
        width=image_width,
        height=image_height,
    )

    # START
    # Start measuring distance
    distance_thread.start()

    print(distance)

    # Taking a picture
    # take_snap(camera, image_format, pic_directory)
