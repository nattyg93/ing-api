"""Utils for running optical character recognition (ocr) on images."""
import base64
import re

import cv2
import numpy
import pytesseract

NON_ALPHANUMERICAL_REGEX = re.compile(r"[\W_]+")


def strip_non_alphanumerical(text: str) -> str:
    """Strip out all non-alphanumerical characters."""
    return NON_ALPHANUMERICAL_REGEX.sub("", text)


def image_to_text(image: numpy.ndarray, single_char=False, strip=True) -> str:
    """Return the result of running ocr on the image (numpy array)."""
    # convert image to greyscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # binarise the image (convert to black or white)
    image = cv2.threshold(
        image, thresh=0, maxval=255, type=(cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    )[1]
    # invert the image (the text is white in the original image)
    image = cv2.bitwise_not(image)
    # configure tesseract to expect a single character
    psm_flag = "-psm" if pytesseract.get_tesseract_version().version[0] < 4 else "--psm"
    tesseract_config = f"{psm_flag} 10" if single_char else ""
    # run ocr on the image
    ocr_text = pytesseract.image_to_string(image, config=tesseract_config)
    if strip:
        ocr_text = strip_non_alphanumerical(ocr_text)
    return ocr_text


def b64_image_to_text(b64_image: str, single_char=False, strip=True) -> str:
    """Return the result of running ocr on a base64 encoded string."""
    numpy_array = numpy.frombuffer(base64.b64decode(b64_image), dtype=numpy.uint8)
    opencv_image = cv2.imdecode(numpy_array, flags=cv2.IMREAD_COLOR)
    return image_to_text(opencv_image, single_char=single_char, strip=strip)


def b64_image_to_int(b64_image: str, single_char=True, strip=True) -> int:
    """
    Return the result as an int of running ocr on a base64 encoded string.

    Raises ValueError if the result is not an integer.
    """
    text = b64_image_to_text(b64_image, single_char=single_char, strip=strip)
    try:
        return int(text)
    except ValueError as error:
        raise ValueError(f'Image does not contain an integer: "{text}"') from error
