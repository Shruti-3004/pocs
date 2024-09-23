
import cv2
import os
import re

data = []

def preprocess(image):
    img = cv2.imread(image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('new.jpg', img)
    return 'new.jpg'

def get_box_file(image, output_path):
    command = 'tesseract {} {} batch.nochop makebox'.format(image, output_path)
    os.system(command)

def get_parsed_output(image, output_file):
    command = 'tesseract {} {} -l eng --psm 4'.format(image, output_file)
    os.system(command)

def store_separate_lines(box_file):
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

def add_delimiters(image, lines):
    img = cv2.imread(image)
    ih, iw, _ = img.shape
    flag = 0
    columns = ['paxnamesector']

    reference_pts = []

    for line in lines:
        newline = ''.join([line[i][0] for i in range(len(line))])
        # print(newline)
        for column in columns:
            # print(column)
            if column in newline.lower():
                # print(newline)
                flag = 1
            if flag == 1:
                for i in range(len(line)-1):
                    if int(line[i+1][1])-int(line[i][1]) > 55:
                        # cv2.putText(img, "|", ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))), cv2.FONT_HERSHEY_SIMPLEX,  
                                                        # 1, (0, 0, 0), 3, cv2.LINE_AA)
                        img = cv2.line(img, ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))+3), ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][4]))-3), (0,0,0), 2)
                        cv2.imwrite('new.jpg', img)
                        reference_pts.append(line[i][1])
                        
    return 'new.jpg'

def convert_text_to_separate_lines(output_file):
    '''
    Method to store text into lists of lines where each list has
    strings that are segregated by the delimiters.
    '''

    text = ''
    with open(output_file+'.txt', 'r', encoding='utf-8') as fp:
        text = fp.read()

    text = text.splitlines()

    spaces = ['', ' ']
    text = [st for st in text if st not in spaces]

    # pprint(text)

    i = 0
    for line in text:
        if re.search('.*pax.*sector.*', line.lower()):
            text = text[i:]
            break
        i += 1

    for j in range(len(text)):
        if '_' in text[j]:
            text[j] = text[j].replace('_', ' ')
        text[j] = text[j].split(' | ')
    
    return text

def get_table(lines):
    '''
    Method to get table coordinates where the rows are divided into separate lists as per the strings' respective columns
    '''
    i = 0
    for line in lines:
        i += 1
        newline = ''.join([line[i][0] for i in range(len(line))])
        # print(newline)
        if re.search('.*pax.*sector.*', newline.lower()):
            column_names = newline.lower().split('|')
            break
            # print(i)

    table = []
    table = lines[i-1:]
    extras = ['~', '_']

    # pprint(table)
    # k = 0

    for i in range(len(table)):
        table[i] = [ch for ch in table[i] if ch[0] not in extras]

    # pprint(table)

    cols = []
    col = []

    for t in table:
        row = []
        for ch in t:
            col.append(ch)
            if ch[0] == '|' or ch == t[-1]:
                if ch[0] == '|':
                    col.remove(ch)
                row.append(col)
                col = []
        cols.append(row)
    
    pprint(cols)
    
    return cols

def merge_rows(column_coords, columns, line_items, line_item_coords, index):
    row = {}
    
    for col in column_coords:
        flag = 0
        for word in line_item_coords:
            if abs(int(col[0][1])-int(word[0][1])) <= 5:
                # print(columns[column_coords.index(col)]+'---->'+line_items[index][line_item_coords.index(word)])
                # print(line_items[index][line_item_coords.index(word)])
                # data.append({columns[column_coords.index(col)]: line_items[index][line_item_coords.index(word)]})
                flag = 1
                row[columns[column_coords.index(col)]] = line_items[index][line_item_coords.index(word)]
                # break
            elif abs(int(col[-1][1])-int(word[-1][1])) <= 20:
                # print(line_items[index][line_item_coords.index(word)])
                # print(columns[column_coords.index(col)]+'---->'+line_items[index][line_item_coords.index(word)])
                # data.append({columns[column_coords.index(col)]: line_items[index][line_item_coords.index(word)]})
                flag = 1
                row[columns[column_coords.index(col)]] = line_items[index][line_item_coords.index(word)]
            elif flag == 0:
                row[columns[column_coords.index(col)]] = None
                
    data.append(row)
    return data

def split_filename(image):
    filename = os.path.split(image)[-1].split('.')[0]
    return filename

import cv2
import os
import re

data = []

