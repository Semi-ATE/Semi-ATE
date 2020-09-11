'''
Created on Aug 19, 2019

@author: hoeren
'''
import os
import struct
from abc import ABC

from ATE.Data.utils.bitfucking import get_bit, set_bit


class register_map_abc(ABC):
    '''
    The Abstract Base Class for all register maps ('internal' for the tester, or 'external' for working with a DUT
    '''
    def __init__(self, configManager=None):
        self.configManager = configManager
        self.name = self.__class__.__name__
        self.device_driver = '/dev/%s' % self.name
        # copy the defaults from the class attributes
        self.address_size = self.address_size # Hahaha, think about this one ;P !!!
        self.word_size = self.word_size
        self.register_map = self.register_map.copy()
        # overwrite from configManager (if needed)
        if self.configManager!=None:
            pass #TODO: Implement
        # do some book keeping
        for variable in self.register_map:
            self.set_template(variable)
        self.set_masks()
        # check if the new self.register_map is well formed
        self.check_register_map()

        self.stat = int(self.register_map_size()/8)
        # open device driver
        if not os.path.exists(self.device_driver):
            pass #TODO: write the default register_map to a file for debugging purposes
        self.fd = open(self.device_driver, 'w+b')
        self.fp = 0
        # overwrite registers from the configManager (if needed)
        if self.configManager!=None:
            pass #TODO: implement
        # cleanup up the register_map
        for variable in self.register_map:
            if self.get_default(variable)==None:
                raise Exception("need to have a no-None default!")
            self.register_map[variable]['changed'] = True
            if self.get_value(variable)==None:
                self.register_map[variable]['value'] = self.get_default(variable)

    def __call__(self):
        pass # move the __init__ stuff here for easier subclassing

    def register_map_size(self, unit='bits'):
        '''
        This method will return the size bits (or word size) of the *USED* register map (regardless if used or not)
        Note: the total register map might be bigger (cfr: self.address_size)
        '''
        register_map_size = 0
        for variable in self.register_map:
            variable_size = self.word_size*(self.get_offset(variable)+self.get_words(variable))
            if variable_size > register_map_size:
                register_map_size = variable_size
        if unit == 'bits':
            return register_map_size
        elif unit == 'words':
            return int(register_map_size/self.word_size)
        else:
            raise Exception("register_map_size accepts 'bits' and 'words' as arguments for unit, not '%s'" % unit)

    def check_register_map(self):
        '''
        Checks to make sure the register_map is well formed
        '''
        # check if all the slices of all variables are well formed
        for variable in self.register_map:
            if not self._slice_ok(variable):
                raise Exception("The slice '%s' of variable '%s' is not well formed!" % (self.get_slice(variable), variable))
        # check if all words fall into the address space

    def set_masks(self):
        '''
        returns a list of booleans, each one indicating if the word needs reading before writing.
        '''
        self.rdmsk_str = []
        self.rdmsk_int = []
        self.wrmsk_str = []
        self.wrmsk_int = []
        self.rbw = []
        for word in range(self.register_map_size('words')):
            sub_mask = []
            for bit in range(self.word_size):
                bit_offset = word*self.word_size+bit
                tmp = '0'
                for variable in self.register_map:
                    if self.register_map[variable]['template'][bit_offset] == '1':
                        tmp = '1'
                sub_mask.append(tmp)
            rdmsk = str.join('', sub_mask)
            self.rdmsk_str.append(rdmsk)
            self.rdmsk_int.append(int(rdmsk,2))
            wrmsk = rdmsk.replace('1', 'x').replace('0', '1').replace('x', '0')
            self.wrmsk_str.append(wrmsk)
            self.wrmsk_int.append(int(wrmsk, 2))
            if '0' in sub_mask:
                self.rbw.append(True)
            else:
                self.rbw.append(False)

    def _is_sub_byte_variable(self, variable):
        '''
        return True if the variable takes less than 1 byte, False otherwise
        '''
        variable_size = self.get_bytes(variable)
        if variable_size == 1:
            variable_slice = self.get_slice(variable)
            if isinstance(variable_slice, tuple):
                if len(variable_slice) == 1:
                    return True
                elif len(variable_slice) == 2:
                    if abs(variable_slice[0]-variable_slice[1]+1) == 8:
                        return False
                    return True
            raise Exception("WTF!")
        return False

    def _is_byte_variable(self, variable):
        '''
        return True if the variable takes exactly 1 byte, False otherwise
        '''
        variable_size = self.get_bytes(variable)
        if variable_size == 1:
            variable_slice = self.get_slice(variable)
            if isinstance(variable_slice, tuple):
                if len(variable_slice) == 1:
                    return False
                elif len(variable_slice) == 2:
                    if abs(variable_slice[0]-variable_slice[1]+1) == 8:
                        return True
                    return False
            raise Exception("WTF!")
        return False

    def _is_multi_byte_variable(self, variable):
        '''
        return True if the variable takes more than 1 byte, False otherwise
        '''
        variable_size = self.get_bytes(variable)
        if variable_size != 1:
            variable_slice = self.get_slice(variable)
            if isinstance(variable_slice, tuple):
                if len(variable_slice) == 1:
                    return False
                elif len(variable_slice) == 2:
                    if abs(variable_slice[0]-variable_slice[1]+1) > 8:
                        return True
                    return False
            raise Exception("WTF!")
        return False

    def _slice_ok(self, variable):
        '''
        check if the slice of variable is well formed and fits
        '''
        slice_to_check = self.get_slice(variable)
        if not isinstance(slice_to_check, tuple):
            return False
        max_bits = (self.get_words(variable) * self.word_size) - 1
        if len(slice_to_check) == 1:
            if slice_to_check[0] > max_bits:
                return False
        elif len(slice_to_check) == 2:
            if slice_to_check[0] <= slice_to_check[1]:
                return False
            if slice_to_check[0] > max_bits:
                return False
        else:
            return False
        return True


    def _slicing_ok(self, offset):
        '''
        check if all variables that include the byte at offset
        This method will check if there are no slicing overlaps for byte at offset
        '''
        chk = 0
        for variable in self._variables_in_byte(offset):
            slice_to_check = self.get_slice(variable)
            if len(slice_to_check) == 1:
                start_bit = slice_to_check[0]
                end_bit = start_bit + 1
            else:
                start_bit = slice_to_check[1]
                end_bit = slice_to_check[0] + 1
            for n in range(start_bit, end_bit):
                bit_to_check = get_bit(n, chk)
                if bit_to_check == 0:
                    chk = set_bit(n, chk, 1)
                else:
                    return False
        return True

    def _slicings_ok(self):
        '''
        This mentod will check if any of the slicings overlap
        '''
        for variable in self.register_map:
            variable_offset = self.get_offset(variable)
            variable_size = self.get_bytes(variable)

            slice_check_ok = self._slicing_ok(variable_offset)
            print('--> %s = %s = %s' % (variable, variable_offset, slice_check_ok))
            if not slice_check_ok:
                return False

    def _in_byte(self, variable, offset):
        '''
        This method checks if Variable is part of the byte at offset
        '''
        start = self.register_map[variable]['offset']
        end = start + self.register_map[variable]['words'] - 1
        if start <= offset and offset <= end:
            return True
        return False

    def _variable_in(self, variable, offset, bytes=1, bytes_slice=(7,0)):
        '''
        This method will return True if (at least a part of) variable (with his bytes and slice) lays inside offset, bytes, bytes_slice; False otherwise
        '''
        variable_offset = self.get_offset(variable)
        variable_bytes = self.get_bytes(variable)
        variable_slice = self.get_slice(variable)
        if len(variable_slice)==1:
            variable_slice_span = 1
            variable_slice_offset = variable_slice[0]
        elif len(variable_slice)==2:
            variable_slice_span = variable_slice[1] - variable_slice[0] + 1
            variable_slice_offset = variable_slice[1]
        else:
            raise Exception("WTF!")
        variable_bits = (int(2**(variable_slice_span))-1)<<(variable_slice_offset)
        print("%s --> %s" % (variable, bin(variable_bits)))


