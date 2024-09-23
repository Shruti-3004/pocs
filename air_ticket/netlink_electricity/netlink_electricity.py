
import datetime
import re
import os
import glob

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
    return 'kwh'

image_path = os.getcwd()

for file in glob.glob(image_path+'\\output\\*')[:1]:
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

            start_date = extract_date(text)[0]
            end_date = extract_date(text)[1]
            supplier_name = extract_supplier_name(text)
            fuel_cons = extract_fuel_consumption(text)
            fuel_cons_unit = extract_fuel_consumption_unit()
    
    print(file)
    print(start_date)
    print(end_date)
    print(supplier_name)
    print(fuel_cons)
    print(fuel_cons_unit)
    print('-----')
