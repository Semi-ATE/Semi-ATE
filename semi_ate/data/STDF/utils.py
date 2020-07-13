'''
Created on 11 Aug 2019

@author: tho
'''
import os
import re
import struct
import sys

from ATE.data.STDF.records import *
from ATE.utils.compression import (
    default_compression,
    get_deflated_file_size,
    supported_compressions,
    supported_compressions_extensions
)
from ATE.utils.magicnumber import (
    extension_from_magic_number_in_file,
    is_compressed_file
)
from ATE.utils.varia import os_is_case_sensitive, path_is_writeable_by_me

# def stdfopen(FileName, mode='rb'):
#     '''
#     returns an open file object to the stdf file.
#     if the file is no STDF file, None is returned.
#     if the STDF file is compressed, returns the file object of the correct algorithm.

#     mode = 'rb' or 'wb' (no text supported ... raise ValueError if not rb or wb)
#     '''
#     if mode!='rb' and mode!='rb': raise ValueError("Only 'rb' and 'wb' are supported.")
#     if not is_STDF(FileName): return None



# def to_df(FileName, progress=True):
#     '''
#     This function will return a pandas data-frame from the given FileName.

#     This process has 3 stages :
#         1) index the FileName
#         2) Analyse
#         2) construct the dataframe

#     ---> needs to move to metis !!! metis.import_stdf(...)

#     '''

#     index = {}
# #   index = {'version' : stdf_version,
# #            'endian'  : stdf_endian,
# #            'records' : { REC_NAM : [offset, ...
# #            'indexes' : { offset : bytearray of the record ...
# #            'parts' : {part# : [offset, offset, offset, ...
#     offset = 0

#     if is_STDF(FileName):
#         endian, version = endian_and_version_from_file(FileName)
#         index['version'] = version
#         index['endian'] = endian
#         index['records'] = {}
#         index['indexes'] = {}
#         index['parts'] = {}
#         PIP = {} # parts in process
#         PN = 1

#         TS2ID = ts_to_id(version)

#         if progress:
#             description = "Indexing STDF file '%s'" % os.path.split(FileName)[1]
#             index_progress = tqdm(total=get_deflated_file_size(FileName), ascii=True, disable=not progress, desc=description, leave=False, unit='b')

#         for _, REC_TYP, REC_SUB, REC in records_from_file(FileName):
#             REC_ID = TS2ID[(REC_TYP, REC_SUB)]
#             REC_LEN = len(REC)
#             if REC_ID not in index['records']: index['records'][REC_ID] = []
#             index['indexes'][offset] = REC
#             index['records'][REC_ID].append(offset)
#             if REC_ID in ['PIR', 'PRR', 'PTR', 'FTR', 'MPR']:
#                 if REC_ID == 'PIR':
#                     pir = PIR(index['version'], index['endian'], REC)
#                     pir_HEAD_NUM = pir.get_value('HEAD_NUM')
#                     pir_SITE_NUM = pir.get_value('SITE_NUM')
#                     if (pir_HEAD_NUM, pir_SITE_NUM) in PIP:
#                         raise Exception("One should not be able to reach this point !")
#                     PIP[(pir_HEAD_NUM, pir_SITE_NUM)] = PN
#                     index['parts'][PN]=[]
#                     index['parts'][PN].append(offset)
#                     PN+=1
#                 elif REC_ID == 'PRR':
#                     prr = PRR(index['version'], index['endian'], REC)
#                     prr_HEAD_NUM = prr.get_value('HEAD_NUM')
#                     prr_SITE_NUM = prr.get_value('SITE_NUM')
#                     if (prr_HEAD_NUM, prr_SITE_NUM) not in PIP:
#                         raise Exception("One should not be able to reach this point!")
#                     pn = PIP[(prr_HEAD_NUM, prr_SITE_NUM)]
#                     index['parts'][pn].append(offset)
#                     del PIP[(prr_HEAD_NUM, prr_SITE_NUM)]
#                 elif REC_ID == 'PTR':
#                     ptr = PTR(index['version'], index['endian'], REC)
#                     ptr_HEAD_NUM = ptr.get_value('HEAD_NUM')
#                     ptr_SITE_NUM = ptr.get_value('SITE_NUM')
#                     if (ptr_HEAD_NUM, ptr_SITE_NUM) not in PIP:
#                         raise Exception("One should not be able to reach this point!")
#                     pn = PIP[(ptr_HEAD_NUM, ptr_SITE_NUM)]
#                     index['parts'][pn].append(offset)
#                 elif REC_ID == 'FTR':
#                     ftr = FTR(index['version'], index['endian'], REC)
#                     ftr_HEAD_NUM = ftr.get_value('HEAD_NUM')
#                     ftr_SITE_NUM = ftr.get_value('SITE_NUM')
#                     if (ftr_HEAD_NUM, ftr_SITE_NUM) not in PIP:
#                         raise Exception("One should not be able to reach this point!")
#                     pn = PIP[(ftr_HEAD_NUM, ftr_SITE_NUM)]
#                     index['parts'][pn].append(offset)
#                 elif REC_ID == 'MPR':
#                     mpr = MPR(index['version'], index['endian'], REC)
#                     mpr_HEAD_NUM = mpr.get_value('HEAD_NUM')
#                     mpr_SITE_NUM = mpr.get_value('SITE_NUM')
#                     if (mpr_HEAD_NUM, mpr_SITE_NUM) not in PIP:
#                         raise Exception("One should not be able to reach this point!")
#                     pn = PIP[(mpr_HEAD_NUM, mpr_SITE_NUM)]
#                     index['parts'][pn].append(offset)
#                 else:
#                     raise Exception("One should not be able to reach this point! (%s)" % REC_ID)
#             if progress: index_progress.update(REC_LEN)
#             offset += REC_LEN

#         if progress:
#             description = "Analyzing data"
#             ttl = len(index['records']['TSR'])
#             analyze_progress = tqdm(total=ttl, ascii=True, position=1, disable=not progress, desc=description, leave=False, unit='tests')

#         TEST_NUM_NAM = {}

#         for tsr_offset in index['records']['TSR']:
#             tsr = TSR(index['version'], index['endian'], index['indexes'][tsr_offset])
#             TEST_NUM = tsr.get_value('TEST_NUM')
#             TEST_NAM = tsr.get_value('TEST_NAM')
#             TEST_TYP = tsr.get_value('TEST_TYP').upper()
#             if TEST_NUM not in TEST_NUM_NAM:
#                 TEST_NUM_NAM[TEST_NUM] = []
#             if (TEST_NAM, TEST_TYP) not in TEST_NUM_NAM[TEST_NUM]:
#                 TEST_NUM_NAM[TEST_NUM].append((TEST_NAM, TEST_TYP))
#             analyze_progress.update()

#         for TEST_NUM in TEST_NUM_NAM:
#             if len(TEST_NUM_NAM[TEST_NUM])==1:
#                 TEST_NUM_NAM[TEST_NUM] = TEST_NUM_NAM[TEST_NUM][0]


#         # Create the indexes of the dataframe
#         ROW_index = sorted(list(index['parts']))
#         TEST_ITM_index = ['LOT_ID', 'MOD_COD', 'X_POS', 'Y_POS'] #TODO: add more ...
#         TEST_NAM_index = ['Meta'] * len(TEST_ITM_index)
#         TEST_NUM_index = ['Meta'] * len(TEST_ITM_index)
#         for TEST_NUM in sorted(TEST_NUM_NAM):
#             TEST_TYP = TEST_NUM_NAM[TEST_NUM][1]
#             if TEST_TYP == 'P':
#                 PTR_FIELDS = ['LO_SPEC', 'LO_LIMIT', 'RESULT', 'HI_LIMIT', 'HI_LIMIT', 'UNITS', 'PF']
#                 TEST_ITM_index+=PTR_FIELDS
#                 TEST_NAM_index+=[TEST_NUM_NAM[TEST_NUM][1]]*len(PTR_FIELDS)
#                 TEST_NUM_index+=[TEST_NUM]*len(PTR_FIELDS)
#             elif TEST_TYP == 'F':

#                 TEST_NUM_index+=[TEST_NUM]*5
#                 TEST_NAM_index+=[TEST_NUM_NAM[TEST_NUM][1]]*5     # VECT_NAME TIME_SET NUM_FAIL X_FAIL_AD Y_FAIL_AD PF
#             elif TEST_TYP == 'M':
#                 pass
#             else:
#                 raise STDFError("Test Type '%s' is unknown" % TEST_TYP)




#         print("\n\n\n")


#         for record_offset in index['parts'][1]:
#             record = index['indexes'][record_offset]
#             T, S = TS_from_record(record)
#             ID = TS2ID[(T,S)]
#             if ID == 'PTR':
#                 ptr = PTR(index['version'], index['endian'], record)
#                 print(ptr)
#             if ID == 'PIR':
#                 pir = PIR(index['version'], index['endian'], record)
#                 print(pir)
#             if ID == 'PRR':
#                 prr = PRR(index['version'], index['endian'], record)
#                 print(prr)





# #         if progress:
# #             description = "Constructing data-frame"
# #             constructing_progress = tqdm(total=len(index['parts']), ascii=True, position=2, disable=not progress, desc=description, leave=False, unit='parts')
# #
# #         for part in index['parts']:
# #             for record_offset in index['parts'][part]:
# #                 Type, SubType = TS_from_record(index['indexes'][record_offset])
# #                 ID = TS2ID[(Type, SubType)]
# #                 if ID == 'FTR':
# #                     ftr = FTR(index['version'], index['endian'], index['indexes'][record_offset])
# #
# #
# #                 if ID == 'PTR':
# #                     ptr = PTR(index['version'], index['endian'], index['indexes'][record_offset])
# #
# #                 if ID == 'MPR':
# #                     ptr = MPR(index['version'], index['endian'], index['indexes'][record_offset])
# #
# #
# #
# #             constructing_progress.update()







#         if progress:
#             index_progress.close()
#             analyze_progress.close()
# #             constructing_progress.close()

#         return index, TEST_NUM_NAM

#     else: #not an STDF file
#         pass

