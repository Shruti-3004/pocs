
from prettyprinter import pprint
import glob
import datetime
import pandas as pd
import os
import json
import re 

def get_traveler_name(self, text):
        traveler_name = ''
        for i in range(len(text)):
            if 'mr' in text[i].lower():
                if 'forma' in text[i].lower():
                    words = text[i].split()
                    newwords = [word.lower().strip() for word in words]
                    for i in range(len(newwords)):
                        if 'forma' in newwords[i]:
                            ind = i
                            break
                        if len(newwords[i])==1 or words[i].islower() or '_' in newwords[i]:
                            ind = i
                            break
                    traveler_name = ' '.join(words[:ind])
                else:
                    name = " ".join([j for j in text[i].split() if len(j)>1 and not j.islower() and "_" not in j])
                    traveler_name = name
                return traveler_name

def get_dates(self, text):
    start_date = ''
    end_date = ''
    try:
        for i in range(len(text)):
            if 'arrival' in text[i].lower():
                start_date = text[i].split()[-1]
                start_date = start_date.replace('‘', '') 
                # print("\n START DATE --> ", start_date)
                if "." not in start_date:
                    start_date = start_date[:2] + "." + start_date[2:4] + "." + start_date[4:]
                elif start_date.count(".") == 1:
                    start_date = start_date.replace(".", "")
                    start_date = start_date[:2] + "." + start_date[2:4] + "." + start_date[4:]
                start_date = datetime.datetime.strptime(start_date, '%d.%m.%y').strftime('%Y-%m-%d')
                end_date = text[i+1].split()[-1]
                end_date = end_date.replace('‘', '')
                # print("\n END DATE --> ", end_date)
                if "." not in end_date:
                    end_date = end_date[:2] + "." + end_date[2:4] + "." + end_date[4:]
                elif end_date.count(".") == 1:
                    end_date = end_date.replace(".", "")
                    end_date = end_date[:2] + "." + end_date[2:4] + "." + end_date[4:]
                end_date = datetime.datetime.strptime(end_date, '%d.%m.%y').strftime('%Y-%m-%d')
                return start_date, end_date
    except Exception as err:
        print("\n ERROR --> ", err)
        return None, None

def get_number_of_rooms(self, text):
    no_of_rooms = 0
    for line in text:
        if 'room :' in line.lower() or 'room 2' in line.lower():
            words = line.split()
            if len(words) > 2:
                no_of_rooms = len(words[2:])
                return no_of_rooms
            else:
                return 1
        if 'room' in line.lower():
            words = line.split()
            no_of_rooms = len(words[1:])
            return no_of_rooms
    return 1

def get_number_of_nights(self, text):
    no_of_nights = 0
    try:
        start_date = self.get_dates(text)[0]
        fyear, fmonth, fday = start_date.split('-')
        fdate = datetime.date(int(fyear), int(fmonth), int(fday))
        end_date = self.get_dates(text)[1]
        lyear, lmonth, lday = end_date.split('-')
        ldate = datetime.date(int(lyear), int(lmonth), int(lday))
        return (ldate-fdate).days
    except:
        pass

def get_hotel_name(self, text):
    hotel_name = ''
    for line in text:
        if 'llc' in line.lower() or "ll" in line.lower():
            if 'india' in line.lower():
                words = line.split()
                newwords = [word.lower() for word in words]
                for i in range(len(newwords)):
                    if 'india' in newwords[i]:
                        ind = i
                        break
                hotel_name = ' '.join(words[ind+1:])
            elif 'swarnabhoomi' in line.lower():
                words = line.split()
                newwords = [word.lower() for word in words]
                for i in range(len(newwords)):
                    if 'swarnabhoomi' in newwords[i]:
                        ind = i
                        break
                hotel_name = ' '.join(words[ind+1:])
            else:
                hotel_name = line
            if "ll" in hotel_name.lower() and "llc" not in hotel_name.lower():
                words = hotel_name.split()
                words[-1] = "LLC"
                hotel_name = ' '.join(words)
            return hotel_name

def get_hotel_city(self, text):
    hotel_city = ''
    for line in text:
        if 'tel' in line.lower() and 'box' in line.lower():
            words = line.split()
            newwords = [word.lower() for word in words]
            for i in range(len(newwords)):
                if 'tel' in newwords[i]:
                    ind = i
                    break
            hotel_city = words[ind-1]
            return hotel_city.strip(',')
            
