#!/usr/bin/env python
'''
test class ygomi_grabcut
'''

import numpy as np
import cv2
import sys
from GrabCutSegment import GrabCutSegment

print cv2.__version__

imgPath = "./data/lena.jpg"
img = cv2.imread(imgPath)
cv2.imshow('source', img)

maskPath = "./data/src_mask_1.png"
mask = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
print mask.shape
cv2.imshow('mask', mask)

iterCount = 3
polygonAcr = 3
DEBUG_ON = 1
ygomiGrabCut = GrabCutSegment(iterCount, polygonAcr, DEBUG_ON)

# test rect
rect = (38, 27, 402, 500)
rect_or_mask = 1
maxPoly = ygomiGrabCut.grabcut(img, mask, rect, rect_or_mask)

# draw segmented image block
img1 = img.copy()
mask255 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
seg_img = cv2.bitwise_and(img1,img1,mask=mask255)

maxPolyList = []
maxPolyList.append(maxPoly)
poly_img = img.copy()
cv2.drawContours(poly_img, maxPolyList, -1, (0, 0, 255),
                 3, cv2.LINE_AA)

if rect_or_mask == 0:
    cv2.rectangle(img, rect[0:2], (rect[0]+rect[2],rect[1]+rect[3]), [0,0,255], 2)

bar = np.zeros((img.shape[0],5,3),np.uint8)
res = np.hstack((img,bar,seg_img,bar,poly_img))
cv2.imwrite('./grabcut_debug/grabcut_output.png',res)