# class File(object):
#
#     def __init__(self, FileName):
#         self.__call__(FileName)
#
#     def __call__(self, FileName):
#         # name & path
#         self.file_name = os.path.abspath(FileName)
#         self.path, self.name = os.path.split(self.file_name)
#         self.base_name = self.name.split('.')[0]
#         # File Exists
#         if not os.path.isfile(self.file_name):
#             raise IOError("File '%s' Not Found" % self.file_name)
#         # compression support
#         if re.search(r'stdf?\.gz$', self.name, re.I) and magicnumber.extension_from_magic_number_in_file(self.file_name)==['.gzip']: # gzip
#             self.is_compressed = True
#             self.compression = 'gz'
#         elif False: # zip
#             pass
#         elif False: # 7z
#             pass
#         else:
#             self.is_compressed = False
#         # Endian & Version
#         if self.is_compressed:
#             with gzip.open(self.file_name, 'rb') as fd:
#                 buff = fd.read(6)
#             CPU_TYPE, STDF_VER = struct.unpack('BB', buff)
#         else:
#             CPU_TYPE, STDF_VER = struct.unpack('BB', self._get_bytes_from_file(4, 2))
#         self.version = 'V%s' % STDF_VER
#         if CPU_TYPE == 1: # sun 1,2,3,4
#             self.endian = '>'
#         elif CPU_TYPE == 2: # PC
#             self.endian = '<'
#         else:
#             self.endian = '?'
#         self.RHF = '%sHBB' % self.endian
#         # verify if version supported
#         if self.version not in supported().versions():
#             name_valid_for_versions=self.is_valid_name_for_versions()
#             if len(name_valid_for_versions)==0:
#                 raise STDFError("'%s' is not an STDF file" % self.file_name)
#             else:
#                 raise STDFError("'%s' pretends to be an STDF file, but it is not" % self.file_name)
#         if self.endian =='?':
#             raise STDFError("Unsupported endian in '%s'" % self.file_name)
#         # Save File Creation
#         self.modification_time = os.path.getmtime(self.file_name)
#         # record identification
#         self.TS2ID = ts_to_id(self.version)
#         self.ID2TS = id_to_ts(self.version)
#         # file pointer
#         if self.is_compressed:
#             self.fd = gzip.open(self.file_name, 'rb')
#         else:
#             self.fd = open(self.file_name, 'rb')
#         # indexes
#         self.records_are_indexed = False
#         self.record_index = {}
#         self.tests_are_indexed = False
#         self.test_index = {}
#
#     def objects_from_indexed_file(self, index, records_of_interest=None):
#         '''
#          This is a Generator of records (not in order!)
#         '''
#         if records_of_interest==None:
#             roi = list(self.ID2TS.keys())
#         elif isinstance(records_of_interest, list):
#             roi = []
#             for item in records_of_interest:
#                 if isinstance(item, str):
#                     if (item in list(self.ID2TS.keys())) and (item not in roi):
#                         roi.append(item)
#         else:
#             raise STDFError("STDF.objects_from_indexed_file(index, records_of_interest) : Unsupported records_of_interest" % records_of_interest)
#         for REC_ID in roi:
#             if REC_ID in index:
#                 for fp in index[REC_ID]:
#                     OBJ = create_record_object(self.version, self.endian, REC_ID, get_record_from_file_at_position(self.fd, fp, self.RHF))
#                     yield OBJ
#
#
#     def build_record_index(self):
#         '''
#         This method will build_uis an index of where which record starts in self.file_name
#         '''
#         def get_record_header(offset):
#             fd.seek(offset)
#             header = fd.read(4)
#             REC_LEN, REC_TYP, REC_SUB = struct.unpack(FMT, header)
#             return REC_LEN, REC_TYP, REC_SUB
#
#         if not self.records_are_indexed:
#             TS2ID = ts_to_id(self.version)
#             FMT = "%sHBB" % self.endian
#             fp = 0
#             size = os.stat(self.file_name).st_size
#             fd = open(self.file_name, 'rb')
#             while True:
#                 REC_LEN, REC_TYP, REC_SUB = get_record_header(fp)
#                 ID = TS2ID[REC_TYP, REC_SUB]
#                 if ID in self.record_index:
#                     self.record_index[ID].append(fp)
#                 else:
#                     self.record_index[ID] = [fp]
#                 fp += (REC_LEN+4)
#                 if fp == size: break
#             self.records_are_indexed = True
#
#     def build_test_index(self):
#         '''
#         This method will build_uis an index for each test
#         '''
#         # make sure the records are indexed
#         if not self.records_are_indexed:
#             self.build_record_index()
#         # build_uis the test index
#         if not self.tests_are_indexed:
#             for OBJ in objects_from_indexed_file(self.fd, self.record_index, ['TSR']):
#                 print(OBJ)
# #                 HEAD_NUM = OBJ.get_value('HEAD_NUM')
# #                 SITE_NUM = OBJ.get_value('SITE_NUM')
# #                 TEST_TYP = OBJ.get_value('TEST_TYP')
# #                 TEST_NUM = OBJ.get_value('TEST_NUM')
# #                 EXEC_CNT = OBJ.get_value('EXEC_CNT')
# #                 FAIL_CNT = OBJ.get_value('FAIL_CNT')
# #                 TEST_NAM = OBJ.get_value('TEST_NAM')
# #
# #                 if TEST_NUM not in self.test_index:
# #                     self.test_index[TEST_NUM] = {}
# #                 if HEAD_NUM not in self.test_index[(TEST_NAM, TEST_NUM, TEST_TYP)]:
# #                     self.test_index[(TEST_NAM, TEST_NUM, TEST_TYP)][HEAD_NUM] = {}
# #                 if SITE_NUM not in self.test_index[(TEST_NAM, TEST_NUM, TEST_TYP)][HEAD_NUM]:
# #                     self.test_index[(TEST_NAM, TEST_NUM, TEST_TYP)][HEAD_NUM][SITE_NUM] = {'CNT' : (EXEC_CNT, FAIL_CNT), 'REF' : []}
# #
# #
# #
# #
# #         self.tests_are_indexed = True
#
#     def check_obligatory_records(self, rebuild_index=False):
#         '''
#         This method will check if the obligatory records are present in self.file_name
#         '''
#         # make sure the file is indexed
#         if not self.is_indexed:
#             self.build_index(rebuild_index)
#         # compile a list of all possible records for self.version
#
#
#
#         # Check if the obligatory records are found,
#         if 'PCR' not in self.index: print("WARNING : No PCR records found")
#         #TODO: add other obligatory records here (make it dynamic from 'RecordDefinitions'
#
#     def _print_record_index(self, rebuild=False):
#         if rebuild or not self.records_are_indexed:
#             self.build_record_index(rebuild)
#         for REC_ID in self.record_index:
#             print("%s : %s" % (REC_ID, len(self.record_index[REC_ID])))
#
#     def _get_bytes_from_file(self, offset, number):
#         '''
#         This method will read 'number' bytes from file starting from 'offset' and return the buffer.
#         '''
#         fd = self.open()
#         fd.seek(offset)
#         buff = fd.read(number)
#         fd.close()
#         return buff
#
#     def size(self):
#         '''
#         This method will return a tupple that denotes the size in bytes of self.file_name.
#         (decompessed_size, compressed_size)
#         If a file is not compressed, the 2 values in the tuple will be equal.
#         '''
#         decompressed_size = 0
#         compressed_size = 0
#         if self.is_compressed:
#             compressed_size = os.stat(self.file_name).st_size
#             with open(self.file_name, 'rb') as fd:
#                 fd.seek(-4, 2) # last 4 bytes give the unpacked size of the file
#                 decompressed_size = struct.unpack('<I', fd.read(4))[0]
#         else:
#             decompressed_size = os.stat(self.file_name).st_size
#             compressed_size = decompressed_size
#         return (decompressed_size, compressed_size)
#
#     def open(self, mode='rb'):
#         '''
#         This method will return a transparent file handle to self.file_name
#         '''
#         if self.is_compressed:
#             return gzip.open(self.file_name, mode)
#         else:
#             return open(self.file_name, mode)
#
#     def md5(self):
#         '''
#         This method will calculate the md5 digest of self.file_name
#         If self.file_name is compressed, it will calculate the md5 of the *UNCOMPRESSED* version.
#         '''
#         if self.is_compressed:
#             return hashlib.md5(gzip.open(self.file_name, 'rb').read()).hexdigest().upper()
#         else:
#             return hashlib.md5(open(self.file_name, 'rb').read()).hexdigest().upper()
#
#     def is_md5_file_name(self):
#         '''
#         This method will return True if the self.name is an MD5 file name.
#         '''
#         base_name = self.name.split('.')[0]
#         if len(base_name)==36 and base_name.startswith('MD5_'):
#             return True
#         return False
#
#     def check_md5(self):
#         '''
#         This method will return True if the file-name's md5 equals the actual digest of the (uncompressed) self.file_name.
#         If self.file_name is not an md5 file name, the result is also False.
#         '''
#         if self.is_md5_file_name():
#             if self.name.split('.')[0].replace('MD5_', '') == self.md5():
#                 return True
#         return False
#
#     def get_part_data(self, PIR_pointer):
#         '''
#         This method will seek self.fd to fp, and expect a PIR record (if not nothing will be returned)
#         From the PIR it determines HEAD_NUM and SITE_NUM.
#         The it continues to read records until it encounters either a PIR for the same HEAD_NUM/SITE_NUM or
#         a PRR With the same HEAD_NUM/SITE_NUM (in which case it also has a SOFT/HARD bin data for the part.
#         The whole data-structure for the part is returned.
#         '''
#         def records_from_part(HEAD_NUM, SITE_NUM):
#             while True:
#                 header = self.fd.read(4)
#                 REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.RHF, header)
#                 footer = self.fd.read(REC_LEN)
#                 OBJ = create_record_object(self.version, self.endian, self.TS2ID[REC_TYP, REC_SUB], header+footer)
#                 REC_ID = self.TS2ID[REC_TYP, REC_SUB]
#                 if REC_ID in ['PRR', 'PTR', 'MPR', 'FTR']:
#                     if OBJ.get_value('HEAD_NUM')==HEAD_NUM and OBJ.get_value('SITE_NUM'):
#                         yield OBJ
#                 elif REC_ID == 'PIR':
#                     if OBJ.get_value('HEAD_NUM')==HEAD_NUM and OBJ.get_value('SITE_NUM'):
#                         break
#
#         retval = {'INF' : {'HEAD_NUM' : -1,
#                            'SITE_NUM' : -1,
#                            'PF' : '',
#                            'NUM_TEST' : 0,
#                            'HARD_BIN' : -1,
#                            'SOFT_BIN' : -1,
#                            'X_COORD' : -32768,
#                            'Y_COORD' : -32768,
#                            'TEST_T' : 0,
#                            'PART_ID' : '',
#                            'PART_TXT' : '',
#                            'PART_FIX' : ''},
#                   'PTR' : {},
#                   'MPR' : {},
#                   'FTR' : {}}
#
#         self.fd.seek(PIR_pointer)
#         _, REC_TYP, REC_SUB, REC = read_record(self.fd, self.RHF)
#         if self.TS2ID[(REC_TYP, REC_SUB)] != 'PIR': raise STDFError("Didn't get a file pointer set to a PIR")
#         PIR = create_record_object(self.version, self.endian, 'PIR', REC)
#         HEAD_NUM = PIR.get_value('HEAD_NUM')
#         SITE_NUM = PIR.get_value('SITE_NUM')
#         retval['INF']['HEAD_NUM'] = PIR.get_value('HEAD_NUM')
#         retval['INF']['SITE_NUM'] = PIR.get_value('SITE_NUM')
#
#         for OBJ in records_from_part(HEAD_NUM, SITE_NUM):
#             if OBJ.id == 'PTR':
#                 HiSpecLim = OBJ.get_value('HI_SPEC')*pow(10, OBJ.get_value('HLM_SCAL'))
#                 LoSpecLim = OBJ.get_value('LO_SPEC')*pow(10, OBJ.get_value('LLM_SCAL'))
#                 HiTestLim = OBJ.get_value('HI_LIMIT')*pow(10, OBJ.get_value('HLM_SCAL'))
#                 LoTestLim = OBJ.get_value('LO_LIMIT')*pow(10, OBJ.get_value('LLM_SCAL'))
#                 Result = OBJ.get_value('RESULT')*pow(10, OBJ.get_value('RES_SCAL'))
#                 Unit = OBJ.get_value('UNITS')
#                 TEST_NUM = OBJ.get_value('TEST_NUM')
#                 TEST_FLG = OBJ.get_value('TEST_FLG')
#                 #PARM_FLG = OBJ.get_value('PARM_FLG')
#                 if TEST_FLG[6:] == ['0', '0']:
#                     PF = 'P'
#                 elif TEST_FLG[6:] == ['0', '1']:
#                     PF = 'F'
#                 else:
#                     PF = '?'
#                 retval['PTR'][TEST_NUM] = (HiSpecLim, HiTestLim, Result, LoTestLim, LoSpecLim, Unit, PF)
#             elif OBJ.id == 'MPR':
#                 pass
#             elif OBJ.id == 'FTR':
#                 pass
#             elif OBJ.id == 'PRR':
#                 retval['INF']['NUM_TEST'] = OBJ.get_value('NUM_TEST')
#                 retval['INF']['HARD_BIN'] = OBJ.get_value('HARD_BIN')
#                 retval['INF']['SOFT_BIN'] = OBJ.get_value('SOFT_BIN')
#                 retval['INF']['X_COORD'] = OBJ.get_value('X_COORD')
#                 retval['INF']['Y_COORD'] = OBJ.get_value('Y_COORD')
#                 retval['INF']['TEST_T'] = OBJ.get_value('TEST_T')
#                 retval['INF']['PART_ID'] = OBJ.get_value('PART_ID')
#                 retval['INF']['PART_TXT'] = OBJ.get_value('PART_TXT')
#                 retval['INF']['PART_FIX'] = OBJ.get_value('PART_FIX')
#                 if OBJ.get_value('PART_FLG')[3:5] == ['0', '0']:
#                     retval['INF']['PF'] = 'P'
#                 elif OBJ.get_value('PART_FLG')[3:5] == ['1', '0']:
#                     retval['INF']['PF'] = 'F'
#                 else:
#                     retval['INF']['PF'] = '?'
#                 break
#             else:
#                 raise "records from part should only return PTR/FTR/MPTR or PRR records"
#         return retval
#
#     def to_df(self, test_of_interest, with_progress=False):
#         '''
#         This method will create and return a pandas dataframe for test_of_interest
#         '''
#         pass
#
#     def to_xlsx(self, tests_of_interest=None, also_clean_tests=True, with_progress=False):
#         '''
#         This method will save the data from the STDF file self.file_name to an .xslx file in the same
#         directory as self.file_name. If the target file already exists, it will be overwritten.
#         '''
#         if not self.is_snarfed:
#             if with_progress:
#                 print("Collecting data ...")
#             self.snarf(with_progress=with_progress)
#
# #         if with_progress:
# #            print "Writing data ..."
# #             pbar = pb.ProgressBar(maxval=8, widgets=[pb.SimpleProgress() , ' =', pb.Percentage(), ' ', pb.Bar(), ' ', pb.Timer(), ' ',pb.ETA()]).start()
#
#
#     # Create workbook
#         xlsx_file_name = os.path.join(self.path, '%s.xlsx' % self.base_name )
#         if os.path.exists(xlsx_file_name):
#             os.unlink(xlsx_file_name)
#         workbook = xlsxwriter.Workbook(xlsx_file_name)
#
#         bold_right = workbook.add_format({'bold': True, 'align' : 'right'})
#
#         bold = workbook.add_format({'bold': True})
#         left = workbook.add_format({'align' : 'left'})
#         right = workbook.add_format({'align' : 'right'})
#         left_percent = workbook.add_format({'align' : 'left', 'num_format' : '0.00%'})
#
#         failed = workbook.add_format({'pattern' : 1, 'bg_color' : 'red', 'bold' : True})
#
#
#
#     # Information Sheet
#         info_sheet = workbook.add_worksheet('Info')
#         info_sheet.write( 0, 0, 'Date and time of job setup :');             info_sheet.write( 0, 1, self.data['INFO']['SETUP_T']);  info_sheet.write( 0, 2, str(DT(self.data['INFO']['SETUP_T'])))
#         info_sheet.write( 1, 0, 'Date and time first part tested :');        info_sheet.write( 1, 1, self.data['INFO']['START_T']);  info_sheet.write( 1, 2, str(DT(self.data['INFO']['START_T'])))
#         info_sheet.write( 2, 0, 'Date and time last part tested :');         info_sheet.write( 2, 1, self.data['INFO']['FINISH_T']); info_sheet.write( 2, 2, str(DT(self.data['INFO']['FINISH_T'])))
#         info_sheet.write( 3, 0, 'Tester station number :');                  info_sheet.write( 3, 1, self.data['INFO']['STAT_NUM'])
#         info_sheet.write( 4, 0, 'Test mode code [A/M/P/E/M/P/Q/space] :');   info_sheet.write( 4, 1, self.data['INFO']['MODE_COD'])
#         info_sheet.write( 5, 0, 'Lot retest code [Y/N/0..9/space] :');       info_sheet.write( 5, 1, self.data['INFO']['RTST_COD'])
#         info_sheet.write( 6, 0, 'Lot disposition code :');                   info_sheet.write( 6, 1, self.data['INFO']['DISP_COD'])
#         info_sheet.write( 7, 0, 'Data protection code [0..9/A..Z/space] :'); info_sheet.write( 7, 1, self.data['INFO']['PROT_COD'])
#         info_sheet.write( 8, 0, 'Burn-in time (in minutes) :');              info_sheet.write( 8, 1, self.data['INFO']['BURN_TIM'])
#         info_sheet.write( 9, 0, 'Command mode code :');                      info_sheet.write( 9, 1, self.data['INFO']['CMOD_COD'])
#         info_sheet.write(10, 0, 'Lot ID (customer specified) :');            info_sheet.write(10, 1, self.data['INFO']['LOT_ID'])
#         info_sheet.write(11, 0, 'Part Type (or product ID) :');              info_sheet.write(11, 1, self.data['INFO']['PART_TYP'])
#         info_sheet.write(12, 0, 'Name of node that generated data :');       info_sheet.write(12, 1, self.data['INFO']['NODE_NAM'])
#         info_sheet.write(13, 0, 'Tester type :');                            info_sheet.write(13, 1, self.data['INFO']['TSTR_TYP'])
#         info_sheet.write(14, 0, 'Job name (test program name) :');           info_sheet.write(14, 1, self.data['INFO']['JOB_NAM'])
#         info_sheet.write(15, 0, 'Job (test program) revision number :');     info_sheet.write(15, 1, self.data['INFO']['JOB_REV'])
#         info_sheet.write(16, 0, 'Sublot ID :');                              info_sheet.write(16, 1, self.data['INFO']['SBLOT_ID'])
#         info_sheet.write(17, 0, 'Operator name or ID (at setup time) :');    info_sheet.write(17, 1, self.data['INFO']['OPER_NAM'])
#         info_sheet.write(18, 0, 'Tester executive software type :');         info_sheet.write(18, 1, self.data['INFO']['EXEC_TYP'])
#         info_sheet.write(19, 0, 'Tester exec software version number :');    info_sheet.write(19, 1, self.data['INFO']['EXEC_VER'])
#         info_sheet.write(20, 0, 'Test phase or step code :');                info_sheet.write(20, 1, self.data['INFO']['TEST_COD'])
#         info_sheet.write(21, 0, 'Test temperature :');                       info_sheet.write(21, 1, self.data['INFO']['TST_TEMP'])
#         info_sheet.write(22, 0, 'Generic user text :');                      info_sheet.write(22, 1, self.data['INFO']['USER_TXT'])
#         info_sheet.write(23, 0, 'Name of auxiliary data file :');            info_sheet.write(23, 1, self.data['INFO']['AUX_FILE'])
#         info_sheet.write(24, 0, 'Package type :');                           info_sheet.write(24, 1, self.data['INFO']['PKG_TYP'])
#         info_sheet.write(25, 0, 'Product family ID :');                      info_sheet.write(25, 1, self.data['INFO']['FAMLY_ID'])
#         info_sheet.write(26, 0, 'Date code :');                              info_sheet.write(26, 1, self.data['INFO']['DATE_COD'])
#         info_sheet.write(27, 0, 'Test facility ID :');                       info_sheet.write(27, 1, self.data['INFO']['FACIL_ID'])
#         info_sheet.write(28, 0, 'Test floor ID :');                          info_sheet.write(28, 1, self.data['INFO']['FLOOR_ID'])
#         info_sheet.write(29, 0, 'Fabrication process ID :');                 info_sheet.write(29, 1, self.data['INFO']['PROC_ID'])
#         info_sheet.write(30, 0, 'Operation frequency or step :');            info_sheet.write(30, 1, self.data['INFO']['OPER_FRQ'])
#         info_sheet.write(31, 0, 'Test specification name :');                info_sheet.write(31, 1, self.data['INFO']['SPEC_NAM'])
#         info_sheet.write(32, 0, 'Test specification version number :');      info_sheet.write(32, 1, self.data['INFO']['SPEC_VER'])
#         info_sheet.write(33, 0, 'Test flow ID :');                           info_sheet.write(33, 1, self.data['INFO']['FLOW_ID'])
#         info_sheet.write(34, 0, 'Test setup ID :');                          info_sheet.write(34, 1, self.data['INFO']['SETUP_ID'])
#         info_sheet.write(35, 0, 'Device design revision :');                 info_sheet.write(35, 1, self.data['INFO']['DSGN_REV'])
#         info_sheet.write(36, 0, 'Engineering lot ID :');                     info_sheet.write(36, 1, self.data['INFO']['ENG_ID'])
#         info_sheet.write(37, 0, 'ROM code ID :');                            info_sheet.write(37, 1, self.data['INFO']['ROM_COD'])
#         info_sheet.write(38, 0, 'Tester serial number :');                   info_sheet.write(38, 1, self.data['INFO']['SERL_NUM'])
#         info_sheet.write(39, 0, 'Supervisor name or ID :');                  info_sheet.write(39, 1, self.data['INFO']['SUPR_NAM'])
#         info_sheet.write(40, 0, 'Handler ID :');                             info_sheet.write(40, 1, self.data['INFO']['HAND_ID'])
#         info_sheet.write(41, 0, 'Probe Card / DIB ID :');                    info_sheet.write(41, 1, self.data['INFO']['PRB_CARD'])
#         info_sheet.write(42, 0, 'Description from Tester exec :');           info_sheet.write(42, 1, self.data['INFO']['EXC_DESC'])
#         info_sheet.write(43, 0, 'Description from user :');                  info_sheet.write(43, 1, self.data['INFO']['USR_DESC'])
#         info_sheet.write(44, 0, 'Number of Test Heads :');                   info_sheet.write(44, 1, len(self.data['HEADS']));         info_sheet.write(44, 2, str(self.data['HEADS']))
#         info_sheet.write(45, 0, 'Number of Test Sites :');                   info_sheet.write(45, 1, len(self.data['SITES']));         info_sheet.write(45, 2, str(self.data['SITES']))
#         info_sheet.write(46, 0, 'Number of parts :');                        info_sheet.write(46, 1, self.data['INFO']['PART_CNT']);   info_sheet.write(46, 2, self.data['PARTS']);     info_sheet.write(46, 3, self.data['PASSES']+self.data['FAILS'])
#         info_sheet.write(47, 0, 'Number of good parts :');                   info_sheet.write(47, 1, self.data['INFO']['GOOD_CNT']);                                                    info_sheet.write(47, 3, self.data['PASSES'])
#         info_sheet.write(48, 0, 'Number of failed parts');                                                                                                                              info_sheet.write(48, 3, self.data['FAILS'])
#         info_sheet.write(49, 0, 'Yield :')
#         if self.data['PASSES']+self.data['FAILS']==0:
#             info_sheet.write(49, 1, 0.0, left_percent)
#         else:
#             info_sheet.write(49, 1, float(self.data['PASSES'])/(self.data['PASSES']+self.data['FAILS']), left_percent)
#         info_sheet.write(50, 0, 'Number of functional parts :');             info_sheet.write(50, 1, self.data['INFO']['FUNC_CNT'])
#         info_sheet.write(51, 0, 'Number of re-tested parts :');              info_sheet.write(51, 1, self.data['INFO']['RTST_CNT'])
#         info_sheet.write(52, 0, 'Number of aborted parts :');                info_sheet.write(52, 1, self.data['INFO']['ABRT_CNT'])
#         if self.is_from_probing():
#             info_sheet.write(53, 0, 'Probing :')
#             info_sheet.write(53, 1, self.count_wafers())
#             info_sheet.write(53, 2, str(self.enumerate_wafers()))
#         else:
#             info_sheet.write(53, 0, 'Final Test :')
#             info_sheet.write(53, 1, 'yes')
#         info_sheet.write(54, 0, 'Average cycle time :')
#         info_sheet.write_formula('B55', '{=(B3-B2)/(D47)}')
#         info_sheet.write(54, 2, 's/part')
#         info_sheet.write(55, 0, 'Average indexing time :')
#         info_sheet.write_formula('B56', '{=(B3-B2)/(D47/(B45*B46))}')
#         info_sheet.write(55, 2, 's/group')
#
#         info_sheet.set_column(0, 0, 34, bold_right) # Column A:A bold and aligned to the right
#         info_sheet.set_column(1, 1, 20, left) # Column B:B normal and aligned tot he left
#         info_sheet.set_column(2, 2, 50, left) # Column C:C normal and aligned to the left
#         info_sheet.set_column(3, 3, 50, left) # Column C:C normal and aligned to the left
#
#     # TEST descriptions
#         test_sheet = workbook.add_worksheet('TESTS')
#         test_sheet.write( 0,  0, 'TEST_NUM', bold)
#         test_sheet.write( 0,  1, 'TEST_NAM', bold)
#         test_sheet.write( 0,  2, 'TEST_TYP', bold)
#         test_sheet.write( 0,  3, 'SEQ_NAM', bold)
#         test_sheet.write( 0,  4, 'LTL', bold)
#         test_sheet.write( 0,  5, 'UTL', bold)
#         test_sheet.write( 0,  6, 'LSL', bold)
#         test_sheet.write( 0,  7, 'USL', bold)
#         test_sheet.write( 0,  8, 'UNITS', bold)
#         test_sheet.write( 0,  9, 'C_HLMFMT', bold)
#         test_sheet.write( 0, 10, 'C_LLMFMT', bold)
#         test_sheet.write( 0, 11, 'C_RESFMT', bold)
#         test_sheet.write( 0, 12, 'LLM_SCAL', bold)
#         test_sheet.write( 0, 13, 'RES_SCAL', bold)
#         test_sheet.write( 0, 14, 'HLM_SCAL', bold)
#         row = 1
#         for TEST_NUM in self.data['TEST']:
#             test_sheet.write(row,  0, TEST_NUM)
#             test_sheet.write(row,  1, self.data['TEST'][TEST_NUM]['TEST_NAM'])
#             test_sheet.write(row,  2, self.data['TEST'][TEST_NUM]['TEST_TYP'])
#             test_sheet.write(row,  3, self.data['TEST'][TEST_NUM]['SEQ_NAM'])
#             test_sheet.write(row,  4, self.data['TEST'][TEST_NUM]['LTL'])
#             test_sheet.write(row,  5, self.data['TEST'][TEST_NUM]['UTL'])
#             test_sheet.write(row,  6, self.data['TEST'][TEST_NUM]['LSL'])
#             test_sheet.write(row,  7, self.data['TEST'][TEST_NUM]['USL'])
#             test_sheet.write(row,  8, self.data['TEST'][TEST_NUM]['UNITS'])
#             test_sheet.write(row,  9, self.data['TEST'][TEST_NUM]['C_HLMFMT'])
#             test_sheet.write(row, 10, self.data['TEST'][TEST_NUM]['C_LLMFMT'])
#             test_sheet.write(row, 11, self.data['TEST'][TEST_NUM]['C_RESFMT'])
#             test_sheet.write(row, 12, self.data['TEST'][TEST_NUM]['LLM_SCAL'])
#             test_sheet.write(row, 13, self.data['TEST'][TEST_NUM]['RES_SCAL'])
#             test_sheet.write(row, 14, self.data['TEST'][TEST_NUM]['HLM_SCAL'])
#             row+=1
#
#     # SBIN sheet
#         sbin_sheet = workbook.add_worksheet('SOFT Bin')
#         sbin_sheet.write(0, 0, 'SBIN_NUM', bold)
#         sbin_sheet.write(0, 1, 'SBIN_NAM', bold)
#         sbin_sheet.write(0, 2, 'P/F', bold)
#         row = 1
#         for SBIN_NUM in self.data['BIN']['SOFT']:
#             sbin_sheet.write(row, 0, SBIN_NUM)
#             sbin_sheet.write(row, 1, self.data['BIN']['SOFT'][SBIN_NUM][0])
#             sbin_sheet.write(row, 2, self.data['BIN']['SOFT'][SBIN_NUM][1])
#             row+=1
#
#     # HBIN sheet
#         hbin_sheet = workbook.add_worksheet('HARD Bin')
#         hbin_sheet.write(0, 0, 'HBIN_NUM', bold)
#         hbin_sheet.write(0, 1, 'HBIN_NAM', bold)
#         hbin_sheet.write(0, 2, 'P/F', bold)
#         row = 1
#         for HBIN_NUM in self.data['BIN']['HARD']:
#             hbin_sheet.write(row, 0, HBIN_NUM)
#             hbin_sheet.write(row, 1, self.data['BIN']['HARD'][HBIN_NUM][0])
#             hbin_sheet.write(row, 2, self.data['BIN']['HARD'][HBIN_NUM][1])
#             row+=1
#
#     # RESULT sheet
#         result_sheet = workbook.add_worksheet('RESULT')
#         result_sheet.write(0, 0, 'LOT', bold)
#         result_sheet.write(0, 1, 'WAF', bold)
#         result_sheet.write(0, 2, 'X', bold)
#         result_sheet.write(0, 3, 'Y', bold)
#         result_sheet.write(0, 4, 'HEAD', bold)
#         result_sheet.write(0, 5, 'SITE', bold)
#         result_sheet.write(0, 6, 'HBIN', bold)
#         result_sheet.write(0, 7, 'SBIN', bold)
#         result_sheet.write(0, 8, 'PART', bold)
#         result_sheet.write(0, 9, 'PF', bold)
#         for entry in self.data['META']:
#             (LOT, WAFER, X_COORD, Y_COORD, HEAD, SITE, HBIN, SBIN, PART, PF) = self.data['META'][entry]
#             result_sheet.write(entry+1, 0, LOT)
#             result_sheet.write(entry+1, 1, WAFER)
#             result_sheet.write(entry+1, 2, X_COORD)
#             result_sheet.write(entry+1, 3, Y_COORD)
#             result_sheet.write(entry+1, 4, HEAD)
#             result_sheet.write(entry+1, 5, SITE)
#             result_sheet.write(entry+1, 6, HBIN)
#             result_sheet.write(entry+1, 7, SBIN)
#             result_sheet.write(entry+1, 8, PART)
#             if PF == 'P':
#                 result_sheet.write(entry+1, 9, 'P')
#             else:
#                 result_sheet.write(entry+1, 9, 'F', failed)
#         column = 10
#         for TEST_NUM in list(self.data['PF'].keys()):
#             if TEST_NUM in self.data['RESULT']: # Parametric test result
#                 crange = '%s1:%s1'%(xlsxwriter.utility.xl_col_to_name(column), xlsxwriter.utility.xl_col_to_name(column+1))
#                 result_sheet.set_column(column, column, 8, right)
#                 result_sheet.set_column(column+1, column+1, 2, left)
#                 result_sheet.merge_range(crange, self.data['TEST'][TEST_NUM]['TEST_NAM'], bold)
#                 for entry in range(len(self.data['PF'][TEST_NUM])):
#                     if entry in self.data['RESULT'][TEST_NUM]:
#                         if np.isfinite(self.data['RESULT'][TEST_NUM][entry]):
#                             result_sheet.write(entry+1, column, self.data['RESULT'][TEST_NUM][entry])
#                     if self.data['PF'][TEST_NUM][entry]:
#                         result_sheet.write(entry+1, column+1, 'P')
#                     else:
#                         result_sheet.write(entry+1, column+1, 'F')
#                 column+=2
#             else: # functional test result
#                 result_sheet.write(0, column, self.data['TEST'][TEST_NUM]['TEST_NAM'], bold)
#                 for entry in range(len(self.data['PF'][TEST_NUM])):
#                     if self.data['PF'][TEST_NUM][entry]:
#                         result_sheet.write(entry+1, column, 'P')
#                     else:
#                         result_sheet.write(entry+1, column, 'F')
#                 column+=1
#
#         result_sheet.freeze_panes(1, 10)
#
#
#     # Test-Fail-Pareto sheet
#         pareto_sheet = workbook.add_worksheet('Test Pareto')
#
#     # Data sheet
#
#     # PF sheet
#
#     # Min sheet
#
#     # Max sheet
#
#
#     # ATR's
#         ATR_sheet = workbook.add_worksheet("ATR's")
#         ATR_sheet.write(0, 0, 'MOD_TIM', bold)
#         ATR_sheet.write(0, 1, 'CMD_LINE', bold)
#         row = 1
#         for MOD_TIM in self.data['ATRs']:
#             ATR_sheet.write(row, 0, MOD_TIM)
#             ATR_sheet.write(row, 1, self.data['ATRs'][MOD_TIM])
#             row+=1
#
#     # DTR's
#         DTR_sheet = workbook.add_worksheet("DTR's")
#         DTR_sheet.write(0, 0, 'PART', bold)
#         DTR_sheet.write(0, 1, 'RECORD', bold)
#         DTR_sheet.write(0, 2, 'TEXT_DAT', bold)
#         row = 1
#         for PART, RECORD in self.data['DTRs']:
#             DTR_sheet.write(row, 0, PART)
#             DTR_sheet.write(row, 1, RECORD)
#             DTR_sheet.write(row, 3, self.data['DTRs'][(PART, RECORD)])
#             row+=1
#
#         workbook.close()
#
#         #pbar.finish()
#
#     def to_pdf(self):
#         pass
#
#     def to_pptx(self):
#         pass
#
#     def to_deav(self, DEAV_repository):
#         pass
#
#     def rename(self, NewFileName=None, preserve=False, overwrite='auto'):
#         '''
#         This method will rename self.file_name to NewName.
#         If NewName is None, the name will be that of the MD5 hash of the file propper (it needs to fit in 39 characters!!!)
#         If NewName contains a path, that will be used (=move & rename) and the object will be re-initialized,
#         if not, self.path will be pre-pended (=rename) and the re-initialization of the object will depend on 'preserve'
#         If the extension(s) of NewFileName are not the same as self.file_name, nothing will be done (return value is False)
#         If preserve is False a rename will be performed and the object will be re-initialized
#         If preserve is True, the original file will be preserved (= copy action) and the object will *NOT* be re-initialized
#         If overwrite is True, a pre-existing NewFileName will be overwritten.
#         If overwrite is True, and a pre-existing NewFileName will not be overwritten(return value is False)
#         If overwrite is 'auto', over writing will be done only if a pre-existing NewFileName is OLDER than self.file_name.
#         The original modification time will always be preserved!
#         On success, True will be returned, False otherwhise
#         '''
#         if NewFileName==None:
#             NewFileName = os.path.join(self.path, "MD5_%s.%s" % (self.md5(), '.'.join(self.name.split('.')[1:])))
#         NewFileName = os.path.abspath(NewFileName)
#         if NewFileName == self.file_name:
#             return False
#         if os.path.exists(NewFileName):
#             if not isinstance(overwrite, bool):
#                 if os.path.getmtime(NewFileName) >= self.modification_time:
#                     overwrite = False
#                 else:
#                     overwrite = True
#             if overwrite == True:
#                 os.unlink(NewFileName)
#         _, NewName = os.path.split(NewFileName)
#         NewExts = '.%s' % '.'.join(NewName.split('.')[1:])
#         OriginalExts = '.%s' % '.'.join(self.name.split('.')[1:])
#         if NewExts == OriginalExts:
#             shutil.copy2(self.file_name, NewFileName)
#             os.utime(NewFileName, (time.time(), self.modification_time)) # just to be sure
#             if not preserve:
#                 os.unlink(self.file_name)
#                 self.__call__(NewFileName)
#             retval = True
#         else:
#             retval = False
#             #TODO: Implement implicit compression/decompression
#         return retval
#
#     def compress(self, preserve=False, overwrite='auto'):
#         '''
#         This method will compress self.file_name if it is not already compressed, in which case nothing is done.
#         If preserve is False (default), the original file will be removed and the object will be re-initialized with the compressed file.
#         If preserve is True, the original file *NOT* be removed and the object will *NOT* be re-initialized.
#         If overwrite is True (default) if the target file already exists, it is overwritten.
#         If overwrite is False, nothing will be done if the target file already exists.
#         If overwrite is 'auto', over writing will be done only if a pre-existing NewFileName is OLDER than self.file_name.
#         The original modification time will always be preserved!
#         On success, True will be returned, False otherwhise
#         '''
#         if not self.is_compressed:
#             NewName = self.name+'.gz'
#             NewFileName = os.path.join(self.path, NewName)
#             if os.path.exists(NewFileName):
#                 if not isinstance(overwrite, bool):
#                     if os.path.getmtime(NewFileName) >= self.modification_time:
#                         overwrite = False
#                     else:
#                         overwrite = True
#                 if overwrite == True:
#                     os.unlink(NewFileName)
#             with open(self.file_name, 'rb') as f_in, gzip.open(NewFileName, 'wb') as f_out:
#                 copyfileobj(f_in, f_out)
#             os.utime(NewFileName, (time.time(), self.modification_time)) # preserver original modification time!
#             if not preserve:
#                 os.unlink(os.path.join(self.path, self.name))
#                 self.__call__(os.path.join(self.path, NewName))
#             return True
#         return False
#
#     def decompress(self, preserve=False, overwrite='auto'):
#         '''
#         This method will de-compress self.file_name if it is compressed. If self.file_name is not compressed, nothing is done.
#         If preserve is False, the original file will be removed and the object will be re-initialized with the de-compressed file.
#         If preserve is True, the original file will *NOT* be removed and the object will *NOT* be re-initialized.
#         If overwrite is True (default) if the target file already exists, it is overwritten.
#         If overwrite is False, nothing will be done if the target file already exists.
#         If overwrite is 'auto', over writing will be done only if a pre-existing NewFileName is OLDER than self.file_name.
#         The original modification time will always be preserved!
#         On success, True will be returned, False otherwhise
#         '''
#         if self.is_compressed:
#             NewName = self.name[:-3]
#             NewFileName = os.path.join(self.path, NewName)
#             if os.path.exists(NewFileName):
#                 if not isinstance(overwrite, bool):
#                     if os.path.getmtime(NewFileName) >= self.modification_time:
#                         overwrite = False
#                     else:
#                         overwrite = True
#                 if overwrite == True:
#                     os.unlink(NewFileName)
#             with open(NewFileName, 'wb') as f_out, gzip.open(self.file_name, 'rb') as f_in:
#                 copyfileobj(f_in, f_out)
#             os.utime(NewFileName, (time.time(), self.modification_time)) # preserve original modification time!
#             if not preserve:
#                 os.unlink(os.path.join(self.path, self.name))
#                 self.__call__(os.path.join(self.path, NewName))
#             return True
#         return False
#
# #    def _version_and_endian(self):
# #        return _ver, _end
#
#     def ends_on_record_boundary(self):
#         '''
#         This function will return True if FileName ends on a record boundary, False if it doesn't.
#
#         This function will not use the 'records_from_file' iterator as that one just ignores the last
#         record if it is a corrupt one!
#
#         It presumes that FileName exists, because if it doesn't exist the return value is also False!
#         '''
#         if guess_type(self.file_name)[1]=='gzip':
#             with open(self.file_name, 'rb') as fd:
#                 fd.seek(-4, 2) # last 4 bytes give the unpacked size of the file
#                 fe = struct.unpack('I', fd.read(4))[0]
#             with gzip.open(self.file_name, 'rb') as fd:
#                 while fd.tell() != fe:
#                     header = fd.read(4)
#                     if len(header)!=4:
#                         return False # Header too short
#                     else:
#                         REC_LEN, _REC_TYP, _REC_SUB = struct.unpack('HBB', header)
#                         _footer = fd.read(REC_LEN)
#                         if len(_footer)!=REC_LEN:
#                             return False # Footer too short
#         else:
#             with open(self.file_name, 'rb') as fd:
#                 fe = os.fstat(fd.fileno()).st_size
#                 while fd.tell() != fe:
#                     header = fd.read(4)
#                     if len(header)!=4:
#                         return False # Header too short
#                     else:
#                         REC_LEN, _REC_TYP, _REC_SUB = struct.unpack('HBB', header)
#                         _footer = fd.read(REC_LEN)
#                         if len(_footer)!=REC_LEN:
#                             return False # Footer too short
#         return True # End on record boundary
#
#     def extensions(self):
#         '''
#         This method returns a list of the used extensions to the STDF version
#         '''
#         #TODO: Implement
#         pass
#
#     def count_records(self, records_of_interest=None):
#         '''
#         This method will return the number of records found in the STDF file.
#         If of_interest==None, all records are considered, if not, only the
#         records in of_interest are considered.
#         '''
#         # set the records_of_interest right
#         all_records = list(id_to_ts(self.version).keys())
#         if records_of_interest==None:
#             roi = all_records
#         elif isinstance(records_of_interest, list):
#             roi = []
#             for item in records_of_interest:
#                 if item in all_records:
#                     roi.append(item)
#         else:
#             raise STDFError("count_records(records_of_interest=%s) : Unsupported 'records_of_interest' type" % records_of_interest)
#         # make sure the records in the file are indexed
#         if not self.records_are_indexed:
#             self.build_record_index()
#         # count the records of interest
#         retval = 0
#         for REC_ID in self.record_index:
#             if REC_ID in roi:
#                 retval+=len(self.record_index[REC_ID])
#         return retval
#
#     def count_tests(self):
#         '''
#         This method will find the number of unique tests in self.file_name
#         '''
#         TestCount = 0
#         MaxTestCount = 0
#         for _REC_LEN, REC_TYP, REC_SUB, _REC in records_from_file(self.file_name):
#             if REC_TYP==5:
#                 if REC_SUB==10: # PIR = start
#                     TestCount = 0
#                 elif REC_SUB==20: # PRR = stop
#                     if TestCount > MaxTestCount:
#                         MaxTestCount = TestCount
#             if REC_TYP==15: # PTR, FTR, MPR, STR or MTR
#                 TestCount+=1
#         return MaxTestCount
#
#     def count_parts(self):
#         '''
#         This method will return the number of parts in self.file_name
#         '''
#         if self.data['PARTS']==None:
#             self.data['PARTS'] = self.count_records(['PRR']) # PRR marks a tested part
#         return self.data['PARTS']
#
#     def count_wafers(self, recount=False):
#         '''
#         This function will determine how many wafers are located in self.file_name.
#         '''
#         if not self.is_snarfed or recount:
#             self.data['WAFERS'] = {}
#             for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['WIR', 'WRR']):
#                 if OBJ.id == 'WIR':
#                     HW = (OBJ.get_value('HEAD_NUM'), OBJ.get_value('WAFER_ID'))
#                     if HW not in self.data['WAFERS']:
#                         self.data['WAFERS'][HW] = {}
#                         self.data['WAFERS'][HW]['START_T'] = [OBJ.get_value('START_T')]
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'] = [OBJ.get_value('SITE_GRP')]
#                         else: self.data['WAFERS'][HW]['SITE_GRP'] = [255]
#                     else:
#                         self.data['WAFERS'][HW]['START_T'].append(OBJ.get_value('START_T'))
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'].append(OBJ.get_value('SITE_GRP'))
#                         else: self.data['WAFERS'][HW]['SITE_GRP'].append(255)
#                 elif OBJ.id == 'WRR': # Wafer Result Record
#                     HW = (OBJ.get_value('HEAD_NUM'), OBJ.get_value('WAFER_ID'))
#                     if HW not in self.data['WAFERS']: # Re-create the corresponding WIR
#                         self.data['WAFERS'][HW] = {}
#                         self.data['WAFERS'][HW]['START_T'] = [OBJ.get_value('FINISH_T')]
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'] = [OBJ.get_value('SITE_GRP')]
#                         else: self.data['WAFERS'][HW]['SITE_GRP'] = [255]
#                     else:
#                         self.data['WAFERS'][HW]['FINISH_T'] = OBJ.get_value('FINISH_T')
#                         self.data['WAFERS'][HW]['USR_DESC'] = OBJ.get_value('USR_DESC')
#                         self.data['WAFERS'][HW]['EXC_DESC'] = OBJ.get_value('EXC_DESC')
#                         if self.version=='V4': self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('FABWF_ID')
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['FRAME_ID'] = OBJ.get_value('FRAME_ID')
#                         else: self.data['WAFERS'][HW]['FRAME_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('FABWF_ID')
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['MASK_ID'] = OBJ.get_value('MASK_ID')
#                         else: self.data['WAFERS'][HW]['MASK_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['HAND_ID'] = ''
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('HAND_ID')
#                         if self.version=='V4': self.data['WAFERS'][HW]['PRB_CARD'] = ''
#                         else: self.data['WAFERS'][HW]['PRB_CARD'] = OBJ.get_value('PRB_CARD')
#         return len(self.data['WAFERS'])
#
#     def count_test_heads(self, hold_on=-1, renew=False):
#         '''
#         '''
#         return self.count_test_heads_and_sites(hold_on, renew)[0]
#
#     def count_test_sites(self, hold_on=-1, renew=False):
#         '''
#         '''
#         return self.count_test_heads_and_sites(hold_on, renew)[1]
#
#     def count_test_heads_and_sites(self, hold_on=-1, renew=False):
#         '''
#
#         '''
#         _hold_on = hold_on
#         if (len(self.data['HEADS'])==0 or len(self.data['SITES'])==0) or renew:
#             if renew:
#                 self.data['HEADS'] = []
#                 self.data['SITES'] = []
#             if self.version=='V4':
#                 for _, _, _, REC in records_from_file(self.file_name, unpack=True, of_interest=['SDR', 'PMR', 'PTR', 'FTR']):
#                     if REC.id in ['SDR', 'PMR']:
#                         if REC.get_value('HEAD_NUM') not in self.data['HEADS']:
#                             self.data['HEADS'].append(REC.get_value('HEAD_NUM'))
#                         if REC.get_value('SITE_NUM') not in self.data['SITES']:
#                             self.data['SITES'].append(REC.get_value('SITE_NUM'))
#                     elif REC.id == 'PTR':
#                         if REC.get_value('HEAD_NUM') not in self.data['HEADS']:
#                             self.data['HEADS'].append(REC.get_value('HEAD_NUM'))
#                             _hold_on = hold_on
#                         if REC.get_value('SITE_NUM') not in self.data['SITES']:
#                             self.data['SITES'].append(REC.get_value('SITE_NUM'))
#                             _hold_on = hold_on
#                         _hold_on-=1
#                         if _hold_on==0: break
#                     elif REC.id == 'FTR':
#                         if REC.get_value('HEAD_NUM') not in self.data['HEADS']:
#                             self.data['HEADS'].append(REC.get_value('HEAD_NUM'))
#                             _hold_on = hold_on
#                         if REC.get_value('SITE_NUM') not in self.data['SITES']:
#                             self.data['SITES'].append(REC.get_value('SITE_NUM'))
#                             _hold_on = hold_on
#                         _hold_on-=1
#                         if _hold_on==0: break
#             else:
#                 # I know that STDF V3 knows PMR's, but I don't know the fields in V3 PMR's ...
#                 if self.look_for_records(of_interest=['PTR']): # use PTR's
#                     for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PTR']):
#                         if OBJ.get_value('HEAD_NUM') not in self.data['HEADS']:
#                             self.data['HEADS'].append(OBJ.get_value('HEAD_NUM'))
#                             _hold_on = hold_on
#                         if OBJ.get_value('SITE_NUM') not in self.data['SITES']:
#                             self.data['SITES'].append(OBJ.get_value('SITE_NUM'))
#                             _hold_on = hold_on
#                         _hold_on-=1
#                         if _hold_on==0: break
#                 elif self.look_for_records(of_interest=['FTR']): # use FTR's
#                     for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['FTR']):
#                         if OBJ.get_value('HEAD_NUM') not in self.data['HEADS']:
#                             self.data['HEADS'].append(OBJ.get_value('HEAD_NUM'))
#                             _hold_on = hold_on
#                         if OBJ.get_value('SITE_NUM') not in self.data['SITES']:
#                             self.data['SITES'].append(OBJ.get_value('SITE_NUM'))
#                             _hold_on = hold_on
#                         _hold_on-=1
#                         if _hold_on==0: break
#         return (len(self.data['HEADS']), len(self.data['SITES']))
#
#     def enumerate(self):
#         '''
#         This method will build_uis a map of the self.file_name so that many other methods
#         can work much faster.
#         '''
#         pass
#
#
#     def enumerate_records(self, records_of_interest=None):
#         '''
#         This method will return a dictionary ID -> #, wher ID is the record
#         ID of the found records, and # is the count of that record in the file.
#         If of_interest is None, all records of the version are considered.
#         If of_interest is a list, only the elements in the list are considered.
#         '''
#         retval = {}
# #         ALL
#
#
#         valid_STDF_records = ts_to_id(self.version)
#         if records_of_interest==None:
#             of_interest = valid_STDF_records
#         elif isinstance(of_interest, list):
#             ID2TS = id_to_ts(self.version)
#             tmp_list = []
#             for item in of_interest:
#                 if isinstance(item, str):
#                     if item in ID2TS:
#                         if ID2TS[item] not in tmp_list:
#                             tmp_list.append(ID2TS[item])
#                 elif isinstance(item, tuple) and len(item)==2:
#                     if item in valid_STDF_records:
#                         if item not in tmp_list:
#                             tmp_list.append(item)
#             of_interest = tmp_list
#         else:
#             raise STDFError("enumerate_records(of_interest=%s) : Unsupported 'of_interest'" % of_interest)
#
#         for _REC_LEN, REC_TYP, REC_SUB, _REC in records_from_file(self.file_name):
#             if (REC_TYP, REC_SUB) in of_interest:
#                 if valid_STDF_records[(REC_TYP, REC_SUB)] not in retval:
#                     retval[valid_STDF_records[(REC_TYP, REC_SUB)]] = 1
#                 else:
#                     retval[valid_STDF_records[(REC_TYP, REC_SUB)]] +=1
#         return retval
#
#     def enumerate_used_soft_bins(self):
#         '''
#         This method will return a dictionary with the soft bin categories used, and the count for each. (PRR based)
#         '''
#         retval = {}
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PRR']):
#             SOFT_BIN = OBJ.get_value('SOFT_BIN')
#             if SOFT_BIN in retval:
#                 retval[SOFT_BIN] += 1
#             else:
#                 retval[SOFT_BIN] = 1
#         return retval
#
#     def enumerate_soft_bins(self):
#         '''
#         This method will return a dictionary of possible soft bin categories, their summary count and their name (SBR based)
#         '''
#         retval = {}
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['SBR']):
#             if OBJ.get_value('SBIN_NUM') not in retval:
#                 if self.version=='V4':
#                     retval[OBJ.get_value('SBIN_NUM')] = (OBJ.get_value('SBIN_NAM'), OBJ.get_value('SBIN_CNT'), OBJ.get_value('SBIN_PF'))
#                 else:
#                     retval[OBJ.get_value('SBIN_NUM')] = (OBJ.get_value('SBIN_NAM'), OBJ.get_value('SBIN_CNT'), ' ')
#             else:
#                 (NAM, CNT, PF) = retval[OBJ.get_value('SBIN_NUM')]
#                 CNT+=OBJ.get_value('SBIN_CNT')
#                 retval[OBJ.get_value('SBIN_NUM')] = (NAM, CNT, PF)
#         return retval
#
#     def enumerate_used_hard_bins(self):
#         '''
#         This method will return a dictionary with the hard bin categories used, and the count for each. (PRR based)
#         '''
#         retval = {}
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PRR']):
#             HARD_BIN = OBJ.get_value('HARD_BIN')
#             if HARD_BIN in retval:
#                 retval[HARD_BIN] += 1
#             else:
#                 retval[HARD_BIN] = 1
#         return retval
#
#     def enumerate_hard_bins(self):
#         '''
#         This method will return a dictionary of possible soft bin categories, their summary count and their name (HBR based)
#         '''
#         retval = {}
#         for _, _, _, OBJ in records_from_file(self.file_name, True, ['HBR']):
#             if OBJ.get_value('HBIN_NUM') not in retval:
#                 if self.version=='V4':
#                     retval[OBJ.get_value('HBIN_NUM')] = (OBJ.get_value('HBIN_NAM'), OBJ.get_value('HBIN_CNT'), OBJ.get_value('HBIN_PF'))
#                 else:
#                     retval[OBJ.get_value('HBIN_NUM')] = (OBJ.get_value('HBIN_NAM'), OBJ.get_value('HBIN_CNT'), ' ')
#             else:
#                 (NAM, CNT, PF) = retval[OBJ.get_value('HBIN_NUM')]
#                 CNT+=OBJ.get_value('HBIN_CNT')
#                 retval[OBJ.get_value('HBIN_NUM')] = (NAM, CNT, PF)
#         return retval
#
#     def enumerate_used_tests(self, with_progress=False):
#         '''
#         This method will return a list of all test names used in self.file_name (PTR, FTR, MPR, STR & MTR based)
#         '''
#         retval = []
#         if with_progress:
#             number_of_parts = self.count_parts()
#             number_of_tests = self.count_tests()
#             current_item = 0
#             pbar = pb.ProgressBar(maxval=number_of_parts * number_of_tests, widgets=[pb.SimpleProgress() , ' =', pb.Percentage(), ' ', pb.Bar(), ' ',pb.Timer(), ' ', pb.ETA()]).start()
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PTR', 'FTR', 'MPR', 'STR', 'MTR']):
#             if self.version=='V4':
#                 if OBJ.get_value('TEST_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             elif self.version=='V3':
#                 if OBJ.get_value('TEST_NAM')!='': TEST_NAM = OBJ.get_value('TEST_NAM')
#                 elif OBJ.get_value('TEXT_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             else:
#                 STDFError("test_names : Unsupported version %s" % self.version)
#             if TEST_NAM not in retval:
#                 retval.append(TEST_NAM)
#             if with_progress:
#                 current_item += 1
#                 pbar.update(current_item)
#         if with_progress:
#             pbar.finish()
#         return retval
#
#     def enumerate_tests(self):
#         pass # TSR based
#
#
#     def enumerate_test_counts(self, with_progress=False):
#         '''
#         This method will return a dictionary with the test names (and numbers), and the count for each.
#         '''
#         retval = {'PTR' : {}, 'FTR' : {}, 'MTR' : {}, 'STR' : {}, 'MPR' : {}}
#         if with_progress:
#             number_of_parts = self.count_parts()
#             number_of_tests = self.count_tests()
#             current_item = 0
#             pbar = pb.ProgressBar(maxval=number_of_parts * number_of_tests, widgets=[pb.SimpleProgress() , ' =', pb.Percentage(), ' ', pb.Bar(), ' ',pb.Timer(), ' ', pb.ETA()]).start()
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=list(retval.keys())):
#             if self.version=='V4':
#                 if OBJ.get_value('TEST_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             elif self.version=='V3':
#                 if OBJ.get_value('TEST_NAM')!='': TEST_NAM = OBJ.get_value('TEST_NAM')
#                 elif OBJ.get_value('TEXT_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             else:
#                 STDFError("test_names : Unsupported version %s" % self.version)
#             if TEST_NAM in retval[OBJ.id]:
#                 retval[OBJ.id][TEST_NAM] += 1
#             else:
#                 retval[OBJ.id][TEST_NAM] = 1
#             if with_progress:
#                 current_item += 1
#                 pbar.update(current_item)
#         if with_progress:
#             pbar.finish()
#         return retval
#
#     def enumerate_test_fails(self, with_progress=False):
#         '''
#         This method will return a fail count per test (as opposed to soft/hard bin categories)
#         '''
#         #TODO: split up in test types
#         retval = {}
#         if with_progress:
#             number_of_parts = self.count_parts()
#             number_of_tests = self.count_tests()
#             current_item = 0
#             pbar = pb.ProgressBar(maxval=number_of_parts * number_of_tests, widgets=[pb.SimpleProgress() , ' =', pb.Percentage(), ' ', pb.Bar(), ' ', pb.Timer(), ' ', pb.ETA()]).start()
#
#         for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PTR', 'FTR', 'MTR', 'STR']):
#             if self.version=='V4':
#                 if OBJ.get_value('TEST_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             elif self.version=='V3':
#                 if OBJ.get_value('TEST_NAM')!='': TEST_NAM = OBJ.get_value('TEST_NAM')
#                 elif OBJ.get_value('TEXT_TXT')!='': TEST_NAM = OBJ.get_value('TEST_TXT')
#                 else: TEST_NAM = "%d" % OBJ.get_value('TEST_NUM')
#             else:
#                 STDFError("test_names : Unsupported version %s" % self.version)
#             TEST_FLG = OBJ.get_value('TEST_FLG')
#             if (TEST_FLG[6]=='1') or (TEST_FLG[6]=='0' and TEST_FLG[7]=='1'): # fail or no result
#                 if TEST_NAM in retval:
#                     retval[TEST_NAM] += 1
#                 else:
#                     retval[TEST_NAM] = 1
#             if with_progress:
#                 current_item += 1
#                 pbar.update(current_item)
#         if with_progress:
#             pbar.finish()
#         return retval
#
#     def enumerate_wafers(self, recount=False):
#         '''
#         This method will return a list of wafer numbers in this STDF file.
#         '''
#         if not self.is_snarfed or recount:
#             self.data['WAFERS'] = {}
#             for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['WIR', 'WRR']):
#                 if OBJ.id == 'WIR':
#                     HW = (OBJ.get_value('HEAD_NUM'), OBJ.get_value('WAFER_ID'))
#                     if HW not in self.data['WAFERS']:
#                         self.data['WAFERS'][HW] = {}
#                         self.data['WAFERS'][HW]['START_T'] = [OBJ.get_value('START_T')]
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'] = [OBJ.get_value('SITE_GRP')]
#                         else: self.data['WAFERS'][HW]['SITE_GRP'] = [255]
#                     else:
#                         self.data['WAFERS'][HW]['START_T'].append(OBJ.get_value('START_T'))
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'].append(OBJ.get_value('SITE_GRP'))
#                         else: self.data['WAFERS'][HW]['SITE_GRP'].append(255)
#                 elif OBJ.id == 'WRR': # Wafer Result Record
#                     HW = (OBJ.get_value('HEAD_NUM'), OBJ.get_value('WAFER_ID'))
#                     if HW not in self.data['WAFERS']: # Re-create the corresponding WIR
#                         self.data['WAFERS'][HW] = {}
#                         self.data['WAFERS'][HW]['START_T'] = [OBJ.get_value('FINISH_T')]
#                         if self.version=='V4': self.data['WAFERS'][HW]['SITE_GRP'] = [OBJ.get_value('SITE_GRP')]
#                         else: self.data['WAFERS'][HW]['SITE_GRP'] = [255]
#                     else:
#                         self.data['WAFERS'][HW]['FINISH_T'] = OBJ.get_value('FINISH_T')
#                         self.data['WAFERS'][HW]['USR_DESC'] = OBJ.get_value('USR_DESC')
#                         self.data['WAFERS'][HW]['EXC_DESC'] = OBJ.get_value('EXC_DESC')
#                         if self.version=='V4': self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('FABWF_ID')
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['FRAME_ID'] = OBJ.get_value('FRAME_ID')
#                         else: self.data['WAFERS'][HW]['FRAME_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('FABWF_ID')
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['MASK_ID'] = OBJ.get_value('MASK_ID')
#                         else: self.data['WAFERS'][HW]['MASK_ID'] = ''
#                         if self.version=='V4': self.data['WAFERS'][HW]['HAND_ID'] = ''
#                         else: self.data['WAFERS'][HW]['FABWF_ID'] = OBJ.get_value('HAND_ID')
#                         if self.version=='V4': self.data['WAFERS'][HW]['PRB_CARD'] = ''
#                         else: self.data['WAFERS'][HW]['PRB_CARD'] = OBJ.get_value('PRB_CARD')
#         retval = []
#         for HEAD_NUM, WAFER_ID in self.data['WAFERS']:
#             retval.append(WAFER_ID)
#         return retval
#
#     def is_from_probing(self):
#         '''
#         This method will determine if the FileName holds probing info or not
#         based on the presence of the WCR/WIR/WRR record(s).
#         '''
#         if not self.is_indexed:
#             self.build_index()
#         records_found = list(self.index.keys())
#         if 'WIR' in records_found or 'WCR' in records_found or 'WRR' in records_found:
#             return True
#         return False
#
#     def is_from_finaltest(self):
#         '''
#         This method will determine if the FileName is from final test or not
#         '''
#         return not self.is_from_probing()
#
#     def is_conform_the_standard(self):
#         '''
#         This function will determine if a given FileName is valid according to the standard.
#             - file name convention with respect to the version
#             - obligatory records
#             - record order
#
#         It presumes the FileName exists.
#
#         if the file is a compressed one, it is decompressed, there should be only ONE file inside, and it should be an STDF file according to the above rules.
#         '''
#         pass #TODO: Implement
#
#     def used_extenstions(self):
#         '''
#         This method will return a list of used extensions in the STDF file.
#         '''
#         pass #TODO: Implement
#
#     def obligatory_records(self):
#         '''
#         This method will return a list of obligatory records (according to the spec) for the given version (and extensions)
#         '''
# #         retval = {}
# #         if self.version in supported.versions():
# #             exts = ['']
# #             if type(Extensions) == list:
# #                 for item in Extensions:
# #                     if item in supported.extensions(Version):
# #                         if item not in exts:
# #                             exts.append(item)
# #             elif Extensions != None:
# #                 raise STDFError("'Extensions' error")
# #
# #             for (REC_TYP, REC_SUB) in RecordDefinitions:
# #                 if Version in RecordDefinitions[(REC_TYP, REC_SUB)]:
# #                     for ext, obligatory_flag in RecordDefinitions[(REC_TYP, REC_SUB)][Version][2]:
# #                         if ext in exts and obligatory_flag==True:
# #                             retval[(REC_TYP, REC_SUB)] = RecordDefinitions[(REC_TYP, REC_SUB)][Version][0]
# #         return retval
#         pass #TODO: Implement
#
#     def holds_obligatory_records(self):
#         pass #TODO: Implement
#
#     def is_valid_name_for_versions(self):
#         '''
#         This method will return a list of STDF versions that self.name is valid for.
#         '''
#         retval = []
#         for Version in supported().versions():
#             RE = re.compile(FileNameDefinitions[Version])
#             if RE.match(self.name)!=None:
#                 retval.append(Version)
#         return retval
#
#     def get_part_pass_count(self, recount=False):
#         '''
#         This method will report the number of passed parts in self.file_name
#         (based on PRR:PART_FLG:bits 3&4)
#         '''
#         return self.get_part_pass_and_fail_counts(recount=recount)[0]
#
#     def get_part_fail_count(self, recount=False):
#         '''
#         This method will report the number of failed parts in self.file_name
#         (based on PRR:PART_FLG:bits 3&4)
#         '''
#         return self.get_part_pass_and_fail_counts(recount=recount)[1]
#
#     def get_part_pass_and_fail_counts(self, recount=False):
#         '''
#         This method will report the number of passes and fails in self.file_name
#         (based on PRR:PART_FLG:bits 3&4)
#         '''
#         if recount or (self.data['PASSES']+self.data['FAILS']==0):
#             self.data['PASSES'] = 0
#             self.data['FAILS'] = 0
#             for _, _, _, OBJ in records_from_file(self.file_name, unpack=True, of_interest=['PRR']):
#                 if OBJ.get_value('PART_FLG')[4] == '0': self.data['PASSES']+=1
#                 else: self.data['FAILS']+=1
#         return self.data['PASSES'], self.data['FAILS']
#
#     def get_yield(self):
#         '''
#         This method will return the yield for self.file_name [0.0..1.0]
#         '''
#         passes, fails = self.get_part_pass_and_fail_counts()
#         total = passes + fails
#         if total==0:
#             return 0.0
#         else:
#             return float(passes)/total
#
#     def get_info(self):
#         '''
#         This method will return a dictionary with the information from the MIR
#         '''
#         def decode_if_needed(buff):
#             if isinstance(buff, str):
#                 return buff
#             else:
#                 return "%s" % buff
#
#         retval = {
#             'Customer'    : '', # FAMLY_ID
#             'Product'     : '', # PART_TYP
#             'Lot'         : '', # LOT_ID
#             'DateCode'    : '', # derived from START_T (or SETUP_T if START_T not available) in format YYWWD
#             'Tester'      : '', # NODE_NAM:STAT_NUM
#             'TestProgram' : '', # JOB_NAM:JOB_REV
#             'TestSpec'    : ''  # SPEC_NAM:SPEC_VER
#         }
#
#         for _REC_LEN, REC_TYP, REC_SUB, REC in records_from_file(self.file_name):
#             if (REC_TYP == 1) and (REC_SUB == 10):
#                 if self.version == 'V4':
#                     obj = create_record_object('V4', self.endian, 'MIR', REC)
#                     # Customer
#                     retval['Customer'] = decode_if_needed(obj.get_value('FAMLY_ID'))
#                     # Product
#                     retval['Product'] = decode_if_needed(obj.get_value('PART_TYP'))
#                     # Lot (Do *NOT add Sublot !!!)
#                     retval['Lot'] = decode_if_needed(obj.get_value('LOT_ID'))
#                     # DateCode
#                     _setup_time = decode_if_needed(obj.get_value('SETUP_T'))
#                     _start_time = decode_if_needed(obj.get_value('START_T'))
#                     if _setup_time != 0:
#                         retval['DateCode'] = DT(_setup_time).datecode
#                     elif _start_time != 0:
#                         retval['DateCode'] = DT(_start_time).datecode
#                     else:
#                         retval['DateCode'] = decode_if_needed(obj.get_value('DATE_COD'))
#                     # Tester
#                     _node_name = decode_if_needed(obj.get_value('NODE_NAM'))
#                     _stat_num = decode_if_needed(obj.get_value('STAT_NUM'))
#                     if _node_name in _stat_num:
#                         _stat_num = _stat_num.replace(_node_name, '')
#                     retval['Tester'] = "%s:%s" % (_node_name, _stat_num)
#                     # TestProgram
#                     _job_name = decode_if_needed(obj.get_value('JOB_NAM'))
#                     _job_ver = decode_if_needed(obj.get_value('JOB_REV'))
#                     if _job_name in _job_ver:
#                         _job_ver = _job_ver.replace(_job_name, '')
#                     retval['TestProgram'] = "%s:%s" % (_job_name, _job_ver)
#                     # TestSpec
#                     _spec_name = decode_if_needed(obj.get_value('SPEC_NAM'))
#                     _spec_ver = decode_if_needed(obj.get_value('SPEC_VER'))
#                     if _spec_name in _spec_ver:
#                         _spec_ver = _spec_ver.replace(_spec_name, '')
#                     retval['TestSpec'] = "%s:%s" % (_spec_name, _spec_ver)
#                 elif self.version == 'V3':
#                     obj = create_record_object('V3', self.endian, 'MIR', REC)
#                     # Customer
#                     retval['Customer'] = '?'
#                     # Product
#                     retval['Product'] = decode_if_needed(obj.get_value('PART_TYP'))
#                     # Lot
#                     _lot = decode_if_needed(obj.get_value('LOT_ID'))
#                     _sub_lot = decode_if_needed(obj.get_value('SBLOT_ID'))
#                     if _lot in _sub_lot:
#                         _sub_lot = _sub_lot.replace(_lot, '')
#                     retval['Lot'] = "%s:%s" % (_lot, _sub_lot)
#                     # DateCode
#                     _setup_time = decode_if_needed(obj.get_value('SETUP_T'))
#                     _start_time = decode_if_needed(obj.get_value('START_T'))
#                     if _setup_time != 0:
#                         retval['DateCode'] = DT(_setup_time).datecode
#                     elif _start_time != 0:
#                         retval['DateCode'] = DT(_start_time).datecode
#                     else:
#                         retval['DateCode'] = ''
#                     # Tester
#                     _node_name = decode_if_needed(obj.get_value('NODE_NAM'))
#                     _stat_num = decode_if_needed(obj.get_value('STAT_NUM'))
#                     if _node_name in _stat_num:
#                         _stat_num = _stat_num.replace(_node_name, '')
#                     retval['Tester'] = "%s:%s" % (_node_name, _stat_num)
#                     # TestProgram
#                     _job_name = decode_if_needed(obj.get_value('JOB_NAM'))
#                     _job_ver = decode_if_needed(obj.get_value('JOB_REV'))
#                     if _job_name in _job_ver:
#                         _job_ver = _job_ver.replace(_job_name, '')
#                     retval['TestProgram'] = "%s:%s" % (_job_name, _job_ver)
#                     # TestSpec
#                     retval['TestSpec'] = '?'
#                 break
#         return retval
#
#     def dump_records(self, unpack=True, surpress_unknown=True, of_interest=None):
#         stdf_valid_records = ts_to_id(self.version)
#         if of_interest==None:
#             of_interest = list(stdf_valid_records.keys())
#         elif isinstance(of_interest, list):
#             ID2TS = id_to_ts(self.version)
#             tmp_list = []
#             for item in of_interest:
#                 if isinstance(item, str):
#                     if item in ID2TS:
#                         if ID2TS[item] not in tmp_list:
#                             tmp_list.append(ID2TS[item])
#                 elif isinstance(item, tuple) and len(item)==2:
#                     if item in stdf_valid_records:
#                         if item not in tmp_list:
#                             tmp_list.append(item)
#                 else:
#                     STDFError("dump_records(unpack=%s, surpress_unknown=%s, records_of_interest=%s) : Can not understand the types in 'records_of_interest'." % (unpack, surpress_unknown, of_interest))
#             of_interest = tmp_list
#         else:
#             STDFError("dump_records(unpack=%s, surpress_unknown=%s, records_of_interst=%s) : Can not understand the 'records_of_interest' parameter." % (unpack, surpress_unknown, of_interest))
#
#         if unpack:
#             for REC_LEN, REC_TYP, REC_SUB, REC in records_from_file(self.file_name, True):
#                 if (REC_TYP, REC_SUB) in of_interest:
#                     print(REC)
#                 elif not surpress_unknown:
#                     print(REC)
#         else:
#             TS2ID = ts_to_id(self.version, self.extensions())
#             for REC_LEN, REC_TYP, REC_SUB, REC in records_from_file(self.file_name, False):
#                 if (REC_TYP, REC_SUB) in of_interest:
#                         print("   %s" % TS2ID[REC_TYP, REC_SUB])
#                         print("      REC_LEN = '%d' [U*2] (Bytes of data following header)" % REC_LEN)
#                         print("      REC_TYP = '%d' [U*1] (Record type)" % REC_TYP)
#                         print("      REC_SUB = '%d' [U*1] (Record sub-type)" % REC_SUB)
#                         print("      REC = '%s'" % hexify(REC))
#                 elif not surpress_unknown:
#                         print("   ???")
#                         print("      REC_LEN = '%d' [U*2] (Bytes of data following header)" % REC_LEN)
#                         print("      REC_TYP = '%d' [U*1] (Record type)" % REC_TYP)
#                         print("      REC_SUB = '%d' [U*1] (Record sub-type)" % REC_SUB)
#                         print("      REC = '%s'" % hexify(REC))
#
#     def trend_plot(self, parameter, df=None, with_progress=False):
#         '''
#         This method will plot the trend curve for parameter
#         If no pandas data frame (df) is provided, one will be build_uis.
#         '''
#         pass



