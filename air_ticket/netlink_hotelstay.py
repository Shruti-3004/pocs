from prettyprinter import pprint
import glob
import datetime
import pandas as pd
import os
from delimiter_netlink_hotelstay import DelimiterNetlinkHotelStay
import json

class NetlinkHotelStay:

    def __init__(self, images):
        self.process_images = images
        self.path_ = 'modules/documents/businesstravel'

    def get_traveler_name(self, text):
        traveler_name = ''
        for i in range(len(text)):
            if 'mr' in text[i].lower():
                if 'forma' in text[i].lower():
                    words = text[i].split()
                    newwords = [word.lower() for word in words]
                    for i in range(len(newwords)):
                        if 'forma' in newwords[i]:
                            ind = i
                            break
                    traveler_name = ' '.join(words[:ind])
                else:
                    traveler_name = text[i]
                return traveler_name

    def get_dates(self, text):
        start_date = ''
        end_date = ''
        for i in range(len(text)):
            if 'arrival' in text[i].lower():
                start_date = text[i].split()[-1]
                start_date = start_date.replace('‘', '')
                start_date = datetime.datetime.strptime(start_date, '%d.%m.%y').strftime('%Y-%m-%d')
                end_date = text[i+1].split()[-1]
                end_date = end_date.replace('‘', '')
                end_date = datetime.datetime.strptime(end_date, '%d.%m.%y').strftime('%Y-%m-%d')
                return start_date, end_date

    def get_number_of_rooms(self, text):
        no_of_rooms = 0
        for line in text:
            if 'room :' in line.lower():
                words = line.split()
                if len(words) > 2:
                    no_of_rooms = len(words[2:])
                    return no_of_rooms
                else:
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
            if 'llc' in line.lower():
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

    def get_hotel_country(self, text, data):
        hotel_country = ''
        hotel_city = self.get_hotel_city(text)
        df_upd = data[data['municipality'] == hotel_city].iloc[0]
        hotel_country = df_upd['iso_country']
        return hotel_country

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

                traveler_name = self.get_traveler_name(text)
                start_date = self.get_dates(text)[0]
                end_date = self.get_dates(text)[1]
                no_of_rooms = self.get_number_of_rooms(text)
                no_of_nights = self.get_number_of_nights(text)
                hotel_name = self.get_hotel_name(text)
                hotel_city = self.get_hotel_city(text)
                hotel_country = self.get_hotel_country(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                with open(text_file, 'a', encoding='utf-8') as fp:
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
        obj = DelimiterNetlinkHotelStay(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)
        for e_file in ensemble_output_files:
            result = {}
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
                    traveler_name = data[0]
                    start_date = data[1]
                    end_date = data[2]
                    no_of_rooms = data[3]
                    no_of_nights = data[4]
                    hotel_name = data[5]
                    hotel_city = data[6]
                    hotel_country = data[7]

                    if traveler_name_final == 0 and traveler_name != '':
                        traveler_name_final = traveler_name
                    if start_date_final == 0 and start_date != '':
                        start_date_final = start_date
                    if end_date_final == 0 and end_date != '':
                        end_date_final = end_date
                    if no_of_rooms_final == 0 and no_of_rooms != '':
                        no_of_rooms_final = no_of_rooms
                    if no_of_nights_final == 0 and no_of_nights != '':
                        no_of_nights_final = no_of_nights
                    if hotel_name_final == 0 and hotel_name != '':
                        hotel_name_final = hotel_name
                    if hotel_city_final == 0 and hotel_city != '':
                        hotel_city_final = hotel_city
                    if hotel_country_final == 0 and hotel_country != '':
                        hotel_country_final = hotel_country

            final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
            with open(final_output_file, 'a') as fp:
                fp.write(str(traveler_name_final)+"\n")
                fp.write(str(start_date_final)+"\n")
                fp.write(str(end_date_final)+"\n")
                fp.write(str(no_of_rooms_final)+"\n")
                fp.write(str(no_of_nights_final)+"\n")
                fp.write(str(hotel_name_final)+"\n")
                fp.write(str(hotel_city_final)+"\n")
                fp.write(str(hotel_country_final)+"\n")

        result["record_type"] = "hotel_stay"
        result["traveler_name"] = traveler_name_final
        result["start_date"] = start_date_final
        result["end_date"] = end_date_final
        result["room_type"] = ""
        result["number_of_Rooms"] = no_of_rooms_final
        result["number_of_Nights"] = no_of_nights_final
        result["hotel_name"] = hotel_name_final
        result["hotel_city"] = hotel_city_final
        result["hotel_country"] = hotel_country_final

        json_file = os.path.join(self.path_, f"json_output/{filename}.json")
        with open(json_file, 'w') as fp:
            json.dump(result, fp)

        return result