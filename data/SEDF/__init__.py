from ATE.Data.Formats.SEDF.records import ImplementedRecords
from ATE.Data.Formats.SEDF.utils import SEDFopen as open

for REC in ImplementedRecords:
    exec("from ATE.Data.Formats.records import %s"%REC)
