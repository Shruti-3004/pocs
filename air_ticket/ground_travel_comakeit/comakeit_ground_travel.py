import re
import glob
from prettyprinter import pprint
import pandas as pd
import os
import datetime
from delimiter_comakeit_groundtravel import DelimiterComakeitGroundTravel

class ComakeitGroundTravel:

    def __init__(self, images):
        self.process_images = images
        self.path_ = 'modules/documents/groundtravel'

    def get_traveler_name(self, text):
        traveler_name = []
        for line in text:
            if 'in words' in line.lower() or 'duty #' in line.lower():
                break
            if 'passengers' in line.lower():
                words = line.split()
                t_name = ' '.join(words[1:])
                traveler_name.append(t_name)
        return traveler_name

    def get_dates(self, text, n):

        s_date = []
        start_dates = []
        e_date = []
        end_dates = []

        if n == 1:
            for line in text:
                if re.search('.*from.*to.*', line.lower()):
                    words = line.lower().split()
                    ind = words.index('from')
                    try:
                        date = datetime.datetime.strptime(words[ind+1], '%d-%m-%Y').strftime('%Y-%m-%d')
                    except:
                        pass
                    s_date.append(date)
                    # start_date.append(s_date)
                    ind = words.index('to')
                    try:
                        date = datetime.datetime.strptime(words[ind+1], '%d-%m-%Y').strftime('%Y-%m-%d')
                    except:
                        pass
                    e_date.append(date)
                    # end_date.append(e_date)
                    break
                if re.search('.*booked by.*date.*', line.lower()) and 's.date e.date s.time e.time' not in line.lower() and 'veh.num. s.date e.date' not in line.lower():
                    words = line.lower().split()
                    ind = words.index('date:')
                    try:
                        date = datetime.datetime.strptime(words[ind+1], '%d-%m-%Y').strftime('%Y-%m-%d')
                    except:
                        pass
                    s_date.append(date)
                    # start_date.append(s_date)
                    e_date.append(date)
                    # end_date.append(e_date)
                    break

            return s_date, e_date

        else:
            flag = 0
            for i in range(len(text)):
                if 's.date e.date s.time e.time' in text[i].lower():
                    for j in range(i+1, len(text)):
                        pattern = ('[0-9][0-9]-[0-9][0-9]')
                        p = re.compile(pattern)
                        result = p.findall(text[j])
                        if result:
                            # print('RESULT----> ', result)
                            try:
                                date = datetime.datetime.strptime(result[0], '%d-%m-%Y').strftime('%Y-%m-%d')
                            except:
                                pass
                            start_dates.append(date)
                            try:
                                date = datetime.datetime.strptime(result[1], '%d-%m-%Y').strftime('%Y-%m-%d')
                            except:
                                pass
                            end_dates.append(date)
                            if 'total' in text[j].lower():
                                flag = 1
                                break
                if flag == 1:
                    break

            return start_dates, end_dates

    def get_distance(self, text, n):
        d = []

        if n == 1 or n == 0:
            for i in range(len(text)):
                if 'start end total extra' in text[i].lower():
                    words = text[i+1].split()
                    dis = words[-2]
                    d.append(dis)
        
        else:
            flag = 0
            for i in range(len(text)):
                if 's.date e.date s.time e.time' in text[i].lower():
                    for j in range(i+1, len(text)):
                        words = text[j].split()
                        if len(words) > 6:
                            dis = words[-7]
                            d.append(dis)
                        if 'total' in text[j].lower():
                            flag = 1
                            break
                if flag == 1:
                    break
            
        return d

    def get_distance_unit(self, text):

        dis_unit = []

        for i in range(len(text)):
            if re.search('.*start.*end.*total.*extra.*', text[i].lower()):
                unit = text[i+1].split()[0]
                if not unit.isnumeric():
                    dis_unit.append(unit)
        
        return dis_unit

    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def get_additional_charges(self, text):

        charges = []
        flag = 0
        debarred = ['total', 'for', 'sor']

        for i in range(len(text)):
            if 'passenger veh.num. s.date e.date' in text[i].lower():
                for j in range(i+1, len(text)):
                    words = text[j].split()
                    # print(words)
                    if 'total' in text[j].lower():
                        flag = 1
                        break
                    if self.is_float(words[-1]) or words[-1].isnumeric():
                        if '.' in words[-1] and len(words[-1].split('.')[-1]) > 0:
                            charges.append(words[-1])
            if flag == 1:
                break
        
        return charges

    def get_stationary_asset(self, text):

        asset = []

        data = {
            'first': 'Dendukuri House',
            'second': 'Galaxy Aurobindo 9th Floor',
            'third': 'Galaxy Aurobindo 5th Floor'
        }

        for line in text:
            if re.search('.*plot no 564/a39.*phase.*road no 92.*', line.lower()):
                asset.append(data['first'])
                break

        return asset

    def get_trip_costs(self, text):
        costs = []
        flag = 0
        amt = 0
        # flag2 = 0

        for i in range(len(text)):
            if 'sr. description rate qty amount' in text[i].lower():
                # flag2 = 1
                for j in range(i+1, len(text)):
                    if '#' in text[j]:
                        for k in range(j+1, len(text)):
                            words = text[k].split()
                            if 'extra hours' in text[k].lower() or 'extra km' in text[k].lower() or 'total' in text[k].lower():
                                # costs.append(amt)
                                flag = 1
                                break
                            if self.is_float(words[-1].replace(',', '')):
                                if '.' in words[-1] and len(words[-1].split('.')[-1]) > 0 and 'total' not in text[k].lower():
                                    # print(words[-1])
                                    # amt += float(words[-1].replace(',', ''))
                                    amt = float(words[-1].replace(',', ''))
                                    costs.append(amt)
                                    break
                                    # print(amt)
                            if '#' in text[k]:
                                costs.append(amt)
                                break
                            # if 'total' in text[k].lower():
                            #     costs.append(amt)
                            #     flag = 1
                            #     break
                    if flag == 1:
                        break
                if flag == 1:
                    break
        
        return costs

    def get_expense_type(self, text):
        return ['Taxi']

    def get_currency_code(self, text):
        return ['INR']

    def get_bill_no(self, text):
        inv_num = []
        for line in text:
            if 'invoice number' in line.lower():
                inv_num.append(line.split()[-1])
                break
        return inv_num

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

                asset_names = self.get_stationary_asset(text)
                traveler_names = self.get_traveler_name(text)
                n = len(traveler_names)
                expense_types = self.get_expense_type(text)
                start_dates = self.get_dates(text, n)[0]
                end_dates = self.get_dates(text, n)[1]
                distances = self.get_distance(text, n)
                distance_units = self.get_distance_unit(text)
                trip_costs = self.get_trip_costs(text)
                currency_codes = self.get_currency_code(text)
                additional_charges = self.get_additional_charges(text)
                bill_nos = self.get_bill_no(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                with open(text_file, 'a', encoding='utf-8') as fp:
                    fp.write(str(asset_names)+"\n")
                    fp.write(str(traveler_names)+"\n")
                    fp.write(str(expense_types)+"\n")
                    fp.write(str(start_dates)+"\n")
                    fp.write(str(end_dates)+"\n")
                    fp.write(str(distances)+"\n")
                    fp.write(str(distance_units)+"\n")
                    fp.write(str(trip_costs)+"\n")
                    fp.write(str(currency_codes)+"\n")
                    fp.write(str(additional_charges)+"\n")
                    fp.write(str(bill_nos)+"\n")
                    fp.write('')
                    fp.write(str(filename)+"\n")
                    fp.write('---\n')
        return ensemble_output_files

    def get_result(self):
        obj = DelimiterComakeitGroundTravel(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)
        result = {}
        asset_names_ex = []
        traveler_names_ex = []
        expense_types_ex = []
        start_dates_ex = []
        end_dates_ex = []
        distances_ex = []
        distance_units_ex = []
        trip_costs_ex = []
        currency_codes_ex = []
        additional_charges_ex = []
        bill_nos_ex = []
        for e_file in ensemble_output_files:

            stationary_asset_final = []
            traveler_names_final = []
            expense_types_final = []
            start_dates_final = []
            end_dates_final = []
            distances_final = []
            distance_units_final = []
            trip_costs_final = []
            currency_codes_final = []
            additional_charges_final = []
            bill_numbers_final = []

            filename = os.path.split(e_file)[-1].split('.txt')[0]
            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    asset_names = data[0]
                    traveler_names = data[1]
                    expense_types = data[2]
                    start_dates = data[3]
                    end_dates = data[4]
                    distances = data[5]
                    distance_units = data[6]
                    trip_costs = data[7]
                    currency_codes = data[8]
                    additional_charges = data[9]
                    bill_nos = data[10]

                    if traveler_names and not traveler_names_final:
                        traveler_names_final = traveler_names

                    n = len(traveler_names_final)

                    if expense_types and not expense_types_final:
                        expense_types_final = expense_types
                        
                    if start_dates and not start_dates_final:
                        start_dates_final = start_dates

                    if end_dates and not end_dates_final:
                        end_dates_final = end_dates

                    if distances and not distances_final:
                        distances_final = distances

                    if distance_units and not distance_units_final:
                        distance_units_final = distance_units

                    if additional_charges and not additional_charges_final:
                        additional_charges_final = additional_charges

                    if asset_names and not stationary_asset_final:
                        stationary_asset_final = asset_names

                    if trip_costs and not trip_costs_final:
                        trip_costs_final = trip_costs

                    if currency_codes and not currency_codes_final:
                        currency_codes_final = currency_codes

                    if bill_nos and not bill_numbers_final:
                        bill_numbers_final = bill_nos

            traveler_names_ex.extend(traveler_names_final)
            asset_names_ex.extend(stationary_asset_final)
            asset_names_ex = asset_names_ex*len(traveler_names_ex)
            expense_types_ex.extend(expense_types_final)
            expense_types_ex = expense_types_ex*len(traveler_names_ex)
            start_dates_ex.extend(start_dates_final)
            end_dates_ex.extend(end_dates_final)
            distances_ex.extend(distances_final)
            if not distances_ex:
                    distances_ex.extend(['None']*len(traveler_names_ex))
            distance_units_ex.extend(distance_units_final)
            if not distance_units_ex:
                distance_units_ex.extend(['None']*len(traveler_names_ex))
            trip_costs_ex.extend(trip_costs_final)
            if not trip_costs_ex:
                trip_costs_ex.extend(['None']*len(traveler_names_ex))
            currency_codes_ex.extend(currency_codes_final)
            additional_charges_ex.extend(additional_charges_final)
            if not additional_charges_ex:
                additional_charges_ex.extend(['None']*len(traveler_names_ex))
            bill_nos_ex.extend(bill_numbers_final)

        final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
        with open(final_output_file, 'a') as fp:
            fp.write(str(asset_names_ex)+"\n")
            fp.write(str(traveler_names_ex)+"\n")
            fp.write(str(expense_types_ex)+"\n")
            fp.write(str(start_dates_ex)+"\n")
            fp.write(str(end_dates_ex)+"\n")
            fp.write(str(distances_ex)+"\n")
            fp.write(str(distance_units_ex)+"\n")
            fp.write(str(trip_costs_ex)+"\n")
            fp.write(str(currency_codes_ex)+"\n")
            fp.write(str(additional_charges_ex)+"\n")
            fp.write(str(bill_nos_ex)+"\n")

        # result["record_type"] = "ground_travel"
        # result["asset_name"] = asset_names_ex
        # result["traveler_names"] = 