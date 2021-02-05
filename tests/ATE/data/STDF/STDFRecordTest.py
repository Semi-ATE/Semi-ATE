import pytest
import struct
import math

class STDFRecordTest:

    def __init__(self , file, endian, debug = False):
        
        self.file = file
        self.endian = endian
        self.debug = debug
        
        if (endian == '>'):
            self.byteorder = 'big'
        elif (endian == '<'):
            self.byteorder = 'little'

    def assert_bits(self, expected_value):
        
        readed_value = self.file.read(1)
        found_value = int.from_bytes(readed_value, self.byteorder)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        bits = format(found_value, '08b')
        for i in range(len(expected_value)):
            assert bits[i] == expected_value[i]

    def assert_var_bits(self, expected_value):

        length_value = self.file.read(2)
        bits_count = int.from_bytes(length_value, self.byteorder)

        if self.debug: print(f"found bits length {bits_count} | expected_value {len(expected_value)}")
        assert bits_count == len(expected_value)
        
        byte_length = math.ceil(bits_count / 8)
        
        for byte_index in range(byte_length):
            readed_value = self.file.read(1)
            found_value = int.from_bytes(readed_value, self.byteorder)
            if self.debug:
                print(f"found_value {found_value} | expected_value {expected_value}")
            bits = format(found_value, '08b')
            for bit_indx in range(8):
                if (bit_indx + byte_index*8) < bits_count:
                    if self.debug:  print(f"found_value {bits[7-bit_indx]} | expected_value {expected_value[bit_indx + byte_index*8]}")
                    assert bits[7-bit_indx] == expected_value[bit_indx + byte_index*8]
            
    def assert_ubyte(self, expected_value):
        
        readed_value = self.file.read(1)
        found_value = int.from_bytes(readed_value, self.byteorder)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_float(self, expected_value):
        
        readed_value = self.file.read(4)
        format = self.endian + 'f'
        [found_value] = struct.unpack(format, readed_value)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert pytest.approx(found_value , 0.000001) == expected_value

    def assert_double(self, expected_value):
        
        readed_value = self.file.read(8)
        format = self.endian + 'd'
        [found_value] = struct.unpack(format, readed_value)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_float_array(self, expected_value):
        '''
        Method that assert array of floats.
            Parameters
            ----------
            expected_value : list of float
            
        '''
        size = len(expected_value);
        for elem in range(size):
            readed_value = self.file.read(4)
            format = self.endian + 'f'
            [found_value] = struct.unpack(format, readed_value)
            if self.debug:
                print(f"found_value {found_value} | expected_value {expected_value}")
            assert pytest.approx(found_value , 0.000001) == expected_value[elem]

    def assert_int(self, number_of_bytes, expected_value):
        
        readed_value = self.file.read(number_of_bytes)
        found_value = int.from_bytes(readed_value, self.byteorder)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_sint(self, number_of_bytes, expected_value):
        
        readed_value = self.file.read(number_of_bytes)
        found_value = int.from_bytes(readed_value, self.byteorder, signed=True)
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_int_array(self, element_size_in_byte, expected_value):
        '''
        Method that assert array of integers.
            Parameters
            ----------
        element_size_in_byte : int
            byte size of every element in the array - 1 for U*1, 2 for U*2 ...
        expected_value : list of int
            
        '''

        size = len(expected_value);
        for elem in expected_value:
            readed_value = self.file.read(element_size_in_byte)
            found_value = int.from_bytes(readed_value, self.byteorder)
            
            if self.debug:
                print(f"found_value {found_value} | expected_value {elem}")
            assert found_value == elem

    def assert_char(self, expected_value):
        
        readed_value = self.file.read(1)
        found_value = readed_value.decode('ascii')
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_char_array(self, number_of_chars, expected_value):
        
        readed_value = self.file.read(number_of_chars)
        found_value = readed_value.decode('ascii')
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        assert found_value == expected_value

    def assert_string_array(self, expected_value):
        
        for i in range(len(expected_value)):
            s = expected_value[i]
            l = len(s)
            self.assert_ubyte(l)
            self.assert_char_array(l, s)

    def assert_nibble_array(self, number_of_nibbles, expected_value):

        bytes_to_read = math.ceil(number_of_nibbles/2)
        indx = 0
        for i in range(bytes_to_read):
            readed_value = self.file.read(1)
            b = readed_value[0]
            first = b & 0x0F
            exp1 = expected_value[i*2]
            assert exp1 == first
            indx += 1
            if i*2+1 < number_of_nibbles:
                second = (b >> 4) & 0x0F
                exp2 = expected_value[i*2+1]
                assert exp2 == second
                indx += 1
            

    def assert_file_record_header(self, rec_len, rec_type, rec_sub):
        
        self.assert_int(2, rec_len);
        self.assert_int(1, rec_type);
        self.assert_int(1, rec_sub);
    
    def assert_instance_field(self, instance, 
                                 element_index, expected_value):

        fields = instance.get_fields(element_index)
        found_value = fields[3]
        if self.debug:
            print(f"found_value {found_value} | expected_value {expected_value}")
        if type(found_value) is float:
            assert pytest.approx(found_value , 0.000001) == expected_value
        elif type(found_value) is list:
            for i in range(len(expected_value)):
                if type(expected_value[i]) == float:
                    found = found_value[i]
                    expected = expected_value[i]
                    assert pytest.approx(found , 0.000001) == expected
                else:    
                    assert found_value[i] == expected_value[i]
        else:
            assert found_value == expected_value
        
    def assert_instance_record_header(self, instance, 
                                     rec_len, rec_type, rec_sub):

        self.assert_instance_field(instance, 0, rec_len)
        self.assert_instance_field(instance, 1, rec_type)
        self.assert_instance_field(instance, 2, rec_sub)
