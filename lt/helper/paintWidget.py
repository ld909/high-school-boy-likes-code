#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt4 import QtGui, QtCore

from annotation import Point, Annotation, CsObject
from labels import name2label, assureSingleInstanceName
from toolBars import State, Tool
from grabCut.GrabCutSegment import GrabCutSegment
from box import Box

class paintWidget(QtGui.QWidget):
    def __init__(self, parent):
        super(paintWidget, self).__init__(parent)

        self.setMouseTracking(True)

        self.parent = parent

        self.w     = 0
        self.h     = 0
        self.xoff  = 0
        self.yoff  = 0
        self.scale = 1
        self.bordergap = 20
        self.annotation = None
        self.defaultLabel = 'unlabelled'
        self.idx = 0

        # The position of the mouse
        self.mousePos         = None
        # TODO: NEEDS BETTER EXPLANATION/ORGANISATION
        self.mousePosOrig     = None
        # The position of the mouse scaled to label coordinates
        self.mousePosScaled   = None
        # If the mouse is outside of the image
        self.mouseOutsideImage = True
        # The position of the mouse upon enabling the zoom window
        self.mousePosOnZoom = None
        self.mouseButtons   = None
        self.mousePressEvent = None

        # A polygon that is drawn by the user
        self.drawPoly         = QtGui.QPolygonF()
        # Treat the polygon as being closed
        self.drawPolyClosed   = False
        # A point of this poly that is dragged
        self.draggedPt        = -1

        self.grabcutObj = GrabCutSegment()

        self.box = Box()

        # Each change is simply a descriptive string
        self.changes          = []
        # A list of objects with changed layer
        self.changedLayer     = []
        # A list of objects with changed polygon
        self.changedPolygon   = []
        # The current object the mouse points to. It's index in self.annotation.objects
        self.mouseObj         = -1
        # The currently selected objects. Their index in self.annotation.objects
        self.selObjs          = []
        # The objects that are highlighted. List of object instances
        self.highlightObjs    = []
        # A label that is selected for highlighting
        self.highlightObjLabel = None
        # Texture for highlighting
        self.highlightTexture = None

        self.images = []
        self.labels = []

        # Image window
        self.image = QtGui.QImage()

    # Create new object
    def appendObject(self, label, polygon):
        # Create empty annotation object
        # if first object
        if not self.annotation:
            self.annotation = Annotation()
            self.annotation.imgWidth = self.image.width()
            self.annotation.imgHeight = self.image.height()

        # Search the highest ID
        newID = 0
        for obj in self.annotation.objects:
            if obj.id >= newID:
                newID = obj.id + 1

        # New object
        # Insert the object in the labels list
        obj = CsObject()
        obj.label = label

        obj.polygon = [Point(p.x(), p.y()) for p in polygon]

        obj.id = newID
        obj.deleted = 0
        obj.verified = 0
        obj.user = ''
        obj.updateDate()

        self.annotation.objects.append(obj)

        # Append to changes
        self.addChange("Created object {0} with label {1}".format(newID, label))

        # # Clear the drawn polygon
        # self.deselectAllObjects()
        # self.clearPolygon()
        #
        # # select the new object
        # self.mouseObj = 0
        # self.selectObject()

    # Disable the popup menu on right click
    def createPopupMenu(self):
        pass

    def redrawAll(self):
        if self.idx not in range(0, len(self.images)):
            # message = 'Show image failed!'
            # self.statusBar().showMessage(message)
            return

        self.clearPolygon()

        imageFileName = self.images[self.idx]
        labelFileName = self.parent.toolBars.getCorrespondLabelFileName(imageFileName,
                                                        os.path.dirname(self.parent.configObj.getLastLabelFile()))

        self.loadImage(imageFileName)
        self.loadLabel(labelFileName)

        self.update()

    def loadImage(self, imageName):
        status = False
        # message = 'Loading image'
        # self.statusBar().showMessage(message)

        filename = os.path.normpath(imageName)

        self.image = QtGui.QImage(filename)
        if self.image.isNull():
            message = "Failed to read image: {0}".format(filename)
        else:
            message = "Read image: {0}".format(filename)
            status = True

        # Update toolbar actions that need an image
        for act in self.parent.toolBars.toolBarObj.actions():
            act.setEnabled(status)

            test = act.iconText()
            if self.idx < 1 and test == 'PrevFile':
                act.setEnabled(False)
            if self.idx >= len(self.images) - 1 and test == 'NextFile':
                act.setEnabled(False)

        self.parent.setWindowTitle(self.parent.applicationTitle + " File: {}".format(imageName))

        # self.statusBar().showMessage(message)

    # Load the labels from file
    # Only loads if they exist
    # Otherwise the filename is stored and that's it
    def loadLabel(self, filename):
        # Clear the current labels first
        self.clearAnnotation()

        if not filename or not os.path.isfile(filename):
            return

        try:
            self.annotation = Annotation()
            self.annotation.fromJsonFile(filename)

            # check image size in json file
            if self.annotation.imgHeight != self.image.height() or \
                            self.annotation.imgWidth != self.image.width():
                print('Wrong image size in json file!')
                self.annotation.imgWidth = self.image.width()
                self.annotation.imgHeight = self.image.height()
        except IOError as e:
            pass
            # This is the error if the file does not exist
            # message = "Error parsing labels in {0}. Message: {1}".format(filename, e.strerror)
            # self.statusBar().showMessage(message)

        # Remeber the status bar message to restore it later
        # restoreMessage = self.statusBar().currentMessage()

        # Restore the message
        # self.statusBar().showMessage(restoreMessage)

    # Clear list of changes
    def clearChanges(self):
        self.changes = []
        self.changedLayer = []
        self.changedPolygon = []

    # Clear the current labels
    def clearAnnotation(self):
        self.annotation = None
        self.clearChanges()
        self.deselectAllObjects()
        self.clearPolygon()

    # Clear the drawn polygon
    def clearPolygon(self):
        # We do not clear, since the drawPoly might be a reference on an object one
        self.drawPoly = QtGui.QPolygonF()
        self.drawPolyClosed = False

    def getPolygon(self, obj):
        poly = QtGui.QPolygonF()
        for pt in obj.polygon:
            point = QtCore.QPointF(pt.x, pt.y)
            poly.append(point)
        return poly

    # Get distance between two points
    def ptDist(self, pt1, pt2):
        # A line between both
        line = QtCore.QLineF(pt1, pt2)
        # Length
        lineLength = line.length()
        return lineLength

    # Add a point to the drawn polygon
    def addPtToPoly(self, pt):
        self.drawPoly.append(pt)

    # Get the point/edge index within the given polygon that is close to the given point
    # Returns (-1,-1) if none is close enough
    # Returns (i,i) if the point with index i is closed
    # Returns (i,i+1) if the edge from points i to i+1 is closest
    def getClosestPoint(self, poly, pt):
        closest = (-1, -1)
        distTh = 4.0
        dist = 1e9  # should be enough
        for i in range(poly.size()):
            curDist = self.ptDist(poly[i], pt)
            if curDist < dist:
                closest = (i, i)
                dist = curDist
        # Close enough?
        if dist <= distTh:
            return closest

        # Otherwise see if the polygon is closed, but a line is close enough
        if self.drawPolyClosed and poly.size() >= 2:
            for i in range(poly.size()):
                pt1 = poly[i]
                j = i + 1
                if j == poly.size():
                    j = 0
                pt2 = poly[j]
                edge = QtCore.QLineF(pt1, pt2)
                normal = edge.normalVector()
                normalThroughMouse = QtCore.QLineF(pt.x(), pt.y(), pt.x() + normal.dx(), pt.y() + normal.dy())
                intersectionPt = QtCore.QPointF()
                intersectionType = edge.intersect(normalThroughMouse, intersectionPt)
                if intersectionType == QtCore.QLineF.BoundedIntersection:
                    curDist = self.ptDist(intersectionPt, pt)
                    if curDist < dist:
                        closest = (i, j)
                        dist = curDist

        # Close enough?
        if dist <= distTh:
            return closest

        # If we didnt return yet, we didnt find anything
        return (-1, -1)

    # Determine if the given point closes the drawn polygon (snapping)
    def ptClosesPoly(self):
        if self.drawPoly.isEmpty():
            return False
        if self.mousePosScaled is None:
            return False
        closestPt = self.getClosestPoint(self.drawPoly, self.mousePosScaled)
        return closestPt == (0, 0)

    # We just closed the polygon and need to deal with this situation
    def closePolygon(self):
        self.drawPolyClosed = True

    # Intersect the drawn polygon with the mouse object
    # and create a new object with same label and so on
    def intersectPolygon(self):
        # Cannot do anything without labels
        if not self.annotation:
            return
        # Cannot do anything without a single selected object
        if self.mouseObj < 0:
            return
        # The selected object that is modified
        obj = self.annotation.objects[self.mouseObj]

        # The intersection of the polygons
        intersection = self.drawPoly.intersected(self.getPolygon(obj))

        if not intersection.isEmpty():
            # Ask the user for a label
            self.drawPoly = intersection
            (label, ok) = self.parent.toolBars.getLabelFromUser(obj.label)

            if ok and label:
                # Append and create the new object
                self.appendObject(label, intersection)

                # Clear the drawn polygon
                self.clearPolygon()

                # Default message
                # self.statusBar().showMessage(self.defaultStatusbar)

        # Deselect
        self.deselectAllObjects()
        # Redraw
        self.update()

    # Merge the drawn polygon with the mouse object
    # and create a new object with same label and so on
    def mergePolygon(self):
        # Cannot do anything without labels
        if not self.annotation:
            return
        # Cannot do anything without a single selected object
        if self.mouseObj < 0:
            return
        # The selected object that is modified
        obj = self.annotation.objects[self.mouseObj]

        # The union of the polygons
        union = self.drawPoly.united(self.getPolygon(obj))

        if not union.isEmpty():
            # Ask the user for a label
            self.drawPoly = union
            (label, ok) = self.parent.toolBars.getLabelFromUser(obj.label)

            if ok and label:
                # Append and create the new object
                self.appendObject(label, union)

                # Clear the drawn polygon
                self.clearPolygon()

                # Default message
                # self.statusBar().showMessage(self.defaultStatusbar)

        # Deselect
        self.deselectAllObjects()
        # Redraw
        self.update()

    # Edit an object's polygon or clear the polygon if multiple objects are selected
    def initPolygonFromObject(self):
        # Cannot do anything without labels
        if not self.annotation:
            return
        # Cannot do anything without any selected object
        if not self.selObjs:
            return
        # # If there are multiple objects selected, we clear the polygon
        # if len(self.selObjs) > 1:
        #     self.clearPolygon()
        #     self.update()
        #     return

        # The selected object that is used for init
        obj = self.annotation.objects[self.selObjs[-1]]

        # Make a reference to the polygon
        self.drawPoly = self.getPolygon(obj)

        # Make sure its closed
        self.drawPolyClosed = True

        # # Update toolbar icons
        # # Enable actions that need a polygon
        # for act in self.actPolyOrSelObj:
        #     act.setEnabled(True)
        # # Enable actions that need a closed polygon
        # for act in self.actClosedPoly:
        #     act.setEnabled(True)

        # Redraw
        self.update()

    # Mouse moved
    # Need to save the mouse position
    # Need to drag a polygon point
    # Need to update the mouse selected object
    def mouseMoveEvent(self, event):
        if self.image.isNull() or self.w == 0 or self.h == 0:
            return

        self.updateMousePos(event.posF())

        if self.parent.toolBars.currTool == Tool.addEditBox:
            # dragging the box
            if self.box.getStatus() == self.box.Status.boxSelection2ndPoint:
                self.drawPoly = self.box.setBox2ndPoint(self.mousePosScaled)
                self.drawPolyClosed = True

        elif self.parent.toolBars.currTool == Tool.addEditPolyPoints:
            # If we are dragging a point, update
            if self.draggedPt >= 0:
                # Update the dragged point
                self.drawPoly.replace(self.draggedPt, self.mousePosScaled)
                # If the polygon is the polygon of the selected object,
                # update the object polygon and
                # keep track of the changes we do
                if self.selObjs:
                    obj = self.annotation.objects[self.selObjs[-1]]
                    obj.polygon[self.draggedPt] = Point(self.mousePosScaled.x(), self.mousePosScaled.y())
                    # Check if we changed the object's polygon the first time
                    if not obj.id in self.changedPolygon:
                        self.changedPolygon.append(obj.id)
                        self.addChange("Changed polygon of object {0} with label {1}".format(obj.id, obj.label))
        elif self.parent.toolBars.currTool == Tool.addEditGrabcut:
            # dragging the box
            if self.grabcutObj.getStatus() == self.grabcutObj.Status.boxSelection2ndPoint:
                self.grabcutObj.setRectRoi2ndPoint(self.mousePosScaled)
            elif self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                # Scribble labeling
                if self.grabcutObj.isFrontGroundLabeling():
                    self.grabcutObj.addStrongFrontGround(self.mousePosScaled)
                elif self.grabcutObj.isBackGroundLabeling():
                    self.grabcutObj.addStrongBackGround(self.mousePosScaled)

        # Update the object selected by the mouse
        self.updateMouseObject()

        # Redraw
        self.update()

    # Mouse button pressed
    # Start dragging of polygon point
    # Enable temporary toggling of zoom
    def mousePressEvent(self, event):
        self.mouseButtons = event.buttons()

        ctrlPressed = event.modifiers() & QtCore.Qt.ControlModifier
        shiftPressed = event.modifiers() & QtCore.Qt.ShiftModifier
        altPressed = event.modifiers() & QtCore.Qt.AltModifier

        self.updateMousePos(event.posF())
        self.mousePressEvent = self.mousePosScaled
        # Handle left click
        if event.button() == QtCore.Qt.LeftButton:
            # If the drawn polygon is closed and the mouse clicks a point,
            # Then this one is dragged around
            if (self.parent.toolBars.state == State.add):
                if self.parent.toolBars.currTool == Tool.addEditBox:
                    self.box.setBox1stPoint(self.mousePosScaled)

                elif (self.parent.toolBars.currTool == Tool.addEditPolyPoints):
                    if self.drawPolyClosed and (self.mousePosScaled is not None):
                        closestPt = self.getClosestPoint(self.drawPoly, self.mousePosScaled)
                        if shiftPressed:
                            if closestPt[0] == closestPt[1]:
                                del self.drawPoly[closestPt[0]]

                                # If the polygon is the polygon of the selected object,
                                # update the object
                                # and keep track of the changes we do
                                if self.selObjs:
                                    obj = self.annotation.objects[self.selObjs[-1]]
                                    del obj.polygon[closestPt[0]]
                                    # Check if we changed the object's polygon the first time
                                    if not obj.id in self.changedPolygon:
                                        self.changedPolygon.append(obj.id)
                                        self.addChange(
                                            "Changed polygon of object {0} with label {1}".format(obj.id, obj.label))

                                self.update()
                        else:
                            # If we got a point (or nothing), we make it dragged
                            if closestPt[0] == closestPt[1]:
                                self.draggedPt = closestPt[0]
                            # If we got an edge, we insert a point and make it dragged
                            else:
                                self.drawPoly.insert(closestPt[1], self.mousePosScaled)
                                self.draggedPt = closestPt[1]
                                # If the polygon is the polygon of the selected object,
                                # update the object
                                # and keep track of the changes we do
                                if self.selObjs:
                                    obj = self.annotation.objects[self.selObjs[-1]]
                                    obj.polygon.insert(closestPt[1],
                                                       Point(self.mousePosScaled.x(), self.mousePosScaled.y()))
                                    # Check if we changed the object's polygon the first time
                                    if not obj.id in self.changedPolygon:
                                        self.changedPolygon.append(obj.id)
                                        self.addChange(
                                            "Changed polygon of object {0} with label {1}".format(obj.id, obj.label))
                elif self.parent.toolBars.currTool == Tool.addEditGrabcut:
                    if self.grabcutObj.getStatus() == self.grabcutObj.Status.boxSelection1stPoint:
                        self.grabcutObj.setRectRoi1stPoint(self.mousePosScaled)
                        self.grabcutObj.setImage(self.image)
                    elif self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                        # Start scribble labeling
                        if shiftPressed:
                            self.grabcutObj.setScribbleBackGroundFlag()
                        else:
                            self.grabcutObj.setScribbleFrontGroundFlag()

            elif self.parent.toolBars.state == State.edit:
                if self.parent.toolBars.currTool == Tool.addEditPolyPoints:
                    if self.mousePosScaled is not None:
                        closestPt = self.getClosestPoint(self.drawPoly, self.mousePosScaled)
                        # not clicking points or edges
                        if closestPt == (-1, -1):
                            if ctrlPressed:
                                # If also Shift is pressed and we have a closed polygon, then we intersect
                                # the polygon with the mouse object
                                if shiftPressed and self.drawPolyClosed:
                                    # self.intersectPolygon()
                                    pass
                                # If also Alt is pressed and we have a closed polygon, then we merge
                                # the polygon with the mouse object
                                elif altPressed and self.drawPolyClosed:
                                    # self.mergePolygon()
                                    pass
                                else:
                                    # Make the current mouse object the selected
                                    # and process the selection
                                    self.selectObject()
                            else:
                                # only select one object
                                self.deselectAllObjects()
                                self.selectObject()
                        # clicking points or edges
                        else:
                            if shiftPressed:
                                if closestPt[0] == closestPt[1]:
                                    # If the polygon is the polygon of the selected object,
                                    # update the object
                                    # and keep track of the changes we do
                                    if len(self.selObjs) == 1:
                                        del self.drawPoly[closestPt[0]]

                                        obj = self.annotation.objects[self.selObjs[-1]]
                                        del obj.polygon[closestPt[0]]
                                        # Check if we changed the object's polygon the first time
                                        if not obj.id in self.changedPolygon:
                                            self.changedPolygon.append(obj.id)
                                            self.addChange("Changed polygon of object {0} with label {1}".format(obj.id,
                                                                                                                 obj.label))

                                    self.update()
                            else:
                                # If we got a point (or nothing), we make it dragged
                                if closestPt[0] == closestPt[1]:
                                    self.draggedPt = closestPt[0]
                                # If we got an edge, we insert a point and make it dragged
                                else:
                                    # If the polygon is the polygon of the selected object,
                                    # update the object
                                    # and keep track of the changes we do
                                    if len(self.selObjs) == 1:
                                        self.drawPoly.insert(closestPt[1], self.mousePosScaled)
                                        self.draggedPt = closestPt[1]

                                        obj = self.annotation.objects[self.selObjs[-1]]
                                        obj.polygon.insert(closestPt[1],
                                                           Point(self.mousePosScaled.x(), self.mousePosScaled.y()))
                                        # Check if we changed the object's polygon the first time
                                        if not obj.id in self.changedPolygon:
                                            self.changedPolygon.append(obj.id)
                                            self.addChange("Changed polygon of object {0} with label {1}".format(obj.id,
                                                                                                                 obj.label))
                elif self.parent.toolBars.currTool == Tool.addEditGrabcut:
                    if self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                        # Start scribble labeling
                        if shiftPressed:
                            self.grabcutObj.setScribbleBackGroundFlag()
                        else:
                            self.grabcutObj.setScribbleFrontGroundFlag()
            else:
                # view state, do nothing when left click
                pass

        # Handle right click
        elif event.button() == QtCore.Qt.RightButton:
            self.toggleZoom(event.posF())

        # Redraw
        self.update()

    # Mouse button released
    # End dragging of polygon
    # Select an object
    # Add a point to the polygon
    # Disable temporary toggling of zoom
    def mouseReleaseEvent(self, event):
        self.mouseButtons = event.buttons()
        ctrlPressed = event.modifiers() & QtCore.Qt.ControlModifier
        shiftPressed = event.modifiers() & QtCore.Qt.ShiftModifier
        altPressed = event.modifiers() & QtCore.Qt.AltModifier

        # Handle left click
        if event.button() == QtCore.Qt.LeftButton:
            if self.parent.toolBars.state == State.add:
                if self.parent.toolBars.currTool == Tool.addEditBox:
                    self.drawPoly = self.box.setBox2ndPoint(self.mousePosScaled)
                    self.drawPolyClosed = True
                    self.box.setStatus(self.box.Status.boxSelection1stPoint)

                elif self.parent.toolBars.currTool == Tool.addEditPolyPoints:
                    # Add the point to the drawn polygon if not already closed
                    if not self.drawPolyClosed:
                        # If the mouse would close the poly make sure to do so
                        if self.ptClosesPoly():
                            self.closePolygon()
                        elif self.mousePosScaled is not None:
                            if not self.drawPolyClosed and self.drawPoly.isEmpty():
                                self.mousePosOnZoom = self.mousePos
                            self.addPtToPoly(self.mousePosScaled)
                    # Otherwise end a possible dragging
                    elif self.drawPolyClosed:
                        self.draggedPt = -1
                if self.parent.toolBars.currTool == Tool.addEditGrabcut:
                    if self.grabcutObj.getStatus() == self.grabcutObj.Status.boxSelection2ndPoint:
                        self.drawPoly = self.grabcutObj.finishBoxSelection()
                        if self.drawPoly:
                            self.closePolygon()
                    elif self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                        # End scribble labeling
                        self.drawPoly = self.grabcutObj.finishScribbling()

            elif self.parent.toolBars.state == State.edit:
                if self.parent.toolBars.currTool == Tool.addEditPolyPoints:
                    self.draggedPt = -1
                if self.parent.toolBars.currTool == Tool.addEditGrabcut:
                    if self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                        # End scribble labeling
                        self.drawPoly = self.grabcutObj.finishScribbling()

                        # Update changes
                        if self.selObjs:
                            obj = self.annotation.objects[self.selObjs[-1]]
                            obj.polygon = [Point(p.x(), p.y()) for p in self.drawPoly]
                            # Check if we changed the object's polygon the first time
                            if not obj.id in self.changedPolygon:
                                self.changedPolygon.append(obj.id)
                                self.addChange("Changed polygon of object {0} with label {1}".format(obj.id, obj.label))

        # Handle right click
        elif event.button() == QtCore.Qt.RightButton:
            self.toggleZoom(event.posF())

        # Redraw
        self.update()

    # Set the mouse positions
    # There are the original positions refering to the screen
    # Scaled refering to the image
    # And a zoom version, where the mouse movement is artificially slowed down
    def updateMousePos(self, mousePosOrig):

        mousePos = mousePosOrig

        mousePosScaled = QtCore.QPointF(float(mousePos.x() - self.xoff) / self.scale,
                                        float(mousePos.y() - self.yoff) / self.scale)
        mouseOutsideImage = not self.image.rect().contains(mousePosScaled.toPoint())

        mousePosScaled.setX(max(mousePosScaled.x(), 0.))
        mousePosScaled.setY(max(mousePosScaled.y(), 0.))
        mousePosScaled.setX(min(mousePosScaled.x(), self.image.rect().right()))
        mousePosScaled.setY(min(mousePosScaled.y(), self.image.rect().bottom()))

        if not self.image.rect().contains(mousePosScaled.toPoint()):
            self.mousePos = None
            self.mousePosScaled = None
            self.mousePosOrig = None
            self.updateMouseObject()
            self.update()
            return

        self.mousePos = mousePos
        self.mousePosScaled = mousePosScaled
        self.mousePosOrig = mousePosOrig
        self.mouseOutsideImage = mouseOutsideImage

    # Update the object that is selected by the current mouse curser
    def updateMouseObject(self):
        self.mouseObj = -1
        if self.mousePosScaled is None:
            return
        if not self.annotation or not self.annotation.objects:
            return
        for idx in reversed(range(len(self.annotation.objects))):
            obj = self.annotation.objects[idx]
            if obj.draw and self.getPolygon(obj).containsPoint(self.mousePosScaled, QtCore.Qt.OddEvenFill):
                self.mouseObj = idx
                break

    # Make the object selected by the mouse the real selected object
    def selectObject(self):
        # If there is no mouse selection, we are good
        if self.mouseObj < 0:
            self.deselectObject()
            return

        # Append the object to selection if it's not in there
        if not self.mouseObj in self.selObjs:
            self.selObjs.append(self.mouseObj)
        # Otherwise remove the object
        else:
            self.deselectObject()

        # update polygon
        self.initPolygonFromObject()

    # Delete the currently selected object
    def deleteObj(self):
        # Cannot do anything without a selected object
        if not self.selObjs:
            return
        # Cannot do anything without labels
        if not self.annotation:
            return

        for selObj in self.selObjs:
            # The selected object that is deleted
            obj = self.annotation.objects[selObj]

            # Save changes
            self.addChange("Deleted object {0} with label {1}".format(obj.id, obj.label))

            del (self.annotation.objects[selObj])

        # Clear polygon
        self.deselectAllObjects()
        self.clearPolygon()

        # Redraw
        self.update()

    # Deselect object
    def deselectObject(self):
        # If there is no object to deselect, we are good
        if not self.selObjs:
            return
        # If the mouse does not select and object, remove the last one
        if self.mouseObj < 0:
            del self.selObjs[-1]
        # Otherwise try to find the mouse obj in the list
        if self.mouseObj in self.selObjs:
            self.selObjs.remove(self.mouseObj)

    # Deselect all objects
    def deselectAllObjects(self):
        # If there is no object to deselect, we are good
        self.selObjs = []
        # self.mouseObj = -1

    # Add a new change
    def addChange(self, text):
        if not text:
            return

        self.changes.append(text)

    # Clear list of changes
    def clearChanges(self):
        self.changes = []
        self.changedLayer = []
        self.changedPolygon = []

    # Clear the drawn polygon and update
    def clearPolygonAndUpdate(self):
        self.deselectAllObjects()
        self.clearPolygon()
        self.update()


    # Modify the layer of the selected object
    # Move the layer up (negative offset) or down (postive offset)
    def modifyLayer(self, offset):
        # Cannot do anything without labels
        if not self.annotation:
            return
        # Cannot do anything without a single selected object
        if len(self.selObjs) != 1:
            return

        # The selected object that is modified
        obj = self.annotation.objects[self.selObjs[-1]]
        # The index in the label list we are right now
        oldidx = self.selObjs[-1]
        # The index we want to move to
        newidx = oldidx + offset

        # Make sure not not exceed zero and the list
        newidx = max(newidx, 0)
        newidx = min(newidx, len(self.annotation.objects) - 1)

        # If new and old idx are equal, there is nothing to do
        if oldidx == newidx:
            return

        # Move the entry in the labels list
        self.annotation.objects.insert(newidx, self.annotation.objects.pop(oldidx))

        # Update the selected object to the new index
        self.selObjs[-1] = newidx
        # self.statusBar().showMessage("Moved object {0} with label {1} to layer {2}".format(obj.id, obj.label, newidx))

        # Check if we moved the object the first time
        if not obj.id in self.changedLayer:
            self.changedLayer.append(obj.id)
            self.addChange("Changed layer for object {0} with label {1}".format(obj.id, obj.label))

    # Toggle the zoom and update all mouse positions
    def toggleZoom(self, mousePosOrig):

        if not self.parent.toolBars.zoomFlag:
            self.parent.toolBars.zoomFlag = True

            self.mousePosOnZoom = self.mousePos
            # Update the mouse position afterwards
            self.updateMousePos(mousePosOrig)
        else:
            self.parent.toolBars.zoomFlag = False

            # Update the mouse position first
            self.updateMousePos(mousePosOrig)
            # Update the dragged point to the non-zoom point
            if self.draggedPt >= 0:
                self.drawPoly.replace(self.draggedPt, self.mousePosScaled)

    # This method is called when redrawing everything
    # Can be manually triggered by self.update()
    # Note that there must not be any other self.update within this method
    # or any methods that are called within
    def paintEvent(self, event):
        # Create a QPainter that can perform draw actions within a widget or image
        qp = QtGui.QPainter()
        # Begin drawing in the application widget
        qp.begin(self)
        # Update scale
        self.updateScale(qp)
        # Determine the object ID to highlight
        self.getHighlightedObject(qp)
        # Draw the image
        self.drawImage(qp)
        # Draw the labels on top
        overlay = self.drawLabel(qp)
        # # Draw the user drawn polygon
        self.drawDrawPoly(qp)
        self.drawDrawRect(qp)
        self.drawScribble(qp)
        # Draw the label name next to the mouse
        self.drawLabelAtMouse(qp)
        # Draw the zoom
        self.drawZoom(qp,None)

        self.parent.toolBars.updateToolbarVisibility()
        # Thats all drawing
        qp.end()

        # Forward the paint event
        QtGui.QMainWindow.paintEvent(self,event)

    # Update the scaling
    def updateScale(self, qp):
        if not self.image.width() or not self.image.height():
            return

        # Horizontal offset
        self.xoff  = self.bordergap # + self.parent.toolBars.toolBarObj.height() +
        # Vertical offset
        self.yoff  = self.bordergap # + self.parent.toolBars.toolBarObj.height()

        # We want to make sure to keep the image aspect ratio and to make it fit within the widget
        # Without keeping the aspect ratio, each side of the image is scaled (multiplied) with
        sx = float(qp.device().width()  - 2*self.xoff) / self.image.width()
        sy = float(qp.device().height() - 2*self.yoff) / self.image.height()

        if self.image.width() > 2*qp.device().width() or self.image.height() > 2*qp.device().height():
            # Keep the original image scale if the image is too large
            self.scale = 1

            self.setMinimumWidth(self.image.width())
            self.setMinimumHeight(self.image.height())
        else:
            # To keep the aspect ratio while making sure it fits, we use the minimum of both scales
            # Remember the scale for later
            self.scale = min( sx , sy )

            self.setMinimumWidth(self.width())
            self.setMinimumHeight(self.height())

        # These are then the actual dimensions used
        self.w     = self.scale * self.image.width()
        self.h     = self.scale * self.image.height()


    # Determine the highlighted object for drawing
    def getHighlightedObject(self, qp):
        # These variables we want to fill
        self.highlightObjs = []
        self.highlightObjLabel = None

        # Without labels we cannot do so
        if not self.annotation:
            return

        # If available set the selected objects
        highlightObjIds = self.selObjs
        # If not available but the polygon is empty or closed, its the mouse object
        if not highlightObjIds and (self.drawPoly.isEmpty() or self.drawPolyClosed) and self.mouseObj>=0 and not self.mouseOutsideImage:
            highlightObjIds = [self.mouseObj]
        # Get the actual object that is highlighted
        if highlightObjIds:
            self.highlightObjs = [ self.annotation.objects[i] for i in highlightObjIds ]
        # Set the highlight object label if appropriate
        if len(highlightObjIds) == 1:
            self.highlightObjLabel = self.annotation.objects[highlightObjIds[-1]].label

    def drawImage(self, qp):
        # Return if no image available
        if self.image.isNull():
            return

        # Save the painters current setting to a stack
        qp.save()
        # Draw the image
        qp.drawImage(QtCore.QRect( self.xoff, self.yoff, self.w, self.h ), self.image)
        # Restore the saved setting from the stack
        qp.restore()


    # Draw the labels in the given QPainter qp
    # optionally provide a list of labels to ignore
    def drawLabel(self, qp, ignore = []):
        if self.image.isNull() or self.w <= 0 or self.h <= 0:
            return
        if not self.annotation:
            return

        # The overlay is created in the viewing coordinates
        # This way, the drawing is more dense and the polygon edges are nicer
        # We create an image that is the overlay
        # Within this image we draw using another QPainter
        # Finally we use the real QPainter to overlay the overlay-image on what is drawn so far

        # The image that is used to draw the overlays
        overlay = QtGui.QImage( self.w, self.h, QtGui.QImage.Format_ARGB32_Premultiplied )
        # Fill the image with the default color
        defaultLabel = name2label[self.defaultLabel]
        col = QtGui.QColor( *defaultLabel.color )
        overlay.fill( col )
        # Create a new QPainter that draws in the overlay image
        qp2 = QtGui.QPainter()
        qp2.begin(overlay)

        # The color of the outlines
        qp2.setPen(QtGui.QColor('white'))
        # Draw all objects
        for obj in self.annotation.objects:
            # Some are flagged to not be drawn. Skip them
            if not obj.draw:
                continue

            # The label of the object
            name      = assureSingleInstanceName( obj.label )
            # If we do not know a color for this label, warn the user
            if not name in name2label:
                print( "The annotations contain unkown labels. This should not happen. Please inform the datasets authors. Thank you!" )
                print( "Details: label '{}', file '{}'".format(name,self.currentLabelFile) )
                continue

            # If we ignore this label, skip
            if name in ignore:
                continue

            poly = self.getPolygon(obj)

            # Scale the polygon properly
            polyToDraw = poly * QtGui.QTransform.fromScale(self.scale,self.scale)

            # Default drawing
            # Color from color table, solid brush
            col   = QtGui.QColor( *name2label[name].color     )
            brush = QtGui.QBrush( col, QtCore.Qt.SolidPattern )
            qp2.setBrush(brush)
            # Overwrite drawing if this is the highlighted object
            if ( obj in self.highlightObjs or name == self.highlightObjLabel ):
                # First clear everything below of the polygon
                qp2.setCompositionMode( QtGui.QPainter.CompositionMode_Clear )
                qp2.drawPolygon( polyToDraw )
                qp2.setCompositionMode( QtGui.QPainter.CompositionMode_SourceOver )
                # Set the drawing to a special pattern
                brush = QtGui.QBrush(col,QtCore.Qt.DiagCrossPattern)
                qp2.setBrush(brush)

            qp2.drawPolygon( polyToDraw )

        # Draw outline of selected object dotted
        for obj in self.highlightObjs:
            brush = QtGui.QBrush(QtCore.Qt.NoBrush)
            qp2.setBrush(brush)
            qp2.setPen(QtCore.Qt.DashLine)
            polyToDraw = self.getPolygon(obj) * QtGui.QTransform.fromScale(self.scale,self.scale)
            qp2.drawPolygon( polyToDraw )

        # End the drawing of the overlay
        qp2.end()
        # Save QPainter settings to stack
        qp.save()
        # Define transparency
        qp.setOpacity(self.parent.configObj.getTransp())
        # Draw the overlay image
        qp.drawImage(self.xoff,self.yoff,overlay)
        # Restore settings
        qp.restore()

        return overlay

    # Draw the polygon that is drawn and edited by the user
    # Usually the polygon must be rescaled properly. However when drawing
    # The polygon within the zoom, this is not needed. Therefore the option transform.
    def drawDrawPoly(self, qp, transform=None):
        # Only draw polygons in add and edit state
        if (self.parent.toolBars.state != State.add) and (self.parent.toolBars.state != State.edit):
            return
        if self.drawPoly.isEmpty():
            return
        if not self.image:
            return

        # Save QPainter settings to stack
        qp.save()

        # The polygon - make a copy
        poly = QtGui.QPolygonF(self.drawPoly)

        # Append the current mouse position
        if not self.drawPolyClosed and (self.mousePosScaled is not None):
            poly.append( self.mousePosScaled )

        # Transform
        if not transform:
            poly = poly * QtGui.QTransform.fromScale(self.scale,self.scale)
            poly.translate(self.xoff,self.yoff)
        else:
            poly = poly * transform

        # Do not fill the polygon
        qp.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

        # Draw the polygon edges
        polyColor = QtGui.QColor(255,0,0)
        qp.setPen(polyColor)
        if not self.drawPolyClosed:
            qp.drawPolyline( poly )
        else:
            qp.drawPolygon( poly )

        # Get the ID of the closest point to the mouse
        if self.mousePosScaled is not None:
            closestPt = self.getClosestPoint( self.drawPoly, self.mousePosScaled )
        else:
            closestPt = (-1,-1)

        # If a polygon edge is selected, draw in bold
        if closestPt[0] != closestPt[1]:
            thickPen = QtGui.QPen(polyColor)
            thickPen.setWidth(3)
            qp.setPen(thickPen)
            qp.drawLine( poly[closestPt[0]], poly[closestPt[1]] )

        # Draw the polygon points
        qp.setPen(polyColor)
        startDrawingPts = 0

        # A bit different if not closed
        if not self.drawPolyClosed:
            # Draw
            self.drawPoint( qp, poly.first(), True, closestPt==(0,0) and self.drawPoly.size()>1 )
            # Do not draw again
            startDrawingPts = 1

        # The next in red
        for pt in range(startDrawingPts,poly.size()):
            self.drawPoint( qp, poly[pt], False, self.drawPolyClosed and closestPt==(pt,pt) )

        # Restore QPainter settings from stack
        qp.restore()

    def drawDrawRect(self, qp):

        qp.save()
        qp.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        qp.setFont(QtGui.QFont('QFont::AnyStyle', 14))
        thickPen = QtGui.QPen()
        qp.setPen(thickPen)

        if self.parent.toolBars.currTool == Tool.addEditBox:
            if self.box.getStatus() == self.box.Status.boxSelection2ndPoint:
                self.drawPoly = self.box.getBox()

        elif self.parent.toolBars.currTool == Tool.addEditGrabcut:
            # show the box when selecting box or finished selecting box
            if self.grabcutObj.getStatus() == self.grabcutObj.Status.boxSelection2ndPoint or \
               self.grabcutObj.getStatus() == self.grabcutObj.Status.scribble:
                box = self.grabcutObj.getBox()

                rect = QtCore.QRectF()

                rect.setX(box[0] * self.scale + self.xoff)
                rect.setY(box[1] * self.scale + self.yoff)

                width = box[2]
                height = box[3]
                rect.setWidth(width * self.scale)
                rect.setHeight(height * self.scale)

                thickPen.setColor(QtGui.QColor(0,255,0))
                thickPen.setWidth(3)
                qp.setPen(thickPen)
                qp.drawRect(rect)

        qp.restore()

    def drawScribble(self, qp, transform = None):
        # Save QPainter settings to stack
        qp.save()

        points = self.grabcutObj.getStrongBackGround()
        if points.size() != 0:
            # Transform
            if not transform:
                points = points * QtGui.QTransform.fromScale(self.scale, self.scale)
                points.translate(self.xoff, self.yoff)
            else:
                points = points * transform

            qp.setPen(QtGui.QColor(255, 0, 0))
            qp.drawPoints(points)

        points = self.grabcutObj.getStrongFrontGround()
        if points.size() != 0:
            # Transform
            if not transform:
                points = points * QtGui.QTransform.fromScale(self.scale, self.scale)
                points.translate(self.xoff, self.yoff)
            else:
                points = points * transform

            qp.setPen(QtGui.QColor(0, 255, 0))
            qp.drawPoints(points)

        qp.restore()

    # Draw a point using the given QPainter qp
    # If its the first point in a polygon its drawn in green
    # if not in red
    # Also the radius might be increased
    def drawPoint(self, qp, pt, isFirst, increaseRadius):
        # The first in green
        if isFirst:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0),QtCore.Qt.SolidPattern))
        # Other in red
        else:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(255,0,0),QtCore.Qt.SolidPattern))

        # Standard radius
        r = 3.0
        # Increase maybe
        if increaseRadius:
            r *= 2.5
        # Draw
        qp.drawEllipse( pt, r, r )

    # Draw the label name next to the mouse
    def drawLabelAtMouse(self, qp):
        # Nothing to do without a highlighted object
        if not self.highlightObjs:
            return
        # Also we do not want to draw the label, if we have a drawn polygon
        if not self.drawPoly.isEmpty():
            return
        # Nothing to without a mouse position
        if not self.mousePos:
            return

        # Save QPainter settings to stack
        qp.save()

        # That is the mouse positiong
        mouse = self.mousePos

        # Will show zoom
        showZoom = self.parent.toolBars.zoomFlag and \
                   self.parent.configObj.getZoomFactor()!=1 and \
                   (not self.image.isNull()) and \
                   (self.w) and (self.h)

        # The text that is written next to the mouse
        mouseText = self.highlightObjs[-1].label

        # Where to write the text
        # Depends on the zoom (additional offset to mouse to make space for zoom?)
        # The location in the image (if we are at the top we want to write below of the mouse)
        off = 36
        if showZoom:
            off += self.parent.toolBars.zoomSize / 2
        if mouse.y()-off > 0: # self.parent.toolBars.toolBarObj.height():
            top = mouse.y()-off
            btm = mouse.y()
            vAlign = QtCore.Qt.AlignTop
        else:
            # The height of the cursor
            if not showZoom:
                off += 20
            top = mouse.y()
            btm = mouse.y()+off
            vAlign = QtCore.Qt.AlignBottom

        # Here we can draw
        rect = QtCore.QRect()
        rect.setTopLeft(QtCore.QPoint(mouse.x()-100,top))
        rect.setBottomRight(QtCore.QPoint(mouse.x()+100,btm))

        # The color
        qp.setPen(QtGui.QColor('white'))
        # The font to use
        font = QtGui.QFont("Helvetica",20,QtGui.QFont.Bold)
        qp.setFont(font)
        # Non-transparent
        qp.setOpacity(1)
        # Draw the text, horizontally centered
        qp.drawText(rect,QtCore.Qt.AlignHCenter|vAlign,mouseText)
        # Restore settings
        qp.restore()

    # Draw the zoom
    def drawZoom(self, qp, overlay):
        # Zoom disabled?
        if not self.parent.toolBars.zoomFlag:
            return
        # No image
        if self.image.isNull() or not self.w or not self.h:
            return
        # No mouse
        if not self.mousePos:
            return

        # Abbrevation for the zoom window size
        zoomSize = self.parent.toolBars.zoomSize
        zoomFactor = self.parent.configObj.getZoomFactor()
        # Abbrevation for the mouse position
        mouse = self.mousePos

        # The pixel that is the zoom center
        pix = self.mousePosScaled
        # The size of the part of the image that is drawn in the zoom window
        selSize = zoomSize / (zoomFactor * zoomFactor)
        # The selection window for the image
        sel = QtCore.QRectF(pix.x() - selSize / 2, pix.y() - selSize / 2, selSize, selSize)
        # The selection window for the widget
        view = QtCore.QRectF(mouse.x() - zoomSize / 2, mouse.y() - zoomSize / 2, zoomSize, zoomSize)

        # Show the zoom image
        qp.drawImage(view, self.image, sel)

        transform = QtGui.QTransform()
        quadFrom = QtGui.QPolygonF()
        quadFrom.append(sel.topLeft())
        quadFrom.append(sel.topRight())
        quadFrom.append(sel.bottomRight())
        quadFrom.append(sel.bottomLeft())
        quadTo = QtGui.QPolygonF()
        quadTo.append(view.topLeft())
        quadTo.append(view.topRight())
        quadTo.append(view.bottomRight())
        quadTo.append(view.bottomLeft())

        if QtGui.QTransform.quadToQuad(quadFrom, quadTo, transform):
            # If we are currently drawing the polygon, we need to draw again in the zoom
            if not self.drawPoly.isEmpty():
                qp.setClipRect(view)
                # transform.translate(self.xoff,self.yoff)
                self.drawDrawPoly(qp, transform)

            # If we are currently scirbbling the image, we need to draw again in the zoom
            self.drawScribble(qp, transform)

        else:
            print("not possible")
