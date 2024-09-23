
import json

class EmiratesIDCard(GoogleApiEngine):
    

    def __init__(self: object, image_file):
        '''
        Constructs all the necessary attributes for emirates ID card object
       
        Parameters
        -----------
            img_obj (ImageProcessing) :: ImageProcessing object to access its attributes 

        Attributes
        -----------
            image_info (dict) :: Stores image_info attribute of ImageProcessing object to extend it with Emirates ID Card Attributes 
            
            doctexts (text object) :: Stores text of all pages
        '''
        self.image_file = image_file

    def get_name(self: object) -> str:

        self.blocks = []
        self.words = []
        # check if it is the front page
        # TODO if face annotation is true, the side of the aadhaar card is front

        # looping through each page in the document
        for i, page in enumerate(self.doctexts[:]):

            # looping through each block on the page
            for j, block in enumerate(page.blocks[:]):

                # looping through each paragraph in the block
                for k, paragraph in enumerate(block.paragraphs):

                    # looping through each word in the paragraph
                    for a, word in enumerate(paragraph.words):

                        # concatenating symbols to store the word in variable word_text
                        word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                    ])

                        self.blocks.append((j, word_text, word.confidence))
                        self.words.append(word_text)
                        # print(j, word_text, word.confidence)
        
        print(self.words)

        try:
            name = ""
            flag = 0

            for i in range(len(self.blocks)):
                if self.blocks[i][1].lower() == "name":
                    flag = 1
                    # name is present after the key 'Name' and continues upto the word 'nationality'
                    for j in range(i+1, len(self.blocks)):
                        if self.blocks[j][1].lower() == "nationality":
                            break
                        # since the card has some arabic text, encode() is used to encode the string to UTF-8
                        elif self.blocks[j][1].encode().isalpha():
                            name += self.blocks[j][1] + " "  
                if flag == 1:
                    break

            self.image_info['text']['name'] = name.strip
            self.name = name.strip()
            return name.strip()

        except Exception as e:
            print(e)
            self.name = None
            return ("Name not found")

    
    def get_card_number(self: object) -> str:

        self.blocks = []
        # check if it is the front page
        # TODO if face annotation is true, the side of the aadhaar card is front

        # looping through each page in the document
        for i, page in enumerate(self.doctexts[:]):

            # looping through each block on the page
            for j, block in enumerate(page.blocks[:]):

                # looping through each paragraph in the block
                for k, paragraph in enumerate(block.paragraphs):

                    # looping through each word in the paragraph
                    for a, word in enumerate(paragraph.words):

                        # concatenating symbols to store the word in variable word_text
                        word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                    ])

                        self.blocks.append((j, word_text, word.confidence))

        try:
            id_number = ""
            flag = 0

            for i in range(len(self.blocks)):
                # id number is present after the key "idnumber"
                if (self.blocks[i][1]+self.blocks[i+1][1]).lower() == "idnumber":
                    flag = 1
                    # if string obtained after 'idnumber' is numeric, it is the id number
                    for j in range(i+1, len(self.blocks)):
                        if self.blocks[j][1][0].isnumeric():
                            id_number = self.blocks[j][1]
                # break the outer loop once the id number is fetched
                if flag == 1:
                    break

            self.image_info['text']['card_number'] = id_number
            self.card_number = id_number
            return id_number

        except Exception as e:
            print(e)
            self.id_number = None
            return ("ID number not found")

    def get_nationality(self: object) -> str:

        self.blocks = []
        # check if it is the front page
        # TODO if face annotation is true, the side of the aadhaar card is front

        # looping through each page in the document
        for i, page in enumerate(self.doctexts[:]):

            # looping through each block on the page
            for j, block in enumerate(page.blocks[:]):

                # looping through each paragraph in the block
                for k, paragraph in enumerate(block.paragraphs):

                    # looping through each word in the paragraph
                    for a, word in enumerate(paragraph.words):

                        # concatenating symbols to store the word in variable word_text
                        word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                    ])

                        self.blocks.append((j, word_text, word.confidence))

        try:
            nationality = ""
            flag = 0

            for i in range(len(self.blocks)):
                # nationality is present after the key 'nationality'
                if self.blocks[i][1].lower() == "nationality":
                    flag = 1

                    for j in range(i+2, len(self.blocks)):
                        # since the card has some arabic text,
                        # encode() is used to encode the string to UTF-8

                        # break the loop after any non alphabetic string is fetched
                        # else before it, the strings are a part of nationality
                        if not self.blocks[j][1].encode().isalpha():
                            break
                        nationality += self.blocks[j][1] + " "

                if flag == 1:
                    break

            self.image_info['text']['nationality'] = nationality.strip()
            self.nationality = nationality.strip()
            return nationality.strip()

        except Exception as e:
            print(e)
            self.nationality = None
            return ("Nationality not found")

    def is_arabic(self, word):
        regex = r"[\u0600-\u06FF]+"
        if re.findall(regex, word):
            return True
        return False

    def get_ar_name(self: object) -> str:

        self.blocks = []
        # check if it is the front page
        # TODO if face annotation is true, the side of the aadhaar card is front

        # looping through each page in the document
        for i, page in enumerate(self.doctexts[:]):

            # looping through each block on the page
            for j, block in enumerate(page.blocks[:]):

                # looping through each paragraph in the block
                for k, paragraph in enumerate(block.paragraphs):

                    # looping through each word in the paragraph
                    for a, word in enumerate(paragraph.words):

                        # concatenating symbols to store the word in variable word_text
                        word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                    ])

                        self.blocks.append((j, word_text, word.confidence))

        try:
            self.ar_name = ""
            flag = 0

            for i in range(len(self.blocks)):
                if self.blocks[i][1][0].isnumeric():
                    for j in range(i+3, len(self.blocks)):
                        if self.is_arabic(self.blocks[j][1]):
                            self.ar_name += self.blocks[j][1]+" "
                        if 'name' in self.blocks[j][1].lower():
                            flag = 1
                            break
                if flag:
                    break

            self.image_info['text']['ar_name'] = self.ar_name.strip()
            self.ar_name = self.ar_name.strip()
            return self.ar_name.strip()

        except Exception as e:
            print(e)
            self.ar_name = None
            return ("Name not found")

    def get_ar_nationality(self):

        self.blocks = []
        # check if it is the front page
        # TODO if face annotation is true, the side of the aadhaar card is front

        # looping through each page in the document
        for i, page in enumerate(self.doctexts[:]):

            # looping through each block on the page
            for j, block in enumerate(page.blocks[:]):

                # looping through each paragraph in the block
                for k, paragraph in enumerate(block.paragraphs):

                    # looping through each word in the paragraph
                    for a, word in enumerate(paragraph.words):

                        # concatenating symbols to store the word in variable word_text
                        word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                    ])

                        self.blocks.append((j, word_text, word.confidence))

        try:
            name = self.get_name()
            name = name.split()[-1]
            self.ar_nationality = ""
            flag = 0

            for i in range(len(self.blocks)):
                if name in self.blocks[i][1]:
                    for j in range(i+3, len(self.blocks)):
                        if 'nationality' in self.blocks[j][1].lower():
                            flag = 1
                            break
                        self.ar_nationality += self.blocks[j][1]
                if flag:
                    break

            self.image_info['text']['ar_nationality'] = self.ar_nationality.strip()
            self.ar_nationality = self.ar_nationality.strip()
            return self.ar_nationality.strip()

        except Exception as e:
            print(e)
            self.ar_nationality = None
            return ("Nationality not found")

    def get_all(self):
        self.doctexts = self.run(self.image_file)
        fp = open('keys.json', encoding='utf-8')
        keys = json.load(fp)
        self.all = {
            "English": {
                "Name": self.get_name(),
                "card_Number": self.get_card_number(),
                "Nationality": self.get_nationality()
            },
            "Arabic":{
                keys["Name"][0]: self.get_ar_name(),
                keys["ID Number"][0]: self.get_card_number(),
                keys["Nationality"][0]: self.get_ar_nationality()
            }
        }
        return self.all
