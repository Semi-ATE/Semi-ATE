'''
Created on Aug 7, 2019

@author: hoeren
'''
import os

from tqdm import tqdm

import STDF
from Semi_ATE.STDF.utils import endian_and_version_from_file
from Semi_ATE.STDF.utils import is_STDF
from Semi_ATE.STDF.utils import records_from_file
from Semi_ATE.STDF.utils import STDFError
from Semi_ATE.STDF.utils import TS_from_record
from Semi_ATE.STDF.utils import ts_to_id
from ATE.utils.compression import get_deflated_file_size


class Metis(object):
    '''
    The Metis class interacts between STDF and the Pandas structures.
    '''

    def __init__(self):
        self.df = None

    def __call__(self, FileName, progress=True):
        self.import_stdf(FileName, progress)

    def import_stdf(self, FileName, progress=True):
        '''
        This method will add FileName to this Metis object.
        '''
        index = {}
        offset = 0



        if is_STDF(FileName):
            endian, version = endian_and_version_from_file(FileName)
            index['version'] = version
            index['endian'] = endian
            index['records'] = {}
            index['indexes'] = {}
            index['parts'] = {}
            PIP = {} # parts in process
            PN = 1

            TS2ID = ts_to_id(version)

        # indexing the stdf file
            if progress:
                desc= "Indexing STDF file '%s'" % os.path.basename(FileName)
                total = get_deflated_file_size(FileName)
                progress_bar = tqdm(total=total, desc=desc, leave=False, unit='b')

            for _, REC_TYP, REC_SUB, REC in records_from_file(FileName):
                REC_ID = TS2ID[(REC_TYP, REC_SUB)]
                REC_LEN = len(REC)
                if REC_ID not in index['records']:
                    index['records'][REC_ID] = []
                index['indexes'][offset] = REC
                index['records'][REC_ID].append(offset)
                if REC_ID in ['PIR', 'PRR', 'PTR', 'FTR', 'MPR']:
                    if REC_ID == 'PIR':
                        pir = STDF.PIR(index['version'], index['endian'], REC)
                        pir_HEAD_NUM = pir.get_value('HEAD_NUM')
                        pir_SITE_NUM = pir.get_value('SITE_NUM')
                        if (pir_HEAD_NUM, pir_SITE_NUM) in PIP:
                            raise Exception("One should not be able to reach this point !")
                        PIP[(pir_HEAD_NUM, pir_SITE_NUM)] = PN
                        index['parts'][PN]=[]
                        index['parts'][PN].append(offset)
                        PN+=1
                    elif REC_ID == 'PRR':
                        prr = STDF.PRR(index['version'], index['endian'], REC)
                        prr_HEAD_NUM = prr.get_value('HEAD_NUM')
                        prr_SITE_NUM = prr.get_value('SITE_NUM')
                        if (prr_HEAD_NUM, prr_SITE_NUM) not in PIP:
                            raise Exception("One should not be able to reach this point!")
                        pn = PIP[(prr_HEAD_NUM, prr_SITE_NUM)]
                        index['parts'][pn].append(offset)
                        del PIP[(prr_HEAD_NUM, prr_SITE_NUM)]
                    elif REC_ID == 'PTR': #TODO: move this one to be the first to be checked, as this will be the most common one!
                        ptr = STDF.PTR(index['version'], index['endian'], REC)
                        ptr_HEAD_NUM = ptr.get_value('HEAD_NUM')
                        ptr_SITE_NUM = ptr.get_value('SITE_NUM')
                        if (ptr_HEAD_NUM, ptr_SITE_NUM) not in PIP:
                            raise Exception("One should not be able to reach this point!")
                        pn = PIP[(ptr_HEAD_NUM, ptr_SITE_NUM)]
                        index['parts'][pn].append(offset)
                    elif REC_ID == 'FTR':
                        ftr = STDF.FTR(index['version'], index['endian'], REC)
                        ftr_HEAD_NUM = ftr.get_value('HEAD_NUM')
                        ftr_SITE_NUM = ftr.get_value('SITE_NUM')
                        if (ftr_HEAD_NUM, ftr_SITE_NUM) not in PIP:
                            raise Exception("One should not be able to reach this point!")
                        pn = PIP[(ftr_HEAD_NUM, ftr_SITE_NUM)]
                        index['parts'][pn].append(offset)
                    elif REC_ID == 'MPR':
                        mpr = STDF.MPR(index['version'], index['endian'], REC)
                        mpr_HEAD_NUM = mpr.get_value('HEAD_NUM')
                        mpr_SITE_NUM = mpr.get_value('SITE_NUM')
                        if (mpr_HEAD_NUM, mpr_SITE_NUM) not in PIP:
                            raise Exception("One should not be able to reach this point!")
                        pn = PIP[(mpr_HEAD_NUM, mpr_SITE_NUM)]
                        index['parts'][pn].append(offset)
                    else:
                        raise Exception("One should not be able to reach this point! (%s)" % REC_ID)
                if progress:
                    progress_bar.update(REC_LEN)
                offset += REC_LEN

        # analyzing TDR's
            if progress:
                progress_bar.close()
                desc = "Analyzing TDF's "
                total = len(index['records']['TSR'])
                progress_bar = tqdm(total=total, desc=desc, leave=False, unit='tests')

            TEST_NUM_NAM = {}

            for tsr_offset in index['records']['TSR']:
                tsr = STDF.TSR(index['version'], index['endian'], index['indexes'][tsr_offset])
                TEST_NUM = tsr.get_value('TEST_NUM')
                TEST_NAM = tsr.get_value('TEST_NAM')
                TEST_TYP = tsr.get_value('TEST_TYP').upper()
                if TEST_NUM not in TEST_NUM_NAM:
                    TEST_NUM_NAM[TEST_NUM] = []
                if (TEST_NAM, TEST_TYP) not in TEST_NUM_NAM[TEST_NUM]:
                    TEST_NUM_NAM[TEST_NUM].append((TEST_NAM, TEST_TYP))
                if progress:
                    progress_bar.update()

        # creating dataframe
            if progress:
                progress_bar.close()
                desc = "Creating dataframe "
                total = len(TEST_NUM_NAM)
                progress_bar = tqdm(total=total, desc=desc, leave=False, unit='tests')

            ROW_index = sorted(list(index['parts']))
            TEST_ITM_index = ['LOT_ID', 'MOD_COD', 'X_POS', 'Y_POS'] #TODO: add more ...
            TEST_NAM_index = ['Meta'] * len(TEST_ITM_index)
            TEST_NUM_index = ['Meta'] * len(TEST_ITM_index)
            for TEST_NUM in sorted(TEST_NUM_NAM):
                TEST_TYP = TEST_NUM_NAM[TEST_NUM][1]
                if TEST_TYP == 'P':
                    PTR_FIELDS = ['LO_SPEC', 'LO_LIMIT', 'RESULT', 'HI_LIMIT', 'HI_LIMIT', 'UNITS', 'PF']
                    TEST_ITM_index+=PTR_FIELDS
                    TEST_NAM_index+=[TEST_NUM_NAM[TEST_NUM][1]]*len(PTR_FIELDS)
                    TEST_NUM_index+=[TEST_NUM]*len(PTR_FIELDS)
                elif TEST_TYP == 'F':

                    TEST_NUM_index+=[TEST_NUM]*5
                    TEST_NAM_index+=[TEST_NUM_NAM[TEST_NUM][1]]*5     # VECT_NAME TIME_SET NUM_FAIL X_FAIL_AD Y_FAIL_AD PF
                elif TEST_TYP == 'M':
                    pass
                else:
                    raise STDFError("Test Type '%s' is unknown" % TEST_TYP)
                if progress:
                    progress_bar.update()

        # filling the dataframe



            # print("\n\n\n")


            # for record_offset in index['parts'][1]:
            #     record = index['indexes'][record_offset]
            #     T, S = TS_from_record(record)
            #     ID = TS2ID[(T,S)]
            #     if ID == 'PTR':
            #         ptr = STDF.PTR(index['version'], index['endian'], record)
            #         print(ptr)
            #     if ID == 'PIR':
            #         pir = STDF.PIR(index['version'], index['endian'], record)
            #         print(pir)
            #     if ID == 'PRR':
            #         prr = STDF.PRR(index['version'], index['endian'], record)
            #         print(prr)





    #         if progress:
    #             description = "Constructing data-frame"
    #             constructing_progress = tqdm(total=len(index['parts']), ascii=True, position=2, disable=not progress, desc=description, leave=False, unit='parts')
    #
    #         for part in index['parts']:
    #             for record_offset in index['parts'][part]:
    #                 Type, SubType = TS_from_record(index['indexes'][record_offset])
    #                 ID = TS2ID[(Type, SubType)]
    #                 if ID == 'FTR':
    #                     ftr = FTR(index['version'], index['endian'], index['indexes'][record_offset])
    #
    #
    #                 if ID == 'PTR':
    #                     ptr = PTR(index['version'], index['endian'], index['indexes'][record_offset])
    #
    #                 if ID == 'MPR':
    #                     ptr = MPR(index['version'], index['endian'], index['indexes'][record_offset])
    #
    #
    #
    #             constructing_progress.update()







            if progress:
                # progress_bar.close()
                progress_bar.close()
    #             constructing_progress.close()

            return index, TEST_NUM_NAM

        else: #not an STDF file
            pass

    def save(self):
        '''
        this method saves this object in an HDF5 container.
        ps: the target (base) directory comes from the environment variable 'metis_dir' (or so)
        '''
        pass

    def pull_in(self, what=''):
        '''
        this method will pull in 'what' to the dynamic data-frame.
        '''




if __name__ == '__main__':
    stdf_file = r'C:/Users/hoeren/Desktop/TDK/resources/stdf/Cohu_D10_2.xz'

    a = Metis()
    a.import_stdf(stdf_file)
