from enum import Enum


class BinTableFieldName(Enum):
    SBinName = 'SBINNAME'
    SBinNum = 'SBIN'
    SBinGroup = 'GROUP'
    SBinDescription = 'DESCRIPTION'
    HBin = 'HBIN'

    def __call__(self):
        return self.value
