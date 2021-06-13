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
        model_dir,
        image_dir,
        **kwargs
) -> None:
    logging.basicConfig(level="DEBUG")
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
    logger.info(f'Model ready.')
    # Main loop
    # Run model
    result = neural_model(image_dir)

    # Print result
    result_text = f'Image {image_dir} has been classified as {result}'
    print(result_text)
    logger.info(result_text)
