
from prettyprinter import pprint
import glob
import airportsdata
import pandas as pd

def extract_entity(text):
    flag = 0
    for line in text:
        if 'entity' in line.lower():
            flag = 1
            if len(line.split()) > 1:
                return 1
            else:
                return 0
    if flag == 0:
        return 0

def extract_name(text):
    flag = 0
    for line in text:
        if 'name' in line.lower():
            if 'sector' in line.lower():
                return 0
            if len(line.split()) > 2:
                print(line)
                return 1
            else:
                return 0
    if flag == 0:
        return 0

def extract_start_date(text):
    flag = 0
    for line in text:
        if 'start' in line.lower() or 'travel date' in line.lower():
            flag = 1
        if flag == 1:
            return 1
    if flag == 0:
        return 0

def extract_end_date(text):
    flag = 0
    for line in text:
        if 'end' in line.lower():
            flag = 1
        
        if flag == 1:
            return 1
        # if 'end' is not present in line,
        # it means the end date is not present in the document only,
        # so it should be considered as accurate
        else:
            return 1

def extract_distance(text):
    flag = 0
    for line in text:
        if 'distance' in line.lower():
            flag = 1
        
        if flag == 1:
            return 1

    if flag == 0:
        return 0

def extract_distance_unit(text):
    dis = extract_distance(text)
    if dis:
        return 1

    else:
        return 0

def extract_source_city(text):
    airports = airportsdata.load('IATA')
    flag = 0
    for i in range(len(text)-1):
        if 'sector' in text[i].lower():
            for city_code in airports.keys():
                if city_code.lower() in text[i+1].lower():
                    flag = 1
                    return 1
            if flag == 0:
                return 0
        elif 'city' in text[i].lower():
            return 1
    if flag == 0:
        return 0

def extract_destination_city(text):
    airports = airportsdata.load('IATA')
    flag = 0
    for i in range(len(text)-1):
        if 'sector' in text[i].lower():
            for city_code in airports.keys():
                if city_code.lower() in text[i+1].lower():
                    flag = 1
                    return 1
            if flag == 0:
                return 0
    if flag == 0:
        return 0

def extract_source_country(text):
    source_city = extract_source_city(text)
    if source_city:
        return 1
    else:
        return 0

def extract_destination_country(text):
    destination_city = extract_destination_city(text)
    if destination_city:
        return 1
    else:
        return 0

matrix = {}
for file in glob.glob('preprocessed2\\*.txt'):
    with open(file, 'r', encoding='utf-8') as fp:
        text = fp.read()
    text = text.splitlines()
    text = [line for line in text if not line.isspace() and len(line) > 0]
    filename = os.path.split(file)[-1].split('.txt')[0]

    flag = 0
    for line in text:
        if 'product' in line.lower():
            flag = 1

    if flag == 1:
        continue
    
    print(file)
    matrix[filename] = []
    matrix[filename].append(extract_entity(text))
    matrix[filename].append(extract_name(text))
    matrix[filename].append(extract_start_date(text))
    matrix[filename].append(extract_end_date(text))
    matrix[filename].append(extract_distance(text))
    matrix[filename].append(extract_distance_unit(text))
    matrix[filename].append(extract_source_city(text))
    matrix[filename].append(extract_destination_city(text))
    matrix[filename].append(extract_source_country(text))
    matrix[filename].append(extract_destination_country(text))

    # pprint(text)
# pprint(matrix)

keys = ['office_name', 'traveler_name', 'start_date', 'end_date', 'distance', 'distance_unit', 'source_city', 'source_country', 'destination_city', 'destination_country']
# print(len(keys))

df = pd.DataFrame(matrix)
df.index = keys
df.to_csv('key-value.csv')
print(df)
