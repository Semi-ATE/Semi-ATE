from ate_master_app.parameter_parser import parser_factory
from ate_master_app.parameter_parser.xml_parameter_parser import XmlParameterParser
from ate_master_app.parameter_parser.filesystem_data_source import FileSystemDataSource
from ate_master_app.utils.master_configuration import MasterConfiguration
from tests.test_masterapp import default_configuration
from tests.utils import (create_xml_file, DEVICE_ID)

import os


BASE_PATH = os.path.dirname(__file__)
XML_PATH = os.path.join(BASE_PATH, 'le306426001_template.xml')
XML_PATH_NEW = os.path.join(BASE_PATH, 'le306426001.xml')


create_xml_file(XML_PATH, XML_PATH_NEW, DEVICE_ID)


def get_logger():
    from ate_common.logger import Logger
    return Logger('test')


class TestParserFactory:
    def default_configuration(self):
        return {'broker_host': '192.168.0.1',
                'broker_port': '8991',
                'sites': ["0", "1"],
                'device_id': '0',
                'jobsource': 'filesystem',
                'jobformat': 'xml.semi-ate',
                "filesystemdatasource_path": '',
                "filesystemdatasource_jobpattern": "le306426001.xml",
                'enable_timeouts': True,
                'skip_jobdata_verification': False,
                'environment': "abs",
                'Handler': "HTO92-20F",
                'tester_type': 'Semi-ATE Master Parallel Tester',
                "site_layout": {"0": [0, 1], "1": [1, 2]},
                'webui_root_path': '',
                'webui_host': '',
                'webui_port': '0',
                'site_layout': [],
                'develop_mode': False}

    def test_create_parser_yields_xml_parser_for_xml_semi_ate(self):
        jobformat = 'xml.semi-ate'
        parser = parser_factory.CreateParser(jobformat)

        assert (type(parser) is XmlParameterParser)

    def test_create_parser_yields_none_for_unknown_value(self):
        jobformat = 'empty'
        parser = parser_factory.CreateParser(jobformat)

        assert (parser is None)

    def test_create_datasource_yields_filesystemdatasource_for_filesystem(self):
        config = default_configuration()
        config['jobsource'] = 'filesystem'
        config['filesystemdatasource_path'] = '.'
        config['filesystemdatasource_jobpattern'] = 'job'
        parser = None
        datasource = parser_factory.CreateDataSource("somejob", MasterConfiguration(**config), parser, get_logger())

        assert (type(datasource) is FileSystemDataSource)

    def test_create_datasource_yields_filesystemdatasource_for_unkown_value(self):
        config = default_configuration()
        config['jobsource'] = 'gremlins'
        parser = None
        datasource = parser_factory.CreateDataSource("somejob", MasterConfiguration(**config), parser, get_logger())

        assert (datasource is None)

    def test_read_data_from_xml_file_file_does_not_exist(self):
        config = default_configuration()
        config['jobsource'] = 'filesystem'
        config['jobformat'] = 'xml.semi-ate'
        config['filesystemdatasource_path'] = './tests/apps'
        config['filesystemdatasource_jobpattern'] = 'ddd.xml'

        parser = parser_factory.CreateParser(config['jobformat'])
        datasource = parser_factory.CreateDataSource("306426.001", MasterConfiguration(**config), parser, get_logger())
        assert (type(datasource) is FileSystemDataSource)
        data = datasource.retrieve_data()
        assert (data is None)

    def test_read_data_from_xml_file_wrong_lot_number(self):
        config = default_configuration()
        config['jobsource'] = 'filesystem'
        config['jobformat'] = 'xml.semi-ate'
        config['filesystemdatasource_path'] = BASE_PATH
        config['filesystemdatasource_jobpattern'] = 'le306426001.xml'

        parser = parser_factory.CreateParser(config['jobformat'])
        datasource = parser_factory.CreateDataSource("11111111", MasterConfiguration(**config), parser, get_logger())
        assert (type(datasource) is FileSystemDataSource)
        data = datasource.retrieve_data()
        assert (data is not None)
        verify_result = datasource.verify_data(data)
        assert (verify_result is False)

    def test_read_data_from_xml_file_device_id_does_not_match(self):
        config = default_configuration()
        config['device_id'] = 'SCT_2121'
        config['jobsource'] = 'filesystem'
        config['jobformat'] = 'xml.semi-ate'
        config['filesystemdatasource_path'] = BASE_PATH
        config['filesystemdatasource_jobpattern'] = 'le306426001.xml'

        parser = parser_factory.CreateParser(config['jobformat'])
        datasource = parser_factory.CreateDataSource("306426.001", MasterConfiguration(**config), parser, get_logger())
        assert (type(datasource) is FileSystemDataSource)
        data = datasource.retrieve_data()
        assert (data is not None)
        verify_result = datasource.verify_data(data)
        assert (verify_result is False)

    def test_read_data_from_xml_file_valid_data(self):
        config = default_configuration()
        config['device_id'] = DEVICE_ID
        config['jobsource'] = 'filesystem'
        config['jobformat'] = 'xml.semi-ate'
        config['filesystemdatasource_path'] = BASE_PATH
        config['filesystemdatasource_jobpattern'] = 'le306426001.xml'
        config['Handler'] = 'HTO92-20F'
        config['Environment'] = 'F1'

        parser = parser_factory.CreateParser(config['jobformat'])
        datasource = parser_factory.CreateDataSource("306426.001", MasterConfiguration(**config), parser, get_logger())
        assert (type(datasource) is FileSystemDataSource)
        data = datasource.retrieve_data()
        assert (data is not None)
        verify_result = datasource.verify_data(data)
        assert (verify_result is True)

    def test_read_data_from_xml_file_invalid_handler_id(self):
        config = default_configuration()
        config['device_id'] = DEVICE_ID
        config['jobsource'] = 'filesystem'
        config['jobformat'] = 'xml.semi-ate'
        config['filesystemdatasource_path'] = BASE_PATH
        config['filesystemdatasource_jobpattern'] = 'le306426001.xml'
        config['Handler'] = 'invalid'
        config['Environment'] = 'F1'

        parser = parser_factory.CreateParser(config['jobformat'])
        datasource = parser_factory.CreateDataSource("306426001", MasterConfiguration(**config), parser, get_logger())
        assert (type(datasource) is FileSystemDataSource)
        data = datasource.retrieve_data()
        assert (data is not None)
        verify_result = datasource.verify_data(data)
        assert (verify_result is False)
