
from ate_master_app.parameter_parser.xml_parameter_parser import XmlParameterParser
from ate_master_app.parameter_parser.filesystem_data_source import FileSystemDataSource
from ate_master_app.parameter_parser.static_data_source import StaticDataSource
from ate_master_app.utils.master_configuration import MasterConfiguration


def CreateParser(jobformat: str):
    if(jobformat == 'xml.semi-ate'):
        return XmlParameterParser()

    return None


def CreateDataSource(jobname: str, configuration: MasterConfiguration, parser, logger):
    jobdatasource = configuration.jobsource

    if(jobdatasource == 'filesystem'):
        return FileSystemDataSource(jobname, configuration, parser, logger)
    if(jobdatasource == "static"):
        return StaticDataSource()

    return None
