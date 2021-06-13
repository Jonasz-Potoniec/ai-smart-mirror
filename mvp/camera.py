import logging
import time
import os
import uuid

from pathlib import Path

import picamera

SOMEONE_VISIBLE = 1
IMAGE_CAPTURED = 2



logger = logging.getLogger(__name__)


class CameraInterface:
    """
    Class for handling camera device using picamera library.
    """
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.start_preview()
        # Camera warm-up time
        time.sleep(2)

    def capture(self, filename: str):
        """
        Take a snapshot from the camera and save the captured image under a given name.

        Parameters:
            filename (str): name of the file with captured image.
        """
        self.camera.capture(filename)

    def close(self):
        """
        Closes video file or capturing device.
        """
        if self.camera:
            self.camera.close()


class ActiveCamera:
    """
    Class implementing one of the possible camera handling interfaces.
    """
    def __init__(self, height: int, width: int):
        self.camera = CameraInterface(height, width)

    def __enter__(self):
        return self.camera

    def __exit__(self, *args, **kwargs):
        if self.camera:
            self.camera.close()


def take_snap(
        camera,
        image_format,
        image_dir,
        **kwargs
) -> None:
    """
    Waiting for message from distance sensor. On message suitable value take snap from camera and broadcast it.
    """
    logging.basicConfig("INFO")

    # prepare directory
    Path(image_dir).mkdir(parents=True, exist_ok=True)

    with camera as active_camera:
        logger.info(f'Camera ready.')
        # Prepare file name
        snap_name = f'{time.time()}.{uuid.uuid4()}.{image_format}'

        # Take a snap and remember image name
        active_camera.capture(
            os.path.join(
                image_dir,
                snap_name
            )
        )
        logger.info(f'Camera took snap: {snap_name}')
