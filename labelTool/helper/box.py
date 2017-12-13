#!/usr/bin/python
#

from PyQt4 import QtGui, QtCore
from collections import namedtuple

class Box:
    Status = namedtuple('Status', ['boxSelection1stPoint', 'boxSelection2ndPoint'])

    def __init__(self):
        '''
        Initialize parameters for box class
        '''
        # setting up flags
        self.__box1stPoint = None
        self.__drawPoly = QtGui.QPolygonF()  # QPolygonF format

        self.__status = self.Status.boxSelection1stPoint

    def clear(self):
        self.__box1stPoint = None
        self.__drawPoly = QtGui.QPolygonF()  # QPolygonF format

        self.__status = self.Status.boxSelection1stPoint

    def setStatus(self, status):
        self.__status = status

    def getStatus(self):
        return self.__status

    def getBox(self):
        return self.__drawPoly

    def setBox1stPoint(self, point):
        self.__drawPoly = QtGui.QPolygonF()  # QPolygonF format
        self.__box1stPoint = point
        self.__status = self.Status.boxSelection2ndPoint

    def setBox2ndPoint(self, point):
        sx = self.__box1stPoint.x()
        sy = self.__box1stPoint.y()
        ex = point.x()
        ey = point.y()

        self.__drawPoly.clear()
        self.__drawPoly.append(QtCore.QPointF(sx, sy))
        self.__drawPoly.append(QtCore.QPointF(sx, ey))
        self.__drawPoly.append(QtCore.QPointF(ex, ey))
        self.__drawPoly.append(QtCore.QPointF(ex, sy))

        return self.__drawPoly