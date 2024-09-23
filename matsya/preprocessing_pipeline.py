
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray
# from deskew import determine_skew
from matplotlib import pyplot as plt
from pdf2image import convert_from_path
import shutil
import glob
import os

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

# def deskew(image):
#     try:
#         print("IMAGE --> ", image)
#         im = io.imread(image)
#         angle = determine_skew(im)
#         rotated = rotate(im, angle, resize=True) * 255
#         io.imsave(image, rotated.astype(np.uint8))
#         return image
#     except:
#         return image 

def pdf_to_images(pdf, filename):
    try:
        pdf = pdf.replace('\\', '\\\\')
        # print(pdf)
        images = convert_from_path(pdf)
        for i in range(len(images)):
            images[i].save('C:\\air_ticket\\comakeit_groundtravel\\images\\{}_page{}'.format(filename, i) +'.jpg', 'JPEG')
    except:
        print("\n PDF --> ", pdf)

def get_pdf_image():
    path = "C:\\Users\\Lenovo\\Downloads\\coMakIT-FInal data\\Business Travel Emission Management\\Ground Travel"
    #store all the file names in this list
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            #append the file name to the list
            filelist.append(os.path.join(root,file))
    # print all the file names
    for file in filelist:
        filename = os.path.split(file)[-1].split('.pdf')[0]
        if ' ' in filename:
            filename = filename.replace(' ', '_')
        # print(filename)
        pdf_to_images(file, filename)

def preprocess_files():
    # print('hello')
    combinations = ['convert_to_grayscale-set_dpi', 'increase_contrast-increase_sharpness-set_dpi', 'increase_contrast-convert_to_grayscale-set_dpi', 'convert_to_grayscale-remove_noise-set_dpi', 'increase_contrast-convert_to_grayscale-remove_noise-set_dpi',
                   'convert_to_rgb-set_dpi']
    # combinations = ['set_dpi-increase_contrast-increase_sharpness']
    # combinations = ['convert_to_rgb-set_dpi']
    psms = [3,4,6,11,12]
    for image in glob.glob('C:\\Users\\Lenovo\\Downloads\\us_dl\\*'):
        # print('helloo')
        print("\n IMAGE --> ", image)
        # filename = os.path.split(image)[-1].split('.jpg')[0]
        # preproc_image = 'preprocess_images\\'+filename+'.jpg'
        # shutil.copy(image, preproc_image)
        for combination in combinations:
            filename = os.path.split(image)[-1].split('.jpg')[0]
            preproc_image = 'C:\\matsya\\us_dl_preprocess\\'+filename+'.jpg'
            shutil.copy(image, preproc_image)
            methods = combination.split('-')
            for method in methods:
                if 'deskew' in method:
                    preproc_image = eval(method+'(preproc_image)')
                else:
                    preproc_image = eval(method+'(preproc_image, preproc_image)')
            # print(combination)
            image_name = 'C:\\matsya\\us_dl_preprocess\\' + filename+'_'+combination+'.jpg'
            print(image_name)
            img = cv2.imread(preproc_image)
            cv2.imwrite(image_name, img)

            for psm in psms:
                parsed_output = 'C:\\matsya\\us_dl_text\\'+filename+'_'+str(psm)+'_'+combination
                command = 'tesseract {} {} -l eng --psm {}'.format(image_name, parsed_output, psm)
                os.system(command)

# get_pdf_image()
preprocess_files()