def preprocess(image):
    img = cv2.imread(image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('new.jpg', img)
    return 'new.jpg'

def get_box_file(image, output_path):
    command = 'tesseract {} {} batch.nochop makebox'.format(image, output_path)
    os.system(command)

def get_parsed_output(image, output_file):
    command = 'tesseract {} {} -l eng --psm 4'.format(image, output_file)
    os.system(command)

def store_separate_lines(box_file):
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

def add_delimiters(image, lines):
    img = cv2.imread(image)
    ih, iw, _ = img.shape
    flag = 0
    columns = ['paxnamesector']

    reference_pts = []

    for line in lines:
        newline = ''.join([line[i][0] for i in range(len(line))])
        # print(newline)
        for column in columns:
            # print(column)
            if column in newline.lower():
                # print(newline)
                flag = 1
            if flag == 1:
                for i in range(len(line)-1):
                    if int(line[i+1][1])-int(line[i][1]) > 55:
                        # cv2.putText(img, "|", ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))), cv2.FONT_HERSHEY_SIMPLEX,  
                                                        # 1, (0, 0, 0), 3, cv2.LINE_AA)
                        img = cv2.line(img, ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][2]))+3), ((int(line[i][3])+int(line[i+1][1]))//2, ih-(int(line[i][4]))-3), (0,0,0), 2)
                        cv2.imwrite('new.jpg', img)
                        reference_pts.append(line[i][1])
                        
    return 'new.jpg'

def convert_text_to_separate_lines(output_file):
    '''
    Method to store text into lists of lines where each list has
    strings that are segregated by the delimiters.
    '''

    text = ''
    with open(output_file+'.txt', 'r', encoding='utf-8') as fp:
        text = fp.read()

    text = text.splitlines()

    spaces = ['', ' ']
    text = [st for st in text if st not in spaces]

    # pprint(text)

    i = 0
    for line in text:
        if re.search('.*pax.*sector.*', line.lower()):
            text = text[i:]
            break
        i += 1

    for j in range(len(text)):
        if '_' in text[j]:
            text[j] = text[j].replace('_', ' ')
        text[j] = text[j].split(' | ')
    
    return text

def get_table(lines):
    '''
    Method to get table coordinates where the rows are divided into separate lists as per the strings' respective columns
    '''
    i = 0
    for line in lines:
        i += 1
        newline = ''.join([line[i][0] for i in range(len(line))])
        # print(newline)
        if re.search('.*pax.*sector.*', newline.lower()):
            column_names = newline.lower().split('|')
            break
            # print(i)

    table = []
    table = lines[i-1:]
    extras = ['~', '_']

    # pprint(table)
    # k = 0

    for i in range(len(table)):
        table[i] = [ch for ch in table[i] if ch[0] not in extras]

    # pprint(table)

    cols = []
    col = []

    for t in table:
        row = []
        for ch in t:
            col.append(ch)
            if ch[0] == '|' or ch == t[-1]:
                if ch[0] == '|':
                    col.remove(ch)
                row.append(col)
                col = []
        cols.append(row)
    
    pprint(cols)
    
    return cols

def merge_rows(column_coords, columns, line_items, line_item_coords, index):
    row = {}
    
    for col in column_coords:
        flag = 0
        for word in line_item_coords:
            if abs(int(col[0][1])-int(word[0][1])) <= 5:
                # print(columns[column_coords.index(col)]+'---->'+line_items[index][line_item_coords.index(word)])
                # print(line_items[index][line_item_coords.index(word)])
                # data.append({columns[column_coords.index(col)]: line_items[index][line_item_coords.index(word)]})
                flag = 1
                row[columns[column_coords.index(col)]] = line_items[index][line_item_coords.index(word)]
                # break
            elif abs(int(col[-1][1])-int(word[-1][1])) <= 20:
                # print(line_items[index][line_item_coords.index(word)])
                # print(columns[column_coords.index(col)]+'---->'+line_items[index][line_item_coords.index(word)])
                # data.append({columns[column_coords.index(col)]: line_items[index][line_item_coords.index(word)]})
                flag = 1
                row[columns[column_coords.index(col)]] = line_items[index][line_item_coords.index(word)]
            elif flag == 0:
                row[columns[column_coords.index(col)]] = None
                
    data.append(row)
    return data

def split_filename(image):
    filename = os.path.split(image)[-1].split('.')[0]
    return filename

if __name__ == '__main__':
    
    image = 'C:\\air_ticket\\images2\\74_Yatra_AAAIN233675535_10.09.2022_page0.jpg'
    filename = split_filename(image)

    image = preprocess(image)

    output_path = 'box_files\\{}'.format(filename)
    get_box_file(image, output_path)

    box_file = 'box_files\\{}.box'.format(filename)
    lines = store_separate_lines(box_file)

    image = add_delimiters(image, lines)
