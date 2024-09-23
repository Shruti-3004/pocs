import cv2
import os
import re
from prettyprinter import pprint
from PIL import Image, ImageEnhance
import glob

class DelimiterNetlinkSupplier:
    # data = []

    def __init__(self, path, images):
        self.path_ = path
        self.process_images = images

    def preprocess(self, image):
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imwrite(image, img)
        return image

    def get_box_file(self, image, output_path):
        command = 'tesseract {} {} batch.nochop makebox'.format(image, output_path)
        os.system(command)

    def get_parsed_output(self, image, output_file):
        command = 'tesseract {} {} -l eng --psm 4'.format(image, output_file)
        os.system(command)

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

    def add_delimiters(self, image, lines, filename):
        img = cv2.imread(image)
        ih, iw, _ = img.shape
        flag = 0
        # columns = ['paxnamesector', 'sectortravel', 'sector', 'paxnametravel']
        columns = ['description']

        reference_pts = []

        for line in lines:
            # pprint(line)
            newline = ''.join([line[i][0] for i in range(len(line))])
            # print(newline)
            for column in columns:
                if column in newline.lower():
                    # print(newline)
                    flag = 1
                if flag == 1:
                    # print('helloo')
                    for i in range(len(line)-1):
                        if int(line[i+1][1])-int(line[i][1]) > 55:
                            cv2.putText(img, "|", ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))), cv2.FONT_HERSHEY_SIMPLEX,  
                                                            1, (0, 0, 0), 2, cv2.LINE_AA)
                            # img = cv2.line(img, ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))+3), ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][4]))-3), (0,0,0), 2)
                            # img = cv2.line(img, ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))+3), ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][4]))-3), (0,0,0), 2)
                            cv2.imwrite('new.jpg', img)
                            reference_pts.append(line[i][1])
                            # print(filename)
                            cv2.imwrite('delimiter_images/'+filename+'.jpg', img)
                            
        return img

    def split_filename(self, image):
        filename = os.path.split(image)[-1].split('.jpg')[0]
        return filename

    def add_delimiters_images(self):
        text_output = []
        for image in self.process_images:
            filename = self.split_filename(image)
            output_path = os.path.join(self.path_, 'box_files/{}'.format(filename))
            self.get_box_file(image, output_path)
            box_file = os.path.join(self.path_, 'box_files/{}.box'.format(filename))
            lines = self.store_separate_lines(box_file)
            self.add_delimiters(image, lines, filename)
            delimiter_image = os.path.join(self.path_,'delimiters_images/'+filename+'.jpg')
            output_file = os.path.join(self.path_, 'delimiter_images_text/{}'.format(filename))
            f = self.get_parsed_output(delimiter_image, output_file)
            text_output.extend(f)
        return text_output