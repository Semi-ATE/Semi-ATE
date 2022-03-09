from enum import Enum


class FileIconTypes(Enum):
    PDF = ['.pdf']
    DOC = ['.doc', '.docx', '.odt']
    XLS = ['.xls', '.xlsx', '.ods']
    PPT = ['.ppt', '.pptx', '.odp']
    TEX = ['.tex', '.latex']
    ODF = ['.odf']
    ODG = ['.odg']
    HTML = ['.htm', '.html']
    PNG = ['.png', '.jpg']
    AVI = ['.avi', '.mp4']
    FLAC = ['.flac', '.mid', '.midi', '.aac']
    TXT = ['.txt']
    MD = ['.md']
    ZIP = ['.zip', '.xz', '.gz', '.bz2']
    FOLDER = ['.']
    PY = ['.py']
    VIRTUAL = ['']

    def __call__(self):
        return self.value