def has_valid_STDF_extension(FileName):
    '''
    returns True if according to the standard, this is a valid STDF extension
    '''
    if os_is_case_sensitive():
        regex = r'std'
    else:
        regex = r'STD'
    elements = re.split(regex, FileName)
    if len(elements)==1:
        return False
    return True

def has_pretty_STDF_extension(FileName):
    '''
    looks if the uncompressed file name ends with '.std' or '.stdf'
    looks if the (supported) compressed file name ends with '.std.xx' or '.stdf.xx'
    here xx are the supported compression extensions
    '''
    if not has_valid_STDF_extension(FileName): return False # based on filename
    if not is_STDF(FileName): return False # based on contents
    if is_compressed_file(FileName, list(supported_compressions_extensions)):
        ext = extension_from_magic_number_in_file(FileName)
        if len(ext)==1 and (FileName.upper().endswith(".STD%s" % ext[0].upper()) or FileName.upper().endswith('.STDF%s' % ext[0].upper())): return True
    else:
        if FileName.upper().endswith(".STD") or FileName.upper().endswith('.STDF'): return True
    return False

def set_pretty_STDF_extension(FileName, use_hash=False):
    '''

    TODO: implement hashing
    '''


def is_WS(FileName, progress=False):
    '''
    This function returns True if the given (compressed) FileName is made during Wafer Sort, False otherwise.
    The only reliable way to determine if the data is generated during Wafer Sort is to look for the presense of 'WIR'.
    This function might take a while on big files, so if progress=True, a progress bar is displayed.
    '''
    raise NotImplemented("Woops, maybe now is a good moment to implement")
    return True

