# The semi-ate-control-app package

This package provides some a command line tool (`launch_control`). In order to use this application you have to configure it first. This tool should be run on some test node, i.e. some host controlling measurement instruments. It communicates with the master application from the `semi-ate-master-app` package by MQTT. The master application sends mqtt-messages to steer the control application. The control application itself is responsible for loading/unloading and executing some test-program. Test results, i.e. STDF records, are send back to the master application.

## Configuration

Configuration of the control application is done by writing a JSON file called **control_config_file.json**. The following key-value-pairs have to be defined:

```JSON
{
    "broker_host": "127.0.0.1",
    "broker_port": 1883,
    "device_id": "SCT-82-1F",
    "site_id": "0",
    "loglevel": 10
}
```

* `broker_host` defines the ip address of the mqtt broker.
* `broker_port` defines the prot of the mqtt broker.
* `device_id` defines a unique id of the so-called test-system. A test system can contain several host running he control applications. And some host running the master application.
* `site_id` is the unique identifier of the host running the control application
* `loglevel` defines the log-level of the control application

The _device_id_ and _site_id_ is used to build unique mqtt-message-topics automatically. The idea is that no test-system influences some other test system.

## Starting the Control Application

We assume that the semi-ate-control-app has been installed in the current python environment. Further configuration **control_config_file.json** file is located in the current folder.

**IMPORTANT**: The configuration file has to be named **control_config_file.json**

```Console
(environment)> launch_control
control 0|21/03/2022 04:14:10 PM |INFO    |mqtt connected
control 0|21/03/2022 04:14:10 PM |INFO    |control state is: idle
```
