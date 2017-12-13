#!/usr/bin/env python
'''
===============================================================================
Interactive Image Segmentation using GrabCut algorithm.
===============================================================================
'''

import numpy as np
import cv2
import sys
import os

from PyQt4 import QtGui, QtCore

from collections import namedtuple

class GrabCutSegment:
    Status = namedtuple('Status', ['boxSelection1stPoint', 'boxSelection2ndPoint', 'scribble'])

    def __init__(self, iterCount = 3, polygonAcr = 3, DEBUG_ON = 0):
        '''
        Initialize parameters for grab cut segmentation algorithm
        @Param: iterCount  : iteration number of calling grab cut once
        @Param: polygonAcr : influence the total number of generated polygon vertex
        @Param: DEBUG_ON   : debug flage: 0 - OFF, 1 - ON
        '''
        # setting up flags
        self.__iterCount = iterCount        # iteration number of calling grab cut once
        self.__polygonAcr = polygonAcr      # influence the total number of generated polygon vertex
        self.__DEBUG_ON = DEBUG_ON          # debug flage: 0 - OFF, 1 - ON
        self.__debugDir = './grabcut_debug/'

        self.__npImage = np.zeros(0)    # input image in NumPy format
        self.__box1stPoint = None
        self.__rectRoi = [0, 0, 0, 0]
        self.__npMaskImage = np.zeros(0)    # inut mask image in NumPy format
        self.__prevMaskImg = np.zeros(0)
        self.__drawPoly = QtGui.QPolygonF()  # QPolygonF format

        self.__scribbleFrontObjectFlag = False
        self.__scribbleBackGroundFlag = False
        self.__strongFrontObjectLabel = []
        self.__strongBackGroundLabel = []

        # configurations
        self.__marginBoxFromPolygon = 20 # pixel
        self.__scribbleWidth = 5

        self.__status = self.Status.boxSelection1stPoint

        # if debug tag is ON, check the debug directory
        if (DEBUG_ON == 1) & (os.path.exists(self.__debugDir) == False):
            os.makedirs(self.__debugDir)

    def clear(self):
        self.__npImage = np.zeros(0)  # input image in NumPy format
        self.__box1stPoint = None
        self.__rectRoi = [0, 0, 0, 0]
        self.__npMaskImage = np.zeros(0)  # inut mask image in NumPy format
        self.__prevMaskImg = np.zeros(0)
        self.__drawPoly = QtGui.QPolygonF()  # QPolygonF format

        self.__scribbleFrontObjectFlag = False
        self.__scribbleBackGroundFlag = False
        self.__strongFrontObjectLabel = []
        self.__strongBackGroundLabel = []

        self.__status = self.Status.boxSelection1stPoint

    def setImage(self, inputQtImage):
        self.__npImage = self.convertQImageToMat(inputQtImage)

    def setRectRoi1stPoint(self, point):
        self.__box1stPoint = point
        self.__status = self.Status.boxSelection2ndPoint

    def getBox1stPoint(self):
        return (self.__rectRoi[0], self.__rectRoi[1])

    def setScribbleFrontGroundFlag(self):
        self.__scribbleFrontObjectFlag = True
        self.__scribbleBackGroundFlag = False

    def setScribbleBackGroundFlag(self):
        self.__scribbleFrontObjectFlag = False
        self.__scribbleBackGroundFlag = True

    def isFrontGroundLabeling(self):
        return self.__scribbleFrontObjectFlag

    def isBackGroundLabeling(self):
        return self.__scribbleBackGroundFlag

    def expandPoint(self, px, py):
        xList = []
        yList = []

        halfWidth = (self.__scribbleWidth - 1) / 2

        for xoff in range(-halfWidth, halfWidth):
            for yoff in range(-halfWidth, halfWidth):
                xList.append(px + xoff)
                yList.append(py + yoff)

        return xList, yList

    def addStrongFrontGround(self, mousePos):
        px = int(mousePos.x() - self.__rectRoi[0])
        py = int(mousePos.y() - self.__rectRoi[1])

        xList, yList = self.expandPoint(px, py)

        for (x, y) in zip(xList, yList):
            if 0 <= x < self.__rectRoi[2] and 0 <= y < self.__rectRoi[3]:
                self.__strongFrontObjectLabel.append([y, x])

    def addStrongBackGround(self, mousePos):
        px = int(mousePos.x() - self.__rectRoi[0])
        py = int(mousePos.y() - self.__rectRoi[1])

        xList, yList = self.expandPoint(px, py)

        for (x, y) in zip(xList, yList):
            if 0 <= x < self.__rectRoi[2] and 0 <= y < self.__rectRoi[3]:
                self.__strongBackGroundLabel.append([y, x])

    def getStrongFrontGround(self):
        return self.convertPointListToQPolygonF(self.__strongFrontObjectLabel)

    def getStrongBackGround(self):
        return self.convertPointListToQPolygonF(self.__strongBackGroundLabel)

    def setRectRoi2ndPoint(self, point):
        sx = self.__box1stPoint.x()
        sy = self.__box1stPoint.y()
        ex = point.x()
        ey = point.y()

        self.__rectRoi = (int(min(sx, ex)), int(min(sy, ey)), int(abs(sx - ex)), int(abs(sy - ey)))

    def getBox(self):
        return self.__rectRoi

    def setStatus(self, inputStatus):
        self.__status = inputStatus

    def getStatus(self):
        return self.__status

    def maskGenFromPolygon(self, rectRoi, qtPolygon):
        maskSizeX = int(rectRoi[3])
        maskSizeY = int(rectRoi[2])

        mask = np.zeros((maskSizeX, maskSizeY), np.uint8)

        # Generate mask map using input polygon
        # todo replace for loop by built in methods to optimizing
        for idxY in range(0, maskSizeY):
            for idxX in range(0, maskSizeX):
                ptIdx = QtCore.QPoint(idxX + int(rectRoi[0]), idxY + int(rectRoi[1]))

                if qtPolygon.containsPoint(ptIdx, QtCore.Qt.OddEvenFill):
                    mask[idxX, idxY] = 3  # probable foreground
                else:
                    mask[idxX, idxY] = 2  # probable background

        return mask

    def extendRectRoi(self, qtRect, imgWidth, imgHeight):
        rect = qtRect.getRect()

        qtRect.setX( int(max(rect[0] - self.__marginBoxFromPolygon, 0)))
        qtRect.setY( int(max(rect[1] - self.__marginBoxFromPolygon, 0)))

        boxWidth = rect[2] + 2*self.__marginBoxFromPolygon
        qtRect.setWidth( int(min(boxWidth, imgWidth-rect[0])))

        boxHeight = rect[3] + 2*self.__marginBoxFromPolygon
        qtRect.setHeight( int(min(boxHeight, imgHeight-rect[1])))

        return qtRect

    def setRectRoiByPolygon(self, qtImage, qtPolygon):
        qtRect = qtPolygon.boundingRect()

        extQtRect = self.extendRectRoi(qtRect, qtImage.rect().right(), qtImage.rect().bottom())

        self.__rectRoi = extQtRect.getRect()

        self.setImage(qtImage)
        self.cutImageByRectRoi()

        self.__box1stPoint = QtCore.QPointF(self.__rectRoi[0], self.__rectRoi[1])

        self.__prevMaskImg = self.maskGenFromPolygon(self.__rectRoi, qtPolygon)
        self.__npMaskImage = self.__prevMaskImg

        self.__drawPoly = qtPolygon

        self.__scribbleFrontObjectFlag = False
        self.__scribbleBackGroundFlag = False
        self.__strongFrontObjectLabel = []
        self.__strongBackGroundLabel = []

        # ROI box has been selected by bounding box of polygon,
        # so jump to scribbel mode directly
        self.__status = self.Status.scribble

    def finishBoxSelection(self):
        # run box method first
        self.__drawPoly = self.run()
        self.__status = self.Status.scribble

        return self.__drawPoly

    def finishScribbling(self):
        self.__scribbleFrontObjectFlag = False
        self.__scribbleBackGroundFlag = False

        if (self.__strongBackGroundLabel != []) or (self.__strongFrontObjectLabel) != []:
            self.updateMask()
            self.__drawPoly = self.run()

            # clear scribbles
            self.__strongBackGroundLabel = []
            self.__strongFrontObjectLabel = []

        return self.__drawPoly

    def updateMask(self):

        self.__npMaskImage = self.__prevMaskImg

        if (self.__strongBackGroundLabel != []):
            backGroundLabel = np.array(self.__strongBackGroundLabel)
            self.__npMaskImage[backGroundLabel[:,0], backGroundLabel[:,1]] = 0
        if (self.__strongFrontObjectLabel != []):
            frontObjectLabel = np.array(self.__strongFrontObjectLabel)
            self.__npMaskImage[frontObjectLabel[:,0], frontObjectLabel[:,1]] = 1

    def run(self):
        if self.__status == self.Status.boxSelection2ndPoint:
            rect_or_mask = 0 # rect
        elif self.__status == self.Status.scribble:
            rect_or_mask = 1  # mask
        else:
            # error status for running.  Return what we have
            return self.__drawPoly

        # cv2.imshow('image',self.__npImage)
        # cv2.waitKey(0)

        status, self.__npMaskImage = self.grabcut(self.__npImage, self.__npMaskImage, self.__rectRoi, rect_or_mask)

        # get the max polygon from segmented mask
        if not status:
            # input wrong segmentation parameters
            maxPoly = np.array([-1, -1])
        else:
            # get the max polygon from segmented mask
            maxPoly = self.maskToPolygon(self.__npMaskImage)

        self.__drawPoly = self.convertNumPyToQPolygonF(maxPoly)

        # Post processing
        if self.__status == self.Status.boxSelection2ndPoint:
            # Prepare small images for next scribble fine tune
            self.cutImageByRectRoi()
            self.cutMaskImageByRectRoi()

        self.__prevMaskImg = self.__npMaskImage

        return self.__drawPoly

    def cutImageByRectRoi(self):
        p0x = self.__rectRoi[0]
        p0y = self.__rectRoi[1]
        p1x = p0x + self.__rectRoi[2]
        p1y = p0y + self.__rectRoi[3]
        self.__npImage = self.__npImage[p0y:p1y, p0x:p1x, :]

    def cutMaskImageByRectRoi(self):
        p0x = self.__rectRoi[0]
        p0y = self.__rectRoi[1]
        p1x = p0x + self.__rectRoi[2]
        p1y = p0y + self.__rectRoi[3]
        self.__npMaskImage = self.__npMaskImage[p0y:p1y, p0x:p1x]

    def grabcut(self, image, mask, rect, rect_or_mask):
        '''
        Do grab cut segmentation algorithm
        @Param: image: np.array, CV_8UC3, shape = (img_h, img_w, 3)
        @Param: mask : np.array, CV_8UC1, shape = (img_h, img_w, 1)
            Key '0' - To select areas of sure background
            Key '1' - To select areas of sure foreground
            Key '2' - To select areas of probable background
            Key '3' - To select areas of probable foreground
        @Param: rect : tuple, rect = (tl_x, tl_y, rect_w, rect_h)
        @Param: rect_or_mask: rect or mask mode: 0 - rect, 1 - mask
        @return: maxPoly: np.array, shape = (vertex_pts_num, 1, 2)
        '''
        ret = True

        # grab cut algrithm
        # step1: define background and foreground model
        img2 = image.copy()
        bgdmodel = np.zeros((1, 65), np.float64)
        fgdmodel = np.zeros((1, 65), np.float64)

        # step2: save src mask image to disk to debug
        if self.__DEBUG_ON == 1:
            mask1 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
            cv2.imwrite(self.__debugDir+'src_mask_255.png', mask1)

        # step3: do segmentation algorithm: 0 - rect, 1 - mask
        if rect_or_mask == 0:
            print "Do segmentation based on input Rect."
            # tranfer upleft and right down vertex
            h, w = image.shape[:2]

            # sx = max(rect[0], 0)
            # sy = max(rect[1], 0)
            # ex = min(rect[0] + rect[2], w-1)
            # ey = min(rect[1] + rect[3], h-1)
            # if Rect is valid
            if 1: #(0<=sx<w) & (0<=ex<w) & (0<=sy<h) & (0<=ey<h):
                # do grab cut based on rect
                #rect = (sx, sy, ex - sx, ey - sy)
                mask = np.zeros(img2.shape[:2], dtype=np.uint8)
                cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, self.__iterCount, cv2.GC_INIT_WITH_RECT)
            else:
                print "Wrong input Rect.Pls Check it!"
                ret = False
        elif rect_or_mask == 1:
            print "Do segmentation based on mask."
            if image.shape[:2] != mask.shape[:2]:
                print "mask size doesn't match with image size. Pls check it!"
                ret = False
            else:
                # do grab cut based on mask
                rect = (0, 0, -1, -1)
                cv2.grabCut(img2, mask, rect, bgdmodel, fgdmodel, self.__iterCount, cv2.GC_INIT_WITH_MASK)
        else:
            print "Wrong input rect_or_mask method!"
            ret = False

        # step4: save segmentation images to disk to debug
        if (ret == True) & (self.__DEBUG_ON == 1):
            mask255 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
            cv2.imwrite(self.__debugDir+'seg_mask_255.png', mask255)

        return ret, mask

    def maskToPolygon(self,mask):
        ''' find the max polygon in mask '''
        if 0: #DEBUG_DISPLAY_ON == 1:
            mask[150, 400] = 1

        mask255 = np.where((mask == 1) + (mask == 3), 255, 0).astype('uint8')
        _, contours0, hierarchy = cv2.findContours(mask255.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        maxArea = 0
        maxContour = contours0[0]
        for contour in contours0:
            area = cv2.contourArea(contour)
            if area > maxArea:
                maxArea = area
                maxContour = contour
        if maxArea > 0:
            maxPoly = cv2.approxPolyDP(maxContour, self.__polygonAcr, True)
        else:
            print "found wrong contours!"

        if self.__status == self.Status.scribble:
            # Change the offset of polygon
            for pt in maxPoly:
                pt[0][0] = pt[0][0] + self.__rectRoi[0]
                pt[0][1] = pt[0][1] + self.__rectRoi[1]

        # draw all contours, not only the max area contour
        if self.__DEBUG_ON == 1:
            contours = [cv2.approxPolyDP(cnt, self.__polygonAcr, True) for cnt in contours0]
            print "contours total number:%s" % len(contours)
            # print contours

            # draw all contours in yellow color
            h, w = self.__npImage.shape[:2]
            vis = np.zeros((h, w, 3), np.uint8)
            im = vis.astype(np.uint8).copy()

            cv2.drawContours(im, contours, -1, (128, 255, 255),
                             3, cv2.LINE_AA)

            # draw the final max area contour in red color
            maxPolyList = []
            maxPolyList.append(maxPoly)
            # if contours(ndarray) are in list, draw connect edges
            # if ndarray, only draw discrete polygon vertex
            cv2.drawContours(im, maxPolyList, -1, (0, 0, 255),
                             3, cv2.LINE_AA)
            cv2.imshow('polygon', im)
            cv2.imwrite(self.__debugDir+'polygon.png', im)

            # TODO: transfer ndarray type to list

        # return the max polygon to outside
        return maxPoly

    def convertQImageToMat(self, incomingImage):
        '''  Converts a QImage into an opencv MAT format  '''

        if incomingImage.format() != 4:
            incomingImage = incomingImage.convertToFormat(4)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        arr = arr[:,:,:3] # discard alpha value
        return arr

    def convertNumPyToQPolygonF(self, inNumpyArr):
        poly = QtGui.QPolygonF()

        for npPoint in inNumpyArr:
            pt = QtCore.QPointF(npPoint[0][0], npPoint[0][1])
            poly.append(pt)

        return poly

    def convertPointListToQPolygonF(self, inPointArr):
        poly = QtGui.QPolygonF()

        for point in inPointArr:
            x = point[1]+self.__rectRoi[0]
            y = point[0]+self.__rectRoi[1]
            pt = QtCore.QPointF(x, y)
            poly.append(pt)

        return poly