import sys
from ATE.data.STDF import STDR

class MPR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'MPR'
        self.local_debug = False
        if version==None or version == 'V4':
            self.version ='V4'
            self.info = '''
Multiple-Result Parametric Record
---------------------------------

Function:
    Contains the results of a single execution of a parametric test in the test program
    where that test returns multiple values. The first occurrence of this record also
    establishes the default values for all semi-static information about the test, such as
    limits, units, and scaling. The MPR is related to the Test Synopsis Record (TSR) by test
    number, head number, and site number.

Frequency:
    * Obligatory, one per multiple-result parametric test execution on each head/site

Location:
    Anywhere in the data stream after the corresponding Part Information Record (PIR)
    and before the corresponding Part Result Record (PRR).
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2',  'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :                                     None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1',  'Ref' :       None, 'Value' :   15, 'Text' : 'Record type                           ', 'Missing' :                                     None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1',  'Ref' :       None, 'Value' :   15, 'Text' : 'Record sub-type                       ', 'Missing' :                                     None},
                'TEST_NUM' : {'#' :  3, 'Type' : 'U*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Test number                           ', 'Missing' :                                     None},
                'HEAD_NUM' : {'#' :  4, 'Type' : 'U*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' :                                        1},
                'SITE_NUM' : {'#' :  5, 'Type' : 'U*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test site number                      ', 'Missing' :                                        1},
                'TEST_FLG' : {'#' :  6, 'Type' : 'B*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test flags (fail, alarm, etc.)        ', 'Missing' :                                  ['0']*8},
                'PARM_FLG' : {'#' :  7, 'Type' : 'B*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Parametric test flags (drift, etc.)   ', 'Missing' : ['1', '1', '0', '0', '0', '0', '0', '0']}, # 0xC0
                'RTN_ICNT' : {'#' :  8, 'Type' : 'U*2',  'Ref' :       None, 'Value' : None, 'Text' : 'Count (j) of PMR indexes              ', 'Missing' :                                        0},
                'RSLT_CNT' : {'#' :  9, 'Type' : 'U*2',  'Ref' :       None, 'Value' : None, 'Text' : 'Count (k) of returned results         ', 'Missing' :                                        0},
                'RTN_STAT' : {'#' : 10, 'Type' : 'xN*1', 'Ref' : 'RTN_ICNT', 'Value' : None, 'Text' : 'Array of j returned states            ', 'Missing' :                                       []}, # RTN_ICNT = 0
                'RTN_RSLT' : {'#' : 11, 'Type' : 'xR*4', 'Ref' : 'RSLT_CNT', 'Value' : None, 'Text' : 'Array of k returned results           ', 'Missing' :                                       []}, # RSLT_CNT = 0
                'TEST_TXT' : {'#' : 12, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'Descriptive text or label             ', 'Missing' :                                       ''},
                'ALARM_ID' : {'#' : 13, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'Name of alarm                         ', 'Missing' :                                       ''},
                'OPT_FLAG' : {'#' : 14, 'Type' : 'B*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Optional data flag See note           ', 'Missing' : ['0', '0', '0', '0', '0', '0', '1', '0']}, # 0x02
                'RES_SCAL' : {'#' : 15, 'Type' : 'I*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test result scaling exponent          ', 'Missing' :                                        0}, # OPT_FLAG bit 0 = 1
                'LLM_SCAL' : {'#' : 16, 'Type' : 'I*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test low limit scaling exponent       ', 'Missing' :                                        0}, # OPT_FLAG bit 4 or 6 = 1
                'HLM_SCAL' : {'#' : 17, 'Type' : 'I*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Test high limit scaling exponent      ', 'Missing' :                                        0}, # OPT_FLAG bit 5 or 7 = 1
                'LO_LIMIT' : {'#' : 18, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Test low limit value                  ', 'Missing' :                                      0.0}, # OPT_FLAG bit 4 or 6 = 1
                'HI_LIMIT' : {'#' : 19, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Test high limit value                 ', 'Missing' :                                      0.0}, # OPT_FLAG bit 5 or 7 = 1
                'START_IN' : {'#' : 20, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Starting input value [condition]      ', 'Missing' :                                      0.0}, # OPT_FLAG bit 1 = 1
                'INCR_IN'  : {'#' : 21, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Increment of input condition          ', 'Missing' :                                       -1}, # OPT_FLAG bit 1 = 1
                'RTN_INDX' : {'#' : 22, 'Type' : 'xU*2', 'Ref' : 'RTN_ICNT', 'Value' : None, 'Text' : 'Array of j PMR indexes                ', 'Missing' :                                       []}, # RTN_ICNT = 0
                'UNITS'    : {'#' : 23, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'Units of returned results             ', 'Missing' :                                       ''},
                'UNITS_IN' : {'#' : 24, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'Input condition units                 ', 'Missing' :                                       ''},
                'C_RESFMT' : {'#' : 25, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'ANSI C result format string           ', 'Missing' :                                       ''},
                'C_LLMFMT' : {'#' : 26, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'ANSI C low limit format string        ', 'Missing' :                                       ''},
                'C_HLMFMT' : {'#' : 27, 'Type' : 'C*n',  'Ref' :       None, 'Value' : None, 'Text' : 'ANSI C high limit format string       ', 'Missing' :                                       ''},
                'LO_SPEC'  : {'#' : 28, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'Low specification limit value         ', 'Missing' :                                      0.0}, # OPT_FLAG bit 2 = 1
                'HI_SPEC'  : {'#' : 29, 'Type' : 'R*4',  'Ref' :       None, 'Value' : None, 'Text' : 'High specification limit value        ', 'Missing' :                                      0.0}  # OPT_FLAG bit 3 = 1
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''
        
        header = self.id + ':'
        
        #    The order of fields is different in STDF and ATDF for FTR record
            
        #    STDF page 53| ATDF page 47
            
        #     3 TEST_NUM    =  3 TEST_NUM   
        #     4 HEAD_NUM    =  4 HEAD_NUM    
        #     5 SITE_NUM    =  5 SITE_NUM  
        #     6 TEST_FLG    
        #     7 PARM_FLG            
        #     8 RTN_ICNT    -> missing
        
        #     9 RSLT_CNT    -> missing    
        #    10 RTN_STAT    = 10 RTN_STAT  
        #    11 RTN_RSLT    = 11 RTN_RSLT
        #                -> 6 TEST_FLG bits 6 & 7 and 7 PARM_FLG bit 5
        #                -> 6 TEST_FLG bits 0, 2, 3, 4 & 5 and 7 PARM_FLG bits 0, 1, 2, 3 & 4
        #    12 TEST_TXT    = 12 TEST_TXT 
        #    13 ALARM_ID    = 13 ALARM_ID 
        #                -> 7 PARM_FLG bits 6 & 7 
        #    14 OPT_FLAG 
        #    15 RES_SCAL
        #    16 LLM_SCAL
        #    17 HLM_SCAL
        #    18 LO_LIMIT
        #    19 HI_LIMIT
        #    20 START_IN
        #    21 INCR_IN
        #    22 RTN_INDX
        #    23 UNITS       = 23 UNITS 
        #    24 UNITS_IN
        #    25 C_RESFMT
        #    26 C_LLMFMT
        #    27 C_HLMFMT
        #    28 LO_SPEC
        #    29 HI_SPEC
        #                = 18 LO_LIMIT
        #                = 19 HI_LIMIT
        #                = 20 START_IN
        #                = 21 INCR_IN
        #                = 24 UNITS_IN
        #                = 22 RTN_INDX
        #                = 25 C_RESFMT
        #                = 26 C_LLMFMT
        #                = 27 C_HLMFMT
        #                = 28 LO_SPEC
        #                = 29 HI_SPEC
        #                = 15 RES_SCAL
        #                = 16 LLM_SCAL
        #                = 17 HLM_SCAL

#       3 TEST_NUM 
        body += "%s|" % self.get_fields(3)[3]
#       4 HEAD_NUM 
        body += "%s|" % self.get_fields(4)[3]
#       5 SITE_NUM  
        body += "%s|" % self.get_fields(5)[3]
#       10 RTN_STAT 
        value = self.get_fields(10)[3]
        for elem in value:
            body += "%s," % elem
        body = body[:-1] 
        body += "|"
#       11 RTN_RSLT   MUST be float!!!
        value = self.get_fields(11)[3]
        for elem in value:
            leading = round(elem,0)
            len_lead = len(str(leading))
            result = round(elem, 9 - len_lead)
            body += "%s," % result
        body = body[:-1] 
        body += "|"        
#       6 TEST_FLG bits 6 & 7
#           bit 6: Pass/fail flag (bit 7) is valid
        if self.get_fields(6)[3][6] == '0':
#           bit 7:
#           0 = Part passed
            if self.get_fields(6)[3][7] == '0':
                body += 'P'
#           1 = Part failed
            elif self.get_fields(6)[3][7] == '1':
                body += 'F'
#       7 PARM_FLG bit 5
        if self.get_fields(7)[3][5] == '0':
            body += '|'
        elif self.get_fields(7)[3][5] == '1':
            body += 'A|'            
#       6 TEST_FLG bits 0, 2, 3, 4 & 5
#       bit 0:
#       0 = No alarm
        if self.get_fields(6)[3][0] == '0':
            body += ''
#       1 = Alarm detected during testing
        elif self.get_fields(6)[3][0] == '1':
            body += 'A'
#       bit 2:
#       0= Test result is reliable
        if self.get_fields(6)[3][2] == '0':
            body += ''
#       1 = Test result is unreliable
        elif self.get_fields(6)[3][2] == '1':
            body += 'U'
#       bit 3:
#       0 = No timeout
        if self.get_fields(6)[3][3] == '0':
            body += ''
#       1 = Timeout occurred
        elif self.get_fields(6)[3][3] == '1':
            body += 'T'
#       bit 4:
#       0 = Test was executed
        if self.get_fields(6)[3][4] == '0':
            body += ''
#       1 = Test not executed
        elif self.get_fields(6)[3][4] == '1':
            body += 'N'
#       bit 5:
#       0 = No abort
        if self.get_fields(6)[3][5] == '0':
            body += ''
#       1= Test aborted
        elif self.get_fields(6)[3][5] == '1':
            body += 'X'
#       7 PARM_FLG bits 0, 1, 2, 3 & 4
#       bit 0:
#       0 = No scale error
        if self.get_fields(7)[3][0] == '0':
            body += ''
#       1 = Scale error
        elif self.get_fields(7)[3][0] == '1':
            body += 'S'
#       bit 1:
#       0 = No drift error
        if self.get_fields(7)[3][1] == '0':
            body += ''
#       1 = Drift error (unstable measurement)
        elif self.get_fields(7)[3][1] == '1':
            body += 'D'
#       bit 2:
#       0 = No oscillation
        if self.get_fields(7)[3][2] == '0':
            body += ''
#       1 = Oscillation detected
        elif self.get_fields(7)[3][2] == '1':
            body += 'O'
#       bit 3:
#       0 = Measured value not high
        if self.get_fields(7)[3][3] == '0':
            body += ''
#       1 = Measured value higher than high test limit
        elif self.get_fields(7)[3][3] == '1':
            body += 'H'
#       bit 4:
#       0 = Measured value not low
        if self.get_fields(7)[3][4] == '0':
            body += '|'
#       1 = Measured value lower than low test limit
        elif self.get_fields(7)[3][4] == '1':
            body += 'L|'
            
#       12 TEST_TXT
        body += "%s|" % self.get_fields(12)[3]
#       13 ALARM_ID
        body += "%s|" % self.get_fields(13)[3]

#       7 PARM_FLG bits 6 & 7
#       bit 6:
#       0 = If result = low limit, then result is “fail.”
        if self.get_fields(7)[3][6] == '0':
            body += ''
#       1 = If result = low limit, then result is “pass.”
        elif self.get_fields(7)[3][6] == '1':
            body += 'L'
#       bit 7:
#       0 = If result = high limit, then result is “fail.”
        if self.get_fields(7)[3][7] == '0':
            body += '|'
#       1 = If result = high limit, then result is “pass.”
        elif self.get_fields(7)[3][7] == '1':
            body += 'H|'

#       23 UNITS         
        body += "%s|" % self.get_fields(23)[3]
#       18 LO_LIMIT
        body += "%s|" % self.get_fields(18)[3]
#       19 HI_LIMIT
        body += "%s|" % self.get_fields(19)[3]
#       20 START_IN
        body += "%s|" % self.get_fields(20)[3]
#       21 INCR_IN
        body += "%s|" % self.get_fields(21)[3]
#       24 UNITS_IN
        body += "%s|" % self.get_fields(24)[3]
#       22 RTN_INDX
        value = self.get_fields(22)[3]
        for elem in value:
            body += "%s," % elem
        body = body[:-1] 
        body += "|"
#       25 C_RESFMT
        body += "%s|" % self.get_fields(25)[3]
#       26 C_LLMFMT
        body += "%s|" % self.get_fields(26)[3]
#       27 C_HLMFMT
        body += "%s|" % self.get_fields(27)[3]
#       28 LO_SPEC
        body += "%s|" % self.get_fields(28)[3]
#       29 HI_SPEC
        body += "%s|" % self.get_fields(29)[3]
#       15 RES_SCAL
        body += "%s|" % self.get_fields(15)[3]
#       16 LLM_SCAL
        body += "%s|" % self.get_fields(16)[3]
#       17 HLM_SCAL
        body += "%s|" % self.get_fields(17)[3]

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval