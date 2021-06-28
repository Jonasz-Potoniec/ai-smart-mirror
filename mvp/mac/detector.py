import logging

from PIL import Image
from torchvision.transforms import (CenterCrop, Compose, Normalize, Resize, ToTensor)

from mask_detector.mask_classifier import MaskClassifier
from mask_detector.models.mobile_net_v2 import MobileNetV2

from torch.utils.data import DataLoader


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
        image_dir,
        neural_model,
        **kwargs
) -> None:
    """
    Waiting for message from camera. On message suitable value check image with the network model.
    """
    logging.basicConfig(level="DEBUG")

    # MODEL
    neural_model.eval()
    logger.info('Model ready.')

    # Prepare object
    transform = Compose([
        Resize(256),  # for MobileNetV2 - set image size to 256
        CenterCrop(224),
        ToTensor(),
        Normalize(mean=[0.406, 0.456, 0.485], std=[0.225, 0.224, 0.229]),  # Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = DataLoader([image_dir], batch_size=1)  # image = Image.open(image_dir)
    # logger.debug("IMAGE SIZE: " + str(image.shape))

    # Run model
    result = neural_model(transform(image))

    # Print result
    logger.info(f'Image has been classified as {result}')
