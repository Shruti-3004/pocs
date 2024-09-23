import re
import glob
from prettyprinter import pprint
import pandas as pd
import os
import datetime
import json
from delimiter_appcino_electricity import DelimiterAppcinoElectricity

class AppcinoElectricity:

    def __init__(self, images):
        self.process_images = images
        # self.path_ = "/var/www/html/image-processing-deployed/modules/documents/businesstravel"
        self.path_ = 'modules/documents/electricity'

    def get_stationary_asset(self, text):
        pprint(text)

    def get_start_date(self, text):
        start_date = ''
        for line in text:
            if 'consumption period' in line.lower():
                for word in line.split():
                    ## add date condition below
                    if '/' in word:
                        formats = ['%d/%m/%Y']
                        for format in formats:
                            try:
                                start_date = datetime.datetime.strptime(word, format).strftime('%Y-%m-%d')
                                return start_date
                            except:
                                pass

    def get_end_date(self, text):
        count = 0
        end_date = ''
        for line in text:
            if 'consumption period' in line.lower():
                for word in line.split():
                    ## add date condition below
                    if '/' in word:
                        if count:
                            formats = ['%d/%m/%Y']
                            for format in formats:
                                try:
                                    end_date = datetime.datetime.strptime(word, format).strftime('%Y-%m-%d')
                                    return end_date
                                except:
                                    pass
                        count += 1

    def get_fuel_consumption(self, text):
        flag = 0
        for i in range(len(text)):
            if 'consumption unit' in text[i].lower():
                amount = 0
                for j in range(i+1, len(text)):
                    if 'total' in text[j].lower():
                        flag = 1
                        break
                    words = text[j].split()
                    for word in words:
                        if not word.isalpha():
                            amount += float(word)
                            break
            if flag:
                return round(amount, 2)

    def get_consumption_unit(self, text):
        return 'kwh'

    def get_fuel_type(self, text):
        return 'electricity'

    def get_supplier(self, text):
        return 'rajasthan patrika pvt ltd'

    def get_stationary_asset(self, text):
        return 'appcino 4th floor and 2nd floor'
    
    def ensemble_output_files(self, text_output):
        ensemble_output_files = []
        names = []
        num = 0
        for file in text_output:
            with open(file, encoding='utf-8') as fp:
                text = fp.read()
                text = text.splitlines()
                text = [line for line in text if not line.isspace() and len(line) > 0]

                filename = os.path.split(file)[-1].split('.txt')[0]
                ind = filename.index('page')
                pre = filename[ind+5:]
                filename = filename[:ind+5]

                asset = self.get_stationary_asset(text)
                start_date = self.get_start_date(text)
                end_date = self.get_end_date(text)
                fuel_consumption = self.get_fuel_consumption(text)
                consumption_unit = self.get_consumption_unit(text)
                fuel_type = self.get_fuel_type(text)
                supplier = self.get_supplier(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                names = [asset, start_date, end_date, fuel_consumption, consumption_unit, fuel_type, supplier]
                with open(text_file, 'a', encoding='utf-8') as fp:
                    for name in names:
                        fp.write(str(name)+"\n")
                    fp.write('')
                    fp.write(str(filename)+"\n")
                    fp.write('---\n')
                num += 1
        return ensemble_output_files

    def get_result(self):
        obj = DelimiterAppcinoElectricity(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)
        result = {}
        asset_name_ex = []
        start_date_ex = []
        end_date_ex = []
        fuel_consumption_ex = []
        consumption_unit_ex = []
        fuel_type_ex = []
        supplier_ex = []

        for e_file in ensemble_output_files:
            asset_final = []
            start_date_final = []
            end_date_final = []
            fuel_consumption_final = []
            consumption_unit_final = []
            fuel_type_final = []
            supplier_final = []

            filename = os.path.split(e_file)[-1].split('.txt')[0]
            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    asset = eval(data[0])
                    start_date = eval(data[1])
                    end_date = eval(data[2])
                    fuel_consumption = eval(data[3])
                    consumption_unit = eval(data[4])
                    fuel_type = eval(data[5])
                    supplier = eval(data[6])

            if asset and not asset_final:
                asset_final = asset

            if start_date and not start_date_final:
                start_date_final = start_date

            if end_date and not end_date_final:
                end_date_final = end_date

            if fuel_consumption and not fuel_consumption_final:
                fuel_consumption_final = fuel_consumption

            if consumption_unit and not consumption_unit_final:
                consumption_unit_final = consumption_unit

            if fuel_type and not fuel_type_final:
                fuel_type_final = fuel_type

            if supplier and not supplier_final:
                supplier_final = supplier

            asset_name_ex.extend(asset_final)
            start_date_ex.extend(start_date_final)
            end_date_ex.extend(end_date_final)
            fuel_consumption_ex.extend(fuel_consumption_final)
            consumption_unit_ex.extend(consumption_unit_final)
            fuel_type_ex.extend(fuel_type_final)
            supplier_ex.extend(supplier_final)

        final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
        names = [asset_name_ex, start_date_ex, end_date_ex, fuel_consumption_ex, consumption_unit_ex, fuel_type_ex, supplier_ex]
        with open(final_output_file, 'a') as fp:
            for name in names:
                fp.write(str(name)+"\n")
        all_data = []
        for a, sd, ed, fc, cu, ft, s in zip(asset_name_ex, start_date_ex, end_date_ex, fuel_consumption_ex, consumption_unit_ex, fuel_type_ex, supplier_ex):
            json_out = {
                'stationary_asset': a,
                'record_type': 'ground_travel',
                'start_date': sd,
                'end_date': ed,
                'fuel_consumption': fc,
                'consumption_unit': cu,
                'fuel_type': ft,
                'supplier': s
            }        
            all_data.append(json_out)
        json_file = os.path.join(self.path_, f"json_output/{filename}.json")
        with open(json_file, 'w') as fp:
            json.dump(all_data, fp)
        all_pages = [{'lineitems': all_data}]
        return all_pages
            # all_pages.append({"lineitems": all_data})
        # result["record_type"] = "ground_travel"
        # result["asset_name"] = asset_names_ex
        # result["traveler_names"] = 
