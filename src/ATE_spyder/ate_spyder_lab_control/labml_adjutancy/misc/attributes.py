"""Create methode or attributes from a dictionary.

Call the methode read() for get, or write() for set attribute, with some checks before and after calling.

:Date: |today|
:Author: Zlin526F

"""

from labml_adjutancy.misc.mqtt_client import mylogger
from enum import Enum
import hightime
from labml_adjutancy.misc.common import str2num

__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"


logger = mylogger()


class create_attributes(object):
    """Create a methode or an attributes from a dictionary.

    :Date: |today|
    :Author: Zlin526F

    Call the methode read() for get, or write() for set attribute, with some checks before and after calling.

    Syntax from this dictonary to create the attributes:

    | {attribute/methode name : (Device command for read/write) , range, call functions}

    :attribute/methode name:
       your favorite name for the attribute/methode

    :Device command:
       * the read nd write command for the instance, e.q. 'TMPA?' or None.
       * or the methode name e.q. 'current_level_autorange'.
    :range:
       could be None, Enum or range value (integer or float)
    :call functions:
       before or after the instance write or read, you can define a functionname, which will be call and manipulate the get/set value

          * 'gb'=  get_before()      -> get, call function before the read instance. Do something before the read instance
          * 'ga'=  get_after()       -> get, call function after the read instance. Do something with the value, e.q. translate from hex to integer
          * 'gac'= get_after_check() -> get, call function after the read instance and check.
          * 'sb'=  set_before()      -> set, call function before write instance
          * 'sac'= set_after_check() -> set, call function after check, before write instance
          * 'sa'=  set_after         -> set, call function after write instance

          The functions itself, have to return the modified value or None if value are not  modified.
          If you get an error in the function, than you should set your return value to ATTR_ERROR


    Example 1:
       >>> class test(create_attributes)
       >>>
       >>>     properties = {'bitTime' :        (('?bt',  'sbt'),     [10, 3400],    {'ga': '_hex2dec(value)', 'sac': '_dec2hex(value)', 'sa': 'readresult(0)'}),
       >>>                   'airtemp' :        (('TMPA?', None),     None,          None),
       >>>                   'dutsensortype' :  (('DSNS?','DSNS'),    [0,4],         None),
       >>>                   'blaba' :          (('BLAA?','BLAB'),    [1.0,4.7];     None),
       >>>                   'compressor' :     (('COOL?','COOL'),   'Compressor',   {'sac': '_compressor(value)'}),
       >>>                  }
       >>>
       >>> class Compressor(Enum) :
       >>>     off= 0
       >>>     on = 1
       >>>
       >>>     def setup_inst(self):
       >>>         self.createattributes(self.properties)    # <-- add this line in your setup_inst
       >>>         super().setup_inst()

    ==> this will create following attributes:
       >>> # create attribute bitTime with get/set :
       >>> self.bitTime             # get attribute : call the methode inst.query('?bt')
       MEASURE - 'yourDevice'.bitTime == 480
       480
       >>> self.bitTime = 20   # set attribute : check if value is integer, and 10<=value<=3400,
       >>>                     # if ok than call inst.write('sbt')
       MEASURE - 'yourDevice'.bitTime := 20

       >>> # create attribute airtemp with get:
       >>> self.airtemp
       MEASURE - 'yourDevice'.airtemp == 22.2
       22.2

       >>> # create attribute dutsensortype with get/set :
       >>> self.dutsensortype     # write inst.query('DSNS?'), return with int(value)
       MEASURE - 'yourDevice'.dutsensortype == 0
       0
       >>> self.dutsensortype = 3  # check if value is integer, and 0<=value<=4,
       >>>                         # if ok than inst.write('DSNS 3')
       MEASURE - 'yourDevice'.dutsensortype := 3
       3
       >>> self.dutsensortype = 5
       ERROR - 'yourDevice'.dutsensortype := 5 outside limits, choose [0, 4]

       >>> # create attribute blaba  with get/set :
       >>> self.blaba         # inst.query('BLAA?'), return with float(value)
       MEASURE - 'yourDevice'.blaba == 3.0
       3.0
       >>> self.blaba = 3.4   # check if value is float, and 1.0<=value<=4.7,
       >>>                    # if ok than inst.write('BLAB')
       MEASURE - 'yourDevice'.blaba := 3.4
       3.4

       >>> # create attribute compressor with get/set and values is Enum:
       >>> self.compressor               #inst.query('COOL?'), return with the enum Compressor
       MEASURE - 'yourDevice'.compressor == Compressor.on
       <Compressor.on: 1>
       >>> compressor = Compressor.on # check if value in Compressor
       >>>                            # if ok than call _compressor(Compressor.on), and than inst.write('COOL 1'),
       MEASURE - 'yourDevice'.compressor := Compressor.on
       >>> compressor = 'on'          # shorter but the same as before
       MEASURE - 'yourDevice'.compressor := Compressor.on
       >>> compressor = 1             # also possible
       MEASURE - 'yourDevice'.compressor := Compressor.on

    Example 2, for calling inst.methode (none read/write):
       >>> properties = {'auto_zero':           ('auto_zero',               'backend.AutoZero',           {'sac': 'checkstate(uncommitted)'}),
       >>>               'aperture_time_units': ('aperture_time_units',     'backend.ApertureTimeUnits',  {'sac': 'checkstate(uncommitted)'}),
       >>>               'aperture_time':       ('aperture_time',            None,                        {'sac': 'checkstate(uncommitted)'}),
       >>>               }

    see also
       * the class :func:`~instruments.smu.tti.base_tti.TTI` :download:`instruments/smu/tti/base_tti <../../../instruments/smu/tti/base_tti.py>`
         show the usage to create many attributes and connect to a smu with one or more channels
       * the class :func:`~instruments.thermostreamer.mpi_ta5k.MPI_TA5K` :download:`instruments/thermostreamer/mpi_ta5k <../../../instruments/thermostreamer/mpi_ta5k.py>`
         show the usage to create many attributes and connect to a thermostreamer
       * the class :func:`~instruments.smu.natinst.pxie41xx` use this class to call inst.methods_name
         :download:`instruments/smu/natinst/pxie41xx.py <../../../instruments/smu/natinst/pxie41xx.py>`

    Tip:
       if your device has no read/write instance, than overwrite the method  _call_instance()
       Example:
          >>> def _call_instance(self, function, rw, value=None):
          >>>     if rw == "wr":
          >>>         self.ch[self.channel].__setattr__(function, value)        # for set attribute
          >>>     elif rw == "rd":
          >>>         value = self.ch[self.channel].__getattribute__(function)  # for get attribute
          >>>     return (value)

    Note:
       necessary Methods in the class above (if you don't overwrite the method _call_instance()):
          >>> def read(self):
          >>>     value = self.inst.read()  # your code for instance read
          >>>     return value
          >>>
          >>> def write(self,value):
          >>>     self.instance.write(value)  # your code for instance write
          >>>
    """

    _attributes = {}
    _ATTRERROR = {
        1: "{!r}.{} always exist, couldn't create this attribute",  # error
        2: "{!r}.{} := {} not possible, parameter have no set!",
        3: "{!r}.{} has no proberty {}, choose {}",
        4: "{!r}.{} := {} outside limits, choose {}",
        5: "{!r}.{}: {}",
        6: "{!r} last command was {} := {}",
        10: " ",  # warning
        20: " ",  # info
        30: "{!r}.{} == {}  (shadow attribute)",  # measure
        31: "{!r}.{} := {}",
        32: "{!r}.{} == {}",
    }

    def __init__(self):
        self._attributes = {}
        self.ATTR_ERROR = "ATTRIBUTE_ERROR"
        """if something wrong with your called methode, than set the result to self.ATTR_ERROR """
        self.attrLast = ""
        """last set/get attribute name."""
        self.attrLastvalue = None
        """last set attribute value."""

    def createattributes(
        self, dictionary, parent=None, child=None, childname=""
    ):
        """
        Create attributes or methods from a dictionary.

        syntax from the dictionary see example in the class documentation.

        Args:
            dictionary (dict):
                {attribute/methode name : (Device command for read/write) , range, call functions}.

        Returns:
            None.

        """
        if child is not None:
            myparent = self if parent is None else parent
            childname = child if childname == "" else childname
            object.__setattr__(myparent, child, Child(myparent, childname))
            parent = getattr(self, child)
            childname = childname if childname == "" else childname + "."
        if self._attributes == {} or child is not None:
            for attribute in dictionary.copy():
                myparent = self if parent is None else parent
                index = 0
                splitattribute = attribute.split(".")
                for partattr in splitattribute:
                    if hasattr(myparent, partattr):
                        pass
                    elif index < len(splitattribute) - 1:
                        object.__setattr__(
                            myparent,
                            partattr,
                            Child(self, f"{childname}{partattr}"),
                        )  # create a child
                        myparent._attributes[
                            partattr
                        ] = "_attrChild"  # and mark it in the _attributes
                    else:
                        object.__setattr__(myparent, partattr, "noinit")
                        myparent._attributes[partattr] = dictionary[attribute]
                    if index < len(splitattribute) - 1:  # has a child
                        myparent = getattr(myparent, partattr)
                    index += 1
            self._attributes = dictionary

    def __setattr__(self, attr, value):
        """Set attribute.

        this methode will be called automatically if you set an attribute.
        Checks whether the atribute is in the attributes-directory.
        If so, the associated functions are called.

        Args:
            ttr (str): attribute name.
            value (anything): setting value for the attribute.

        Returns:
            None.

        """
        if hasattr(self, "_attributes") and attr in self._attributes:
            self.attrLast = attr
            self.attrLastvalue = value
            orgvalue = value
            fparam = self._attributes[
                attr
            ]  # search in the directory the accociated function parameter
            error = False
            if isinstance(fparam, tuple) and fparam[1] is None:
                self._attrlogger(2, attr, value)
                return
            error, value = self._call_function("sb", fparam, value)
            if error:
                return
            error, value = self._validateattributes(
                attr, value, fparam[1]
            )  # check attributes
            if error:
                return
            error, value = self._call_function("sac", fparam, value)
            if error:
                return
            self._call_instance(
                self._get_functionname(fparam, "wr"), "wr", value
            )  # call write function
            error, result = self._call_function("sa", fparam, value)
            if error:
                return
            if isinstance(fparam[0], tuple) and fparam[0][0] is None:
                super(__class__, self).__setattr__(
                    "_" + attr, value
                )  # no read available -> set shadow attribute
            self._attrlogger(31, attr, orgvalue)  # get measure info
            if hasattr(self, "mqtt_enable") and self.mqtt_enable:
                if isinstance(value, Enum):
                    self.publish_get(attr, value.name)
                else:
                    self.publish_get(attr, orgvalue)
            super(__class__, self).__setattr__(f"{attr}_cache", value)
        else:
            super(__class__, self).__setattr__(attr, value)

    def __getattribute__(self, attr):
        """Get attribute.

        this methode will be called automatically if you get an attribute.
        Checks whether the atribute is in the attributes-directory.
        If so, the associated functions are called.

        Args:
            attr (str): attribute name.

        Returns:
            value (anything): getting value the inst.read()

        """
        if (
            attr != "__class__"
            and attr != "mqtt_list"
            and attr != "_attributes"
            and attr in self._attributes
            and self._attributes[attr] != "_attrChild"
        ):
            self.attrLast = attr
            self.attrLastvalue = None
            fparam = self._attributes[attr]
            if isinstance(fparam, tuple) and fparam[0] is None:
                value = super(__class__, self).__getattribute__("_" + attr)
                self._attrlogger(30, attr, value)
                return value
            error, value = self._call_function("gb", fparam, None)
            if error:
                return
            value = self._call_instance(
                self._get_functionname(fparam, "rd"), "rd"
            )  # get the read function and make the call
            error, value = self._call_function("ga", fparam, value)
            if error:
                return
            if type(fparam[1]) == dict:
                # keys = [key for key, val in fparam[1].items() if val == value]
                # value = str(keys)
                # print(f'{self.attrLast} = {keys}')

                for key, val in fparam[1].items():
                    if value == val:
                        value = key
                # else:
                #     print(f'{self.attrLast} = {value}')
            elif type(value) == hightime.timedelta:
                value = value.total_seconds()
            elif (
                fparam[1] is not None
                and value is not None
                and isinstance(fparam[1][0], int)
            ):  # is range(=fparam[1]) an integer?
                value = int(float(value))
            elif (
                fparam[1] is not None
                and value is not None
                and isinstance(fparam[1][0], float)
            ):  # is range a float?
                value = float(value)
            else:
                if not isinstance(
                    value, (float, int)
                ):  # if value is an string ?
                    value = str2num(value)
                if not isinstance(
                    value, Enum
                ):  # is value an Enum?  -> do nothing
                    check, enum = self._ifenum(
                        fparam[1]
                    )  # check if range an enum?
                    if check:
                        error = True  # check if value in enum
                        for name in enum:
                            if value == name.value:
                                value = name
                                error = False
                        if error:
                            self._enum_error(attr, value, enum)
            error, value = self._call_function("gac", fparam, value)
            if error:
                return
            self._attrlogger(32, attr, value)
            if hasattr(self, "mqtt_enable") and self.mqtt_enable:
                if isinstance(value, Enum):
                    self.publish_get(attr, value.name)
                else:
                    self.publish_get(attr, value)
            super(__class__, self).__setattr__(f"{attr}_cache", value)
        else:
            value = super(__class__, self).__getattribute__(attr)
        return value

    def _attrlogger(self, msgnr, *kwargs):
        # if self.instName[-3:] == '[0]':
        # instName_short = self.instName[:len(self.instName) - 3]
        # else:
        # instName_short = self.instName
        msg = self._ATTRERROR[msgnr].format(self.instName, *kwargs)
        if msgnr < 10:
            logger.error(msg)
        elif msgnr < 20:
            logger.warning(msg)
        elif msgnr < 30:
            logger.info(msg)
        elif msgnr < 40:
            logger.measure(msg)
        elif msgnr < 50:
            logger.error("error: message not implemented !")

    def _enum_error(self, function_name, val, enum):
        msg = ""
        for values in enum:
            msg += "/" + values.name
        self._attrlogger(3, function_name, val, msg[1:])

    def _validateattributes(self, attr, value, validaterange=None):
        """Check if value in the validate range.

        Args:
            attr (string): attribute name.
            value (TYPE):  None, list or enum.
            validaterange (TYPE, optional): DESCRIPTION. Defaults to None.

        Returns:
            error (bool): True or False.
            value (anything): orginal value, or the enum.
        """
        error = False
        is_enum, enum = self._ifenum(
            validaterange
        )  # check if validaterange an enum
        if validaterange is None:
            return error, value
        elif isinstance(validaterange, list):
            if value < validaterange[0] or value > validaterange[1]:
                error = True
                self._attrlogger(4, attr, value, validaterange)
        elif type(validaterange) == dict:
            if value in validaterange:
                value = validaterange[value]
            else:
                error = True
                self._attrlogger(
                    3, attr, value, validaterange.keys()
                )  # Todo : how can i remove the 'dict_keys' in the output?
        elif is_enum:
            error = True
            if isinstance(value, str):  # check if string in enum
                for name in enum:
                    if value == name.name:
                        value = name
                        error = False
            elif isinstance(value, enum):
                error = False
            else:
                for name in enum:
                    if value == name.value:
                        value = name
                        error = False
            if error:
                self._enum_error(attr, value, enum)
        return error, value

    def _ifenum(self, value):
        """Check if type(value)==enum.

        enum have to be in the path of self , e.q: self.test(value='test') or self.backend.test (value='backend.test')

        Args:
            value (anything): the value which want to be checked.

        Returns:
            bool: True or False.
            enum: the enum, if value is enum, otherwise None.

        """
        result = False
        enum = None
        if value is None or isinstance(value, (list, float, int)):
            return False, None
        elif isinstance(value, str):
            value = value.split(".")
            enum = self.__getattribute__(value[0])
            if len(value) > 1:
                for i in range(1, len(value)):
                    enum = enum.__getattribute__(value[i])
            result = True
        #        elif hasattr(self,value):
        #            enum=self.__getattribute__(value)
        #            result=True
        return result, enum

    def _get_functionname(self, dictline, rw):
        if isinstance(dictline[0], tuple):
            if rw == "wr":
                result = dictline[0][1]
            elif rw == "rd":
                result = dictline[0][0]
        else:
            result = dictline[0]
        return result

    def _call_function(self, typ, fparam, value=None):
        found = -1
        result = value
        error = 0
        if isinstance(fparam[2], dict) and typ in fparam[2]:
            functioncall = fparam[2][typ]  # get the function call
            found = 1
        if found != -1:
            function = functioncall.split("(")[0]  # seperate function
            values = functioncall.split("(")[1][:-1]  # seperate arguments
        if found != -1 and values.find("value") > -1:
            if values.find(",") > -1:
                logger.error(
                    "attributes.create_attributes error in {}, functioncall with more than one values ({}) are not implemented yet, please investigate".format(
                        values, fparam
                    )
                )
                values = values.replace("value", str(value))
            else:
                values = value
        if found != -1:
            try:
                if values is None:
                    result = getattr(self, function)()
                else:
                    result = getattr(self, function)(values)
                if result is None:
                    result = value
                elif result == "ERROR":
                    self._attrlogger(6, self.attrLast, self.attrLastvalue)
                    return True, value
            except Exception as e:
                error = self.ATTR_ERROR
                self._attrlogger(5, function, e)
        return error, result

    def _call_instance(self, function, rw, value=None):
        """
        Read/write interface to the instance.

        if your device have no read/write than overwrite this function in your class.
        see e.q. instruments/instruments/smu/natinst/base_natinst.py

        Args:
            function (methode): method which will be call.
            rw (str):
               * 'wr' -> inst.write(function,value)
               *'rd' -> inst.write(function), value=inst.read()

            value (anything, optional):
                only necessary for 'wr', your value which will be write

        Returns:
            value (str):
                DESCRIPTION.

        """
        if isinstance(value, Enum):
            value = value.value
        if rw == "wr":
            self.write("{}{}".format(function, value))
        elif rw == "rd":
            self.write("{}".format(function))
            value = self.read()
            return value


class Child(create_attributes):
    def __init__(self, root, instName):
        self.root = root
        self.instName = instName
        self._attributes = {}

    def write(self, msg):
        self.root.publish_get(
            f"{self.instName}.{self.attrLast}", self.attrLastvalue
        )

    def read(self):
        cache = f"{self.attrLast}_cache"
        value = getattr(self, cache) if hasattr(self, cache) else None
        self.root.publish_get(f"{self.instName}.{self.attrLast}", value)
        return value
