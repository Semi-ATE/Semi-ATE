# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 12:00:27 2022

Create interactive widgets from an svg image.

@author: jung

This lib is based on the following information or other libs:
   - https://pypi.org/project/svgelements/  for calculation from the transformation matrix
   - animated svg graphics:  https://funprojects.blog/2021/12/07/animated-svg-graphics-in-python/
      -> principle adopted for changing text
   - selectable image: https://stackoverflow.com/questions/59090988/clickable-svg-image-to-run-method
      - image is not adjusted to the size of the window
      - not applicable to items within an image, because transform from parent missing
   - https://forum.qt.io/topic/109025/updating-qgraphicseffect-for-qgraphicssvgitem/6

   - QtWidgets.QGraphicsView
       https://doc.qt.io/qt-5/qgraphicsview.html


What is available for reading, writing, manipulating from svg-files:
   - svgelements https://github.com/meerk40t/svgelements      -> this lib is used in this class
      - more robust as svg.path, include other elements like points, matrix, color
   - SVG manipulation within a GUI https://github.com/MoplusplusApp/Moplusplus
   - https://doc.qt.io/qtforpython/overviews/graphicsview.html
   - svglib
      - only reading SVG files and converting them (to a reasonable degree) to other formats using the ReportLab Open Source toolkit.
   - CairoSVG  https://cairosvg.org/
      - convert to png, pdf, ps and svg
   - svg.path
      - svg.path is a collection of objects that implement the different path commands in SVG, and a parser for SVG path definitions.
   - drawSvg
      - A Python 3 library for programmatically generating SVG images (vector drawings) and rendering them or displaying them in a Jupyter notebook.
   - svgutils  https://svgutils.readthedocs.io/en/latest/transform.html
      - basic svg transformations


TODO: - si units missing
      - min,max values for the QDoubleSpinBox
      - show combobox for string values

      - mouse bewegungen abfangen und setToolTip anzeigen

