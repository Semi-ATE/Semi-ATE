# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:18:05 2021

@author: jung
"""
import numpy as np
import ast
import copy
from ate_common.logger import LogLevel


def str2num(value, base=10, default=""):
    """translate str to numeric value.

    if value start with 0x than it is a hex number.
    if value start with 0b than it is a binary number.
    if value = '' -> set to default value
    """
    #    if type(value) in [bool, int, float, np.int32, np.float64]:
    if type(value) != str:
        return value
    value = value.strip()
    if value == "" or value is None:
        value = default
        return
    if value.find("0x") == 0:
        base = 16
    elif value.find("0b") == 0:
        base = 2
    try:
        return int(value, base)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def multistrcall(self, commandlist):
    #    if type(command) == str:
    #        command = command.split(',')
    #        result = []
    for cmd in commandlist:
        strcall(self, cmd, commandlist[cmd][0])


def strcall(self, command, value=None, typ=None, mqttcheck=False):
    """
    make a call from the command:
        result = common.strcall(tcc, 'regs.HW_ID.read()')
        result = common.strcall(self, 'smu.voltage=5.3' , mqttcheck=True)'
        result = common.strcall(self, 'smu.blabla()', 4.7, mqttcheck=True)'
    needs the the logger from self

    Parameters
    ----------
    command : string

    value : int/float/list, optional
        DESCRIPTION. The default is None.
    typ : None/'set'/'get'
        DESCRIPTION. If the command an mqtt-command, than you have coice if it is settable or gettable
    mqttcheck : True/False, optional
        DESCRIPTION. The default is False. Check if the command is in the mqtt_list. If not, the command will not be execute

    Returns
    -------
    myresult : the result from the call
    """
    if self is None:
        print("strcall: initialise missing, self is None -> do nothing")
        return
    parent = self
    instname = self.instName + "." if hasattr(self, "instName") else ""
    mqttcmd = command
    if mqttcmd.find("(") > 0:
        mqttcmd = mqttcmd[: mqttcmd.find("(") + 1] + ")"
        typ = "func"
    if mqttcheck and mqttcmd not in ["mqtt_status"] + parent.mqtt_list:
        instname = parent.instName if hasattr(self, "instName") else parent
        print(f"   Warning strcall: {instname} get {mqttcmd}, but it is not in the mqtt_list")
        return "ERROR"
    if typ == "set":
        value = tuple(value) if type(value) == list else str2num(value)
        evalue = f'"{value}"' if isinstance(value, str) else value
        try:
            exec(f"self.{command} = {evalue}")
            print(f"   self.{instname}{command} := {value}")
        except Exception as ex:
            print(f"   strcall error: 'self.{instname}{command} := {value}' get an exception: {ex}")
        return None
    elif typ == "get":
        try:
            value = eval(f"self.{command}")
            print(f"   self.{instname}{command} == {value}")
        except Exception as ex:
            print(f"   strcall get error: 'self.{instname}{command}' get an exception: {ex}")
        return value
    elif typ == "func":
        command = command[: command.find("(")]
        para = ""
        if type(value) == list:
            for val in value:
                para += f"'{val}',"
            para = para[:-1]
        elif type(value) == str and value != "":
            para = f"'{value}'"
        elif para is not None:
            para = value
        try:
            exec(f"self.{command}({para})")
            print(f"   self.{instname}{command}({para})")
        except Exception as ex:
            print(f"   strcall error func: self.{instname}{command}({para}), get an exception: {ex}\n      typ(value)={type(value)}) ")
        return None


def convertExpr2Expression(Expr):
    Expr.lineno = 0
    Expr.col_offset = 0
    result = ast.Expression(Expr.value, lineno=0, col_offset=0)
    return result


def exec_with_return(code, parent=None):
    """
    Exec with return

    implement from https://stackoverflow.com/questions/33409207/how-to-return-value-from-exec-in-function

    Parameters
    ----------
    code : TYPE
        DESCRIPTION.
    parent : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    code_ast = ast.parse(code)

    init_ast = copy.deepcopy(code_ast)
    init_ast.body = code_ast.body[:-1]

    last_ast = copy.deepcopy(code_ast)
    last_ast.body = code_ast.body[-1:]

    exec(compile(init_ast, "<ast>", "exec"), globals())
    if type(last_ast.body[0]) == ast.Expr:
        return eval(compile(convertExpr2Expression(last_ast.body[0]), "<ast>", "eval"), globals(), {"self": parent})
    else:
        exec(compile(last_ast, "<ast>", "exec"), globals(), {"self": parent})


def arange(myitems):
    """create from 'myitems' an array like in matlab.

    e.q. "18:-1:6:"
    "18:-1:6, 5.9:-0.1:4.1"
    "18:-1:6, 5.9:-0.1:4.1, 7, 9"

    also possible: "18:6:-1"
    """
    result = None
    if myitems.find(",") > 0:
        delimiter = ","
    elif myitems.find(";") > 0:
        delimiter = ";"
    else:
        delimiter = " "
    for item in myitems.split(delimiter):
        if item.find(":"):
            split = item.split(":")
            start = str2num(split[0])
            if len(split) == 1:
                myresult = start
            else:
                if len(split) == 2:
                    inc = 1
                    stop = str2num(split[1])
                else:
                    stop = str2num(split[2])
                    inc = 1 if len(split) < 3 else str2num(split[1])
                if inc > stop:
                    temp = inc
                    inc = stop
                    stop = temp
                if len(split) == 2 and start > stop:
                    inc = -1
                try:
                    correctur = inc  # to calculate like matlab 3:6:1 -> 3,4,5,6  normaly in python 3,4,5
                    myresult = np.arange(start, stop + correctur, inc)
                except Exception:
                    myresult = f"Syntax error in {item}"
        else:
            myresult = item
        result = myresult if result is None else np.append(result, myresult)
    return result


def choice(arg, myargs):
    """
    check if arg in myargs

    Parameters
    ----------
    arg : string
        DESCRIPTION.
    myargs : array of strings
        DESCRIPTION.

    Returns
    -------
    bool
        True/False
    """
    if arg not in myargs:
        print(f"checkargs: attribute {arg} not valid")
        return False
    return True


def checkargs(myargs, **kwargs):
    for arg in kwargs:
        if arg not in myargs:
            print(f"checkargs: attribute {arg} not valid")


def check(msg, target, actual, tolerance=0, mask=None):
    """
    Compare target with the acutal value.

     Parameters
     ----------
     msg : TYPE
         DESCRIPTION.
     target : TYPE
         the target value
             if str and start with 0x than each X is a 4bit mask
             if str and start with 0b than each x is a 1bit mask
     actual : TYPE
         the actual value.
     tolerance : float or integer, optional
         DESCRIPTION. The default is 0.
     mask : Integer or None(default)

     Returns
     -------
     error : bool
         True : target = actual value
         False : target != actual value.

    """
    error = 0
    if type(target) == str and len(target) > 3:
        if target[1] == "x":  # it is a hex number with mask information
            target = target.replace("_", "", len(target))
            mask = 0
            for index in range(2, len(target)):
                mask = (mask << 4) + (15 if target[index] != "X" else 0)
            target = str2num(target.replace("X", "0", len(target)))
        elif target[1] == "b":  # it is a bin number with mask information
            target = target.replace("_", "", len(target))
            mask = 0
            for index in range(2, len(target)):
                mask = (mask << 1) + (1 if target[index] != "x" else 0)
            target = str2num(target.replace("x", "0", len(target)))
    if type(actual) != type(target):
        error = 1
        msg = f"{msg}  diffenrent type from target={type(target)}  and actual=(type(actual) -> couldn't check')"
    elif type(actual) is list:
        if len(target) != len(actual):
            print("Warning: len() from target list (={len(target)}) <-> actual list ({len(actual)}), are different!!!!")
        for index in range(0, len(actual)):
            if actual[index] != target[index]:
                print("ERROR: Wrong value at adr 0x{:2x}, read 0x{:x}, expected 0x{:x} ".format(index, actual[index], target[index]))
                error += 1
        msg = f"{msg}: {len(actual)} Word checked ->"
        if error == 0:
            msg = f"{msg} OK"
        else:
            msg = f"{msg} Error"
    elif type(actual) is int:
        if mask is not None and (actual & mask) != (target & mask):
            error = 1
            msg = f"{msg}  target: 0x{target&mask:x} != actual: 0x{actual&mask:x}"
        elif mask is None and actual != target:
            error = 1
            msg = "{}  target: 0x{:x} != actual: 0x{:x}".format(msg, target, actual)
        else:
            msg = "{} == 0x{:2x}".format(msg, actual)
    elif (type(actual) is str) or (type(actual) is bool):
        if target != actual:
            error = 1
            msg = f"{msg}  target: {target} != actual: {actual}"
        else:
            msg = "{msg} = {actual}"
    elif type(actual) is float:  # float checked with tolerance
        if (target < (actual - tolerance)) or (target > (actual + tolerance)):
            error = 1
            msg = f"{msg}:  expected {target} +- {tolerance} <>{actual}"
        else:
            msg = f"{msg}:  expected {target} +- {tolerance} == {actual}"
    else:
        print("Check Error: type {} not yet implant !".format(type(actual)))
        error = 1
    if error > 0:
        print(f"ERROR: {msg}")
    else:
        print(f"MEASURE {msg}")
    return error


def color(n, s):
    code = {
        "bold": 1,
        "faint": 2,
        "italic": 3,
        "underline": 4,
        "blink_slow": 5,
        "blink_fast": 6,
        "negative": 7,
        "conceal": 8,
        "strike_th": 9,
        "ack": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenda": 35,
        "cyan": 36,
        "white": 37,
        "black": 40,
        "b_red": 41,
        "b_green": 42,
        "b_yellow": 43,
        "b_blue": 44,
        "b_magenda": 45,
        "b_cyan": 46,
        "b_white": 47,
    }
    try:
        num = str(code[n])
        value = "\033[" + num + "m" + s + "\033[0m"
        return value
    except Exception:
        pass


if __name__ == "__main__":

    class test:

        mqtt_list = [
            "CH0.connect()",
            "CH0.drv.vdl",
            "CH0.drv.vdh",
            "CH0.disconnect()",
            "CH1.connect()",
            "CH1.drv.vdl",
            "CH1.drv.vdh",
            "CH1.disconnect()",
            "CH2.connect()",
        ]

        def strcall_test(self):
            strcall(
                self,
                'CH0.disconnect("PBUS_F")',
                value=None,
                typ=None,
                mqttcheck=True,
            )

    print(arange("18:5:-1"))
    print(arange("6:4:-1"))
    print(arange("6:4:-0.1"))
    print(arange("-6:-4:0.1"))
    print(arange("18:5:-1, 5.9:4.1:-0.1, 4:-18:-1, -18:5:1, 4.1:5.9:0.1, 6:19:1"))
    print(arange("18:5:-1, 5.9:4.1:-0.1, 5, 8"))
    print(arange("18:5:-1,  4, 8"))
    print(arange("18:5:-1   6, 9"))
    print(arange("18:5"))
    print(arange("5:5"))
