#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, json

# Helper class that contains the current configuration of the Gui
# This config is loaded when started and saved when leaving
class Config:
    # Constructor
    def __init__(self):
        self.__defaultSettings()

    def __defaultSettings(self):
        # The filename of the image we currently working on
        self.__lastImageFile = "."
        # The filename of the labels we currently working on
        self.__lastLabelFile = "."
        # The transparency of the labels over the image
        self.__transp = 0.5
        # The zoom factor
        self.__zoomFactor = 2.0

    def setLastImageFile(self, inputStr):
        self.__lastImageFile = str(inputStr)

    def setLastLabelFile(self, inputStr):
        self.__lastLabelFile = str(inputStr)

    def setTransp(self, inputNum):
        self.__transp = inputNum

    def setZoomFactor(self, inputNum):
        self.__zoomFactor = inputNum


    def getLastImageFile(self):
        return self.__lastImageFile

    def getLastLabelFile(self):
        return self.__lastLabelFile

    def getTransp(self):
        return self.__transp

    def getZoomFactor(self):
        return self.__zoomFactor

    # Load from given filename
    def load(self, filename):
        msgTxt = ''

        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as f:
                    jsonText = f.read()
                    jsonDict = json.loads(jsonText)
                    for key in jsonDict:
                        if key in self.__dict__:
                            self.__dict__[key] = jsonDict[key]

                self.__lastImageFile = os.path.normpath(self.__lastImageFile)
                self.__lastLabelFile = os.path.normpath(self.__lastLabelFile)
                msgTxt = 'Load config file succeeded'
            except:
                self.__defaultSettings()
                msgTxt = "Wrong config file, use default settings"
        else:
            # if the config file does not exist, use default settings
            self.__defaultSettings()
            msgTxt = "No config file found, use default settings"

        return msgTxt

    # Save to given filename (using pickle)
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.__dict__, default=lambda o: o.__dict__, sort_keys=True, indent=4))

# main function for unit test
def main():
    cfg = Config()
    cfg.save('configTest.json')
    cfg.load('configTest.json')


if __name__ == '__main__':
    main()