def get_stationary_asset(self, text):

    asset = ''

    data = {
        'first': 'Dendukuri House',
        'second': 'Galaxy Aurobindo 9th Floor',
        'third': 'Galaxy Aurobindo 5th Floor',
        'fourth': 'New Chennai Township Pvt Ltd',
        'fifth': 'Rishabh Info Park Pvt Ltd'
    }

    for line in text:
        if re.search('.*plot no 564/a39.*phase.*road no 92.*', line.lower()):
            asset = (data['first'])
            break
        elif re.search('.*phase.*road no. 92.*plot no.*', line.lower()):
            asset = (data['first'])
        elif re.search('.*1st floor.*amrita tower.*', line.lower()) or 'amritatower' in line.lower():
            asset = (data['fourth'])
        elif re.search('.*rr tower.*', line.lower()):
            asset = (data['fifth'])
    return asset

def get_hotel_country(self, text, data):
    hotel_country = ''
    hotel_city = self.get_hotel_city(text)
    df_upd = data[data['city'] == hotel_city].iloc[0]
    hotel_country = df_upd['country']
    return hotel_country

data = pd.read_excel("C:/air_ticket\World_DB.xlsx")
for file in glob.glob('C:\\air_ticket\\netlink_hotel_stay\\output\\*'):
    traveler_name_final = 0
    start_date_final = 0
    end_date_final = 0
    no_of_rooms_final = 0
    no_of_nights_final = 0
    hotel_name_final = 0
    hotel_city_final = 0
    hotel_country_final = 0
    asset_final = 0
    with open(file, encoding='utf-8') as fp:
        text = fp.read()
        if "arrival" in text.lower() and "departure" in text.lower():
            # print("FILE --> ", file)
            text = text.splitlines()
            text = [line for line in text if not line.isspace() and len(line) > 0]
            
            filename = os.path.split(file)[-1].split('.txt')[0]
            ind = filename.index('page')
            pre = filename[ind+5:]
            filename = filename[:ind+5]

            traveler_name = get_traveler_name(text)
            start_date = get_dates(text)[0]
            end_date = get_dates(text)[1]
            no_of_rooms = get_number_of_rooms(text)
            no_of_nights = get_number_of_nights(text)
            hotel_name = get_hotel_name(text)
            hotel_city = get_hotel_city(text)
            hotel_country = get_hotel_country(text, data)
            asset = get_stationary_asset(text)

            print(traveler_name)
            print(start_date)
            print(end_date)
            print(no_of_rooms)
            print(no_of_nights)
            print(hotel_name)
            print(hotel_city)
            print(hotel_country)
            print(asset)

            
            # with open(text_file, 'a', encoding='utf-8') as fp:
            #     fp.write(str(traveler_name)+"\n")
            #     fp.write(str(start_date)+"\n")
            #     fp.write(str(end_date)+"\n")
            #     fp.write(str(no_of_rooms)+"\n")
            #     fp.write(str(no_of_nights)+"\n")
            #     fp.write(str(hotel_name)+"\n")
            #     fp.write(str(hotel_city)+"\n")
            #     fp.write(str(hotel_country)+"\n")
            #     fp.write(str(asset)+"\n")
            #     fp.write('')
            #     fp.write(str(filename)+"\n")
            #     fp.write('---\n')

            # if traveler_name and not traveler_name_final:
            #     traveler_name_final = traveler_name
            
            # if start_date and not start_date_final:
            #     start_date_final = start_date
            
            # if end_date and not end_date_final:
            #     end_date_final = end_date

            # if no_of_rooms and not no_of_rooms_final:
            #     no_of_rooms_final = no_of_rooms

            # if no_of_nights and not no_of_nights_final:
            #     no_of_nights_final = no_of_nights

            # if hotel_name and not hotel_name_final:
            #     hotel_name_final = hotel_name

            # if hotel_city and not hotel_city_final:
            #     hotel_city_final = hotel_city

            # if hotel_country and not hotel_country_final:
            #     hotel_country_final = hotel_country

            # if asset and not asset_final:
            #     asset_final = asset
