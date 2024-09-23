import dateparser
from datetime import datetime
import glob
from prettyprinter import pprint
import pandas as pd
import cv2
import os
import re
import airportsdata

class ComakeitAirTravel:

    def is_date(self, string):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        # formats = ['%d %b']
        # try: 
        #     print(dateparser.parse(string, date_formats = formats))
        #     return True

        # except ValueError:
        #     return False

        formats = ["%d %b %Y", "%d%b %Y", "%d%b%Y"]
    
        # checking if format matches the date
        res = False
        
        # using try-except to check for truth value
        for format in formats:
            try:
                res = bool(datetime.strptime(string, format))
                return res
            except ValueError:
                res = False
        return res

    # def contains_date(string):
    #     date_formats = ['%d%b %Y', '%d %b %Y']
    #     for format in date_formats:
    #         try:
    #             datetime.strptime(re.search(format, string).group(), format)
    #             return True
    #         except (AttributeError, ValueError):
    #             pass
    #             # print(e)
    #     return False

    def darken_text(self, image, k, filter):
        img = cv2.imread(image)
        if filter == 'gray':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if filter == 'rgb':
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # k = 3
        result = 255*(img/255)**k
        cv2.imwrite('result.jpg', result)
        return 'result.jpg'

    def extract_name(self, text):
        name = ''
        flag = 0
        for i in range(len(text)-1):
            if 'name' in text[i].lower() and 'sector' not in text[i].lower():
                flag = 1
                if ':' in text[i]:
                    name =  text[i].strip().split('Name:')[-1].strip()
                    break
                if '-' in text[i]:
                    name = text[i].strip().split('Name - ')[-1].strip()
                    break
        if flag == 0:
            for i in range(len(text)):
                if 'pax name' in text[i].lower():
                    if 'mr' in text[i-1].lower():
                        name = text[i-1].strip()
                        break

        if 'adt' in name.lower():
            ind = name.lower().index('adt')
            name = name[:ind+3]
            if ')' not in name:
                if '.' in name[-1]:
                    name = name.replace('.', ')')
                else:
                    name += ')'
            else:
                i = name.index(')')
                name = name[:i+1]
        
        if name[-2:].lower() == 'ad':
            name += 'T)'

        extras = ['Name - ', 'Names', 'name.']

        for extra in extras:
            if extra in name:
                name = name.strip(extra)
        
        if '|' in name:
            if name.index('|') == 0:
                name = name.replace('|', '')
            else:
                name = name.replace('|', 'I')

        return name

    def remove_exc(self, sc):
        if len(sc) == 3 and '!' in sc:
            sc = sc.replace('!', 'I')
        elif len(sc) > 3 and '!' in sc:
            sc = sc.replace('!', '')
        if '(' in sc:
            i = sc.index('(')
            sc = sc[:i]
        if '.' in sc:
            sc = sc.replace('.', '')
        if '=' in sc:
            sc = sc.replace('=', '')
        return sc
        

    def extract_source_city(self, text):
        # print('source city-------------')
        # pprint(text)
        source_cities = []
        destination_cities = []
        flag1 = 0
        debarred = ['spicejet', 'india', 'sg', 'al', 'airline', 'airlines', 'i5', 'asia', '15', 'jet', 'u2', 'airway', '6e', '6684)', '‘qr']
        for i in range(len(text)-1):
            if 'sector' in text[i].lower() or 'pax' in text[i].lower() or 'travel' in text[i].lower():
                flag1 = 1
                sc = ''
                dc = ''
                flag2 = 0
                for j in range(i+1, len(text)):
                    # print(text[j])
                    words = text[j].split()
                    # print(words)
                    for word in words:
                        # print(word)
                        try:
                            if '-' in word:
                                ind = word.find(next(filter(str.isalpha, word)))
                                word = word[ind:]
                                # print(word)
                        except:
                            pass
                            
                        if 'airlines' in word.split('-')[0].lower():
                            # print('AIRLINESSSS')
                            continue
                        if 'indigo' in word.split('-')[0].lower() or 'charge' in word.split('-')[0].lower():
                            # print('INDIGOOOOO')
                            break
                        #  and not any(chr.isdigit() for chr in word)
                        if '-' in word and len(word.split('-')[0]) >= 3 and '(' not in word.split('-')[0] and '{' not in word:
                            
                            if '(' in word:
                                ind = word.index('(')
                                word = word[:ind]
                            ch_ind = word.find(next(filter(str.isalpha, word)))
                            # print(ch_ind)
                            word = word[ch_ind:]
                            
                            sc = word.split('-')[0]
                            sc = self.remove_exc(sc)
                            if sc.lower() not in debarred and len(sc) == 3:
                                source_cities.append(sc)

                            dc = word.split('-')[1]
                            dc = self.remove_exc(dc)
                            if dc.lower() not in debarred and len(dc) == 3:
                                destination_cities.append(dc)
                            continue

            if flag1 == 1:
                break
        
        return source_cities, destination_cities

    def extract_start_date(self, text):
        start_dates = []
        flag1 = 0
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for i in range(len(text)-1):
            if 'travel date' in text[i].lower():
                flag1 = 1
                for j in range(i+1, len(text)):
                    words = text[j].split('|')
                    for word in words:
                        # print(word+'---->'+str(is_date(word.strip())))
                        if self.is_date(word.strip(" ,")):
                            date = word.strip(" ,")
                            # if len(word[i]) == 5:
                            #     date = word[i][:2]+" "+word[i][2:]+" "+word[i+1]
                            # elif len(word[i]) == 7:
                            #     date = word[i-1]+" "+word[i][:3]+" "+word[i][3:]
                            # elif len(word[i]) == 9:
                            #     date = word[i][:2]+" "+word[i][2:5]+" "+word[i][5:]
                            # elif len(word[i]) == 3:
                            #     date = word[i-1]+" "+word[i]+" "+word[i+1]
                            # if date[:2].isnumeric():
                            #     if '.' in date:
                            #         date = date.replace('.', '')
                            #     start_dates.append(date)
                            start_dates.append(date)
                            continue
                        else:
                            flag2 = 0
                            date = ''
                            debarred = ['remarks:', 'separate', 'connaught']
                            word = word.split()
                            for i in range(len(word)):
                                for month in months:
                                    if month in word[i].lower() and word[i].lower() not in debarred:
                                        flag2 = 1
                                        ind = word[i].lower().index(month)
                                        # print(word[i])
                                        word[i] = word[i].strip('.')
                                        try:
                                            if not word[i][ind-1].isalpha() or not word[i-1].isalpha():
                                                if len(word[i]) == 5:
                                                    date = word[i][:2]+" "+word[i][2:]+" "+word[i+1]
                                                elif len(word[i]) == 7:
                                                    date = word[i-1]+" "+word[i][:3]+" "+word[i][3:]
                                                elif len(word[i]) == 9:
                                                    date = word[i][:2]+" "+word[i][2:5]+" "+word[i][5:]
                                                elif len(word[i]) == 3:
                                                    date = word[i-1]+" "+word[i]+" "+word[i+1]
                                                if date[:2].isnumeric():
                                                    if '.' in date:
                                                        date = date.replace('.', '')
                                                    start_dates.append(date)
                                                    break
                                        except:
                                            pass
                                if flag2 == 1:
                                    continue
            if flag1 == 1:
                break

        return start_dates

    def get_result(self):
        pass

    ticket_details = {}
    names = []
    source_cities = []
    destination_cities = []
    start_dates = []
    end_dates = []
    # C:\air_ticket\images2\74_Yatra_AAAIN233675535_10.09.2022_page0.jpg
    for file in glob.glob('C:\\air_ticket\\delimiters2\\*.txt'):
        with open(file, 'r', encoding='utf-8') as fp:
            text = fp.read()
        text = text.splitlines()
        text = [line for line in text if not line.isspace() and len(line) > 0]
        # pprint(text)
        filename = os.path.split(file)[-1].split('.txt')[0]

        # pprint(text)
        print(filename)
        # print()

        # name = extract_name(text)
        # print(name)
        # names = []
        # source_cities = []
        # destination_cities = []
        # start_dates = []
        # end_dates = []

        name = extract_name(text)
        if len(name) == 0:
            ## call darken text function and call extract name function again
            img_file = 'C:\\air_ticket\\images2\\{}.jpg'.format(filename)
            dark_image = darken_text(img_file, 3, 'gray')
            command = 'tesseract {} text_output -l eng --psm 4'.format(dark_image)
            os.system(command)
            with open('text_output.txt', 'r', encoding='utf-8') as fp:
                text_for_name = fp.read()
            text_for_name = text_for_name.splitlines()
            text_for_name = [line for line in text_for_name if not line.isspace() and len(line) > 0]
            # print('NAME---------------------')
            # pprint(text)
            name = extract_name(text_for_name)

        if len(name) == 0:
            img_file = 'C:\\air_ticket\\delimiters2\\{}.jpg'.format(filename)
            dark_image = darken_text(img_file, 3, 'gray')
            command = 'tesseract {} text_output -l eng --psm 4'.format(dark_image)
            os.system(command)
            with open('text_output.txt', 'r', encoding='utf-8') as fp:
                text_for_name2 = fp.read()
            text_for_name2 = text_for_name2.splitlines()
            text_for_name2 = [line for line in text_for_name2 if not line.isspace() and len(line) > 0]
            # print('NAME---------------------')
            # pprint(text)
            name = extract_name(text_for_name2)

        if len(name) == 0:
            img_file = 'C:\\air_ticket\\delimiters2\\{}.jpg'.format(filename)
            dark_image = darken_text(img_file, 4, 'gray')
            command = 'tesseract {} text_output -l eng --psm 4'.format(dark_image)
            os.system(command)
            with open('text_output.txt', 'r', encoding='utf-8') as fp:
                text_for_name3 = fp.read()
            text_for_name3 = text_for_name3.splitlines()
            text_for_name3 = [line for line in text_for_name3 if not line.isspace() and len(line) > 0]
            # print('NAME---------------------')
            # pprint(text)
            name = extract_name(text_for_name3)
        
        if len(name) == 0:
            img_file = 'C:\\air_ticket\\images2\\{}.jpg'.format(filename)
            dark_image = darken_text(img_file, 5, 'rgb')
            command = 'tesseract {} text_output -l eng --psm 4'.format(dark_image)
            os.system(command)
            with open('text_output.txt', 'r', encoding='utf-8') as fp:
                text_for_name4 = fp.read()
            text_for_name4 = text_for_name4.splitlines()
            text_for_name4 = [line for line in text_for_name4 if not line.isspace() and len(line) > 0]
            # print('NAME---------------------')
            # pprint(text)
            name = extract_name(text_for_name4)

        if len(name) == 0:
            img_file = 'C:\\air_ticket\\delimiters2\\{}.jpg'.format(filename)
            dark_image = darken_text(img_file, 6, 'gray')
            command = 'tesseract {} text_output -l eng --psm 4'.format(dark_image)
            os.system(command)
            with open('text_output.txt', 'r', encoding='utf-8') as fp:
                text_for_name5 = fp.read()
            text_for_name5 = text_for_name5.splitlines()
            text_for_name5 = [line for line in text_for_name5 if not line.isspace() and len(line) > 0]
            # print('NAME---------------------')
            # pprint(text)
            name = extract_name(text_for_name5)

        print('Name ----> ', name)
        source_city, destination_city = extract_source_city(text)
        print('Source City ----> ', source_city)
        print('Destination City ----> ', destination_city)
        start_date = extract_start_date(text)
        end_date = extract_start_date(text)
        print('Start Date ----> ', start_date)
        print('End Date ----> ', end_date)
        # if name is not None:
            # names.append(name*len(start_dates))
        # print(names)
        
        text_file = 'textfiles5\\{}.txt'.format(filename)
        with open(text_file, 'w', encoding='utf-8') as fp:
            if not name.strip():
                name = 'None'
            fp.write(name+"\n")
            fp.write(str(source_city)+"\n") 
            fp.write(str(destination_city)+"\n") 
            fp.write(str(start_date)+"\n")
            fp.write(str(end_date)+"\n")
            fp.write(str(filename)+"\n") 
        
        print('---------------------------------------------------------')


        l = len(destination_city)

        for i in range(len(source_city)):
            names.append(name)
        
        for i in range(len(source_city)):
            source_cities.append(source_city[i])
        
        for i in range(len(destination_city)):
            destination_cities.append(destination_city[i])
        
        for i in range(len(start_date)):
            start_dates.append(start_date[i])
            
        for i in range(len(end_date)):
            end_dates.append(end_date[i])

        # ticket_details['Page'] = filename
        ticket_details['Name'] = names
        ticket_details['Source City'] = source_cities
        ticket_details['Destination City'] = destination_cities
        ticket_details['Start Date'] = start_dates
        ticket_details['End Date'] = end_dates