def is_FT(FileName, progress=False):
    '''
    This function returns True if the given (compressed) FileName is made during Final Test, False otherwhise.
    The only reliable way to determine if the date is generated dureing Final Test is to look for the absense of 'WIR'.
    This function might take a while on big files, so if progress=True, a progress bar is displayed.
    '''
    return not is_WS(FileName, progress)



def is_STDF(FileName):
    '''
    This function will read the first 4 bytes of a file, and see if byte 3 == 0 and byte 4 ==10
    (that is the magic number of an STDF file) if so return True, False otherwise.

    Note, it is checked if the file is compressed (only supports gzip, bz2 and lzma), if so,
    the uncompressed file is examined.
    '''
    if not os.path.exists(FileName):
        return False

    if not os.path.isfile(FileName):
        return False

    if is_compressed_file(FileName, ['.gz', '.xz', '.bz2']):
        extension = extension_from_magic_number_in_file(FileName)[0]
        if extension == '.gz':
            import gzip
            with gzip.open(FileName, 'rb') as fd:
                FAR = fd.read(4)
                REC_TYP, REC_SUB = struct.unpack('BB', FAR[2:4])
                if REC_TYP == 0 and REC_SUB == 10:
                    return True
                else:
                    return False
        elif extension == '.bz2':
            import bz2
            with bz2.open(FileName, 'rb') as fd:
                FAR = fd.read(4)
                REC_TYP, REC_SUB = struct.unpack('BB', FAR[2:4])
                if REC_TYP == 0 and REC_SUB == 10:
                    return True
                else:
                    return False
        elif extension == '.xz':
            import lzma
            with lzma.open(FileName, 'rb') as fd:
                FAR = fd.read(4)
                REC_TYP, REC_SUB = struct.unpack('BB', FAR[2:4])
                if REC_TYP == 0 and REC_SUB == 10:
                    return True
                else:
                    return False
        else:
            raise Exception("Shouldn't reach this point (%s)" % extension)
    else:
        with open(FileName, 'rb') as fd:
            FAR = fd.read(4)
            REC_TYP, REC_SUB = struct.unpack('BB', FAR[2:4])
            if REC_TYP == 0 and REC_SUB == 10:
                return True
            else:
                return False

