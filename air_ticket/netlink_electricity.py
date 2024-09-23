import re
import glob
from prettyprinter import pprint
import pandas as pd
import datetime
from .delimiter_netlink_electricity import DelimiterNetlinkElectricity

class NetlinkElectricity:
    def __init__(self, images):
        self.process_images = images
        self.path_ = 'modules/documents/electricity'

    def extract_date(self, text):
        start_date = ''
        end_date = ''
        for line in text:
            x = re.search('.+from.+to.+', line.lower())
            if x:
                words = line.lower().split()
                ind_from = words.index('from')
                start_date = words[ind_from+1]
                start_date = datetime.datetime.strptime(start_date, '%d/%m/%y').strftime('%Y-%m-%d')
                ind_to = words.index('to')
                end_date = words[ind_to+1]
                end_date = datetime.datetime.strptime(end_date, '%d/%m/%y').strftime('%Y-%m-%d')
        return start_date, end_date

    def extract_supplier_name(self, text):
        supplier_name = ''
        if 'annexure' not in text[0].lower():
            supplier_name = text[0]
        return supplier_name

    def extract_fuel_consumption(self, text):
        total_fuel = 0
        for i in range(len(text)):
            if 'particulars' in text[i].lower():
                break
        values = []
        for j in range(i+1, len(text)):
            if '--' in text[j].split()[-2] or '-' in text[j].split()[-2]:
                break
            values.append(float(text[j].split()[-2]))
            sum_values = sum(values)
        return sum_values

    def extract_fuel_consumption_unit(self):
        return 'kWh'

    def get_result(self):
        obj = DelimiterNetlinkElectricity(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        for text_file in text_output:

            start_dates = []
            end_dates = []
            supplier_names = []
            total_fuels = []
            units = []
            asset_names = []
            fuel_types = []

            flag = 0
            with open(text_file) as fp:
                text = fp.read()
                text = text.splitlines()
                text = [line for line in text if not line.isspace() and len(line) > 0]

                for line in text:
                    x = re.search('.+particulars.+units.+', line.lower())
                    if x:
                        flag = 1
                        break
                
                if flag:
                    asset_name = 'NETLINK DIGITAL SOLUTION INDIA PVT LTD'
                    asset_names.append(asset_name)
                    # print(asset_name)
                    start_date = self.extract_date(text)[0]
                    start_dates.append(start_date)
                    # print(start_date)
                    end_date = self.extract_date(text)[1]
                    end_dates.append(end_date)
                    # print(end_date)
                    supplier_name = self.extract_supplier_name(text)
                    supplier_names.append(supplier_name)
                    # print(supplier_name)
                    total_fuel = self.extract_fuel_consumption(text)
                    total_fuels.append(total_fuel)
                    # print(total_fuel)
                    unit = self.extract_fuel_consumption_unit()
                    units.append(unit)
                    # print(unit)
                    fuel_type = 'Electricity'
                    fuel_types.append(fuel_type)