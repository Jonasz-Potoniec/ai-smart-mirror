import argparse
import logging
import os

from mask_detector.mask_classifier import MaskClassifier
from mask_detector.models.mobile_net_v2 import MobileNetV2


IMAGE_CAPTURED = 2
PIC_DIRECTORY = '/temp/images/'
MODEL_DIRECTORY = '/models/'

logger = logging.getLogger(__name__)


def model_loader(path: str):
    """
    Load model from checkpoint file.

    Parameters:
        path (str): path to saved checkpoint model.

    Return:
        trained model based on saved model file with all trained weights.
    """
    net = MobileNetV2()
    return MaskClassifier.load_from_checkpoint(path, net=net)


def detect_mask(
        topic_distance,  # Load event bus module configuration
        model_dir,
        image_dir,
        **kwargs
) -> None:
    """
    Waiting for message from camera. On message suitable value check image with the network model.
    """
    # PREPARATION
    # Check if model directory exist
    if not os.path.exists(model_dir):
        raise FileExistsError("Given directory do not exist. Directory: ", model_dir)
    # Check if image directory exist
    if not os.path.exists(image_dir):
        raise FileExistsError("Given directory do not exist. Directory: ", image_dir)
    # Load model
    neural_model = model_loader(model_dir)
    neural_model.eval()

    # MODEL
    logger.info(f'Model ready, listening for events: {topic_distance} from {received_url}')
    # Main loop
    while True:
        # Waiting for any message
        # TODO: wait for signal from ECU

        # Load image
        image_path = image_dir + msg

        # Run model
        result = neural_model(image_path)

        # Print result
        result_text = f'Image {msg} has been classified as {result}'
        print(result_text)
        logger.info(result_text)


if __name__ == "__main__":
    # Creates Argument Parser object named parser
    parser = argparse.ArgumentParser(description='Detector server')

    # Set arguments
    parser.add_argument(
        '--event_bus_server',
        default="127.0.0.1",
    )
    parser.add_argument(
        '--port_in',
        default="5556",
        help='Port on which app listens for events'
    )
    parser.add_argument(
        '--topic_in',
        type=int,
        default=IMAGE_CAPTURED,
    )
    parser.add_argument(
        '--log_level',
        default="INFO",
        help='Sets log level - what messages are printed out'
    )
    parser.add_argument(
        '--image_dir',
        default=PIC_DIRECTORY,
        help='Captured images output directory'
    )
    parser.add_argument(
        '--model_dir',
        default=MODEL_DIRECTORY,
        help='Saved model directory',
    )
    args = parser.parse_args()

    # Setting logger
    logging.basicConfig(
        level=args.log_level.upper()
    )

    # Run module
    main(
        event_bus_server=args.event_bus_server,
        receiving_port=args.port_in,
        topic_distance=args.topic_in,
        model_dir=args.image_dir,
        image_dir=args.image_dir
    )
