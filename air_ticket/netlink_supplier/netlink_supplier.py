
import datetime
import re
from prettyprinter import pprint

def extract_supplier_name(text_pages, rates):
    supplier_name = ''
    for i in range(len(text_pages)):
        page = text_pages[i].splitlines()
        page = [line for line in page if not line.isspace() and len(line) > 0]
        for line in page:
            if 'buyer' in line.lower():
                return [supplier_name]*len(rates)
            if 'limited' in line.lower():
                ind = line.lower().split().index('limited')
                supplier_name = ' '.join(line.split()[:ind+1])
                return [supplier_name]*len(rates)
            elif 'services' in line.lower():
                ind = line.lower().split().index('services')
                supplier_name = ' '.join(line.split()[:ind+1])
                return [supplier_name]*len(rates)
            elif 'ltd,' in line.lower():
                ind = line.lower().split().index('ltd,')
                supplier_name = ' '.join(line.split()[1:ind+1]).strip(',')
                return [supplier_name]*len(rates)

# def extract_item_name(text):
#     item_name = ''
#     for i in range(len(text)):
#         if 'description' in text[i].lower():
#             for j in range(i+1, len(text)):
#                 if 'no.' in text[j].lower() or 'rate' in text[j].lower() or ('no' in text[j].lower() and len(text[j].split()) == 1):
#                     continue
#                 # print('text[j]---> ', text[j])
#                 if '|' not in text[j].lower():
#                     if 'laptop' in text[j].lower():
#                         ind = text[j].lower().split().index('laptop')
#                         item_name = ' '.join(text[j].split()[:ind+1])
#                         # return item_name
#                         # break
#                 else:
#                     item_name = text[j].split('|')[1]

#                 if ':' in item_name:
#                     ind = item_name.index(':')
#                     item_name = item_name[:ind]

#                 return item_name.strip()

def extract_item_names(text_pages):
    items = []
    # print(text_pages[-1])
    for i in range(len(text_pages)):
        page = text_pages[i].splitlines()
        page = [line for line in page if not line.isspace() and len(line) > 0]
        # print(page)
        for j in range(len(page)):
            # print(page[j].lower(), len(page))

            if 'description' in page[j].lower() or ('no.' in page[j].lower() and len(page[j].split())==1):

                items.extend(page[j+1:])
                break

    # for i in range(len(items)):


    # pprint(items)

    ## extract item names and associated serial numbers
    item_names = []
    serial_nums = []
    ser = []
    ser_nums = []
    debarred = ['pt', 'continued', 'computer', 'rate']
    for i in range(len(items)):
        if 'nos' in items[i].lower():
            words = items[i].split()
            ## separate item name from rest of words/list
            for j in range(len(words)):
                if 'nos' in words[j].lower():
                    if ' '.join(words[:j]).lower() not in debarred:
                        item_names.append(' '.join(words[:j]))
                    if ser:
                        serial_nums.append(ser)
                        ser = []
                    break
        if re.findall('.*serial.*no.*', items[i].lower()):
            ser.append(items[i])
        if 'igst' in items[i].lower():
            serial_nums.append(ser)
            break
        if re.findall('.*sr.*no.*', items[i].lower()):
            for j in range(i, len(items)):
                if 'igst' in items[j].lower():
                    break
                arr = items[j].split(',')
                for i in range(len(arr)):
                    if 'sr no.' in arr[i].lower() and len(arr) == 1:
                        continue
                    ser_nums.append(arr[i])
            serial_nums.append(ser_nums)
                # print('arr---> ', arr)
                # serial_nums.extend(items[j].split(','))
    
    for i in range(len(serial_nums)):
        
        if type(serial_nums[i]) == str and re.findall('.*sr.*no.*', serial_nums[i].lower()):
            serial_nums[i] = serial_nums[i].split()[-1]
        if len(serial_nums[i]) == 0:
            serial_nums.remove(serial_nums[i])
        # if type(serial_nums[i]) == str:
        #     words = serial_nums[i].split()
        #     for j in range(len(words)):
        #         if words[j].lower() in debarred:
        #             serial_nums.remove(serial_nums[i])
        #             break
    
    final_items = []
    for i in range(len(item_names)):
        for j in range(len(serial_nums[i])):
            final_items.append(item_names[i]+' '+serial_nums[i][j])

    # print('item_names---> ', item_names)
    # print('serial_nums---> ', serial_nums)

    return final_items, serial_nums


    # return items

def extract_rate(text_pages, serial_nums):
    items = []
    for i in range(len(text_pages)):
        page = text_pages[i].splitlines()
        page = [line for line in page if not line.isspace() and len(line) > 0]
        # print(page)
        for j in range(len(page)):
            # print(page[j].lower(), len(page))

            if 'description' in page[j].lower() or ('no.' in page[j].lower() and len(page[j].split())==1):

                items.extend(page[j+1:])
                break

    # for i in range(len(items)):


    # pprint(items)

    ## extract item names and associated serial numbers
    item_names = []
    
    debarred = ['pt', 'continued', 'computer', 'rate']
    for i in range(len(items)):
        if 'nos' in items[i].lower():
            words = items[i].split()
            ## separate item name from rest of words/list
            for j in range(len(words)):
                if 'nos' in words[j].lower():
                    if ' '.join(words[:j]).lower() not in debarred:
                        item_names.append(' '.join(words))
                    break

    debarred = ['pti', 'pty', 'tonost', 'pp tt', 'tat']
    for it in item_names:
        for d in debarred:
            if d in it.lower():
                # print(it)
                item_names.remove(it)

    unwanted_ch = "|/)}"

    for i in range(len(item_names)):
        for ch in unwanted_ch:
            item_names[i] = item_names[i].replace(ch, ' ')
        item_names[i] = item_names[i].replace('  ', ' ')
    
    rates = []
    for item_name in item_names:
        rates.append(item_name.split()[-3])
    # pprint(rates)

    # print(serial_nums)
    # pprint(item_names)

    final_rates = []
    for i in range(len(serial_nums)):
        final_rates.extend([rates[i]]*len(serial_nums[i]))
    # print(final_rates)

    return final_rates

