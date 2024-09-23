import re
from dateutil import parser
import datetime
import os
from delimiter_netlink_supplier import DelimiterNetlinkSupplier

class NetlinkSupplier:
    def __init__(self, images):
        self.process_images = images
        self.path_ = 'modules/documents/supplier'

    def extract_supplier_name(self, text):
        supplier_name = ''
        for line in text:
            if 'limited' in line.lower():
                ind = line.lower().split().index('limited')
                supplier_name = ' '.join(line.split()[:ind+1])
                return supplier_name
            elif 'services' in line.lower():
                ind = line.lower().split().index('services')
                supplier_name = ' '.join(line.split()[:ind+1])
                return supplier_name
            elif 'ltd,' in line.lower():
                ind = line.lower().split().index('ltd,')
                supplier_name = ' '.join(line.split()[1:ind+1]).strip(',')
                return supplier_name

    def extract_item_name(self, text):
        item_name = ''
        for i in range(len(text)):
            if 'description' in text[i].lower():
                for j in range(i+1, len(text)):
                    if 'no.' in text[j].lower() or 'rate' in text[j].lower() or ('no' in text[j].lower() and len(text[j].split()) == 1):
                        continue
                    # print('text[j]---> ', text[j])
                    if '|' not in text[j].lower():
                        if 'laptop' in text[j].lower():
                            ind = text[j].lower().split().index('laptop')
                            item_name = ' '.join(text[j].split()[:ind+1])
                            # return item_name
                            # break
                    else:
                        item_name = text[j].split('|')[1]

                    if ':' in item_name:
                        ind = item_name.index(':')
                        item_name = item_name[:ind]

                    return item_name.strip()

    def extract_spent_amount(self, text):
        amount = ''
        for line in text:
            if 'total' in line.lower():
                amount = line.split()[-1]
                if '[' not in amount:
                    return amount.strip()

    def extract_quantity(self, text):
        quantity = ''
        flag = 0
        item_name = self.extract_item_name(text)
        for i in range(len(text)-1):
            if 'quantity' in text[i].lower():
                cols = text[i].split('|')
                # print(cols)
                for j in range(i+1, len(text)):
                    if item_name in text[j]:
                        words = text[j].lower().split('|')
                        words = [word.strip() for word in words]
                        # print(words)
                        if len(words) == len(cols) and 'rate' not in words:
                            # print(words)
                            flag = 1
                            quantity = words[3]
                            quantity = re.findall(r'\d+', quantity)[0]
                            return quantity
                        else:
                            break
            if flag == 0:
                if 'total' in text[i].lower():
                    words = text[i].split()
                    for word in words:
                        if word.isnumeric():
                            quantity = word
                            return quantity

    def extract_unit(self):
        return 'Each'

    def extract_spent_date(self, text):
        date = ''
        supplier_name = self.extract_supplier_name(text)
        for i in range(len(text)):
            if supplier_name in text[i]:
                words = text[i+1].split()
                if '-' in words[-1]:
                    date = words[-1]
                    formats = ['%d-%b-%Y', '%d-%b-%y']
                    for format in formats:
                        try:
                            date = datetime.datetime.strptime(date, format).strftime('%Y-%m-%d')
                        except:
                            pass
                    break
                else:
                    date = words[-2]+words[-1]
                    date = date[:2]+' '+date[2:-4]+' '+date[-4:]
                    date = datetime.datetime.strptime(date, '%d %B %Y').strftime('%Y-%m-%d')
                    break
        return date

    def extract_currency_code(self):
        return 'INR'

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

                supplier_name = self.extract_supplier_name(text)
                # print(supplier_name)
                item_name = self.extract_item_name(text)
                # print(item_name)
                spent_amount = self.extract_spent_amount(text)
                # print(spent_amount)
                quantity = self.extract_quantity(text)
                # print(quantity)
                unit_of_measure = self.extract_unit()
                # print(unit_of_measure)
                spent_date = self.extract_spent_date(text)
                # print(spent_date)
                currency_code = self.extract_currency_code(text)

                text_file = os.path.join(self.path_, 'ensemble_output/{}.txt'.format(filename))
                if text_file not in ensemble_output_files:
                    ensemble_output_files.append(text_file)

                with open(text_file, 'a', encoding='utf-8'):
                    if not item_name:
                        item_name = 'None'
                    fp.write(item_name+"\n")
                    if not spent_amount:
                        spent_amount = 'None'
                    fp.write(spent_amount+"\n")
                    if not quantity:
                        quantity = 'None'
                    fp.write(quantity+"\n")
                    fp.write(unit_of_measure+"\n")
                    fp.write(spent_date+"\n")
                    if not supplier_name:
                        supplier_name = 'None'
                    fp.write(supplier_name+"\n")
                    fp.write(currency_code+"\n")
                    fp.write('')
                    fp.write(str(filename)+"\n")

        return ensemble_output_files

    def get_result(self):
        obj = DelimiterNetlinkSupplier(self.path_, self.process_images)
        text_output = obj.add_delimiters_images()
        ensemble_output_files = self.ensemble_output_files(text_output)
        all_pages = []
        print("OUTPUT FILES --> ", ensemble_output_files)
        for e_file in ensemble_output_files:
            result = {}

            item_name_f = ''
            spent_amount_f = ''
            quantity_f = ''
            unit_of_measure_f = ''
            spent_date_f = ''
            supplier_name_f = ''
            currency_code_f = ''

            item_name_flag = 0
            spent_amount_flag = 0
            quantity_flag = 0
            unit_of_measure_flag = 0
            spent_date_flag = 0
            supplier_name_flag = 0
            currency_code_flag = 0

            filename = os.path.split(e_file)[-1].split('.txt')[0]
            with open(e_file) as fp:
                outputs = fp.read().split("---\n")[:-1]
                for out in outputs:
                    data = out.splitlines()
                    item_name = data[0]
                    spent_amount = data[1]
                    quantity = data[2]
                    unit_of_measure = data[3]
                    spent_date = data[4]
                    supplier_name = data[5]
                    currency_code = data[6]

                    if item_name_flag == 0 and item_name != '':
                        item_name_flag = 1
                        fp.write(item_name+"\n")
                    if spent_amount_flag == 0 and spent_amount != '':
                        spent_amount_flag = 1
                        fp.write(spent_amount+"\n")
                    if quantity_flag == 0 and quantity != '':
                        quantity_flag = 1
                        fp.write(quantity+"\n")
                    if unit_of_measure_flag == 0 and unit_of_measure != '':
                        unit_of_measure_flag = 1
                        fp.write(unit_of_measure+"\n")
                    if spent_date_flag == 0 and spent_date != '':
                        spent_date_flag = 1
                        fp.write(spent_date+"\n")
                    if supplier_name_flag == 0 and supplier_name != '':
                        supplier_name_flag = 1
                        fp.write(supplier_name+"\n")
                    if currency_code_flag == 0 and currency_code != '':
                        currency_code_flag = 1
                        fp.write(currency_code+"\n")

            final_output_file = os.path.join(self.path_, 'final_ensemble_output/{}.txt'.format(filename))
            with open(final_output_file, 'a') as fp:
                item_name_f = item_name
                fp.write(str(item_name_f)+"\n")
                spent_amount_f = spent_amount
                fp.write(str(spent_amount_f)+"\n")
                quantity_f = quantity
                fp.write(str(quantity_f)+"\n")
                unit_of_measure_f = unit_of_measure
                fp.write(str(unit_of_measure_f)+"\n")
                spent_date_f = spent_date
                fp.write(str(spent_date_f)+"\n")
                supplier_name_f = supplier_name
                fp.write(str(supplier_name_f)+"\n")
                currency_code_f = currency_code
                fp.write(str(currency_code_f)+"\n")
                fp.write(str([filename])+"\n")
        
        result["address"] = None
        result["amount"] = {}
        result["amount"]["amount_paid"] = spent_amount_f
        result["amount"]["currency_code"] = currency_code_f
        result["amount"]["balance_due"] = None
        result["amount"]["due_date"] = None
        result["amount"]["invoice_total"] = None
        result["firm_name"] = None
        result["supplier_name"] = supplier_name_f
        result["invoice_number"] = None
        result["invoice_date"] = spent_date_f
        result["line_items"] = [[{}]]
        result["line_items"][0][0]["amount"] = None
        result["line_items"][0][0]["item_name"] = item_name_f
        result["line_items"][0][0]["s_no"] = 1
        result["line_items"][0][0]["quantity"] = quantity_f
        result["line_items"][0][0]["unit_of_measure"] = unit_of_measure_f
        result["phone"] = None

        return [result]