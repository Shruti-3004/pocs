
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray
from deskew import determine_skew
from matplotlib import pyplot as plt
from pdf2image import convert_from_path
import shutil
import glob

def set_dpi(image, preproc_image):
    im = Image.open(image)
    im.save(preproc_image, dpi=(300,300))
    return preproc_image

def increase_contrast(image, preproc_image):
    im = Image.open(image)
    enhancer = ImageEnhance.Contrast(im)
    factor = 2 #increase contrast
    im_output = enhancer.enhance(factor)
    im_output.save(preproc_image)
    return preproc_image

def increase_sharpness(image, preproc_image):
    im = Image.open(image)
    enhancer = ImageEnhance.Sharpness(im)
    factor = 2
    im_output = enhancer.enhance(factor)
    im_output.save(preproc_image)
    return preproc_image

def convert_to_grayscale(image, preproc_image):
    im = cv2.imread(image)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(preproc_image, im)
    return preproc_image

def convert_to_rgb(image, preproc_image):
    im = cv2.imread(image)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    cv2.imwrite(preproc_image, im)
    return preproc_image

def otsu_threshold(image, preproc_image):
    im = cv2.imread(image)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # im = cv2.threshold(im, 120, 255, cv2.THRESH_BINARY, cv2.THRESH_OTSU)[1]
    im = cv2.adaptiveThreshold(im,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    cv2.imwrite(preproc_image, im)
    return preproc_image

def remove_noise(image, preproc_image):
    im = cv2.imread(image)
    im = cv2.fastNlMeansDenoising(im, None, 20, 7, 21)
    cv2.imwrite(preproc_image, im)
    return preproc_image

def deskew(image):
    im = io.imread(image)
    angle = determine_skew(im)
    rotated = rotate(im, angle, resize=True) * 255
    io.imsave(image, rotated.astype(np.uint8))
    return image

def pdf_to_images(pdf, filename):
    pdf = pdf.replace('\\', '\\\\')
    # print(pdf)
    images = convert_from_path(pdf)
    for i in range(len(images)):
        images[i].save('images2\\{}_page{}'.format(filename, i) +'.jpg', 'JPEG')
