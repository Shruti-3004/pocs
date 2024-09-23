import cv2
import os
import re
from prettyprinter import pprint
from PIL import Image, ImageEnhance
import glob

class DelimiterComakeitHotelStay:
    # data = []
    # os.environ['TESSERACT'] = "/var/www/html/image-processing-deployed"
    # os.environ['TESSDATA_PREFIX'] = "/var/www/html/image-processing-deployed/tessdata" 
    os.environ['TESSERACT'] = "C:\\Program Files (x86)\\tesseract\\bin"
    os.environ['TESSDATA_PREFIX'] = "C:\\Program Files (x86)\\tesseract\\share\\tessdata"

    def __init__(self, path, images):
        self.path_ = path 
        self.process_images = images 

    def get_box_file(self, image, output_path):
        command = 'tesseract {} {} batch.nochop makebox'.format(image, output_path)
        os.system(command)

    def get_parsed_output(self, image, output_file):
        output_file_4 = output_file + "_4"
        command = 'tesseract {} {} -l eng --psm 4'.format(image, output_file_4)
        os.system(command)
        return [output_file_4 + ".txt"]

    def store_separate_lines(self, box_file):
        '''
        Method to separate lines along with box cooridnates
        into nested list.
        '''

        text = ''
        with open(box_file, 'r', encoding='utf-8') as fp:
            text = fp.read()

        text = text.splitlines()

        ch_coords = []

        for ch in text:
            ch_split = ch.split()
            ch_coords.append(ch_split)

        lines = []
        line = []
        max_diff = [1]

        for i in range(len(ch_coords)-1):
            c = ch_coords[i][0]

            if int(ch_coords[i][1]) <= int(ch_coords[i+1][1]) or int(ch_coords[i][1]) - int(ch_coords[i+1][1]) in max_diff:
                line.append(ch_coords[i])
            else:
                line.append(ch_coords[i])
                lines.append(line)
                line = []

        return lines

    def add_delimiters(self, image, filename):
        img = cv2.imread(image)
        full_path = os.path.join(self.path_, "delimiters_images/"+filename+'.jpg')
        cv2.imwrite(full_path, img)
                            
        return img

    def add_delimiters_images(self):
        text_output = []
        for image in self.process_images:
            filename = self.split_filename(image)
            self.add_delimiters(image, filename)
            delimiter_image = os.path.join(self.path_,'delimiters_images/'+filename+'.jpg')
            output_file = os.path.join(self.path_, 'delimiter_images_text/{}'.format(filename))
            f = self.get_parsed_output(delimiter_image, output_file)
            text_output.extend(f)
        return text_output