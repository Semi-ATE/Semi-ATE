
from ATE.TES.apps.masterApp.parameter_parser.xml_parameter_parser import XmlParameterParser
from ATE.TES.apps.masterApp.parameter_parser.filesystem_data_source import FileSystemDataSource
from ATE.TES.apps.masterApp.parameter_parser.static_data_source import StaticDataSource


def CreateParser(jobformat: str):
    if(jobformat == 'xml.micronas'):
        return XmlParameterParser()

    return None


def CreateDataSource(jobname: str, configuration: dict, parser):
    jobdatasource = configuration['jobsource']

    if(jobdatasource == 'filesystem'):
        return FileSystemDataSource(jobname, configuration, parser)
    if(jobdatasource == "static"):
        return StaticDataSource()

    return None
