#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, glob
from PyQt4 import QtGui, QtCore
from collections import namedtuple
from labels import name2label

State = namedtuple('State', ['view', 'add', 'edit'])

Tool  = namedtuple('Tool', ['none', 'addEditBox', 'addEditPolyPoints', 'addEditGrabcut', 'delPoly'])

IconCfg = namedtuple('IconCfg', ['name', 'hotkey', 'callback', 'iconImage', 'tips', 'activeFlag'])

class toolBars(QtGui.QToolBar):
    def __init__(self, parent):
        super(toolBars, self).__init__()

        self.parent = parent

        self.toolBarObj = None
        self.addBarObj  = None
        self.editBarObj = None

        self.state = State.view
        self.currTool = Tool.none

        self.zoomFlag = False
        self.zoomSize = 800 # pixel

    # Create toolbar with actions specified in iconConfig
    def createToolBar(self, toolbarName, position, iconConfig):
        toolbarObj = QtGui.QToolBar(toolbarName)
        self.parent.addToolBar(position, toolbarObj)
        iconDir = os.path.join(os.path.dirname(__file__), '../icons')

        for icon in iconConfig:
            iconText = '&{}'.format(icon.name)
            newAction = QtGui.QAction(QtGui.QIcon(os.path.join(iconDir, icon.iconImage)), iconText, self.parent)
            newAction.setShortcuts(icon.hotkey)
            self.setTip(newAction, icon.tips)
            newAction.triggered.connect(icon.callback)
            toolbarObj.addAction(newAction)
            newAction.setEnabled(icon.activeFlag)

        return toolbarObj

    def updateToolbarVisibility(self):
        if self.state == State.view:
            self.addBarObj.hide()
            self.editBarObj.hide()

            for act in self.addBarObj.actions():
                act.setEnabled(False)
            for act in self.editBarObj.actions():
                act.setEnabled(False)

        elif self.state == State.add:
            self.addBarObj.show()
            self.editBarObj.hide()

            for act in self.addBarObj.actions():
                act.setEnabled(True)
            for act in self.editBarObj.actions():
                act.setEnabled(False)

        elif self.state == State.edit:
            self.addBarObj.hide()
            self.editBarObj.show()

            for act in self.addBarObj.actions():
                act.setEnabled(False)
            for act in self.editBarObj.actions():
                act.setEnabled(True)

    def prepareToolBar(self):
        toolBarCfg = [
            #       'name',         'hotkey',   'callback',         'iconImage',        'tips',             'activeFlag'
            IconCfg('OpenFile', 'o', self.selectFiles, 'open.png', 'Open file', True),
            IconCfg('PrevFile', ['left'], self.prevImage, 'back.png', 'Previous image', False),
            IconCfg('NextFile', ['right'], self.nextImage, 'next.png', 'Next image', False),
            IconCfg('NewLabel', 'n', self.addLabel, 'newobject.png', 'New label', False),
            IconCfg('EditLable', 'e', self.editLabel, 'edit.png', 'Edit label', False),
            IconCfg('Minus', '-', self.minusAct, 'minus.png', 'Increase transparency', False),
            IconCfg('Plus', '=', self.plusAct, 'plus.png', 'Decrease transparency', False),
            IconCfg('Zoom', 'z', self.toggleZoomButton, 'zoom.png', 'Zoom in', False),
        ]

        addBarCfg = [
            #       'name',         'hotkey',   'callback',         'iconImage',        'tips',             'activeFlag'
            IconCfg('Box', 'b',     self.addObjByBox,     'newboxobject.png', 'Add object by box', False),
            IconCfg('Polygon', 'p', self.addObjByPolygon, 'newobject.png', 'Add object by polygon', False),
            IconCfg('Grabcut', 'g', self.addObjByGrabCut, 'grabcut.png', 'Add object by grabcut', False),
            IconCfg('ClearPolygon', ['q', 'Esc'], self.clearPolygonAct, 'clearpolygon.png', 'Clear working polygon',
                    False),
            IconCfg('SaveAddedObj', 's', self.saveNewObject, 'save.png', 'Save new object', False),
        ]

        editBarCfg = [
            #       'name',         'hotkey',   'callback',         'iconImage',        'tips',             'activeFlag'
            IconCfg('Grabcut', 'h', self.editObjByGrabcut, 'grabcut.png', 'Edit object by grabcut', False),
            IconCfg('LayerUp', ['up'], self.layerUp, 'layerup.png', 'Bring forward', False),
            IconCfg('LayerDown', ['down'], self.layerDown, 'layerdown.png', 'Send backward', False),
            IconCfg('Delete', ['d', 'delete'], self.deleteObj, 'deleteobject.png', 'Delete object', False),
            IconCfg('changeLabel', 'c', self.changeLabel, 'modify.png', 'Change label', False),
            IconCfg('SaveEditedObj', 's', self.saveEditObject, 'save.png', 'Save edited object', False),
            # IconCfg('NextFile',     'right',    self.nextImage,     'next.png',         'Next image',       False),
        ]

        # Create toolbars
        self.toolBarObj = self.createToolBar('Tools', QtCore.Qt.TopToolBarArea, toolBarCfg)
        self.addBarObj = self.createToolBar('Add', QtCore.Qt.LeftToolBarArea, addBarCfg)
        self.editBarObj = self.createToolBar('Edit', QtCore.Qt.LeftToolBarArea, editBarCfg)

        self.updateToolbarVisibility()

    def selectFiles(self):
        # Reset the status bar to this message when leaving
        # backupMessage = self.statusBar().currentMessage()
        # message = 'Select folders containing images and labels'
        # self.statusBar().showMessage(message)

        self.currTool = Tool.none
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.clearPolygonAct()
        self.state = State.view
        self.updateToolbarVisibility()

        # select image file from file system
        imageFileQt = QtGui.QFileDialog.getOpenFileName(self, "Select image file",
                                                        self.parent.configObj.getLastImageFile(),
                                                        "Image files(*.png *.jpg *.bmp)")
        imageFile = str(imageFileQt)
        if os.path.exists(imageFile):
            self.parent.configObj.setLastImageFile(imageFile)

            imageNamePattern = os.path.join(os.path.dirname(imageFile), '*' + os.path.splitext(imageFile)[-1])
            self.parent.paintArea.images = glob.glob(imageNamePattern)
            self.parent.paintArea.images.sort()
            if imageFile in self.parent.paintArea.images:
                self.parent.paintArea.idx = self.parent.paintArea.images.index(imageFile)
            else:
                self.parent.paintArea.idx = 0

            labelFileQt = QtGui.QFileDialog.getOpenFileName(self, "Select label file, cancel to create new label",
                                                            self.parent.configObj.getLastLabelFile(),
                                                            "Label files(*.json)")
            labelFile = str(labelFileQt)
            if os.path.exists(labelFile):
                self.parent.configObj.setLastLabelFile(labelFile)

                labelNamePattern = os.path.join(os.path.dirname(labelFile), '*' + os.path.splitext(labelFile)[-1])
                self.parent.paintArea.labels = glob.glob(labelNamePattern)
                self.parent.paintArea.labels.sort()
            else:
                # new config file
                labelFile = self.getCorrespondLabelFileName(imageFile, os.path.dirname(imageFile))
                self.parent.configObj.setLastLabelFile(labelFile)

        self.parent.paintArea.redrawAll()

        self.state = State.view

        # Reset messages back
        # self.statusBar().showMessage(backupMessage)

    # Switch to previous image in file list
    # Load the image
    # Load its labels
    # Update the mouse selection
    # View
    def prevImage(self):
        if not self.parent.paintArea.images:
            return
        if self.parent.paintArea.idx > 0:
            if self.checkAndSave():
                self.currTool = Tool.none
                self.parent.paintArea.idx -= 1
                self.state = State.view
                self.parent.paintArea.redrawAll()
        return

    # Switch to next image in file list
    # Load the image
    # Load its labels
    # Update the mouse selection
    # View
    def nextImage(self):
        if not self.parent.paintArea.images:
            return
        if self.parent.paintArea.idx < len(self.parent.paintArea.images) - 1:
            if self.checkAndSave():
                self.currTool = Tool.none
                self.parent.paintArea.idx += 1
                self.state = State.view
                self.parent.paintArea.redrawAll()
        return

    def editLabel(self):
        if self.checkAndSave():
            self.currTool = Tool.addEditPolyPoints
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.clearPolygonAct()
            self.state = State.edit
            self.updateToolbarVisibility()

    def addLabel(self):
        if self.checkAndSave():
            self.currTool = Tool.none
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.clearPolygonAct()
            self.state = State.add
            self.updateToolbarVisibility()

    # Clear the drawn polygon and update
    def clearPolygonAct(self):
        self.parent.paintArea.clearPolygonAndUpdate()

    # Increase label transparency
    def minusAct(self):
        self.parent.configObj.setTransp(max(self.parent.configObj.getTransp() - 0.2, 0.0))
        self.parent.paintArea.update()

    # Decrease label transparency
    def plusAct(self):
        self.parent.configObj.setTransp(min(self.parent.configObj.getTransp() + 0.2, 1.0))
        self.parent.paintArea.update()

    def addObjByBox(self):
        self.currTool = Tool.addEditBox

    def addObjByPolygon(self):
        self.currTool = Tool.addEditPolyPoints
        self.setCursor(QtCore.Qt.ArrowCursor)

    def addObjByGrabCut(self):
        self.currTool = Tool.addEditGrabcut
        self.setCursor(QtCore.Qt.CrossCursor)
        self.parent.paintArea.grabcutObj.clear()

        self.parent.paintArea.update()

    def editObjByGrabcut(self):
        # To edit object polygon only one object should be selected
        if len(self.parent.paintArea.selObjs) != 1:
            return

        self.currTool = Tool.addEditGrabcut
        self.setCursor(QtCore.Qt.CrossCursor)
        self.parent.paintArea.grabcutObj.clear()
        self.parent.paintArea.grabcutObj.setRectRoiByPolygon(self.parent.paintArea.image, self.parent.paintArea.drawPoly)
        self.parent.paintArea.grabcutObj.setStatus(self.parent.paintArea.grabcutObj.Status.scribble)

        self.parent.paintArea.update()

    # Create a new object from the current polygon
    def saveNewObject(self):
        if not self.parent.paintArea.drawPolyClosed:
            return True

        # Ask the user for a label
        (label, ok) = self.getLabelFromUser()

        if ok and label:
            # Append and create the new object
            self.parent.paintArea.appendObject(label, self.parent.paintArea.drawPoly)

            if self.checkAndSave():
                # Clear the drawn polygon
                self.parent.paintArea.deselectAllObjects()
                self.parent.paintArea.clearPolygon()

                # Redraw
                self.parent.paintArea.update()

    def saveEditObject(self):
        if self.checkAndSave():
            # Clear the drawn polygon
            self.parent.paintArea.deselectAllObjects()
            self.parent.paintArea.clearPolygon()

            # Redraw
            self.parent.paintArea.update()

    # Delete the currently selected object
    def deleteObj(self):
        self.parent.paintArea.deleteObj()

    # Move object a layer up
    def layerUp(self):
        # Change layer
        self.parent.paintArea.modifyLayer(+1)
        # Update
        self.parent.paintArea.update()

    # Move object a layer down
    def layerDown(self):
        # Change layer
        self.parent.paintArea.modifyLayer(-1)
        # Update
        self.parent.paintArea.update()

    def changeLabel(self):
        # Cannot do anything without labels
        if not self.parent.paintArea.annotation:
            return
        # Cannot do anything without a selected object
        if not self.parent.paintArea.selObjs:
            return

        # The last selected object
        obj = self.parent.paintArea.annotation.objects[self.parent.paintArea.selObjs[-1]]
        # default label
        defaultLabel = obj.label
        defaultId = -1
        # If there is only one object the dialog text can be improved
        if len(self.parent.paintArea.selObjs) == 1:
            defaultId = obj.id

        (label, ok) = self.getLabelFromUser(defaultLabel, defaultId)

        if ok and label:
            for selObj in self.parent.paintArea.selObjs:
                # The selected object that is modified
                obj = self.parent.paintArea.annotation.objects[selObj]

                # Save changes
                if obj.label != label:
                    self.parent.paintArea.addChange(
                        "Set label {0} for object {1} with previous label {2}".format(label, obj.id, obj.label))
                    obj.label = label
                    obj.updateDate()

        # Update
        self.parent.paintArea.update()

    # Toggle the zoom and update all mouse positions
    def toggleZoomButton(self):

        if not self.zoomFlag:
            self.zoomFlag = True
            iconImageName = 'zoom_red.png'

            self.parent.paintArea.mousePosOnZoom = self.parent.paintArea.mousePos
        else:
            self.zoomFlag = False
            iconImageName = 'zoom.png'

        # Update icon image
        iconDir = os.path.join(os.path.dirname(__file__), '../icons')
        for act in self.toolBarObj.actions():
            test = act.iconText()
            if test == 'Zoom':
                act.setIcon(QtGui.QIcon(os.path.join(iconDir, iconImageName)))

        self.parent.paintArea.update()

    def setTip(self, action, tip):
        ''' Helper method that sets tooltip and statustip
        Provide an QAction and the tip text
        This text is appended with a hotkeys and then assigned '''
        tip += " (Hotkeys: '" + "', '".join([str(s.toString()) for s in action.shortcuts()]) + "')"
        action.setStatusTip(tip)
        action.setToolTip(tip)

    def getCorrespondLabelFileName(self, fullImageFileName, labelDir):
        imageFileName = os.path.basename(fullImageFileName)

        # for cityscapes style label file names
        if '_leftImg8bit' in imageFileName:
            imageFileExt = '_leftImg8bit.png'

            if 'gtFine' in labelDir:
                labelFileExt = '_gtFine_polygons.json'
            else:
                labelFileExt = '_gtCoarse_polygons.json'
        else:
            # use the same file name as image
            imageFileExt = os.path.splitext(imageFileName)[-1]
            labelFileExt = '.json'

        labelFileBaseName = imageFileName.replace(imageFileExt, labelFileExt)
        labelFileName = os.path.join(labelDir, labelFileBaseName)
        labelFileName = os.path.normpath(labelFileName)

        return labelFileName

    def checkAndSave(self):
        # Without changes it's ok to leave the image
        if not self.parent.paintArea.changes:
            return True

        # Backup of status message
        # restoreMessage = self.statusBar().currentMessage()
        # Create the dialog
        dlgTitle = "Save changes?"
        # self.statusBar().showMessage(dlgTitle)
        text = "Do you want to save the following changes?\n"
        for c in self.parent.paintArea.changes:
            text += "- " + c + '\n'
        buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel
        ret = QtGui.QMessageBox.question(self, dlgTitle, text, buttons, QtGui.QMessageBox.Save)
        proceed = False
        # If the user selected yes -> save
        if ret == QtGui.QMessageBox.Save:
            proceed = self.save()
        # If the user selected to discard the changes, clear them
        elif ret == QtGui.QMessageBox.Discard:
            self.parent.paintArea.clearChanges()
            self.parent.paintArea.redrawAll()
            proceed = True
        # Otherwise prevent leaving the image
        else:
            proceed = False
        # self.statusBar().showMessage(restoreMessage)

        if proceed == True:
            self.state = State.view
            self.currTool = Tool.none
            self.parent.paintArea.grabcutObj.clear()
            self.parent.paintArea.update()

        return proceed

    # Ask the user to select a label
    # If you like, you can give an object ID for a better dialog texting
    # Note that giving an object ID assumes that its current label is the default label
    # If you dont, the message "Select new label" is used
    # Return is (label, ok). 'ok' is false if the user pressed Cancel
    def getLabelFromUser(self, defaultLabel="", objID=-1):
        # Reset the status bar to this message when leaving
        # restoreMessage = self.statusBar().currentMessage()

        # Update defaultLabel
        if not defaultLabel:
            defaultLabel = self.parent.paintArea.defaultLabel

        # List of possible labels
        items = QtCore.QStringList(name2label.keys())
        items.sort()
        default = items.indexOf(defaultLabel)
        if default < 0:
            # self.statusBar().showMessage('The selected label is missing in the internal color map.')
            return

        # Specify title
        dlgTitle = "Select label"
        message = dlgTitle
        question = dlgTitle
        if objID >= 0:
            message = "Select new label for object {0} with current label {1}".format(objID, defaultLabel)
            question = "Label for object {0}".format(objID)
        # self.statusBar().showMessage(message)

        # Create and wait for dialog
        (item, ok) = QtGui.QInputDialog.getItem(self, dlgTitle, question, items, default, False)

        # Process the answer a bit
        item = str(item)

        # Restore message
        # self.statusBar().showMessage(restoreMessage)

        # Return
        return (item, ok)


    # Save labels
    def save(self):
        # Status
        saved = False
        # Message to show at the status bar when done
        message = ""
        imageFileName = self.parent.paintArea.images[self.parent.paintArea.idx]
        # Only save if there are changes, labels, an image filename and an image
        if self.parent.paintArea.changes and self.parent.paintArea.annotation and imageFileName:
            # Determine the label filename
            # If we have a loaded label file, then this is also the filename
            filename = self.getCorrespondLabelFileName(imageFileName,
                                                       os.path.dirname(self.parent.configObj.getLastLabelFile()))

            if filename:
                proceed = True
                # warn user that he is overwriting an old file
                if os.path.isfile(filename):
                    msgBox = QtGui.QMessageBox(self)
                    msgBox.setWindowTitle("Overwriting")
                    msgBox.setText(
                        "Saving overwrites the original file and it cannot be reversed. Do you want to continue?")
                    msgBox.addButton(QtGui.QMessageBox.Cancel)
                    okButton = msgBox.addButton(QtGui.QMessageBox.Ok)
                    msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
                    msgBox.setIcon(QtGui.QMessageBox.Warning)
                    msgBox.exec_()

                    # User clicked on "OK"
                    if msgBox.clickedButton() == okButton:
                        pass
                    else:
                        # Do nothing
                        message += "Nothing saved, no harm has been done. "
                        proceed = False

                # Save JSON file
                if proceed:
                    try:
                        self.parent.paintArea.annotation.toJsonFile(filename)
                        saved = True
                        message += "Saved labels to {0} ".format(filename)
                    except IOError as e:
                        message += "Error writing labels to {0}. Message: {1} ".format(filename, e.strerror)

            else:
                message += "Error writing labels. Cannot generate a valid filename. "

            # Clear changes
            if saved:
                self.parent.paintArea.clearChanges()
        else:
            message += "Nothing to save "
            saved = True

        # Show the status message
        # self.statusBar().showMessage(message)

        return saved

