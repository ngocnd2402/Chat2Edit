from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np
from rembg import remove
import cv2
from typing import Tuple
from scipy import fftpack
    
def scale_brightness(image: np.ndarray, factor: float) -> np.ndarray:
    image = Image.fromarray(image)
    image = ImageEnhance.Brightness(image).enhance(factor)
    image = np.array(image)
    return image

def scale_contrast(image: np.ndarray, factor: float) -> np.ndarray:
    image = Image.fromarray(image)
    image = ImageEnhance.Contrast(image).enhance(factor)
    image = np.array(image)
    return image

def scale_blurness(image: np.ndarray, factor: float) -> np.ndarray:
    radius = factor * 10
    image = Image.fromarray(image)
    image = image.filter(ImageFilter.GaussianBlur(radius))
    image = np.array(image)
    return image

def scale_sharpness(image: np.ndarray, factor: float) -> np.ndarray:
    percent = factor * 100
    image = Image.fromarray(image)
    image = image.filter(ImageFilter.UnsharpMask(percent))
    image = np.array(image)
    return image

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    image = Image.fromarray(image)
    image = image.convert("L")
    image = image.convert("RGB")
    image = np.array(image)
    return image


def convert_to_negative(image: np.ndarray) -> np.ndarray:
    image = Image.fromarray(image)
    image = ImageOps.invert(image)
    image = image.convert("RGB")
    image = np.array(image)
    return image


def erase(image: np.ndarray) -> np.ndarray:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image[:, :, 3] = 0
    return image

  
def denoise_NL(image: np.ndarray) -> np.ndarray:
    if len(image.shape) > 2: image = cv2.fastNlMeansDenoisingColored(image, None, 15, 15, 11, 29)  #colored image
    else: image = cv2.fastNlMeansDenoising(image, h=10)
    return image
  
  
def denoise_gaussian(image: np.ndarray) -> np.ndarray:
    image = cv2.GaussianBlur(image, (5,5), 0)
    return image
  

def edge_sobel(image: np.ndarray, scale = 1, delta = 0, ddepth = cv2.CV_16S) -> np.ndarray:
    src = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    grad = cv2.cvtColor(grad, cv2.COLOR_GRAY2BGR)
    return grad

def edge_canny(image: np.ndarray, blur_ksize=5, threshold1=35, threshold2=35) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_gaussian = cv2.GaussianBlur(gray,(blur_ksize,blur_ksize),0)
    img_canny = cv2.Canny(img_gaussian,threshold1,threshold2)
    img_canny = cv2.cvtColor(img_canny, cv2.COLOR_GRAY2BGR)
    return img_canny
  
def horizontal_flip(image: np.ndarray) -> np.ndarray:
    return cv2.flip(image, 1)


def vertical_flip(image: np.ndarray) -> np.ndarray:
    return cv2.flip(image, 0)


def rotate_clockwise(image: np.ndarray, angle: float) -> np.ndarray:
    return rotate_counter_clockwise(image, -angle)


def rotate_counter_clockwise(image: np.ndarray, angle: float) -> np.ndarray:
    image = Image.fromarray(image)
    image = image.rotate(angle=angle, expand=True)
    image = np.array(image)
    return image


def zoom(image: np.ndarray, factor: float, pivot) -> np.ndarray:
    """
    Zoom the input image around a pivot point by a given factor.

    :param image: Input image (NumPy ndarray).
    :param pivot: Pivot point as a tuple (x, y).
    :param factor: Zoom factor (e.g., 1.5 for 1.5x zoom).
    :return: Zoomed image (NumPy ndarray).
    """
    
    height, width = image.shape[0], image.shape[1]

    # Calculate the pivot point in the image coordinates.
    pivot_x, pivot_y = pivot

    # Create an affine transformation matrix for the zoom.
    matrix = np.array([[factor, 0, (1 - factor) * pivot_x],
                       [0, factor, (1 - factor) * pivot_y]])

    # Apply the transformation using cv2.warpAffine.
    zoomed_image = cv2.warpAffine(image, matrix, (width, height))

    return zoomed_image


def forebackground_segment(image: np.ndarray) -> np.ndarray:
    fg_mask = remove(image, alpha_matting=True, only_mask=True, post_process_mask=True)
    bg_mask = 255 - fg_mask
    return {
        "foreground": fg_mask, 
        "background": bg_mask
    }

def balance_histogram(image: np.ndarray) -> np.ndarray:
    img_ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    img_ycbcr[:,:,0] = clahe.apply(img_ycbcr[:,:,0])
    result_image = cv2.cvtColor(img_ycbcr, cv2.COLOR_YCrCb2BGR)
    return result_image

def img_to_sketch(image: np.ndarray) -> np.ndarray:
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blurred_image = cv2.bitwise_not(blurred_image)
    sketch_image = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
    return sketch_image