def is_supported_compressed_STDF_file(FileName):
    '''
    Returns True if FileName is a supported compressed file, False otherwise
    '''
    if not is_STDF(FileName): return False
    ext = extension_from_magic_number_in_file(FileName, supported_compressions_extensions)
    if len(ext)!=1: return False
    return True

def endian_and_version_from_file(FileName):
    '''
    Returns the endian and version from FileName.
    if something went wrong, both are empty strings.
    '''
    tmp = records_from_file(FileName)
    endian = ''
    version = ''
    if tmp!=None: # success
        endian = tmp.endian
        version = tmp.version
    return endian, version

def MIR_from_file(FileName):
    '''
    return *THE* MIR object from FileName.
    '''
    endian, version = endian_and_version_from_file(FileName)
    if endian=='' or version=='': return MIR()
    for _, REC_TYP, REC_SUB, REC in records_from_file(FileName):
        if REC_TYP==1 and REC_SUB==10: break
    return MIR(version, endian, REC)

def SDRs_from_file(FileName):
    '''
    return the SDR(s) objects from FileName.
    '''
    retval = []
    endian, version = endian_and_version_from_file(FileName)
    print(endian, version)
    if endian=='' or version=='': return retval
    for _, REC_TYP, REC_SUB, REC in records_from_file(FileName):
        if (REC_TYP, REC_SUB) not in [(0, 10), (0, 20),(1, 10),(1, 70), (1, 80)]: break
        if (REC_TYP, REC_SUB) == (1, 80):
            retval.append(REC)
    return retval

