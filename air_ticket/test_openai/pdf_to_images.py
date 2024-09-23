
import os

path ="C:\\Users\\Lenovo\\Downloads\\NetZero\\NetZero\\Business Travel Emission Management"

#store all the file names in this list
filelist = []

for root, dirs, files in os.walk(path):
	for file in files:
        #append the file name to the list
		filelist.append(os.path.join(root,file))


# print all the file names
for file in filelist:
    filename = os.path.split(file)[-1].split('.pdf')[0]
    if ' ' in filename:
        filename = filename.replace(' ', '_')
    # print(filename)
    pdf_to_images(file, filename)
