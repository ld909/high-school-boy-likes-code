#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

from helper.config import Config
from helper.annotation import Point, Annotation, CsObject
from helper.labels import name2label, assureSingleInstanceName
from helper.toolBars import *
from helper.paintWidget import paintWidget
from grabCut.GrabCutSegment import GrabCutSegment

from PyQt4 import QtGui, QtCore

class labelTool(QtGui.QMainWindow):
    # Constructor
    def __init__(self):
        # Construct base class
        super(labelTool, self).__init__()

        # Toolbar
        self.toolBars = toolBars(self)
        self.toolBars.prepareToolBar()

        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)

        self.paintArea = paintWidget(self)

        self.scrollArea = QtGui.QScrollArea()
        # self.scrollArea.setVerticalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOn )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAutoFillBackground(True)
        self.scrollArea.setWidget(self.paintArea)

        # Looking for label tool configuration file under the same directory with this file
        configDir = os.path.dirname(__file__)
        self.configFile = os.path.join(configDir, "labelTool.conf")
        self.configObj = Config()
        message = self.configObj.load(self.configFile)
        # self.statusBar().showMessage(message)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.scrollArea)
        centralWidget.setLayout(vbox)

        # Open in full screen
        self.screenShape = QtGui.QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width(), self.screenShape.height())

        self.applicationTitle = 'Label Tool v0.1'
        self.setWindowTitle(self.applicationTitle)

    # Destructor
    def __del__(self):
        self.checkAndSave()
        self.configObj.save(self.configFile)

    # Disable the popup menu on right click
    def createPopupMenu(self):
        pass

def main():
    app = QtGui.QApplication(sys.argv)

    tool = labelTool()
    tool.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