def TS_from_record(record):
    '''
    given an STDF record (bytearray), extract the REC_TYP and REC_SUB
    Note: This will work on *ALL* records.
    '''
    return struct.unpack("BB", record[2:4])

def HEAD_NUM_and_SITE_NUM_from_record(record):
    '''
    given and STDF record (bytearray), extract the HEAD_NUM and SITE_NUM
    Note : HEAD_NUM and SITE_NUM are not always located at the same (byte) offset.

                REC_TYP   REC_SUB   HEAD_NUM   SITE_NUM (V4)
           PCR      1        30        4          5
           HBR      1        40        4          5
           SBR      1        50        4          5
           PMR      1        60     variable   variable <-- will not support here
           SDR      1        80        4        array   <-- will not support here
           WIR      2        10        4          /     <-- will not support here
           WRR      2        20        4          /     <-- will not support here
           PIR      5        10        4          5
           PRR      5        20        4          5
           TSR      10       30        4          5
           PTR      15       10        9          10    < most likely
           MPR      15       15        9          10    < most likely
           FTR      15       20        9          10    < most likely
    '''
    REC_TYP, REC_SUB = TS_from_record(record)
    HEAD_NUM = 0
    SITE_NUM = 0
    if REC_TYP == 15: # PTR, MTR & FTR
        if REC_SUB in [10, 15, 20]:
            HEAD_NUM, SITE_NUM = struct.unpack("BB", record[8:10])
    elif REC_TYP == 5: # PIR, PRR
        if REC_SUB in [10, 20, 30]:
            HEAD_NUM, SITE_NUM = struct.unpack("BB", record[4:6])
    elif REC_TYP == 1: # PCR, HBR, SBR
        if REC_SUB in [30, 40, 50]:
            HEAD_NUM, SITE_NUM = struct.unpack("BB", record[4:6])
    return HEAD_NUM, SITE_NUM

