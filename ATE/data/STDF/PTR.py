import sys
from ATE.data.STDF import STDR

class PTR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'PTR'
        self.local_debug = False
        if version==None or version == 'V4':
            self.version = 'V4'
            self.info = '''
Parametric Test Record
----------------------

Function:
    Contains the results of a single execution of a parametric test in the test program. The
    first occurrence of this record also establishes the default values for all semi-static
    information about the test, such as limits, units, and scaling. The PTR is related to the
    Test Synopsis Record (TSR) by test number, head number, and site number.

Frequency:
    * Obligatory, one per parametric test execution on each head/site

Location:
    Under normal circumstances, the PTR can appear anywhere in the data stream after
    the corresponding Part Information Record (PIR) and before the corresponding Part
    Result Record (PRR).
    In addition, to facilitate conversion from STDF V3, if the first PTR for a test contains
    default information only (no test results), it may appear anywhere after the initial
    "FAR-(ATRs)-MIR-(RDR)-(SDRs)" sequence, and before the first corresponding PTR, but need not appear
    between a PIR and PRR.
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'FPE' : None,                                     'Missing' : None   },
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :   15, 'Text' : 'Record type                           ', 'FPE' : None,                                     'Missing' : None   },
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   10, 'Text' : 'Record sub-type                       ', 'FPE' : None,                                     'Missing' : None   },
                'TEST_NUM' : {'#' :  3, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Test number                           ', 'FPE' : None,                                     'Missing' : None   },
                'HEAD_NUM' : {'#' :  4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test head number                      ', 'FPE' : None,                                     'Missing' : 1      },
                'SITE_NUM' : {'#' :  5, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test site number                      ', 'FPE' : None,                                     'Missing' : 1      },
                'TEST_FLG' : {'#' :  6, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test flags (fail, alarm, etc.)        ', 'FPE' : None,                                     'Missing' : ['0']*8},
                'PARM_FLG' : {'#' :  7, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Parametric test flags (drift, etc.)   ', 'FPE' : None,                                     'Missing' : ['0']*8},
                'RESULT'   : {'#' :  8, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Test result                           ', 'FPE' : None,                                     'Missing' : 0.0    },
                'TEST_TXT' : {'#' :  9, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test description text or label        ', 'FPE' : None,                                     'Missing' : ''     },
                'ALARM_ID' : {'#' : 10, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Name of alarm                         ', 'FPE' : None,                                     'Missing' : ''     },
                'OPT_FLAG' : {'#' : 11, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Optional data flag                    ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 255    }, #TODO: Needs some more work
                'RES_SCAL' : {'#' : 12, 'Type' : 'I*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test results scaling exponent         ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0      },
                'LLM_SCAL' : {'#' : 13, 'Type' : 'I*1', 'Ref' : None, 'Value' : None, 'Text' : 'Low limit scaling exponent            ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0      },
                'HLM_SCAL' : {'#' : 14, 'Type' : 'I*1', 'Ref' : None, 'Value' : None, 'Text' : 'High limit scaling exponent           ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0      },
                'LO_LIMIT' : {'#' : 15, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Low test limit value                  ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0.0    },
                'HI_LIMIT' : {'#' : 16, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'High test limit value                 ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0.0    },
                'UNITS'    : {'#' : 17, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test units                            ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : ''     },
                'C_RESFMT' : {'#' : 18, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'ANSI C result format string           ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : ''     },
                'C_LLMFMT' : {'#' : 19, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'ANSI C low limit format string        ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : ''     },
                'C_HLMFMT' : {'#' : 20, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'ANSI C high limit format string       ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : ''     },
                'LO_SPEC'  : {'#' : 21, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Low specification limit value         ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0.0    },
                'HI_SPEC'  : {'#' : 22, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'High specification limit value        ', 'FPE' : "self.fields['OPT_FLAG']['Value']!=None", 'Missing' : 0.0    }
            }

        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''
        
        header = self.id + ':'

#         The order of fields is different in STDF and ATDF for PTR record
#         
#         STDF page 47| ATDF page 43
#         
#          3 TEST_NUM    =  3 TEST_NUM   
#          4 HEAD_NUM    =  4 HEAD_NUM    
#          5 SITE_NUM    =  5 SITE_NUM  
#          6 TEST_FLG    
#          7 PARM_FLG        
#          8 RESULT      =  8 RESULT
#                           6 TEST_FLG bits 6 and 7
#                           7 PARM_FLG bit 5
#                           6 TEST_FLG bits 0, 2, 3, 4, 5
#                           7 PARM_FLG bits 0, 1, 2, 3, 4
#          9 TEST_TXT    =  9 TEST_TXT 
#         10 ALARM_ID    = 10 ALARM_ID  
#         11 OPT_FLAG    > missing        
#                           7 PARM_FLG bits 6 and 7
#         12 RES_SCAL
#         13 LLM_SCAL
#         14 HLM_SCAL
#         15 LO_LIMIT
#         16 HI_LIMIT
#         17 UNITS       = 17 UNITS  
#                          15 LO_LIMIT
#                          16 HI_LIMIT
#         18 C_RESFMT    = 18 C_RESFMT  
#         19 C_LLMFMT    = 19 C_LLMFMT  
#         20 C_HLMFMT    = 20 C_HLMFMT  
#         21 LO_SPEC     = 21 LO_SPEC  
#         22 HI_SPEC     = 22 HI_SPEC  
#                          12 RES_SCAL
#                          13 LLM_SCAL
#                          14 HLM_SCAL

#       3 TEST_NUM 
        body += self.gen_atdf(3)
#       4 HEAD_NUM 
        body += self.gen_atdf(4)
#       4 SITE_NUM 
        body += self.gen_atdf(5)
#       8 RESULT 
        body += self.gen_atdf(8)

#        Pass/Fail Flag:
#        TEST_FLG bits 6 & 7
#        PARM_FLG bit 5
#        
#            The Pass/Fail Flag indicates the result of the test. 
#            If the flag is empty, the test completed without a pass/fail 
#            indication from the test program.Legal values are:
#                A =Test passed alternate limits
#                F =Test failed
#                P =Test passed standard limits
#                empty =Test completed without pass/failindication

        buff = ''
#        TEST_FLG
#        bit 6:
#            0 = Pass/fail flag (bit 7) is valid
#            1 = Test completed with no pass/fail indication

        v = self.get_fields(6)[3] 
        if v != None and v[6] == '1':
            buff += ' '
        elif v != None and v[6] == '0':
            test_status = 'Unknown'
#            TEST_FLG
#            bit 7:
#                0 = Test passed
#                1 = Test failed

            if sv[7] == '0':
                buff += 'P'
                test_status = 'P'
            elif v[7] == '1':
                buff += 'F'
                test_status = 'F'

#       7    PARM_FLG
#            bit 5:
#                0 = Test failed or test passed standard limits
#                1 = Test passed alternate limits
            v = self.get_fields(7)[3] 
            if v != None and v[5] == '0':
                buff += test_status
            elif v != None and [5] == '1':
                buff += 'A'
        body += "%s|" % buff
#        Alarm Flags:
#            TEST_FLG bits 0, 2, 3, 4 & 5
#            PARM_FLG bits 0, 1, 2, 3 & 4
#            
#            This field may contain zero or more flags. Each flag indicates 
#            an alarm or error condition that occurred during the test 
#            execution. Legal values are:
#                
#                A = Alarm detected
#                D = Drift error
#                H = Measured value higher than test limit
#                L = Measured value lower than low limit
#                N = Test was not executedO = Oscillation detected
#                S = Scale errorT = Time-out occurred
#                U = Test result is unreliable
#                X = Test aborted
#            

        buff = ''

#        6 TEST_FLG
#        bit 0:
#            0 = No alarm
#            1 = Alarm detected during testing

        v = self.get_fields(6)[3] 
        if v != None and v[0] == '0':
            buff += ' '
        elif v != None and v[0] == '1':
            buff += 'A'
#            TEST_FLG
#            bit 2:
#                0 = Test result is reliable
#                1 = Test result is unreliable                
            if v[2] == '0':
                buff += ' '
            elif v[2] == '1':
                buff += 'U'
#            TEST_FLG
#            bit 3:
#                0 = No timeout
#                1 = Timeout occurred
            if v[3] == '0':
                buff += ' '
            elif v[3] == '1':
                buff += 'T'
#            TEST_FLG
#            bit 4:
#                0 = Test was executed
#                1 = Test was not executed
            if v[4] == '0':
                buff += ' '
            elif v[4] == '1':
                buff += 'N'
#            TEST_FLG
#            bit 5:
#                0 = No abort
#                1 = Test aborted
            if v[5] == '0':
                buff += ' '
            elif v[5] == '1':
                buff += 'X'
#            PARM_FLG
#            bit 0:
#                0 = No scale error
#                1 = Scale error
            if self.get_fields(7)[3][0] == '0':
                buff += ' '
            elif self.get_fields(7)[3][0] == '1':
                buff += 'S'
#            7 PARM_FLG
#            bit 1:
#                0 = No drift error
#                1 = Drift error (unstable measurement)
            v = self.get_fields(7)[3] 
            if v != None and v[1] == '0':
                buff += ' '
            elif v != None and v[1] == '1':
                buff += 'D'
#            PARM_FLG
#            bit 2:
#                0 = No oscillation
#                1 = Oscillation detected
            if v != None and v[2] == '0':
                buff += ' '
            elif v != None and v[2] == '1':
                buff += 'O'
#            PARM_FLG
#            bit 3:
#                0 = Measured value not high
#                1 = Measured value higher than high test limit
            if v != None and v[3] == '0':
                buff += ' '
            elif v != None and v[3] == '1':
                buff += 'H'
#            PARM_FLG
#            bit 4:
#                0 = Measured value not low
#                1 = Measured value higher than low test limit
            if v != None and v[4] == '0':
                buff += ' '
            elif v != None and v[4] == '1':
                buff += 'L'

        body += "%s|" % buff
                
#       9 TEST_TXT 
        body += self.gen_atdf(9)
#       10 ALARM_ID
        body += self.gen_atdf(10)

#        Limit Compare:
#            PARM_FLG bits 6 & 7
#
#                By default, limits are compared such that the test fails 
#                when the low limit is greater than the test result or the 
#                high limit is less than the test result. If that is the 
#                case, this field should be empty. Otherwise, the field 
#                should contain one or two letters indicating:                
#                
#                L = Low limit comparison was >=
#                H = High limit comparison was <=
#            
        buff = ''

#        7 PARM_FLG
#        bit 6:
#            0 = If result = low limit, then result is “fail.”
#            1 = If result = low limit, then result is “pass.”
        v = self.get_fields(7)[3] 
        if v != None and v[6] == '0':
            buff += ' '
        elif v != None and v[6] == '1':
            buff += 'L'
#        7 PARM_FLG
#        bit 7:
#            0 = If result = high limit, then result is “fail.”
#            1 = If result = high limit, then result is “pass.”
        if v != None and v[7] == '0':
            buff += ' '
        elif v != None and v[7] == '1':
            buff += 'H'

        body += "%s|" % buff

#       17 UNITS  
        body += self.gen_atdf(17)
#       15 LO_LIMIT  
        body += self.gen_atdf(15)
#       16 HI_LIMIT  
        body += self.gen_atdf(16)
#       18 C_RESFMT  
        body += self.gen_atdf(18)
#       19 C_LLMFMT  
        body += self.gen_atdf(19)
#       20 C_HLMFMT  
        body += self.gen_atdf(20)
#       21 C_HLMFMT  
        body += self.gen_atdf(21)
#       22 HI_SPEC  
        body += self.gen_atdf(22)
#       12 RES_SCAL 
        body += self.gen_atdf(12)
#       13 LLM_SCAL 
        body += self.gen_atdf(13)
#       14 HLM_SCAL
        body += self.gen_atdf(14)

        body = body[:-1] 

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval    