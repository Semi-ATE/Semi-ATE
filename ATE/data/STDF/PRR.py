import sys
from ATE.data.STDF import STDR


class PRR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'PRR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info = '''
Part Results Record
-------------------

Function:
    Contains the result information relating to each part tested by the test program. The
    PRR and the Part Information Record (PIR) bracket all the stored information
    pertaining to one tested part.

Frequency:
    * Obligatory
    * One per part tested.

Location:
    Anywhere in the data stream after the corresponding PIR and before the MRR.
    Sent after completion of testing each part.
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :                                     None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    5, 'Text' : 'Record type                           ', 'Missing' :                                     None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   20, 'Text' : 'Record sub-type                       ', 'Missing' :                                     None},
                'HEAD_NUM' : {'#' :  3, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' :                                        1},
                'SITE_NUM' : {'#' :  4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test site number                      ', 'Missing' :                                        1},
# changed by seimit : bits 5 - 7: Reserved for future use — must be 0, page 44 from STDF v4
#               'PART_FLG' : {'#' :  5, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Part information flag                 ', 'Missing' : ['0', '0', '0', '1', '0', '0', '0', '1']},
                'PART_FLG' : {'#' :  5, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Part information flag                 ', 'Missing' : ['0', '0', '0', '1', '0', '0', '0', '0']},
                'NUM_TEST' : {'#' :  6, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Number of tests executed              ', 'Missing' :                                        0},
                'HARD_BIN' : {'#' :  7, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Hardware bin number                   ', 'Missing' :                                        0},
                'SOFT_BIN' : {'#' :  8, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Software bin number                   ', 'Missing' :                                    65535},
                'X_COORD'  : {'#' :  9, 'Type' : 'I*2', 'Ref' : None, 'Value' : None, 'Text' : '(Wafer) X coordinate                  ', 'Missing' :                                   -32768},
                'Y_COORD'  : {'#' : 10, 'Type' : 'I*2', 'Ref' : None, 'Value' : None, 'Text' : '(Wafer) Y coordinate                  ', 'Missing' :                                   -32768},
                'TEST_T'   : {'#' : 11, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Elapsed test time in milliseconds     ', 'Missing' :                                        0},
                'PART_ID'  : {'#' : 12, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Part identification                   ', 'Missing' :                                       ''},
                'PART_TXT' : {'#' : 13, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Part description text                 ', 'Missing' :                                       ''},
                'PART_FIX' : {'#' : 14, 'Type' : 'B*n', 'Ref' : None, 'Value' : None, 'Text' : 'Part repair information               ', 'Missing' :                                       []}
            }

        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''
        
        header = self.id + ':'

#        The order of fields is different in STDF and ATDF for PRR record
#        
#        STDF page 43| ATDF page 39
#        
#         3 HEAD_NUM    =  3 HEAD_NUM    
#         4 SITE_NUM    =  4 SITE_NUM  
#         5 PART_FLG    
#         6 NUM_TEST        
#         7 HARD_BIN       
#         8 SOFT_BIN       
#         9 X_COORD       
#        10 Y_COORD       
#        11 TEST_T       
#        12 PART_ID     = 12 PART_ID
#                          6 NUM_TEST
#                          5 PART_FLG bits 3 & 4
#                          7 HARD_BIN
#                          8 SOFT_BIN
#                          9 X_COORD
#                         10 Y_COORD
#                          5 PART_FLG bit 0 or 1
#                         5 PART_FLG bit 2
#                         11 TEST_T
#        13 PART_TXT    = 13 PART_TXT
#        14 PART_FIX    = 14 PART_FIX
    
#       3 HEAD_NUM 
        body += self.gen_atdf(3)
#       4 SITE_NUM 
        body += self.gen_atdf(4)
#       12 PART_ID 
        body += self.gen_atdf(12)
#       6 NUM_TEST 
        body += self.gen_atdf(6)
        
#                             5 PART_FLG bits 3 & 4
#           bit 4: 0 = Pass/fail flag (bit 3) is valid
        v = self.get_fields(5)[3] 
        if v != None and v[4] == '0':
            # 0 = Part passed
            if self.get_fields(5)[3][3] == '0':
                body += 'P|'
            # 1 = Part failed
            elif self.get_fields(5)[3][3] == '1':
                body += 'F|'
#           bit 4: 1 = Device completed testing with no pass/fail indication (i.e., bit 3 is invalid)
        elif v != None and v[4] == '1':
            buff += ' |'
#                              7 HARD_BIN
        body += self.gen_atdf(7)
#                              8 SOFT_BIN
        body += self.gen_atdf(8)
#                              9 X_COORD
        body += self.gen_atdf(9)
#                             10 Y_COORD
        body += self.gen_atdf(10)
#                              5 PART_FLG bit 0 or 1
#           Note: Either Bit 0 or Bit 1 can be set, but not both. 
        v = self.get_fields(5)[3] 

        if v != None and v[0] == '1' and v[1] == '1':
            raise STDFError("export to atdf error: PRR PART_FLG bits 0 and 1 are both set, which is not allowed" )
        elif v != None and v[0] == '1':
            body += "I|"
        elif v != None and v[1] == '1':
            body += "C|"
#                              5 PART_FLG bit 2
        if v != None and v[2] == '0':
            body += "|"
        elif v != None and v[2] == '1':
            body += "Y|"
#                             11 TEST_T
        body += self.gen_atdf(11)
#                             13 PART_TXT
        body += self.gen_atdf(13)
#                             14 PART_FIX
        value = self.get_fields(14)[3]
        if value != None:
            # converting bits into HEX values
            byte_list = []
            byte_value = 0
            bit = 0
            for i in range(len(value)):
                el = value[i]
                byte_value |= int(el) << bit
                bit += 1
                if bit == 8:
                    byte_list.append(byte_value)
                    byte_value = 0
                    bit = 0
            # ToDo : to make real n*bits
    #            if bit != 0:
            final_value = ''
            for elem in byte_list:
                final_value += hex(elem)[2:]
            body += final_value.upper()

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
    