def TEST_NUM_from_record(record, endian):
    '''
    given a PTR, MPR or FTR record, extract the test Number.
    Note: TEST_NUM is for these records always located on offset 4..7

                REC_TYP   REC_SUB   TEST_NUM (V4)
           PTR      15       10       4:7
           MPR      15       15       4:7
           FTR      15       20       4:7

          Also note that endian is important here!
    '''
    REC_TYP, REC_SUB = TS_from_record(record)
    TEST_NUM = -1
    if REC_TYP == 15 and REC_SUB in [10, 15, 20]:
        TEST_NUM = struct.unpack("%sI" % endian, record[4:7])
    return TEST_NUM

class records_from_file(object):
    '''
    This is a *QUICK* iterator class that returns the next record from an STDF file each time it is called.
    It is fast because it doesn't check versions, extensions and it doesn't unpack the record and skips unknown records.
    It does support gzip, bz2 and lzma compression.
    '''
    def __init__(self, FileName):
        self.fd = None
        if not isinstance(FileName, str): return
        if not os.path.exists(FileName): return
        if not os.path.isfile(FileName): return
        if not is_STDF(FileName): return
        if is_supported_compressed_STDF_file(FileName):
            ext = extension_from_magic_number_in_file(FileName)
            if len(ext)!=1: return
            compression = supported_compressions_extensions[ext[0]]
            if compression=='lzma':
                import lzma
                self.fd = lzma.open(FileName, 'rb')
            elif compression=='bz2':
                import bz2
                self.fd = bz2.open(FileName, 'rb')
            elif compression=='gzip':
                import gzip
                self.fd = gzip.open(FileName, 'rb')
            else:
                raise Exception("the %s compression is supported but not fully implemented." % compression)
        else:
            self.fd = open(FileName, 'rb')
        buff = self.fd.read(6)
        CPU_TYPE, STDF_VER = struct.unpack('BB', buff[4:])
        if CPU_TYPE == 1: self.endian = '>'
        elif CPU_TYPE == 2: self.endian = '<'
        else: self.endian = '?'
        self.version = 'V%s' % STDF_VER
        self.fd.seek(0)
        self.unpack_fmt = '%sHBB' % self.endian

    def __del__(self):
        if self.fd != None:
            self.fd.close()

    def __iter__(self):
        return self

    def __next__(self):
        while self.fd!=None:
            while True:
                header = self.fd.read(4)
                if len(header)!=4:
                    raise StopIteration
                REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.unpack_fmt, header)
                footer = self.fd.read(REC_LEN)
                if len(footer)!=REC_LEN:
                    raise StopIteration
                return REC_LEN, REC_TYP, REC_SUB, header+footer


if __name__ == '__main__':
    FileName = r'C:/Users/hoeren/Desktop/TDK/resources/stdf/Advantest93K.std'
    for REC in records_from_file(FileName):
        print(REC)
