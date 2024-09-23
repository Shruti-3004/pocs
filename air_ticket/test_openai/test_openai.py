import cv2
import numpy as np
import os

image = cv2.imread('images\\page0.jpg')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

kernel = np.ones((3,3),np.uint8)
erosion = cv2.erode(thresh,kernel,iterations = 1)
dilation = cv2.dilate(erosion,kernel,iterations = 1)

contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for cnt in contours:
    rect = cv2.minAreaRect(cnt)
    angle = rect[2]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

line_contours = []
for cnt in contours:
    x,y,w,h = cv2.boundingRect(cnt)
    if w > 50 and h > 15:
        line_contours.append(cnt)

cv2.imwrite('preprocessed_image.jpg', rotated)

command = 'tesseract preprocessed_image.jpg stdout -l eng --psm 4'
print(os.popen(command).read())