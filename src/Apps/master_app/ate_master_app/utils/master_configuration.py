from pydantic import BaseModel
from ate_common.logger import LogLevel


class MasterConfiguration(BaseModel):
    broker_host: str = 'localhost'
    broker_port: int = 8081
    device_id: str
    sites: list
    Handler: str
    environment: str
    webui_host: str
    webui_port: str
    webui_root_path: str
    jobsource: str
    jobformat: str
    filesystemdatasource_path: str
    filesystemdatasource_jobpattern: str
    skip_jobdata_verification: bool = False
    enable_timeouts: int
    user_settings_filepath: str = None
    site_layout: list
    tester_type: str
    loglevel: int = LogLevel.Warning()
    develop_mode: bool = False
