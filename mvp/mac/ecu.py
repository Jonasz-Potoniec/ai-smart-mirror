import logging
import time
import os

from camera import ActiveCamera
from camera import make_snap
from detector import detect_mask
from detector import model_loader

logger = logging.getLogger(__name__)


def run(camera: object, image_format: str, snap_directory: str, neural_model: object):
    # Taking a picture
    snap_name = make_snap(camera, image_format, snap_directory)
    logger.debug(f'Snap at directory: {snap_name}')
    time.sleep(3)

    # Detect mask
    try:
        detect_mask(snap_directory + snap_name, neural_model)
    finally:
        os.remove(snap_directory + snap_name)

    # To not spam with measurements, wait until renewing the whole process
    time.sleep(20)


if __name__ == "__main__":
    # PREPARATION
    logging.basicConfig(level="DEBUG")

    # Prepare camera
    image_width = 1024
    image_height = 768
    image_format = 'jpg'
    snap_directory = 'mvp/mac/tmp/'
    snap_name_container = ['']

    camera = ActiveCamera(
        width=image_width,
        height=image_height,
    )

    # Prepare model
    model_dir = 'mvp/mac/tmp/models/epoch=16-step=8499.ckpt'
    if not os.path.exists(model_dir):
        raise FileExistsError("Given directory do not exist. Directory: ", model_dir)

    neural_model = model_loader(model_dir)

    # Prepare image destination
    image_dir = 'mvp/mac/tmp/images/'
    if not os.path.exists(image_dir):
        raise FileExistsError("Given directory do not exist. Directory: ", image_dir)

    # START
    while True:
        run(camera, image_format, snap_directory, neural_model)
