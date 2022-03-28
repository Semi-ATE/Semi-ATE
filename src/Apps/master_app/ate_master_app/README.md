# The semi-ate-master-app package

This package provides a command line tool (`launch_master`). In order to use this application you have to configure it first. This tool should be run on host that either runs the control application from the `semi-ate-control-app` package or that is connected via ethernet to further hosts running the control application.
The master application controls the so-called control applications, i.e. test nodes. To do so the master sends commands to the different test nodes using MQTT messages. Among others these commands
include commands for loading and unloading test programs and starting the test execution.

The muster application can be controlled using a web interface or it is controlled by some handler application.

## Configuration

Configuration of the master application is done by writing a JSON file called **master_config_file.json**. The following key-value-pairs have to be defined:

```JSON
{
    "broker_host": "127.0.0.1",
    "broker_port": 1883,
    "device_id": "SCT-82-1F",
    "sites": [
        "0"
    ],
    "Handler": "HTO92-20F",
    "environment": "F1",
    "webui_host": "127.0.0.1",
    "webui_port": "8081",
    "jobsource": "filesystem",
    "jobformat": "xml.semi-ate",
    "skip_jobdata_verification": false,
    "filesystemdatasource.path": ".",
    "filesystemdatasource.jobpattern": "le#jobname#.xml",
    "enable_timeouts": true,
    "user_settings_filepath": "master_user_settings.json",
    "site_layout": { "0": [0, 0]},
    "tester_type": "Semi-ATE Master Single Tester",
    "loglevel": 10,
    "web_root_folder": "./"
}
```

* `broker_host` defines the ip address of the mqtt broker.
* `broker_port` defines the prot of the mqtt broker.
* `site_layout` defines the site layout of the different test sites.
* `device_id` defines the name of the test site
* `sites` defines an array containing the test node ids running the control application
* `Handler` defines the name of some device handler or wafer handler, i.e. prober
* `environment` defines the test environment (F1, F2, F3, P1, P2, P3)
* `webui_host` defines the ip of the web interface for controlling he master application manually
* `webui_port` defines the port number of the web interface
* `webui_root_path` defines the URI of the web-resources, i.e. the folder containing the index.html of some web application.
* `jobsource` defines the location where to find test job definitions
* `jobformat` defines the format of the job definitions
* `skip_jobdata_verification` defines whether the job definition has to be verified
* `filesystemdatasource.path` defines the path where to find job definitions
* `filesystemdatasource.jobpattern` defines the pattern for the name of the test job file. This is done by replacing _#jobname#_ by the job id, i.e. the lot id.
* `enable_timeouts` defines whether or not timeouts are enabled. If enabled the system will produce some error message if certain things like becomming ready, loading or undloading a test program etc. take to much time.
* `user_settings_filepath` defines where the user specific settings are stored. These settings are set via the web interface.
* `site_layout` defines for each site the layout. The layout is the start coordinate of some site
* `tester_type` defines the type of he tester. This provided by the tester plugin.
* `loglevel` defines the log-level of the control application

## Starting the Master Application

We assume that the semi-ate-master-app package has been installed in the current python environment. Further the configuration file **master_config_file.json** is located in the current folder.

**IMPORTANT**: The configuration file has to be named **master_config_file.json**

```Console
(environment)> launch_master
======== Running on http://127.0.0.1:8081 ========
(Press CTRL+C to quit)
master   |22/03/2022 04:45:37 PM |INFO    |mqtt connected
master   |22/03/2022 04:45:37 PM |INFO    |Master state is connecting
```