# def extract_spent_amount(text):
#     amount = ''
#     for line in text:
#         if 'total' in line.lower():
#             amount = line.split()[-1]
#             if '[' not in amount:
#                 return amount.strip()

# def extract_quantity(text):
#     quantity = ''
#     flag = 0
#     item_name = extract_item_name(text)
#     for i in range(len(text)-1):
#         if 'quantity' in text[i].lower():
#             cols = text[i].split('|')
#             # print(cols)
#             for j in range(i+1, len(text)):
#                 if item_name in text[j]:
#                     words = text[j].lower().split('|')
#                     words = [word.strip() for word in words]
#                     # print(words)
#                     if len(words) == len(cols) and 'rate' not in words:
#                         # print(words)
#                         flag = 1
#                         quantity = words[3]
#                         quantity = re.findall(r'\d+', quantity)[0]
#                         return quantity
#                     else:
#                         break
#         if flag == 0:
#             if 'total' in text[i].lower():
#                 words = text[i].split()
#                 for word in words:
#                     if word.isnumeric():
#                         quantity = word
#                         return quantity

def extract_unit(rates):
    return ['Each']*len(rates)

def extract_quantity(rates):
    return [1]*len(rates)

def extract_spent_date(text_pages, rates):
    for i in range(len(text_pages)):
        page = text_pages[i].splitlines()
        page = [line for line in page if not line.isspace() and len(line) > 0]
        # print(page)
        for j in range(len(page)):
    # for i in range(len(text)):
            if re.findall('.*invoice no.*dated.*', page[j].lower()) or 'dated' in page[j].lower():
                return [page[j+1].split()[-1]]*len(rates)

def extract_currency_code(rates):
    return ['INR']*len(rates)

def get_stationary_asset(text_pages, rates):

    asset = ''

    data = {
        'first': 'Dendukuri House',
        'second': 'Galaxy Aurobindo 9th Floor',
        'third': 'Galaxy Aurobindo 5th Floor',
        'fourth': 'New Chennai Township Pvt Ltd',
        'fifth': 'Rishabh Info Park Pvt Ltd'
    }

    for i in range(len(text_pages)):
        page = text_pages[i].splitlines()
        page = [line for line in page if not line.isspace() and len(line) > 0]
        for line in page:
            if re.search('.*plot no 564/a39.*phase.*road no 92.*', line.lower()):
                asset = (data['first'])
                break
            elif re.search('.*phase.*road no. 92.*plot no.*', line.lower()):
                asset = (data['first'])
                break
            elif re.search('.*1st floor.*amrita tower.*', line.lower()) or 'amrita tower' in line.lower() or 'amritatower' in line.lower():
                asset = (data['fourth'])
                break
            elif re.search('.*rr tower.*', line.lower()):
                asset = (data['fifth'])
                break

        if asset:
            return [asset]*len(rates)
        else:
            return ['None']*len(rates)

final_item_names = []
final_rates = []
final_spent_date = []
final_curr_code = []
final_qty = []
final_asset = []
final_supplier_name = []
final_filenames = []

for file in glob.glob('C:\\air_ticket\\netlink_supplier\\ensemble_files\\*'):
    print(file.split('\\')[-1])
    
    with open(file) as fp:
        text = fp.read()
        text_pages = text.split('---')[:-1]

        supplier_name = extract_supplier_name(text_pages, rates)
        # print(supplier_name)
        item_names = extract_item_names(text_pages)[0]
        serial_nums = extract_item_names(text_pages)[1]
        # print(item_names)
        rates = extract_rate(text_pages, serial_nums)
        spent_date = extract_spent_date(text_pages, rates)
        curr_code = extract_currency_code(rates)
        qty = extract_quantity(rates)
        asset = get_stationary_asset(text_pages, rates)
        filename = file.split('\\')[-1].split('.txt')[0]
        # print(asset)

        # text = text.splitlines()
        # text = [line for line in text if not line.isspace() and len(line) > 0]
        
        # supplier_name = extract_supplier_name(text)
        # print(supplier_name)
        # spent_date = extract_spent_date(text)
        # print(spent_date)
        # print('--------')

    # print(len(item_names))
    # print(len(rates))
    # print(len(spent_date))
    # print(len(curr_code))
    # print(len(qty))

    final_item_names.extend(item_names)
    final_rates.extend(rates)
    final_spent_date.extend(spent_date)
    final_curr_code.extend(curr_code)
    final_qty.extend(qty)
    final_asset.extend(asset)
    final_supplier_name.extend(supplier_name)
    final_filenames.extend([filename]*len(rates))

print(len(final_item_names))
print(len(final_rates))
print(len(final_spent_date))
print(len(final_curr_code))
print(len(final_qty))
print(len(final_asset))
print(len(final_supplier_name))
print(len(final_filenames))