#     def _construct_byte(self, offset):
#         retval = 0x00
#         for variable in self._variables_in_byte(offset):
#             print(self.get_slice(variable))

#     def variables_using_bit(self, offset):
#         retval = []
#         for variable in self.register_map:
#             if self.register_map[variable]['template'][offset] == '1':
#                 retval.append(variable)
#         return retval

    def get_bit_from_template(self, offset, variable):
        return self.register_map[variable]['template'][offset]

    def dump(self):
        '''
        This method will return a byte array of the register_map, unused bits are put to 0
        '''



    def get_offset(self, variable):
        return self.register_map[variable]['offset']

    def get_words(self, variable):
        return self.register_map[variable]['words']

    def get_slice(self, variable):
        return self.register_map[variable]['slice']

    def get_default(self, variable):
        return self.register_map[variable]['default']

    def get_access(self, variable):
        return self.register_map[variable]['access']

    def get_value(self, variable):
        return self.register_map[variable]['value']

    def get_template(self, variable):
        if not hasattr(self.register_map[variable], 'template'):
            self.set_template(variable)
        return self.register_map[variable]['template']

    def set_template(self, variable):
        template = []
        for _ in range(self.register_map_size('words')):
            template_item = ['0' for _ in range(self.word_size)]
            template += template_item

        var_offset_in_bits = self.word_size * self.get_offset(variable)
        var_words = self.get_words(variable)

        var_slice = self.get_slice(variable)
        var_slice_start = (self.word_size * var_words) - var_slice[0] - 1

        if len(var_slice) == 1:
            var_slice_stop = var_slice_start + 1
        elif len(var_slice) == 2:
            var_slice_stop = (self.word_size * var_words) - var_slice[1]
        else:
            raise Exception("WTF!")
        for i in range(var_offset_in_bits+var_slice_start, var_offset_in_bits+var_slice_stop):
            template[i] = '1'
        self.register_map[variable]['template'] = template

    def set_value(self, variable, value):
        self.register_map[variable]['value'] = value
        self.register_map[variable]['changed'] = True

    def isChanged(self, variable):
        return self.register_map[variable]['changed']

    def read(self, variable=None):
        '''
        This method will read a variable from the element.
        If variable == None, all readable variables are red from element and stored in self.register_map
        '''
        pass

    def write(self, variable=None, value=None, flush=True):
        '''
        This method will write variable to the element.
        If flush == False, only the self.register_map will be updated (and the 'changed' flag set)
        If variable == None, all variables from self.register_map will be written to element.

        use cases:

            variable | value   | flush
            ---------+---------+------
            None     | X       | True  --> Write all writeable variables from self.register_map to the element
            None     | X       | False --> does *NOTHING*
            str      | val     | True  --> Writes 'val' to variable 'str' in self.register_map *AND* the element (the changed flag will not be set)
            str      | val     | False --> Writes 'val' to variable 'str' in self.retister_map but *NOT* to the element (the changed flag will be set)

        write needs to to type/cast/size checking !
        needs to update the self.fp
        '''
        pass

    def tell(self):
        '''
        This method will return the file object's current position for the device on ChipSelect CS.
        '''
        return(self.fp)

    def _stat(self):
        '''
        This method will return the size of the file (determined from the register_map --> biggest offset + his bytes - 1 )
        '''
        retval = 0
        for variable in self.register_map:
            if isinstance(self.register_map[variable], dict):
                trial = self.register_map[variable]['offset'] + self.register_map[variable]['words'] - 1
                if trial > retval:
                    retval = trial
            elif isinstance(self.register_map[variable], list):
                continue
            else:
                raise Exception("WTF")
        return retval

    def seek(self, offset, from_what=0):
        '''
        This method will set the file object's current position for the device on ChipSelect CS.

        from_what = 0 --> beginning of the file
                    1 --> from the current file position
                    2 --> from the end of the file (offset should thus be *NEGATIVE*)

        Note : if offset = -1 and from_what = 0, the object's current position will be at the end!
        '''
        if from_what == 0: # from beginning of the file
            self.fp = offset
        elif from_what == 1: # from the current file position
            self.fp += offset
        elif from_what == 2: # from the end of the file
            if offset > 0: # offset needs to be negative!!!
                raise Exception("seek offset needs to be negative!!!")
                #TODO: think about this ... can't we support positive values ?!?
            self.fp = self.stat + offset
        else:
            raise Exception("WTF!")

    def print_templates(self):
        header = str.join(' ', [str.center('%s'%i, self.word_size) for i in range(self.register_map_size('words'))])
        print(header)
        for variable in self.register_map:
            template = [self.register_map[variable]['template'][i:i+self.word_size] for i in range(0, len(self.register_map[variable]['template']), self.word_size)]
            template_str = ''
            for word in range(self.register_map_size('words')):
                template_str += str.join('', template[word]) + ' '
            template_str = template_str.replace('0', '.')
            print("%s : %s" % (template_str, variable))
        footer = ''
        for word in range(self.register_map_size('words')):
            footer_item = str.rjust('%s'%((word*self.word_size)+(self.word_size-1)), self.word_size) + ' '
            if word == 0:
                footer_item = '0' + str.rjust('%s'%(self.word_size-1), self.word_size-1) + ' '
            footer += footer_item
        print(footer)
        rbw = ''
        for word in range(self.register_map_size('words')):
            rbw += str.center('%s'%self.rbw[word], self.word_size) + ' '
        print("%s : read before write" % rbw)
        rdmsk_str = ''
        for word in range(self.register_map_size('words')):
            rdmsk_str += self.rdmsk_str[word] + ' '
        print("%s : read mask binary" % rdmsk_str)
        wrmsk_str = ''
        for word in range(self.register_map_size('words')):
            wrmsk_str += self.wrmsk_str[word] + ' '
        print("%s : write mask binary" % wrmsk_str)



    def __del__(self):
        if self.configManager!=None:
            self.configManager.save(self.config)
        if hasattr(self, 'fd'):
            self.fd.close()

    def __str__(self):
        retval = "%s:\n" % self.name
        for variable in self.register_map:
            var = variable
            val = self.register_map[variable]['value']
            size = abs(self.register_map[variable]['slice'][0] - self.register_map[variable]['slice'][1] + 1)
            retval += "   %s : %s (%s bits)\n" % (var, val, size )
        return retval


