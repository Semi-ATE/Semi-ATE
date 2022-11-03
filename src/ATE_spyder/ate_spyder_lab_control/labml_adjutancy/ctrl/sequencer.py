# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: C. Jung

INFO:
    icons von https://github.com/spyder-ide/qtawesome
        conda install qtawesome

TODO:

"""
import os
from PyQt5 import QtWidgets, QtCore
import qtawesome as qta
from labml_adjutancy.misc.common import str2num

__author__ = "Zlin526F"
__copyright__ = "Copyright 2021, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.1"


class Sequencer(object):
    """ """

    # CHECK_OFFSET_X = 3
    # CHECK_WIDTH = 17
    # CB_OFFSET_X = CHECK_WIDTH + 5
    # CB_OFFSET_Y = 20
    # CB_SPACE_X = 5
    # CB_SPACE_Y = 20
    # CB_WIDTH = 95
    # BLOCK_SPACE_Y = 20
    # INNERBLOCK_SPACE_Y = 5

    def __init__(self, parent, gui):
        """Initialise the class semi_control."""
        self.parent = parent
        self.gui = gui
        self.gui.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.paraBox = []
        self.choicesParameter = []
        self._parameters = []
        # self.count = 0
        self.finish = False

    def load(self, path, test_program_name):
        from labml_adjutancy.misc.jsondict import JsonDict

        # for index in range(1, len(self.paraBox)):
        #     self.remove_paraBox()
        self.parent.logger.debug(
            f"    Sequencer load path = {path}, name= {test_program_name}"
        )
        print(f"    Sequencer load path = {path}, name= {test_program_name}")
        # open the jsonfile for the test_program_name and collect all information about the shmoo parameter
        tests = JsonDict(
            os.path.join(
                path,
                "definitions",
                "sequence",
                f"sequence{test_program_name}.json",
            )
        )
        choicesParameter = {}
        if not hasattr(tests, "contents"):
            return
        for test in tests.contents.values(key="test"):
            myparameter = []
            mytest = tests.contents.index("test", test)
            if type(mytest) != list:
                mytest = [mytest]
            input_paramters = mytest[0].definition.input_parameters

            is_selected = False
            for index in range(0, len(mytest)):
                is_selected = (
                    True
                    if mytest[index].definition.is_selected
                    else is_selected
                )
            myparameter.append(is_selected)
            for key in input_paramters.keys():
                if (
                    hasattr(input_paramters[key], "shmoo")
                    and input_paramters[key].shmoo
                    and key not in choicesParameter
                ):
                    myparameter.append(key)
            if myparameter != []:
                instance = mytest[0].definition.description
                choicesParameter[instance] = myparameter
        self.choicesParameter = choicesParameter
        self.parent.logger.debug(
            f"      Sequencer choices parameter: {choicesParameter}"
        )
        parameters = (
            self._parameters
            if len(self.parameters) == 0 or self.parameters[0][1] == ""
            else self.parameters
        )
        for index in range(0, len(self.paraBox)):
            self.remove_paraBox()
        self.create_paraBox()
        self.parent.logger.debug(f"      Sequencer settings: {parameters}")
        index = 0
        for value in parameters:
            if index == 0:
                self.add2Parameters(self.paraBox[0].cb, self.choicesParameter)
            else:
                self.create_paraBox()
            self.paraBox[index].check.setChecked(value[0])
            cbindex = self.paraBox[index].cb.findText(value[1])
            if cbindex >= 0:
                self.paraBox[index].cb.setCurrentIndex(cbindex)
            else:
                cbindex = 0
            self.paraBox[index].edit.setText(value[2])
            self.paraBoxValues = (value[2], index)
            for shift in range(0, value[3]):
                self.move_paraBox(index, 1)
            index += 1

    @property
    def paraBoxValues(self):
        mybox = self.paraBox[self.paraboxindex]
        try:
            mybox.value = (
                mybox.values[mybox.index] if len(mybox.values) > 0 else ""
            )
        except Exception:
            mybox.value = ""
        mybox.lvalue.setText(str(mybox.value))
        return mybox.value

    @paraBoxValues.setter
    def paraBoxValues(self, parameter):
        from labml_adjutancy.misc.common import arange

        boxindex = parameter[1]
        parameter = parameter[0]
        mybox = self.paraBox[boxindex]
        values = arange(parameter)
        if type(values) in (int, float):
            values = [values]
        mybox.values = values
        mybox.index = 0
        mybox.last = False
        self.paraboxindex = boxindex
        self.paraBoxValues

    def getnextvalue(self, boxindex):
        """result the actual value and increment the index count"""
        mybox = self.paraBox[boxindex]
        self.paraboxindex = boxindex
        result = self.paraBoxValues
        if not hasattr(mybox, "index"):
            return result
        mybox.index += 1
        if mybox.index < (len(mybox.values)):
            mybox.last = False
        else:
            mybox.index = 0
            mybox.last = True
        self.paraBoxValues
        return result

    def setfirstvalue(self):
        for boxindex in range(0, len(self.paraBox)):
            mybox = self.paraBox[boxindex]
            self.paraboxindex = boxindex
            mybox.index = 0
            mybox.last = False
            self.paraBoxValues

    def add2Parameters(self, combobox, table):
        combobox.clear()
        parameters = []
        for test in table:
            for parameter in table[test]:
                if type(parameter) == bool:
                    selectable = parameter
                    continue
                if parameter not in parameters:
                    combobox.addItem(parameter)
                    if not selectable:
                        combobox.setItemIcon(
                            combobox.count() - 1,
                            qta.icon(
                                "ei.remove-sign",
                                color="white",
                                scale_factor=1.0,
                                color_active="orange",
                            ),
                        )
                    parameters.append(parameter)
        return

    def create_paraBox(self):
        BOX_OFFSET_X = 3
        BOX_OFFSET_Y = 10
        BOX_HEIGHT = 60
        BOX_WIDTH = 155
        INNERBLOCK_OFFSET_X = 3
        INNERBLOCK_OFFSET_Y = 10
        CB_WIDTH = 95
        CB_HEIGHT = 16

        index = len(self.paraBox)
        self.paraBox.append(QtWidgets.QGroupBox(self.gui))
        pb = self.paraBox[-1]
        pb.setGeometry(
            QtCore.QRect(
                BOX_OFFSET_X,
                BOX_OFFSET_Y + index * (BOX_HEIGHT),
                BOX_WIDTH,
                BOX_HEIGHT,
            )
        )
        pb.show()
        pb.check = QtWidgets.QCheckBox(pb)
        pb.check.setGeometry(
            QtCore.QRect(
                INNERBLOCK_OFFSET_X,
                INNERBLOCK_OFFSET_Y,
                pb.check.geometry().height(),
                pb.check.geometry().height(),
            )
        )
        pb.check.show()
        pb.cb = QtWidgets.QComboBox(pb)
        pb.cb.setGeometry(
            QtCore.QRect(
                pb.check.geometry().x() + pb.check.geometry().width() - 8,
                INNERBLOCK_OFFSET_Y,
                CB_WIDTH,
                CB_HEIGHT,
            )
        )
        pb.cb.show()
        pb.edit = QtWidgets.QLineEdit(pb)
        pb.edit.setGeometry(
            QtCore.QRect(
                pb.cb.geometry().x(),
                pb.cb.geometry().x() + INNERBLOCK_OFFSET_Y,
                CB_WIDTH,
                CB_HEIGHT,
            )
        )
        pb.edit.setToolTip(
            "Syntax:\n 4:6  -> loop from 4 til 6 step 1\n 4.5:6.0:0.1 -> loop from 4.5 til 6.0 step 0.1\n 4.6,6.5,8.3 -> seperate values 4.6,4.6,6.5,8.3/n "
        )
        pb.edit.editingFinished.connect(lambda: self.editfinish(index))
        pb.edit.show()
        pb.lvalue = QtWidgets.QLabel(pb)
        pb.lvalue.setGeometry(
            QtCore.QRect(
                pb.edit.geometry().x()
                + pb.edit.geometry().width()
                + INNERBLOCK_OFFSET_X,
                pb.edit.geometry().y(),
                30,
                CB_HEIGHT,
            )
        )
        pb.lvalue.setText("")
        pb.lvalue.show()
        pb.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        pb.rb_addAction = QtWidgets.QAction(pb)
        pb.rb_addAction.setText("add sequencer")
        pb.setToolTip("choose parameter \nor left mouse button for menu")
        pb.addAction(pb.rb_addAction)
        if index > 0:
            pb.rb_minusAction = QtWidgets.QAction(pb)
            pb.rb_minusAction.setText("remove sequencer")
            pb.addAction(pb.rb_minusAction)
            pb.rb_minusAction.triggered.connect(self.remove_paraBox)
            pb.rb_identAction = QtWidgets.QAction(pb)
            pb.rb_identAction.setText("indent")
            pb.rb_identAction.setToolTip("for creating nested loops")
            pb.addAction(pb.rb_identAction)
            pb.rb_identAction.triggered.connect(
                lambda: self.move_paraBox(index, 1)
            )
            pb.rb_marchAction = QtWidgets.QAction(pb)
            pb.rb_marchAction.setText("march")
            pb.addAction(pb.rb_marchAction)
            pb.rb_marchAction.triggered.connect(
                lambda: self.move_paraBox(index, -1)
            )
            pb.rb_marchAction.setVisible(False)
        pb.rb_addAction.triggered.connect(lambda: self.create_paraBox())
        self.add2Parameters(pb.cb, self.choicesParameter)
        if index > 0:
            self.paraBox[-2].rb_addAction.setVisible(
                False
            )  # only last parabox has the add item
        if index > 1:
            self.paraBox[-2].rb_minusAction.setVisible(False)
        pb.level = 0
        return

    def remove_paraBox(self):
        pb = self.paraBox[-1]
        if len(self.paraBox) >= 2:
            self.paraBox[-2].rb_addAction.setVisible(True)
        if len(self.paraBox) > 2:
            self.paraBox[-2].rb_minusAction.setVisible(True)
        pb.check.destroy()
        pb.check.deleteLater()
        pb.cb.destroy()
        pb.cb.deleteLater()
        pb.edit.destroy()
        pb.edit.deleteLater()
        pb.rb_addAction.deleteLater()
        pb.destroy()
        pb.deleteLater()
        self.paraBox.pop()

    def move_paraBox(self, index, inc):
        pb = self.paraBox[index]
        pb.level += inc
        pb.setGeometry(
            pb.geometry().x() + inc * 10,
            pb.geometry().y(),
            pb.geometry().width(),
            pb.geometry().height(),
        )
        new_width = pb.geometry().x() + pb.geometry().width() + 2
        self.parent.logger.debug(
            f"      width = {self.gui.geometry().width()}, new width= {new_width}"
        )
        if self.gui.geometry().width() < new_width:
            self.gui.setGeometry(
                self.gui.geometry().x(),
                self.gui.geometry().y(),
                new_width,
                self.gui.geometry().height(),
            )  # TODO: isn't running :-(
            self.gui.updateGeometry()
        if pb.level > 0:
            pb.rb_marchAction.setVisible(True)
        else:
            pb.rb_marchAction.setVisible(False)

    def editfinish(self, index):
        newvalues = self.paraBox[index].edit.text()
        self.parameters[index][2] = newvalues
        self.paraBoxValues = (newvalues, index)
        self.finish = False
        # self.parent.logger.debug(f'      editfinish {newvalues}')
        self.parent.saveconfig()

    @property
    def parameters(self):
        values = []
        for index in range(0, len(self.paraBox)):
            pb = self.paraBox[index]
            values.append(
                [
                    pb.check.isChecked(),
                    pb.cb.currentText(),
                    pb.edit.text(),
                    pb.level,
                ]
            )
        return values

    @parameters.setter
    def parameters(self, values):
        self.parent.logger.debug(f"Sequencer set parameters:={values}")
        self._parameters = values

    def getnext(self, start=True):
        parameters = self.parameters
        index = 0
        result = []
        foundnewvalue = False
        incloop = -2
        self.parent.logger.debug(f"Sequencer parameters = {parameters}")
        self.parent.logger.debug(
            f"     self.choicesParameter = {self.choicesParameter}"
        )
        if self.finish:
            self.setfirstvalue()
            self.finish = False
            return "finish", True
        for index in range(len(parameters), 0, -1):
            name = parameters[index - 1][1]
            if not parameters[index - 1][0]:  # enabled?
                continue
            if not foundnewvalue:  # inc the loop
                value = str2num(self.getnextvalue(index - 1))
                if self.paraBox[index - 1].last:
                    self.parent.logger.debug("     inc loop before ")
                    incloop = index - 2
                foundnewvalue = True
            elif (
                foundnewvalue and not self.paraBox[index - 1].last
            ):  # get old value
                self.paraboxindex = index - 1
                value = self.paraBoxValues
            else:
                self.parent.logger.debug("     shmoo finish")
                self.finish = True
                result = "finish"
                break
            if value == "":
                continue
            if type(value) == str:
                self.parent.logger.error(
                    f"     parameter, from {name}:={value} is not valid "
                )
                result = []
                break
            for test in self.choicesParameter:
                if (
                    name in self.choicesParameter[test]
                    and self.choicesParameter[test][0]
                ):
                    result.append(
                        {
                            "parametername": f"{test}.{name}",
                            "value": f"{value}",
                        }
                    )
        last = self.finish if foundnewvalue else True
        if incloop > -1:
            self.getnextvalue(incloop)
        elif incloop == -1:
            self.finish = True
        self.parent.logger.debug(
            f"     Sequencer getnext: {result}, {self.finish}"
        )
        # last = self.finish
        # if self.finish:
        #    self.parent.logger.debug('     shmoo finish, set first values')
        #    self.setfirstvalue()
        return result, last
