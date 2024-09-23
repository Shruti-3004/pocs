from prettyprinter import pprint
import glob
import datetime
import pandas as pd
import os
import json
import re
from delimiter_comakeit_hotelstay import DelimiterComakeitHotelStay

class ComakeitHotelStay:

    def __init__(self, images):
        self.process_images = images
        self.path_ = 'modules/documents/businesstravel'

    def get_stationary_asset(self, text):
        asset = []
        data = {
            'first': 'Dendukuri House',
            'second': 'Galaxy Aurobindo 9th Floor',
            'third': 'Galaxy Aurobindo 5th Floor',
        }
        for line in text:
            if re.search('.*7th.*floor.*block.*', line.lower()) or re.search('.*9th.*floor.*galaxy.*', line.lower()) or re.search('.*aurobindo.*galaxy.*9th.*floor.*', line.lower()):
                asset.append(data['second'])
                break
            if re.search('.*plot.*no.*564.*a.*39.*', line.lower()):
                asset.append(data['first'])
                break
        return asset

    def get_traveler_name(self, text):
        traveler_name = []
        flag = 0
        for line in text:
            if 'name' in line.lower() and 'bill' in line.lower():
                words = line.split()
                lowerwords = line.lower().split()
                for i in range(len(words)):
                    if 'name' in words[i].lower():
                        for j in range(len(lowerwords)):
                            if 'bill' in lowerwords[j]:
                                ind = j
                                break
                        flag = 1
                        traveler_name.append(' '.join(words[i+2:ind]))
                        # print('NAME--------------> ', traveler_name)
                        break
                if flag:
                    break

        return traveler_name

    def get_start_date(self, text):
        date = ''
        new_date = []
        flag = 0
        for line in text:
            if 'arrival date' in line.lower():
                words = line.split()
                lwords = line.lower().split()
                ind = lwords.index('date')
                for i in range(ind+1, len(words)):
                    # print('WORDS---> ', words[i])
                    if '/' in words[i]:
                        flag = 1
                        date = words[i]
                        break
                if flag:
                    break
        
        formats = ['%d/%m/%Y']
        for format in formats:
            try:
                d = datetime.datetime.strptime(date, format).strftime('%Y-%m-%d')
                new_date.append(d)
            except:
                pass
        
        return new_date

    def get_end_date(self, text):
        date = ''
        new_date = []
        flag = 0
        for line in text:
            if 'departure date' in line.lower():
                words = line.split()
                lwords = line.lower().split()
                if 'date' in lwords:
                    ind = lwords.index('date')
                if 'date:' in lwords:
                    ind = lwords.index('date:')
                for i in range(ind+1, len(words)):
                    # print('WORDS---> ', words[i])
                    if '/' in words[i]:
                        flag = 1
                        date = words[i]
                        break
                if flag:
                    break
        
        formats = ['%d/%m/%Y']
        for format in formats:
            try:
                d = datetime.datetime.strptime(date, format).strftime('%Y-%m-%d')
                new_date.append(d)
            except:
                pass
        
        return new_date

    def get_no_of_rooms(self, text):
        rooms = []
        no_of_rooms = []
        for line in text:
            if 'room no' in line.lower():
                words = line.split()
                lwords = line.lower().split()
                ind = lwords.index('room')
                for i in range(ind, len(words)):
                    if words[i].isnumeric():
                        rooms.append(words[i])
                break
        no_of_rooms.append(len(rooms))
        return no_of_rooms

    def get_no_of_nights(self, text):
        no_of_nights = []
        nights = 0
        try:
            start_date = self.get_start_date(text)
            end_date = self.get_end_date(text)
            for i in range(len(start_date)):
                fyear, fmonth, fday = start_date[i].split('-')
                fdate = datetime.date(int(fyear), int(fmonth), int(fday))
                lyear, lmonth, lday = end_date[i].split('-')
                ldate = datetime.date(int(lyear), int(lmonth), int(lday))
                nights = (ldate-fdate).days
                # print('NIGHTS----> ', nights)
                no_of_nights.append(nights)
            return no_of_nights
        except:
            pass

    def get_hotel_name(self, text):
        hotel_name = []
        for i in range(len(text)):
            if 'hotels' in text[i].lower() and len(text[i].split()) > 1:
                hotel_name.append(text[i])
                break
            if 'tax invoice' in text[i].lower():
                hotel_name.append(text[i+1])
                break
        return hotel_name

    def clean_name(self, hotel_city):
        final_hotel_city = []
        for hc in hotel_city:
            if ',' in hc:
                hc = hc.replace(',', '')
            if '-' in hc:
                hc = hc.replace('-', '')
            final_hotel_city.append(hc)
        if final_hotel_city:
            return final_hotel_city
        return hotel_city

    def get_hotel_city(self, text):
        hotel_city = []
        for i in range(len(text)):
            try:
                if re.search('.*\d{6}.*', text[i]):
                    words = text[i].split()
                    print('WORDS---> ', words)
                    if len(words) < 3 and 'pan no' not in text[i-1].lower():
                        print('TEXT I-1---> ', text[i-1])
                        hotel_city.append(text[i-1].split()[-2])
                        print(hotel_city)
                        break
                    else:
                        words = text[i].split()
                        for j in range(len(words)):
                            if re.search('.*\d{6}.*', words[j]) and 'gstn' not in text[i].lower():
                                ind = j
                                break
                        if 'enclave' in text[i].lower():
                            hotel_city.append(words[ind-2])
                        else:
                            hotel_city.append(words[ind-1])
                        break
            except Exception as e:
                print('ERROR---> ', e)
                pass
        
        hotel_city = self.clean_name(hotel_city)
        return hotel_city

    def get_hotel_country(self, text):
        hotel_country = []
        h_country = ''
        # hotel_city = get_hotel_city(text)
        
        # if hotel_city:
        #     for city in hotel_city:
        #         if city:
        #             try:
        #                 value = data[data['city'] == city.strip()].iloc[0]
        #                 h_country = value['country']
        #                 hotel_country.append(h_country)
        #                 return hotel_country
        #             except:
        #                 pass
        return ['IN']

    def ensemble_output_files(self, text_output):
        ensemble_output_files = []
        for file in text_output:
            with open(file) as fp:
                text = fp.read()
                text = text.splitlines()
                text = [line for line in text if not line.isspace() and len(line) > 0]
                
                filename = os.path.split(file)[-1].split('.txt')[0]
                ind = filename.index('page')
                pre = filename[ind+5:]
                filename = filename[:ind+5]

                stationary_asset = self.get_stationary_asset(text)
                traveler_name = self.get_traveler_name(text)
                start_date = self.get_start_date(text)
                end_date = self.get_end_date(text)
                no_of_rooms = self.get_no_of_rooms(text)
                no_of_nights = self.get_no_of_nights(text)
                hotel_name = self.get_hotel_name(text)
                hotel_city = self.get_hotel_city(text)
                hotel_country = self.get_hotel_country(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                with open(text_file, 'a', encoding='utf-8') as fp:
                    fp.write(stationary_asset+"\n")
                    fp.write(traveler_name+"\n")
                    fp.write(start_date+"\n")
                    fp.write(end_date+"\n")
                    fp.write(no_of_rooms+"\n")
                    fp.write(no_of_nights+"\n")
                    fp.write(hotel_name+"\n")
                    fp.write(hotel_city+"\n")
                    fp.write(hotel_country+"\n")
                    fp.write('')
                    fp.write(str(filename)+"\n")
                    fp.write('---\n')

        return ensemble_output_files

    def get_result(self):
        obj = DelimiterComakeitHotelStay(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)

        stationary_asset_ex = []
        traveler_name_ex = []
        start_date_ex = []
        end_date_ex = []
        no_of_rooms_ex = []
        no_of_nights_ex = []
        hotel_name_ex = []
        hotel_city_ex = []
        hotel_country_ex = []

        for e_file in ensemble_output_files:
            result = {}
            stationary_asset_final = 0
            traveler_name_final = 0
            start_date_final = 0
            end_date_final = 0
            no_of_rooms_final = 0
            no_of_nights_final = 0
            hotel_name_final = 0
            hotel_city_final = 0
            hotel_country_final = 0

            filename = os.path.split(e_file)[-1].split('.txt')[0]
            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    stationary_asset = data[0]
                    traveler_name = data[1]
                    start_date = data[2]
                    end_date = data[3]
                    no_of_rooms = data[4]
                    no_of_nights = data[5]
                    hotel_name = data[6]
                    hotel_city = data[7]
                    hotel_country = data[8]

                    if stationary_asset and not stationary_asset_final:
                        stationary_asset_final = stationary_asset

                    if traveler_name and not traveler_name_final:
                        traveler_name_final = traveler_name

                    if start_date and not start_date_final:
                        start_date_final = start_date

                    if end_date and not end_date_final:
                        end_date_final = end_date
                    
                    if no_of_rooms and not no_of_rooms_final:
                        no_of_rooms_final = no_of_rooms

                    if no_of_nights and not no_of_nights_final:
                        no_of_nights_final = no_of_nights
                    
                    if hotel_name and not hotel_name_final:
                        hotel_name_final = hotel_name

                    if hotel_city and not hotel_city_final:
                        hotel_city_final = hotel_city
                    
                    if hotel_country and not hotel_country_final:
                        hotel_country_final = hotel_country

            if not stationary_asset_ex:
                stationary_asset_ex.extend(stationary_asset_final)
            if not traveler_name_ex:
                traveler_name_ex.extend(traveler_name_final)
            if not start_date_ex:
                start_date_ex.extend(start_date_final)
            if not end_date_ex:
                end_date_ex.extend(end_date_final)
            if not no_of_rooms_ex:
                no_of_rooms_ex.extend(no_of_rooms_final)
            if not no_of_nights_ex:
                no_of_nights_ex.extend(no_of_nights_final)
            if not hotel_name_ex:
                hotel_name_ex.extend(hotel_name_final)
            if not hotel_city_ex:
                hotel_city_ex.extend(hotel_city_final)
            if not hotel_country_ex:
                hotel_country_ex.extend(hotel_country_final)
        
        final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
        with open(final_output_file, 'a') as fp:
            fp.write(str(stationary_asset_ex)+"\n")
            fp.write(str(traveler_name_ex)+"\n")
            fp.write(str(start_date_ex)+"\n")
            fp.write(str(end_date_ex)+"\n")
            fp.write(str(no_of_rooms_ex)+"\n")
            fp.write(str(no_of_nights_ex)+"\n")
            fp.write(str(hotel_name_ex)+"\n")
            fp.write(str(hotel_city_ex)+"\n")
            fp.write(str(hotel_country_ex)+"\n")