if __name__ == '__main__':

    class CTCA(register_map_abc):

        address_size = 5 # bits
        word_size = 16 # bits
        register_map = {
            'version'       : {'offset' : 0x000, 'words' : 1, 'slice' : (7, 0), 'default' : None, 'access' : 'R',  'desc' : 'Version',                                                'presets' : None},
            'major_version' : {'offset' : 0x000, 'words' : 1, 'slice' : (7, 4), 'default' :  0xb, 'access' : 'R',  'desc' : 'Major version',                                          'presets' : None},
            'minor_version' : {'offset' : 0x000, 'words' : 1, 'slice' : (3, 0), 'default' :  0x0, 'access' : 'R',  'desc' : 'Minor version',                                          'presets' : None},

            'regd_enable'   : {'offset' : 0x001, 'words' : 1, 'slice' :   (4,), 'default' :  0x1, 'access' : 'RW', 'desc' : 'Enable digital regulator in scan mode',                  'presets' : {0: "Disable", 1: "Enable"}},




            'CH0_GAIN'        : {'offset' : 0x001, 'words' : 1, 'slice' : (7, 6), 'default' : 0x00, 'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'CH0_REF_MONITOR' : {'offset' : 0x001, 'words' : 1, 'slice' : (5,),   'default' : 0x00, 'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : {0: "4mA drive strength", 1 : "8mA drive strength"}},
            'CH0_RX'          : {'offset' : 0x001, 'words' : 1, 'slice' : (4,),   'default' : 0x00, 'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : {0: "Disable", 1: "Enable"}},
            'CH0_OFFSET'      : {'offset' : 0x002, 'words' : 3, 'slice' : (23,0), 'default' : 100,  'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'CH0_OFFSET_HI'   : {'offset' : 0x002, 'words' : 1, 'slice' : (7,0),  'default' : 0,    'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'CH0_OFFSET_MID'  : {'offset' : 0x003, 'words' : 1, 'slice' : (7,0),  'default' : 0,    'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'CH0_OFFSET_LO'   : {'offset' : 0x004, 'words' : 1, 'slice' : (7,0),  'default' : 0,    'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'brol'            : {'offset' : 0x004, 'words' : 9, 'slice' : (54,5), 'default' : 0,    'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
            'CH1_GAIN'        : {'offset' : 0x005, 'words' : 4, 'slice' : (24,0), 'default' : 100,  'access' : 'RW', 'value' : None, 'desc' : '', 'presets' : None},
        }

    ctca = CTCA()
    ctca.print_templates()

#     print("%s" % TEST.variables_using_bit(16))
