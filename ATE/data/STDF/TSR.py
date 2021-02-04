import sys
from ATE.data.STDF import STDR


class TSR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'TSR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info = '''
Test Synopsis Record
--------------------

Function:
    Contains the test execution and failure counts for one parametric or functional test in
    the test program. Also contains static information, such as test name. The TSR is
    related to the Functional Test Record (FTR), the Parametric Test Record (PTR), and the
    Multiple Parametric Test Record (MPR) by test number, head number, and site
    number.

Frequency:
    * Obligatory, one for each test executed in the test program per Head and site.
    * Optional summary per test head and/or test site.
    * May optionally be used to identify unexecuted tests.

Location:
    Anywhere in the data stream after the initial sequence (see page 14) and before the MRR.
    When test data is being generated in real-time, these records will appear after the last PRR.
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None       },
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :   10, 'Text' : 'Record type                           ', 'Missing' : None       },
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   30, 'Text' : 'Record sub-type                       ', 'Missing' : None       },
                'HEAD_NUM' : {'#' :  3, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' : 255        },
                'SITE_NUM' : {'#' :  4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test site number                      ', 'Missing' : 255        },
                'TEST_TYP' : {'#' :  5, 'Type' : 'C*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test type [P/F/space]                 ', 'Missing' : ' '        },
                'TEST_NUM' : {'#' :  6, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Test number                           ', 'Missing' : None       },
                'EXEC_CNT' : {'#' :  7, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of test executions             ', 'Missing' : 4294967295},
                'FAIL_CNT' : {'#' :  8, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of test failures               ', 'Missing' : 4294967295},
                'ALRM_CNT' : {'#' :  9, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of alarmed tests               ', 'Missing' : 4294967295},
                'TEST_NAM' : {'#' : 10, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test name                             ', 'Missing' : ''         },
                'SEQ_NAME' : {'#' : 11, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Sequencer (program segment/flow) name ', 'Missing' : ''         },
                'TEST_LBL' : {'#' : 12, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test label or text                    ', 'Missing' : ''         },
                'OPT_FLAG' : {'#' : 13, 'Type' : 'B*1', 'Ref' : None, 'Value' : None, 'Text' : 'Optional data flag See note           ', 'Missing' : ['1']*8    },
                'TEST_TIM' : {'#' : 14, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Average test execution time in seconds', 'Missing' : 0.0        },
                'TEST_MIN' : {'#' : 15, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Lowest test result value              ', 'Missing' : 0.0        },
                'TEST_MAX' : {'#' : 16, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Highest test result value             ', 'Missing' : 0.0        },
                'TST_SUMS' : {'#' : 17, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Sum of test result values             ', 'Missing' : 0.0        },
                'TST_SQRS' : {'#' : 18, 'Type' : 'R*4', 'Ref' : None, 'Value' : None, 'Text' : 'Sum of squares of test result values  ', 'Missing' : 0.0        }
            }

        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''
        
        header = self.id + ':'

#         The order of fields is different in STDF and ATDF for TSR record
#         
#         STDF page 45| ATDF page 41
#         
#          3 HEAD_NUM    =  3 HEAD_NUM    
#          4 STEP_NUM    =  4 STEP_NUM  
#          5 TEST_TYP    
#          6 TEST_NUM    =  6 TEST_NUM   
#          7 EXEC_CNT        
#          8 FAIL_CNT
#          9 ALRM_CNT    
#         10 TEST_NAM    =  10 TEST_NAM
#                            5 TEST_TYP
#                            7 EXEC_CNT
#                            8 FAIL_CNT
#                            9 ALRM_CNT
#         11 SEQ_NAME    = 11 SEQ_NAME 
#         12 TEST_LBL    = 12 TEST_LBL  
#         13 OPT_FLAG    > missing        
#         14 TEST_TIM    = 14 TEST_TIM      
#         15 TEST_MIN    = 15 TEST_MIN           
#         16 TEST_MAX    = 16 TEST_MAX         
#         17 TST_SUMS    = 17 TST_SUMS      
#         18 TST_SQRS    = 18 TST_SQRS                          

        f = self.get_fields(3)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(4)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(6)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(10)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(5)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(7)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(8)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(9)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(11)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(12)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(14)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(15)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(16)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(17)[3]
        if f == None:
            body += "|"
        else:
            body += "%s|" % f

        f = self.get_fields(18)[3]
        if f == None:
            body += ""
        else:
            body += "%s" % f

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval