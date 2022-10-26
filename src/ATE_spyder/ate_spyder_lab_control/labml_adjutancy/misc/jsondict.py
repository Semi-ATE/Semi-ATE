"""
Jsondict.

Created on Thu Jan  7 17:18:03 2021

TODO: started from projectsetup, so, some functions have to delete or to clear....

@author: jung
"""
import os
import json

# from labml_instruments.base_instrument import logger
from labml_adjutancy.misc import common
from labml_adjutancy.misc import file_io


__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"


class JsonDecoder(json.JSONDecoder):
    def decode(self, obj):
        # TODO: implementend parser for hexnumbers and other special formats....
        return json.JSONDecoder.decode(self, obj)


class diclist(list):
    """Dictionary list"""

    def __init__(*args, **kwargs):
        global myparent
        if len(args) > 1:
            myparent = args[1]
            args = list(args)
            del args[1]
        list.__init__(*args, **kwargs)

    def __getattr__(mylist, key):
        if key in mylist:
            list.__getattribute__(mylist, key)
        else:
            return diclist.values(mylist, key)

    def keys(mylist):
        """get a list of all key words in mylist"""
        result = []
        for item in mylist:
            for key in item.keys():
                if key not in result:
                    result.append(key)
        return result

    def index(mylist, index, value=None):
        if type(index) is int:
            return mylist[index]
        else:
            result = []
            for count in mylist:
                if index in count:
                    if value is None or (value is not None and count[index] == value):
                        result.append(count)
            if len(result) == 1:
                return result[0]
            return result

    def values(mylist, key=None):
        """Get the value(s) from the key found in mylist."""
        result = None
        # if key is not None and key in diclist.keys(mylist):
        if key is not None:
            if len(diclist.keys(mylist)) == 1:
                result = list(mylist[diclist.keys(mylist).index(key)].values())
            else:
                result = []
                for index in mylist:
                    if key in index:
                        result.append(index[key])
        elif len(mylist) > 0:
            result = []
            for item in mylist:
                if key is None:
                    value = list(item.values())[0]
                elif key in list(item.values())[0].keys():
                    value = list(item.values())[0][key]
                else:
                    value = None
                if type(value) is str:
                    value = common.str2num(value)
                result.append(value)
        return result

    def run(mylist, **kwargs):
        """Call the runmacro from the parent."""
        result = None
        if myparent is not None and hasattr(myparent, "runmacro"):
            # logger.debug(f'run macro {myparent.mylastdotdic}: {mylist}')
            print(f"run macro {myparent.mylastdotdic}: {mylist}")
            result = myparent.runmacro(mylist, **kwargs)
        else:
            # logger.error(f'No instruction how to should interprete the list: {mylist}')
            print(f"No instruction how to should interprete the list: {mylist}")
        return result


class setupstr(str):
    def arange(items):
        return common.arange(items)

    def start(items):
        return common.arange(items)[0]

    def end(items):
        return common.arange(items)[-1]


class dotdict(dict):
    """dot.notation access to dictionary attributes."""

    def myget(keyname, value):
        result = dict.get(keyname, value)
        if value not in ["size", "shape"]:
            myparent.mylastdotdic = value
            # print(f'keyname: {keyname},\nvalue: {value},\nresult: {result},\n')
            if result is None:
                # logger.warning(f"'dotdict' has no attribute {value} -> result is None")
                raise AttributeError(f"'dotdict' has no attribute {value} ")
        return result

    __getattr__ = myget  # __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class JsonDict(object):
    """
    Class for the handling json dictionaries.
    """

    _RESULT = "result_projectsetup.json"
    _SETUPFILE = "tb_projectsetup.json"
    _MYCLASS = "myclass"

    def __init__(self, filename):
        """Open a json-file and assign the values to a dot-dictionary."""
        if filename is dict:
            self.contents = filename
        elif os.path.exists(filename):
            print(filename)
            with file_io.openFile(filename, "r") as file:
                try:
                    self.contents = json.load(file, cls=JsonDecoder)
                except Exception as error:
                    # logger.error(f"JsonDict: syntax error in {filename} : {error}")      # TODO!: add json validator: pip install jsonschema
                    print(f"    JsonDict: syntax error in {filename} : {error}")
                    return None
        else:
            # logger.error(f"JsonDict: {filename} not exists:")
            print(f"    JsonDict: {filename} not exists:")
            return None
        self.contents = self.create_dotdic(self.contents, self)
        self.mylastdotdic = None
        self.lastresult = None
        self.lastmacro = None

    def create_dotdic(self, dic, root=None):
        """Make from a dictionary a dot-dictionary with diclist."""
        if type(dic) == list:
            mydic = diclist(root, dic)
            for index in range(0, len(dic)):
                mydic[index] = self.create_dotdic(mydic[index])
            return mydic
        for mydic in dic.keys():
            if type(dic[mydic]) == dict:
                if root is not None:
                    object.__setattr__(root, mydic, self.create_dotdic(dic[mydic]))
                dic[mydic] = self.create_dotdic(dic[mydic])
            elif type(dic[mydic]) == list:
                dic[mydic] = diclist(self, dic[mydic])
            elif type(dic[mydic]) == str and dic[mydic].find(":") > 0:  # found an arange-function -> change to setupstr
                dic[mydic] = setupstr(dic[mydic])
        return dotdict(dic)

    def _replaceSomeThing(self, jsontable):
        """Check if jsontable has environment-variables starts with $, or jsontable has path-value.

        if yes than replace environment-variables with its value,
        if it a path-value than add //samba
        """
        for key in jsontable:
            if type(jsontable) == dict:
                value = jsontable[key]
            else:
                value = key
            if type(value) == dict or type(value) == list:
                self._replaceSomeThing(value)
            elif type(value) == str and value.find("$") > -1:  # find environment variables inside the value?
                tmp = value.split("/")
                nvalue = ""
                for s in tmp:
                    if s.find("$") == 0:
                        s = os.environ.get(s[1:])
                    nvalue += s + "/"
                if nvalue != "":
                    if type(jsontable) == dict:
                        jsontable[key] = nvalue[:-1]
                    else:
                        jsontable[1] = nvalue[:-1]
            elif (
                type(value) == str
                and len(value) > 0
                and value[0] == "/"
                and os.name == "nt"
                and value.find(f"{self.network}") != 0
            ):
                if type(jsontable) == dict:
                    jsontable[key] = self.network + value
                else:
                    jsontable[1] = self.network + value

    def write(self, path, name=None, value=None):
        """Write path to the dictionary in my class ProjectSetup.

        Path must be a string like 'instruments.smu'
        normaly append this path to result
        if path start with setup than write to setup.path

        e.q. write('instruments.smu', 'port', 'pxie5')
             write('setup.HostName', os.environ.get('COMPUTERNAME'))
        """
        path = path.split(".")
        lastindex = "result"
        if path[0] == "setup":
            lastindex = "setup"
            path.pop(0)
        mydic = self.__dict__[lastindex]
        lastdic = mydic
        for index in path:
            if index not in mydic.keys():  # than create new dictionary
                if type(mydic) is diclist:
                    if mydic == []:
                        lastdic[lastindex] = dotdict({index: diclist(self)})
                        mydic = lastdic[lastindex]
                    else:
                        mydic.append(dotdict({index: diclist(self)}))
                        mydic = lastdic[lastindex][-1]
                else:
                    mydic[index] = diclist(self)
            lastdic = mydic
            if type(mydic) is diclist:
                mydic = mydic.values(index)
            else:
                mydic = mydic[index]
            lastindex = index
        if name is None:
            mydic += [value]
        else:
            mydic += [{name: value}]

    def runmacro(self, cmdlist, **kwargs):
        """Execute commands in the cmdlist.

        kwargs: 'wr2setup' : write result to the setup.result json file.
        """
        wr2setup = False
        if "output" in kwargs:
            wr2setup = kwargs["output"] == "wr2setup"
        result = []
        macro = myparent.mylastdotdic
        self.lastmacro = macro
        for cmd in cmdlist:
            myresult = self.call(cmd)
            if myresult is not None:
                result.append(myresult)
                self.lastresult = result
            if wr2setup:
                self.write(macro, cmd, myresult)
        if len(result) == 1:
            result = result[0]
        self.lastresult = result
        if cmdlist == []:
            # logger.warning(f'Macro {macro} not defined in setup')
            print(f"Macro {macro} not defined in setup")
            if wr2setup:
                self.write("macro", macro, "not defined in setup")
        return result

    def _write(self):
        """Write the dictionary to the logfile."""
        # self.__dict__.pop('init')
        with open(self._RESULT, "w") as outfile:
            outfile.write("{")
            self.jsondump(outfile, self.setup)
            outfile.write("    ,\n")
            self.jsondump(outfile, "result")
            # json.dump(self.setup, outfile, indent=2)
            # json.dump(self.result, outfile, indent=2)     # sort_keys=True
            outfile.write("\n}")
        # logger.info(f'write results to {self._RESULT}')
        print(f"write results to {self._RESULT}")

    def jsondump(self, file, dictionary, ident=4):
        """Dump the dictionary to json-format.

        you can also use json.dump but I think this generated output-format is better for easy reading
        """

        def space(ident, lenght=2):
            if lenght < 2 and ident > 4:
                return
            for i in range(0, ident):
                file.write(" ")

        end = ""
        spara = "{"
        if type(dictionary) is str:
            space(ident, 3)
            file.write(f'"{dictionary}": {spara}')
            dictionary = self.__dict__[dictionary]
            end = "}"
            ident = 8
            space(ident, 3)
        length = len(dictionary)
        index = 0
        more = ","
        cr = "\n"
        if length < 2 and ident > 4:
            cr = ""
        else:
            pass
        file.write(f"{cr}")
        for item in dictionary:
            index += 1
            if index == length:
                more = ""
            if type(dictionary) in [dict, dotdict]:
                value = dictionary[item]
            else:
                value = dictionary[index - 1]
            spara = "{"
            epara = "}"
            if type(value) in [list, diclist]:
                spara = "["
                epara = "]"
            if type(value) in [dict, dotdict, list, diclist]:
                space(ident, length)
                try:
                    if item == value and type(item) is dict:  # is it a list with dictionaries
                        json.dump(item, file)
                        file.write(f"{more}{cr}")
                    elif item == value:  # it is a list with dotdictionaries
                        file.write(f"{spara}")
                        self.jsondump(file, value, ident + 4)
                        file.write(f"{epara}{more}{cr}")
                    else:  # it is dict or dotdict
                        file.write(f'"{item}": {spara}')
                        self.jsondump(file, value, ident + 4)
                        file.write(f"{epara}{more}{cr}")
                except Exception:
                    file.write(f"ERROR!!!: coudn't write {item} as json dump {more}{cr}")
            else:
                if type(value) == str:
                    value = f'"{value.replace(os.sep, "/")}"'
                space(ident, length)
                if item != value:
                    file.write(f'"{item}": {value}{more}{cr}')
                else:
                    file.write(f"{value}{more}{cr}")
        if cr != "":
            space(ident - 4, length)
        file.write(f"{end}")

    def __repr__(self):
        # return f"{self.contents}"
        return f"{self.__class__}"


if __name__ == "__main__":
    from pytestsharing.instruments.base_instrument import logsetup

    logsetup()

    tests = JsonDict(
        r"C:\Users\jung\Work Folders\Projecte\Repository\hatc\0203\units\lab\source\python\tb_ate\definitions\test\test.json"
    )
    print(tests.contents.keys())
    print(tests.contents.values(key="name"))
    print(tests.contents.values(key="hardware"))
    tests.contents.index(0)
    shmoo_values = []
    for name in tests.contents.values(key="name"):
        input_paramters = tests.contents.index("name", name).definition.input_parameters
        for key in input_paramters.keys():
            if input_paramters[key].Shmoo and key not in shmoo_values:
                shmoo_values.append(key)
    print(shmoo_values)