"""

from lxml import etree
import svgelements  # https://pypi.org/project/svgelements/
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtSvg import QGraphicsSvgItem, QSvgRenderer
from qtpy.QtCore import Signal


class SvgItem(QGraphicsSvgItem):
    """ """

    clickBox = Signal(str, QtCore.QPoint)
    clickHelpBox = Signal(str, QtCore.QPoint)

    def __init__(self, id, renderer, parent=None, element=None):
        super().__init__(parent)
        self.id = id
        self.setSharedRenderer(renderer)  # necessary for setting lifetime
        bounds = renderer.boundsOnElement(id)
        self.setElementId(id)
        self.setPos(bounds.topLeft())
        self.setFlags(QGraphicsSvgItem.ItemIsSelectable)  # | QGraphicsSvgItem.ItemSendsGeometryChanges)
        # self.installEventFilter(self)
        self.boxes = {}

    def mousePressEvent(self, event: "QtWidgets.QGraphicsSceneMouseEvent"):
        """
        Overwrite the mousePressEvent from QGraphicsSvgItem.

        Send the clickBox or clickHelpBox Signal with the name from the element and the coordinates.

        Parameters
        ----------
        event : 'QtWidgets.QGraphicsSceneMouseEvent'
            DESCRIPTION.

        Returns
        -------
        None.

        """
        x = event.pos().x()
        y = event.pos().y()
        for tid in self.boxes:  # find the accociated box and get the text attribute
            box = self.boxes[tid]
            if (x >= box["x"] and x <= box["x"] + box["w"]) and (y <= box["y"] and y >= box["y"] - box["h"]):
                rectangle = self.mapRectToScene(box["x"], box["y"], box["w"], box["h"])  # Scenen coordinats
                # rectangle = self.mapRectFromScene(box['x'], box['y'], box['w'], box['h'])       # item coordinats(
                rectangle = QtCore.QRectF(
                    event.screenPos().x(), event.screenPos().y(), rectangle.width(), rectangle.height()
                )
                point = QtCore.QPoint(int(rectangle.x()), int(rectangle.y()))
                if event.button() == 1:  # right Mousebutton
                    self.clickBox.emit(tid, point)
                elif event.button() == 2:  # left Mousebutton
                    self.clickHelpBox.emit(tid, point)
        super().mousePressEvent(event)

    def paint(self, painter, option, widget=None):
        """
        Overwerite the paint-function  from QGraphicsSvgItem.

        Parameters
        ----------
        painter : TYPE
            DESCRIPTION.
        option : TYPE
            DESCRIPTION.
        widget : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        #  set a graphics colorize effect when item is selected, and disable the effect when deselected
        # if self.isSelected():
        #     self._effect = QtCore.QGraphicsColorizeEffect()
        #     self._effect.setColor(Qt.red)
        #     self._effect.setStrength(.5)
        #     self.setGraphicsEffect(self._effect)
        # else:
        #     pass
        #     #self.setGraphicsEffect(0)
        QGraphicsSvgItem.paint(self, painter, option, widget)

    def eventFilter(self, obj, event):
        """
        Set an event Filter.

        Parameters
        ----------
        obj : TYPE
            DESCRIPTION.
        event : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        print(event.type())
        return super(QGraphicsSvgItem, self).eventFilter(obj, event)


class SvgIaViewer(QtWidgets.QGraphicsView):
    """
    SVG interactive Viewer
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)  # https://doc.qt.io/qtforpython/overviews/graphicsview.html
        self._renderer = QSvgRenderer()
        self.setScene(self._scene)

    def setSvg(self, filename):
        """
        Render the svg-file 'filename'.

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.resetTransform()
        self._scene.clear()
        self.root = etree.parse(filename)
        result = self._renderer.load(filename)
        if not result:
            print(f"couldn't load {filename}")
            return
        self.mainSvg = SvgItem(self.getid(self.root.getroot()), self._renderer)
        self.mainSvg.setX(0)
        self.mainSvg.setY(0)
        self.mainSvg.setElementId("")  # force repainting, otherwise the image is empty...
        self._scene.addItem(self.mainSvg)

    def updateSvg(self):
        """Update the rendering from the svg."""
        update = etree.tostring(self.root, xml_declaration=True)
        self._renderer.load(update)
        self.mainSvg.setElementId("")  # force repainting

    def setBox(self, name, element):
        """
        Found the retangle from the element, save the coordinates in self.mainSvg.boxes and transformed to the parent position.

        Each element must be placed within a rectangle.

        Parameters
        ----------
        searchid : TYPE
            id from the text svg-field.

        Returns
        -------
        list
            x,y position and widht/height from the retangle.
        """
        bmatrix = None
        box = None
        parentid = self.getid(element)
        root = element
        while element.getparent() is not None:  # go up and search for the first rectangle
            if parentid is not None:
                item = SvgItem(parentid, self._renderer, element=element)
                if box is None and item.boundingRect().width() != 0.0 and "transform" in element.keys():
                    box = item.boundingRect()
                    bmatrix = svgelements.Matrix(element.attrib["transform"])
                    box = {"w": box.width(), "h": box.height()}
            elif (
                box is None and element.getchildren() != []
            ):  # there are no id's in orginal visio-> svg-files, so use another methode
                for child in element.getchildren():
                    if "d" in child.keys():
                        box = svgelements.Path(child.attrib["d"])
                        box = {"w": box.bbox()[2], "h": box.bbox()[3]}
                bmatrix = svgelements.Matrix(element.attrib["transform"])
            element = element.getparent()
            parentid = self.getid(element)
            if "transform" in element.keys() and box is not None:
                bmatrix *= svgelements.Matrix(element.attrib["transform"])  # recalcuate the transform matrix
        if bmatrix is not None:
            self.mainSvg.boxes[name] = {"x": bmatrix.e, "y": bmatrix.f, "w": box["w"], "h": box["h"]}
            root.set("x", "1.0")

    def getid(self, element):
        """
        Get the id from the element.

        Not all elements have an id. It depends on the program with which the svg-image was created :-(
        If now id found than it returns None

        Parameters
        ----------
        element : TYPE
            DESCRIPTION.

        Returns
        -------
        result : string
            the id from the element.

        """
        try:
            result = element.attrib["id"]
        except Exception:
            result = None
        return result

    def getAllTxtwColor(self, color, tlen=3):
        """
        Give a dictionary from all Text elements with the specific color and a length from minimum tlen.

        Parameters
        ----------
        color : string
            color which is used.
        tlen :
            minimum text length

        Returns
        -------
           result list

        """
        color = color.upper()
        result = {}
        for element in self.root.iter("*"):
            if (
                "fill" in element.keys()
                and element.attrib["fill"].upper() == color
                and element.text is not None
                and len(element.text) >= tlen
            ):
                result[element.text] = element, "get", "text"
        return result

    def getAllTxtColors(self, tlen=3):
        """
        Give a list of colors from all text elements with a length from minimum tlen.

        Parameters
        ----------
        tlen :
            minimum text length

        Returns
        -------
           result list

        """
        result = []
        for element in self.root.iter("*"):
            if "fill" in element.keys() and element.text is not None and len(element.text) >= tlen:
                color = element.attrib["fill"].upper()
                if color not in result:
                    result.append(element.attrib["fill"].upper())
        return result


class InteractiveSvgWidget(QtWidgets.QWidget):
    """
    Interactive SVG Widget.

    Make a svg image interactive. You can set values and replace elements inside the svg-image.

    """

    editWidth = 60
    editHeight = 20

    changedId = Signal(str, str)

    def __init__(self, svgfilename, firstname=""):
        super().__init__()
        self.viewer = SvgIaViewer(self)
        self.firstname = firstname
        vb_layout = QtWidgets.QVBoxLayout(self)
        vb_layout.addWidget(self.viewer)
        self.elements = {}
        self.viewer.setSvg(svgfilename)
        self.viewer.mainSvg.clickBox.connect(self._clickBox)
        self.viewer.mainSvg.clickHelpBox.connect(self._clickHelpBox)
        self.setGeometry(0, 0, int(self.viewer.scene().width()) + 50, int(self.viewer.scene().height()) + 50)
        self.setMouseTracking = True
        self.setAutoFillBackground(True)
        # self.setStyleSheet("""QToolTip {color: black; border: black solid 1px}""")

        self.edit = QtWidgets.QDoubleSpinBox(self.viewer)
        self.edit.editingFinished.connect(lambda: self._editfinish())
        self.edit.hide()
        self.edit.abort = False

    def loadSvg(self, filename, svgtxt=None):
        """Load the svg-file and parse it.

        if svgtxt != None, then return with the parent from this element.
        else with the etree.
        """
        svg = etree.parse(filename)
        if svgtxt is None:
            return svg
        available = []
        for element in svg.iter("*"):
            if element.text == svgtxt:
                return element.getparent()
            elif element.text is not None and element.text[0] != "\n":
                available.append(element.text)
        print(f"loadSvg: {svgtxt} not found, but found {available}")
        return None

    def replaceSvg(self, name, replace):
        """
        Replace the svg-element with 'name'.

        Parameters
        ----------
        name : string
            name from an svg-element.
        replace : <Element> from etree
            DESCRIPTION.

        Returns
        -------
        None.

        """
        child = self._getGrandChildElement(self.elements[name][0].getparent(), "d")
        child.attrib["d"] = self._getGrandChildElement(replace, "d").attrib["d"]
        self.viewer.updateSvg()

    def _getGrandChildElement(self, element, attrib):
        """
        Serach for 'attrib' in all grandchild.items().

        Parameters
        ----------
        element : <element> from a etree.
        attrib : string
            name from the attribute.

        Returns
        -------
        the grandchild with the attribute.

        """
        result = None
        for child in element.getchildren():
            for grandchild in child.getchildren():
                if attrib in grandchild.keys():
                    result = grandchild
                    break
        return result

    def setTextColor(self, color):
        """Fill the dictionary 'self.elements' with all Text elements with this color, listen to getattribute."""
        self.elements.update(self.viewer.getAllTxtwColor(color))

    def setAllsvgElementsWTxt(self, svgtxt):
        """
        Fill the dictionary 'self.elements' with  all elements, where text is starting with the string 'svgtxt'.

        Parameters
        ----------
        svgid : string

        Returns
        -------
        result : list
            return a list with the elements.

        """
        for element in self.viewer.root.iter("*"):
            if element.text is not None and element.text.find(svgtxt) == 0:
                self.elements[element.text] = element, None, "element"

    def setclickableText(self):
        """Make  'self.elements' with the attribute 'text' clickable, now the element listen to setattr."""
        for name in self.elements:
            if self.elements[name][2] == "text" and self.elements[name][1] == "get":
                self.viewer.setBox(name, self.elements[name][0])
                self.elements[name] = self.elements[name][0], "set", "text"

    def setElementSvg(self, name=None, *files):
        """Set all 'self.elements' with the attribute 'element'==None to get(=listen to getattr).

        Load all files and search for the parent with the name.
        """
        mySvg = []
        for file in files:
            mySvg.append(self.loadSvg(file, name))
        for ename in self.elements:
            if self.elements[ename][2] == "element" and self.elements[ename][1] is None:
                self.replaceSvg(ename, mySvg[0])
                self.elements[ename] = self.elements[ename][0], "get", "element", mySvg, 0

    def setclickableElement(self):
        """Make all 'self.elements' with the attribute 'element' clickable, now the element listen to setattr."""
        box = None
        for name in self.elements:
            if self.elements[name][2] == "element" and self.elements[name][1] == "get":
                element = self.elements[name][0].getparent()
                box = None
                bmatrix = None  # todo: bmatrix = Matrix(1, 0, 0, 1, 0, 0)
                while element is not None:
                    if box is None:
                        grandchild = self._getGrandChildElement(element, "d")
                        if grandchild is not None:
                            box = svgelements.Path(grandchild.attrib["d"])
                            box = {
                                "w": box.bbox()[2],
                                "h": box.bbox()[3],
                            }  # see https://github.com/meerk40t/svgelements
                            element = grandchild.getparent()
                    if box is not None and "transform" in element.keys():
                        if bmatrix is None:
                            bmatrix = svgelements.Matrix(element.attrib["transform"])
                        else:
                            bmatrix *= svgelements.Matrix(element.attrib["transform"])
                    element = element.getparent()
            if box is not None:
                self.viewer.mainSvg.boxes[name] = {"x": bmatrix.e, "y": bmatrix.f, "w": box["w"], "h": box["h"]}
                element = list(self.elements[name])
                element[1] = "set"
                self.elements[name] = element
        return

    def setIdText(self, tid, text):
        """
        Set the element with the name 'tid' to the value 'text'.

        Parameters
        ----------
        tid : strig
            Text id.
        text: string
            new text string

        Returns
        -------
        None.

        """
        element = self.elements[tid][0]
        if self.elements[tid][2] == 'text':
            element.text = f"{tid}:{text}"
            self.viewer.updateSvg()
        elif self.elements[tid][2] == 'element':
            self.replaceSvg(tid, self.elements[tid][3][text])


    def getAllTxtColors(self, tlen=3):
        """
        Give a list of colors from all text elements with a length from minimum tlen.

        Parameters
        ----------
        tlen :
            minimum text length

        Returns
        -------
           result list

        """
        result = []
        for element in self.viewer.root.iter("*"):
            if "fill" in element.keys() and element.text is not None and len(element.text) >= tlen:
                color = element.attrib["fill"].upper()
                if color not in result:
                    result.append(element.attrib["fill"].upper())
        return result

    @QtCore.pyqtSlot(str, QtCore.QPoint)
    def _clickBox(self, tid, viewpoint):
        if tid is None:
            self._editfinish()
        typ = self.elements[tid][2]
        if typ == "text":
            self.edit.element = self.elements[tid][0]
            color = self.edit.element.attrib["fill"]
            text = self.edit.element.text.split(":")
            value = float(text[-1]) if len(text) > 1 and text[-1].find("None") < 0 else 0
            viewpoint = self.mapFromGlobal(viewpoint)
            self.edit.setGeometry(QtCore.QRect(viewpoint.x(), viewpoint.y(), self.editWidth, self.editHeight))
            self.edit.setStyleSheet(f"color: {color}")
            self.edit.setValue(value)
            self.edit.show()
        elif typ == "element":
            index = self.elements[tid][4] + 1 if self.elements[tid][4] + 1 < len(self.elements[tid][3]) else 0
            self.replaceSvg(tid, self.elements[tid][3][index])
            self.elements[tid] = (
                self.elements[tid][0],
                self.elements[tid][1],
                self.elements[tid][2],
                self.elements[tid][3],
                index,
            )
            self.changedId.emit(f"{self.firstname}.{tid}", str(index))  # send the signal to the parent

    @QtCore.pyqtSlot(str, QtCore.QPoint)
    def _clickHelpBox(self, tid, viewpoint):
        # ToDo: create a QLabel and show it
        element = self.elements[tid][0]
        msg = f"{element.text}:  This could be a Tip\n With some information about the using\n      :-)"
        print(msg)
        self.setToolTip(msg)

    def _editfinish(self):
        if self.edit.abort:
            self.edit.abort = False
            return
        self.edit.abort = False
        newvalue = self.edit.value()
        text = self.edit.element.text.split(":")
        self.edit.hide()
        self.edit.element.text = f"{text[0]}:{newvalue}"
        self.viewer.updateSvg()
        self.changedId.emit(f"{self.firstname}.{text[0]}", str(newvalue))  # send the signal to the parent

    def resizeEvent(self, newSize):
        """Overwrite the resizeEvent from QWidget.

        This isn't running correctl, it must be improved.
        """
        self.edit.hide()
        if newSize.oldSize().width() < 0:
            self.startSize = newSize.size()
            self.viewer.mainSvg.setScale(1.0)
        else:
            scale = newSize.size().width() / self.startSize.width()
            self.viewer.mainSvg.setScale(scale)
        super().resizeEvent(newSize)

    def keyPressEvent(self, event):
        """Escape close the edit-field and refuse the value."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.edit.abort = True
            self.edit.hide()
        super().keyPressEvent(event)


if __name__ == "__main__":
    import sys
    import os

    app = QtWidgets.QApplication(sys.argv)
    dirname = os.path.dirname(__file__) + "../../gui/instruments/miniSCT/"
    filename = "SCT8_v7_PDC.svg"

    window = InteractiveSvgWidget(dirname + filename)  # this is the orginal svg data
    print(f"The used Text colors are : {window.getAllTxtColors()}")

    # set/get
    window.setTextColor(
        "#c00000"
    )  # fill a dictionary 'elements' with all Text elements with this color, listen to getattribute
    window.setclickableText()  # make the 'elements' clickable, now the element also listen to setattr

    window.setAllsvgElementsWTxt(
        "SPST"
    )  # search for all elements which has an text item 'SPST'  -> this are the switches
    window.setElementSvg("SWITCH", dirname + "sw0.svg", dirname + "sw1.svg")
    window.setclickableElement()  # make the elements cklickable

    window.setAllsvgElementsWTxt("SPDT")  # double-throw switch
    # window.setElementSvg('SWITCH', dirname+'sw0.svg', dirname+'sw1.svg')
    # window.setclickableElement()

    # only get
    window.setTextColor("#00B050")  # all green Textboxes are only listening

    # set the get's
    window.setIdText("i_cnt_avrg", 100)
    window.setIdText("i_meas", 0.45)
    
    window.setIdText('SPST.252', 1)

    window.setStyleSheet("background-color: white;")
    # window.setGeometry(500, 300, 900, 700)
    window.show()
    sys.exit(app.exec_())
