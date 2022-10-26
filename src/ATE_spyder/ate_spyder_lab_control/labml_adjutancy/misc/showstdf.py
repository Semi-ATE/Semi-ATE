# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 18:27:20 2022

@author: jung
"""
import os
from Metis.tools import stdf2ph5
import pandas as pd
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class showStdf():
    RESULTDIR = 'result_h5'
    Translate = {'PTR': {
                    'PTR.HEAD_NUM': 'Head',
                    'PTR.SITE_NUM': 'Site',
                    # 'PTR.TEST_TXT': 'Text',
                    # 'PTR.RESULT': 'Result',
                    'PTR.UNITS': 'Unit',
                    'PTR.TEST_NUM': 'TestNo'}
                 }
    SI = {
            1.000000e+24: 'y',
            1.000000e+21: 'z',
            1.000000e+18: 'a',
            1.000000e+15: 'f',
            1.000000e+12: 'p',
            1.000000e+09: 'n',
            1.000000e+06: 'µ',
            1.000000e+03: 'm',
            1.000000e+00: '',
            1.000000e-03: 'k',
            1.000000e-06: 'M',
            1.000000e-09: 'G',
            1.000000e-12: 'T',
            1.000000e-15: 'P',
            1.000000e-18: 'E',
            1.000000e-21: 'Z',
            1.000000e-24: 'Y',
            }

    def __init__(self, path, filename, lot, resultdir):
        self.hdf5_file = f'{path}{self.RESULTDIR}/{lot}.hdf5'
        self.filename = filename

        if Path(self.hdf5_file).is_file() and os.path.getmtime(path+filename) > os.path.getmtime(self.hdf5_file):
            os.remove(self.hdf5_file)
        if not Path(self.hdf5_file).is_file():
            stdf2ph5.SHP(False).import_stdf_into_hdf5(path+filename, path+resultdir, disable_progress=False)

    def getdataFrame(self):
        def setCell(cell_value):
            highlight = 'background-color: darkorange;'
            default = ''
            if type(cell_value) in [float, int]:
                if cell_value % 2 == 0:
                    return highlight
            return default

        try:
            ptr = pd.read_hdf(self.hdf5_file, f'/raw_stdf_data/{self.filename}/PTR', mode='r')
            # tsr = pd.read_hdf(self.hdf5_file, f'raw_stdf_data/{self.filename}/TSR', mode= r')
        except Exception:
            return None
            # EXEC_CNT, FAIL_CNT, ALRM_CNT
        ptr['fmt'] = ptr['PTR.C_HLMFMT'].apply(lambda x: x.decode()[1:])
        # f'{x:{fmt}}'
        # ptr['fmt'].apply(lambda x: x)
        # f"{x:{ptr['fmt'].apply(lambda x: x)}}"     how set the right format ??
        fmt = '7.3f'
        ptr['mul'] = 10**ptr['PTR.RES_SCAL'].apply(lambda x: float(x))
        ptr['SI'] = ptr['mul'].apply(lambda x: self.SI[x])
        ptr['LTL'] = (ptr['PTR.LO_LIMIT']*ptr['mul']).apply(lambda x: f'{x:{fmt}} ') + ptr['SI'].apply(lambda x: x) + ptr['PTR.UNITS'].apply(lambda x: x.decode())
        ptr['UTL'] = (ptr['PTR.HI_LIMIT']*ptr['mul']).apply(lambda x: f'{x:{fmt}} ') + ptr['SI'].apply(lambda x: x) + ptr['PTR.UNITS'].apply(lambda x: x.decode())
        ptr['Result'] = (ptr['PTR.RESULT']*ptr['mul']).apply(lambda x: f'{x:{fmt}} ') + ptr['SI'].apply(lambda x: x) + ptr['PTR.UNITS'].apply(lambda x: x.decode())
        ptr['Test'] = ptr['PTR.TEST_TXT'].apply(lambda x: x.decode())

        ptr['LSL'] = (ptr['PTR.LO_SPEC']*ptr['mul']).apply(lambda x: f'{x:{fmt}} ') + ptr['SI'].apply(lambda x: x) + ptr['PTR.UNITS'].apply(lambda x: x.decode())
        ptr['USL'] = (ptr['PTR.HI_SPEC']*ptr['mul']).apply(lambda x: f'{x:{fmt}} ') + ptr['SI'].apply(lambda x: x) + ptr['PTR.UNITS'].apply(lambda x: x.decode())

        # ptr['Result'] = ptr['Result'].apply(lambda x: f'{x:{ptr["fmt"].apply(lambda x: x)}} ') + ptr['SI'].apply(lambda x: x)  + ptr['PTR.UNITS'].apply(lambda x: x.decode())
        # ptr.style.applymap(lambda x: 'background-color : yellow' if x>ptr.iloc[0,0] else '')

        ptr['LSL'] = ptr['LSL'].apply(lambda x: x if x.find('inf') < 0 else '')
        ptr['LTL'] = ptr['LTL'].apply(lambda x: x if x.find('inf') < 0 else '')
        ptr['UTL'] = ptr['UTL'].apply(lambda x: x if x.find('inf') < 0 else '')
        ptr['USL'] = ptr['USL'].apply(lambda x: x if x.find('inf') < 0 else '')

        ptr.rename(columns=self.Translate['PTR'], inplace=True)

        ptr['Pass'] = ptr['PTR.TEST_FLG'].apply(lambda x: x.decode('ascii'))
        for val in range(0, len(ptr['Pass'])):
            if ptr['Pass'][0] == 0:
                ptr['Result'][val].style.set_properies(**{'background-color': 'green'})
            elif ptr['Pass'][0] == 1:
                ptr['Result'][val].style.set_properies(**{'background-color': 'red'})

        # pd.options.display.float_format = '{:.2f}'.format

        # df.style.applymap(setCell)

        # pd.options.display.float_format = '${:, .2f}'.format
        return ptr

    def show(self, tableview):
        df = self.getdataFrame()
        if df is None:
            return
        keys = df[['TestNo', 'Test', 'LSL', 'LTL', 'Result', 'UTL', 'USL', 'Pass', 'PTR.TEST_FLG', 'PTR.PARM_FLG']]
        model = pandasModel(keys)
        # tableview = QTableView()
        tableview.setModel(model)
        # tableview.resize(800, 600)
        tableview.show()

    def close():
        pass


if __name__ == '__main__':
    import sys
    path = "C:/Users/jung/ATE/Docu/Beispiele/"
    filename = 'stdf1.stdf'
    lot = '322207.000'

    #path = f"{os.getenv('SPY_PYTHONPATH')}/src/HW0/FT/"
    #filename = 'tb_ate_hw0_ft_device1_engineering_myflow.stdf'
    #lot = 'no_lot'
    # self.dataframe = showstdf.showStdf(path+'/', f'{self.test_program_name}.stdf', lot, 'result_h5')

    # C:/Users/jung/Work Folders/Projecte/Repository/hana/0504/units/lab/source/python/tb_ate\src\HW0\FT/, tb_ate_HW0_FT_Device1_engineering_myFlow.stdf, no_lot, result_h5
    # C:/Users/jung/Work Folders/Projecte/Repository/hana/0504/units/lab/source/python/tb_ate/src/HW0/FT/, tb_ate_hw0_ft_device1_engineering_myflow.stdf, no_lot, result_h5
    df = showStdf(path, filename, lot, 'result_h5')

    pd.set_option('display.max_columns', 50)
    myframe = df.getdataFrame()
    show = myframe[['TestNo', 'Test', 'LSL', 'LTL', 'Result', 'UTL', 'USL', 'Pass', 'PTR.TEST_FLG', 'PTR.PARM_FLG']]

    app = QApplication(sys.argv)
    model = pandasModel(show)
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())
