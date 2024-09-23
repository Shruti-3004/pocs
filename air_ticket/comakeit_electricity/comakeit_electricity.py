from prettyprinter import pprint
import glob
import datetime
import pandas as pd
import os
import json
import re
from delimiter_comakeit_electricity import DelimiterComakeitElectricity

class ComakeitElectricity:

    def __init__(self, images):
        self.process_images = images
        self.path_ = "/var/www/html/image-processing-deployed/modules/documents/businesstravel"
        # self.path_ = 'modules/documents/businesstravel'

    def get_stationary_asset(self, text):
        asset = []

        data = {
            'first': 'Dendukuri House',
            'second': 'Galaxy Aurobindo 9th Floor',
            'third': 'Galaxy Aurobindo 5th Floor',
        }

        for line in text:
            if re.search('.*plot no.*564/.*a.*39.*', line.lower()):
                asset.append(data['first'])
                break
        
        return asset

    def get_consumption_unit(self, text):
        return ['KWH']

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def get_fuel_consumption(self, text):
        cons = []
        flag = 0
        for line in text:
            if 'total consumption' in line.lower() or 'otal consumption' in line.lower():
                words = line.split()
                for i in range(len(words)-1):
                    if words[i].lower() == 'consumption':
                        # print('words---> ', words)
                        words[i+1] = words[i+1].strip('-_—__')
                        if self.isfloat(words[i+1]) and '.' in words[i+1] and len(words[i+1].split('.')[-1]) > 0 and len(words[i+1].split('.')[-1]) < 3:
                                flag = 1
                                cons.append(words[i+1])
                                break
                    if flag:
                        break
            if flag:
                break
        return cons

    def get_supplier(self, text):
        supplier = []
        for line in text:
            if 'limited' in line.lower():
                supplier.append(line)
                break
        return supplier

    def get_date(self, text):
        start_date = []
        end_date = []
        for line in text:
            if 'date' in line.lower():
                words = line.split()
                if '-' in words[-1] and not re.search('[a-zA-Z]', words[-1]):
                    # print(words[-1])
                    month = words[-1].split('-')[1]
                    if month == '01':
                        start_date.append('2022-01-01')
                        end_date.append('2022-01-31')
                        break
                    if month == '02':
                        start_date.append('2022-02-01')
                        end_date.append('2022-02-28')
                        break
                    if month == '03':
                        start_date.append('2022-03-01')
                        end_date.append('2022-03-31')
                        break
                    if month == '04':
                        start_date.append('2022-04-01')
                        end_date.append('2022-04-30')
                        break
                    if month == '05':
                        start_date.append('2022-05-01')
                        end_date.append('2022-05-31')
                        break
                    if month == '06':
                        start_date.append('2022-06-01')
                        end_date.append('2022-06-30')
                        break
                    if month == '07':
                        start_date.append('2022-07-01')
                        end_date.append('2022-07-31')
                        break
                    if month == '08':
                        start_date.append('2022-08-01')
                        end_date.append('2022-08-31')
                        break
                    if month == '09':
                        start_date.append('2022-09-01')
                        end_date.append('2022-09-30')
                        break
                    if month == '10':
                        start_date.append('2022-10-01')
                        end_date.append('2022-10-31')
                        break
                    if month == '11':
                        start_date.append('2022-11-01')
                        end_date.append('2022-11-30')
                        break
                    if month == '12':
                        start_date.append('2022-12-01')
                        end_date.append('2022-12-31')
                        break
                    # break
        return start_date, end_date

    def get_fuel_type(self, text):
        return ['Electricity']

    def ensemble_output_files(self, text_output):
        ensemble_output_files = []
        for file in text_output:
            print("FILE --> ", file)
            with open(file, encoding='utf-8') as fp:
                text = fp.read()
                text = text.splitlines()
                text = [line for line in text if not line.isspace() and len(line) > 0]
                
                filename = os.path.split(file)[-1].split('.txt')[0]
                ind = filename.index('page')
                pre = filename[ind+5:]
                filename = filename[:ind+5]

                stationary_asset = self.get_stationary_asset(text)
                fuel_consumption = self.get_fuel_consumption(text)
                consumption_unit = self.get_consumption_unit(text)
                start_date = self.get_date(text)[0]
                end_date = self.get_date(text)[1]
                fuel_type = self.get_fuel_type(text)
                supplier = self.get_supplier(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                
                keys = [stationary_asset, fuel_consumption, consumption_unit, start_date, end_date, fuel_type, supplier]
                with open(text_file, 'a', encoding='utf-8') as fp:
                    for key in keys:
                        fp.write(str(key)+"\n")
                    fp.write('')
                    fp.write(str(filename)+"\n")
                    fp.write('---\n')

        return ensemble_output_files

    def get_result(self):
        obj = DelimiterComakeitElectricity(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)

        for e_file in ensemble_output_files:
            result = {}
            stationary_asset_final = []
            fuel_consumption_final = []
            consumption_unit_final = []
            start_date_final = []
            end_date_final = []
            fuel_type_final = []
            supplier_final = []

            filename = os.path.split(e_file)[-1].split('.txt')[0]
            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    stationary_asset = eval(data[0])
                    fuel_consumption = eval(data[1])
                    consumption_unit = eval(data[2])
                    start_date = eval(data[3])
                    end_date = eval(data[4])
                    fuel_type = eval(data[5])
                    supplier = eval(data[6])

                    if stationary_asset and not stationary_asset_final:
                        stationary_asset_final = stationary_asset

                    if fuel_consumption and not fuel_consumption_final:
                        fuel_consumption_final = fuel_consumption

                    if consumption_unit and not consumption_unit_final:
                        consumption_unit_final = consumption_unit

                    if start_date and not start_date_final:
                        start_date_final = start_date

                    if end_date and not end_date_final:
                        end_date_final = end_date

                    if fuel_type and not fuel_type_final:
                        fuel_type_final = fuel_type

                    if supplier and not supplier_final:
                        supplier_final = supplier

        final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
        keys = [stationary_asset_final, fuel_consumption_final, consumption_unit_final, start_date_final, end_date_final, fuel_type_final, supplier_final]
        with open(final_output_file, 'a') as fp:
            for key in keys:
                fp.write(str(key)+"\n")

        result["record_type"] = "electricity"
        values = [stationary_asset_final, fuel_consumption_final, consumption_unit_final, start_date_final, end_date_final, fuel_type_final, supplier_final]
        keys = ['stationary_asset', 'fuel_consumption', 'consumption_unit', 'start_date', 'end_date', 'fuel_type', 'supplier']
        for k, v in zip(keys, values):
            if v:
                result[k] = v[0]
                # if k in ['number_of_Rooms', 'number_of_Nights']:
                #     result[k] = int(v[0])
            else:
                result[k] = None
        print(result)
        json_file = os.path.join(self.path_, f"json_output/{filename}.json")
        with open(json_file, 'w') as fp:
            json.dump(result, fp)
        all_pages.append({"lineitems": [result]})
        return all_pages

