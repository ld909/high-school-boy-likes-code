
# coding: utf-8

import cv2
import numpy as np
import sys
import os

sys.path.append( os.path.normpath( os.path.join( os.path.dirname( __file__ ) , '..') ) )
from helper.annotation import Point, Annotation, CsObject
from helper.labels import trainId2cslabel

from cityscapes2Ygo import cs2yg


suffix_enabled = ['.png', '.jpg']
mid_name='.psp'

REMOVE_PSP_FILE = 1

def getAnnotation(img):
    ann = Annotation()
    ann.imgHeight, ann.imgWidth = img.shape[:2]

    labels = np.unique(img)
    tempimg = img[:, :, 1]
    objId = 0
    polygons = []  # for test
    for label in labels:
        bImg = np.zeros(tempimg.shape, dtype=np.uint8)
        indices = np.argwhere(tempimg==label)
        bImg[indices[:,0], indices[:,1]]=255
        _,contours,hierarchy = cv2.findContours(bImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #RETR_TREE
        for contour in contours:
            obj = CsObject()
            obj.label = trainId2cslabel[label].name
            obj.id = objId
            pntArr =  cv2.approxPolyDP(contour, 3, 1)
            # print pntArr
            for pl in pntArr:
                for p in pl:
                    obj.polygon.append(Point(np.int(p[0]), np.int(p[1])))
            ann.objects.append(obj)
            objId = objId + 1
    return ann


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileparam = sys.argv[1]
        if os.path.isfile(fileparam):
            img = cv2.imread(fileparam)
            ann = getAnnotation(img)
            jsonfile = os.path.splitext(fileparam)[0] + mid_name + '.json'
            ann.toJsonFile(jsonfile)
            if(REMOVE_PSP_FILE != 1):
                print("saved to psp json: " + jsonfile)
            argstr = [jsonfile, os.path.dirname(jsonfile)]
            cs2yg(argstr)
            if(REMOVE_PSP_FILE == 1):
                os.remove(jsonfile)
        elif os.path.isdir(fileparam):
            for dirpath, dirnames, filenames in os.walk(fileparam):
                for filename in filenames:
                    if os.path.splitext(filename)[1] in suffix_enabled:
                        imagefile = os.path.join(dirpath, filename)
                        print("image file:" + imagefile)
                        img = cv2.imread(imagefile)
                        ann = getAnnotation(img)
                        jsonname = os.path.splitext(filename)[0] + mid_name + '.json'
                        jsonfile = os.path.join(dirpath, jsonname)
                        ann.toJsonFile(jsonfile)
                        if (REMOVE_PSP_FILE != 1):
                            print("saved to psp json: " + jsonfile)
                        argstr = [jsonfile, dirpath]
                        cs2yg(argstr)
                        if (REMOVE_PSP_FILE == 1):
                            os.remove(jsonfile)
        else:
            print('Oops!')
    else:
        print('Input a folder or an image!')
