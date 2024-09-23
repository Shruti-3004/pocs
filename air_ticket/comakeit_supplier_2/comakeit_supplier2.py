import glob
import os
import re
import datetime
from .delimiter_comakeit_supplier import DelimiterComakeitSupplier
import json

class ComakeitSupplier:

    def __init__(self, images):
        self.process_images = images
        self.path_ = "/var/www/html/image-processing-deployed/modules/documents/invoice"
        # self.path_ = 'modules/documents/invoice'

    def get_spent_amount(self, text):
        spent_amt = []
        amt = 0.0
        debarred = ['|', '~—', '_', '‘Total', '“Total', '(Rs.)']
        for line in text:
            if 'total amount after tax' in line.lower():
                amt = line.split()[-1]
                if not amt[0].isalpha() and amt not in debarred:
                    # print('yess1')
                    spent_amt.append(amt)
            elif 'grand total' in line.lower() and not spent_amt:
                amt = line.split()[-1]
                if not amt[0].isalpha() and amt not in debarred:
                    # print('yess2')
                    spent_amt.append(amt)
            elif 'total' in line.lower() and not spent_amt:
                amt = line.split()[-1]
                if not amt[0].isalpha() and amt not in debarred:
                    # print('yess3')
                    spent_amt.append(amt)
            elif 'grand total with gst' in line.lower() and not spent_amt:
                amt = line.split()[-1]
                if not amt[0].isalpha() and amt not in debarred:
                    # print('yess4')
                    spent_amt.append(amt)

        if not spent_amt:
            spent_amt = [None]
        return spent_amt

    def get_currency_code(self, text):
        all_text = ' '.join(t for t in text)
        keys = ['inr', 'rupees', 'rs']
        for key in keys:
            if key in all_text.lower():
                return ['INR']

    def get_spent_date(self, text):
        t = ' '.join(text)
        if 'amazon' in t.lower() or 'paytm' in t.lower():
            for line in text:
                if 'bill date' in line.lower():
                    date = line.split()[-1]
                    break
                if 'order placed' in line.lower():
                    date = ' '.join(line.split()[-3:])
                    break
            formats = ['%d-%m-%Y', '%d %B %Y']
            for format in formats:
                        try:
                            d = datetime.datetime.strptime(date, format).strftime('%Y-%m-%d')
                            return [d]
                        except:
                            pass

        all_text = ' '.join(t for t in text)
        flag = 0
        inv_date = []
        date = ''
        debarred = ['date.', '[dated', 'no.', '1dated', 'date,', 'due.', '‘dated', '|dated']

        for i in range(len(text)):

            if 'invoice date' in text[i].lower():
                date = text[i].split()[-1]
                # inv_date.append(date)
                if date.lower() not in debarred and ':' not in date and not date.isalpha() and len(date) > 4:
                    inv_date.append(date)
                    # print('DATE---> ', inv_date)
                break
            elif 'date' in text[i].lower() and not date:
                date = text[i].split()[-1]
                # print(date)
                # inv_date.append(date)
                if date.lower() not in debarred and ':' not in date and not date.isalpha() and len(date) > 4:
                    inv_date.append(date)
                    # print('DATE---> ', inv_date)
                break
            elif re.search('.*invoice no.*dated.*', text[i].lower()) and not date:
                date = text[i+1].split()[-1]
                # inv_date.append(date)
                if date.lower() not in debarred and ':' not in date and not date.isalpha() and len(date) > 4:
                    inv_date.append(date)
                    # print('DATE---> ', inv_date)
                break
            elif re.search('.*inv.*date.*', text[i].lower()):
                date = text[i].split()[-1]
                # inv_date.append(date)
                if date.lower() not in debarred and ':' not in date and not date.isalpha() and len(date) > 4:
                    inv_date.append(date)
                    # print('DATE---> ', inv_date)
                break

        inv_date_new = []
        for d in inv_date:
            formats = ['%d-%b-%Y', '%d-%m-%Y', '%d/%m/%Y', '%d-%b-%y']
            for format in formats:
                        try:
                            d = datetime.datetime.strptime(d, format).strftime('%Y-%m-%d')
                            inv_date_new.append(d)
                        except:
                            pass
        
        if not inv_date_new:
            inv_date_new = [None]
        return inv_date_new

    def clean_name(self, s_name):
        words = s_name.split()
        new_words = s_name.lower().split()
        keys = ['invoice', 'lnyelee-no-']
        ind = 0

        for key in keys:
            if key in new_words:
                ind = new_words.index(key)
                break
        
        if ind:
            s_name = ' '.join(words[:ind])
        
        # if not s_name:
        #     s_name = [None]
        return s_name

    def get_supplier_name(self, text):
        supp_name = []
        debarred = ['~', 'tax', 'ae', 'irn', 'aren', 'original', 'duplicate', 'transporter', 'si', '36dqypr6397n1z8', 'input', 'gst', 'ack', 'status', 'e-invoice']

        for line in text:
            if 'paytm' in line.lower():
                return ['PAYTM']
            if 'amazon' in line.lower():
                return ['AMAZON']

        for i in range(len(text)):
            s_name = text[i]
            flag = 0
            for deb in debarred:
                if deb in s_name.lower():
                    flag = 1
                    break
            if flag == 1:
                continue
            if flag == 0:
                if re.search('.*[0-9].*', s_name):
                    continue
                s_name = self.clean_name(s_name)
                # for s in s_name:
                #     if s.isnumeric():
                #         print(s_name)
                supp_name.append(s_name)
            break

        # if not supp_name:
        #     supp_name = [None]
        return supp_name

    def get_stationary_asset(self, text):
        asset = []

        data = {
            'first': 'Dendukuri House',
            'second': 'Galaxy Aurobindo 9th Floor',
            'third': 'Galaxy Aurobindo 5th Floor',
        }

        for line in text:
            if re.search('.*plot no.*564/a39.*phase.*road no 92.*', line.lower()):
                asset.append(data['first'])
                break
            elif re.search('.*plot no.*564/a.*39.*', line.lower()):
                asset.append(data['first'])
                break
            elif re.search('.*plot.*564/a.*39.*', line.lower()):
                asset.append(data['first'])
                break
            elif re.search('.*phase.*road no. 92.*plot no.*', line.lower()):
                asset.append(data['first'])
                break
            elif re.search('.*9th.*aurobindo galaxy.*', line.lower()):
                # print('ASSET----> ', data['second'])
                asset.append(data['second'])
                break
            elif re.search('.*9th.*aurabindo.*', line.lower()):
                # print('ASSET----> ', data['second'])
                asset.append(data['second'])
                break
            elif re.search('.*aurobindo.*9th.*', line.lower()):
                # print('ASSET----> ', data['second'])
                asset.append(data['second'])
                break

        # if not asset:
        #     asset = [None]
        return asset

    def clean_text(self, text):
        new_text = []
        for line in text:
            line = line.replace('|', '')
            line = line.replace('\\', '')
            line = line.replace(')', '')
            line = line.replace('(', '')
            line = line.replace('{', '')
            new_text.append(line)
        
        # if not new_text:
        #     new_text = [None]
        return new_text

    def contains_float(self, line):
        words = line.split()
        for word in words:
            try:
                float(word)
                return True
            except ValueError:
                return False

    def clean_item_names(self, item_names):
        # print('ITEM NAMES TO BE CLEANED---> ', item_names)
        debarred = ['no’s', 'nos', 'no', 'sno\'s', 'c19 out']
        for i in range(len(item_names)):
            if item_names[i].lower() in debarred:
                return item_names[:i]
            if self.contains_float(item_names[i]):
                return item_names[:i]

        ind = 0
        for j in range(len(item_names)):
            words = item_names[j].split()
            for i in range(len(words)):
                for deb in debarred:
                    if deb in words[i].lower():
                        ind = i
                        break
                if ind:
                    break
            if ind:
                item_names[j] = ' '.join(words[:ind])
            # return item_names

        debarred2 = ['sees!', 'so ae sages', 'eas!', ': —', 'nos', 'no\'s']
        new_item_names = []
        remove_items = []

        # print('ITEM NAMES---> ', item_names)

        for deb in debarred2:
            for item in item_names:
                # print('ITEM---> ', item)
                if deb in item.lower():
                    # print('ITEM---> ', item)
                    remove_items.append(item)

        # print('REMOVED ITEMS---> ', remove_items)
        new_item_names = [item for item in item_names if item not in remove_items]

        if new_item_names:
            return new_item_names
            
        return item_names

    def get_item_names(self, text):
        t = ' '.join(text)
        if 'amazon' in t.lower() or 'paytm' in t.lower():

            supplier = self.get_supplier_name2(text)
            for i in range(len(text)):
                if 'postpaid mobile' in text[i].lower():
                    if supplier[0].lower() == 'amazon':
                        return ['Amazon Bill- Post paid Mobile Bill']
                if 'water bill' in text[i].lower():
                    if supplier[0].lower() == 'amazon':
                        return ['Amazon Bill- Water bill']
                if 'landline bill' in text[i].lower():
                    if supplier[0].lower() == 'amazon':
                        return ['Amazon Bill- Landline bill']
                if 'description' in text[i].lower():
                    item = ''
                    for j in range(i+1, len(text)):
                        if 'total' in text[j].lower():
                            return [item]
                        words = text[j].split()
                        if 'Rs.' in words:
                            ind = words.index('Rs.')
                            item += ' '.join(words[:ind])
                        else:
                            item += text[j]

        debarred = ['services', 'tax', 'eee', 'sens', 'aia', 'serial', 'eas!', 'sa rs ie.', '[eels', 'noï¿½s']
        item_names = []
        text = self.clean_text(text)

        for i in range(len(text)):
            if ('particulars' in text[i].lower() and 'described' not in text[i].lower()) or 'description' in text[i].lower() or 'quantity' in text[i].lower():
                for j in range(i+1, len(text)):
                    if re.search('.*total.*', text[j].lower()) or re.search('.*totai.*', text[j].lower()):
                        break
                    flag = 0
                    for deb in debarred:
                        if deb in text[j].lower():
                            flag = 1
                            break
                    if flag == 1:
                        continue
                    words = text[j].split()
                    name = ''
                    for k in range(len(words)):
                        if k == 0:
                            if words[k].isnumeric():
                                # flag2 = 1
                                continue
                        if words[k].isnumeric() and len(words[k]) > 3:
                            break
                        else:
                            # if flag2 == 1:
                            if re.search('.*no.*s', text[j].lower()) and 'total' not in text[j].lower():
                                name += words[k] + " "
                            elif self.contains_float(text[j]):
                                name += words[k] + " "
                            
                    if name:
                        item_names.append(name.strip())
        
        # print('ITEM NAMES---> ', item_names)
        item_names = self.clean_item_names(item_names)
        # print('ITEM NAMES---> ', item_names)
        # if not item_names:
        #     item_names = [None]
        return item_names

    def get_quantity(self, text):
        t = ' '.join(text)
        if 'amazon' in t.lower() or 'paytm' in t.lower():
            items = self.get_item_names(text)
            if items is None:
                return [0]
            return [len(items)]
        
        # item_names = get_item_names(text)
        text = self.clean_text(text)
        quantities = []
        q_line = []
        flag = 0

        for i in range(len(text)):
            if 'quantity' in text[i].lower():
                for j in range(i+1, len(text)):
                    if 'total' in text[j].lower() or 'signature valid' in text[j].lower() or 'output cgst' in text[j].lower():
                        flag = 1
                        break
                    if 'services' in text[j].lower() or 'serial' in text[j].lower():
                        continue
                    if 'no. services' in text[j].lower():
                        continue
                    if re.search('.*no.*s.*', text[j].lower()) or re.search('.*no.*', text[j].lower()):
                        # print('TRUUEEE')
                        q_line.append(text[j])
            if flag:
                break
        
        debarred = ['=']

        # print('QUANTITY LINE---> ', q_line)
        for q in q_line:
            words = q.split()
            for i in range(len(words)):
                if re.search('.*no.*s.*', words[i].lower()) or re.search('.*no.*', words[i].lower()):
                    if any(char.isdigit() for char in words[i].lower()) and words[i].lower() not in debarred and words[i][0].isnumeric():
                        quantities.append(words[i])
                    else:
                        if words[i-1].lower() not in debarred:
                            quantities.append(words[i-1])
                    break
        
        # print('QUANTITIES---> ', quantities)
        new_quantities = []
        # flag = 0
        for quan in quantities:
            new_quan = ''
            if 'sno\'s' in quan.lower():
                break
            for ch in quan:
                if ch.isnumeric() or ch == '.':
                    new_quan += ch
                else:
                    flag = 1
                    break
            if (new_quan.isnumeric() or self.contains_float(new_quan)) and len(new_quan) < 8:
                new_quantities.append(new_quan)

        # if not new_quantities:
        #     new_quantities = [None]
        return new_quantities

    def extract_unit(self, text):
        return ['Each']
    
    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def get_line_item_amount(self, text):
        line_item_amounts = []
        flag = 0

        for i in range(len(text)):
            if re.search('.*quantity.*amount.*', text[i].lower()):
                for j in range(i+1, len(text)):
                    if 'igst' in text[j].lower():
                        flag = 1
                        break
                    # print(text[j].split()[-1])
                    # print('CONTAINS FLOAT---> ', isfloat(text[j].split()[-1]))
                    amt = text[j].split()[-1].replace(',', '')
                    # print('AMT---> ', amt)
                    if len(text[j].split()) > 1 and self.isfloat(amt):
                        # print('AMOUNT---> ', text[j].split()[-1])
                        line_item_amounts.append(text[j].split()[-1])
            if flag:
                break
        
        return line_item_amounts


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
                item_names = self.get_item_names(text)
                spent_amounts = self.get_spent_amount(text)
                currency_codes = self.get_currency_code(text)
                quantities = self.get_quantity(text)
                units = self.extract_unit(text)
                spent_dates = self.get_spent_date(text)
                suppliers = self.get_supplier_name(text)
                amt_ = self.get_line_item_amount(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)
                with open(text_file, 'a', encoding='utf-8') as fp:
                    fp.write(str(asset_names)+"\n")
                    fp.write(str(item_names)+"\n")
                    fp.write(str(spent_amounts)+"\n")
                    fp.write(str(currency_codes)+"\n")
                    fp.write(str(quantities)+"\n")
                    fp.write(str(units)+"\n")
                    fp.write(str(spent_dates)+"\n")
                    fp.write(str(suppliers)+"\n")
                    fp.write(str(amt_)+"\n")
                    fp.write("---\n")
        return ensemble_output_files

    def get_result(self):
        obj = DelimiterComakeitSupplier(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        print("OUTPUT FILES --> ", ensemble_output_files)
        result = {}

        for e_file in ensemble_output_files:

            stationary_asset_final = ''
            item_names_final = []
            spent_amount_final = ''
            currency_code_final = ''
            quantities_final = []
            units_final = []
            spent_date_final = ''
            suppliers_final = ''
            amount_final = []

            filename = os.path.split(e_file)[-1].split('.txt')[0]

            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    asset_names = eval(data[0])
                    item_names = eval(data[1])
                    spent_amounts = eval(data[2])
                    currency_codes = eval(data[3])
                    quantities = eval(data[4])
                    units = eval(data[5])
                    spent_dates = eval(data[6])
                    suppliers = eval(data[7])
                    amts = eval(data[8])

                    if asset_names and not stationary_asset_final:
                        stationary_asset_final = asset_names[0]

                    if item_names and not item_names_final:
                        item_names_final = item_names
                    if len(item_names) > len(item_names_final):
                        item_names_final = item_names

                    if spent_amounts and not spent_amount_final:
                        spent_amount_final = spent_amounts[0]

                    if currency_codes and not currency_code_final:
                        currency_code_final = currency_codes[0]

                    if quantities and not quantities_final:
                        quantities_final = quantities
                    if len(quantities) > len(quantities_final):
                        quantities_final = quantities

                    if units and not units_final:
                        units_final = units

                    if spent_dates and not spent_date_final:
                        spent_date_final = spent_dates[0]

                    if suppliers and not suppliers_final:
                        suppliers_final = suppliers[0]

                    if amts and not amount_final:
                        amount_final = amts 
                    
        max_len = max(len(quantities_final), len(item_names_final), len(units_final))
        print("MAXI LEN --> ", max_len)
        if len(quantities_final)<max_len:
            if quantities_final:
                l = max_len - len(quantities_final)
                quantities_final = quantities_final*l
            else:
                quantities_final = [None]*max_len
        if len(item_names_final)<max_len:
            if item_names_final:
                l = max_len - len(item_names_final)
                item_names_final = item_names_final*l
            else:
                item_names_final = [None]*max_len
        if len(amount_final)<max_len:
            amount_final = amount_final + [None]*(max_len-len(amount_final))
        units_final = units_final*max_len
        final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
        with open(final_output_file, 'a') as fp:
            fp.write(str(stationary_asset_final)+"\n")
            fp.write(str(item_names_final)+"\n")
            fp.write(str(spent_amount_final)+"\n")
            fp.write(str(currency_code_final)+"\n")
            fp.write(str(quantities_final)+"\n")
            fp.write(str(units_final)+"\n")
            fp.write(str(spent_date_final)+"\n")
            fp.write(str(suppliers_final)+"\n")
            fp.write(str(amount_final)+"\n")
        result["address"] = None
        result["amount"] = {}
        result["amount"]["amount_paid"] = spent_amount_final
        # result["amount"]["currency_code"] = currency_code_final
        result["amount"]["balance_due"] = None
        result["amount"]["due_date"] = None
        result["amount"]["invoice_total"] = None
        result["firm_name"] = None
        result["supplier_name"] = suppliers_final
        result["invoice_number"] = None
        result["invoice_date"] = spent_date_final
        result["line_items"] = [[]]
        num = 1
        for i, j, k, a in zip(item_names_final, quantities_final, units_final, amount_final):
            r = {"Amount": a,
            "Item_Name" : i,
            "S_No": num,
            'currency_code' : currency_code_final,
            "Quantity": j,
            "Unit_Of_Measure" : k}
            result['line_items'][0].append(r)
            num += 1
        result["phone"] = None

        json_file = os.path.join(self.path_, f"json_output/{filename}.json")
        with open(json_file, 'w') as fp:
            json.dump(result, fp)
        return [result]
