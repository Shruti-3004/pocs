import cv2
import os
import re
from prettyprinter import pprint
from PIL import Image, ImageEnhance
import glob

class DelimiterNetlinkElectricity:
    # data = []

    def __init__(self, path, images):
        self.path = path
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
                            cv2.imwrite('ensemble_delimiters_supplier\\'+filename+'.jpg', img)
                            
        return img

    def split_filename(self, image):
        filename = os.path.split(image)[-1].split('.jpg')[0]
        return filename

    def add_delimiters_images(self):
        text_output = []
        for img in self.process_images:
            filename = os.path.split(img)[-1].split('.jpg')[0]
            image = cv2.imread(img)
            result = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255,
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Remove horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            remove_horizontal = cv2.morphologyEx(thresh,
                                                cv2.MORPH_OPEN,
                                                horizontal_kernel,
                                                iterations=2)
            cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

            # Remove vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            remove_vertical = cv2.morphologyEx(thresh,
                                            cv2.MORPH_OPEN,
                                            vertical_kernel,
                                            iterations=2)
            cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(result, [c], -1, (255, 255, 255), 5)

            preproc_image = 'delimiters_images\\'+filename+'.jpg'
            cv2.imwrite(preproc_image, result)

            output_file = 'delimiters_images_text\\'+filename
            command = 'tesseract {} {} -l eng --psm 4'.format(preproc_image, output_file)
            os.system(command)

            text_output.extend(output_file)
        return text_output