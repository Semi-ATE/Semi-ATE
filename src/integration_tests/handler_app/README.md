# The semi-ate-handler-app package

This package provides a command line tool (`launch_handler`). In order to use this application you have to configure it first. This tool should be run on some host controlling a handler. It communicates with the master application from the `semi-ate-master-app` package over MQTT.
First that handler application detects the master application. Next the master sends the initialized status. After this message is received by the handler application the handler can send commands to he master application in order to load, start and terminate some test-program.

## Configuration

Configuration of the handler application is done by writing a JSON file called **handler_config_file.json**. The following key-value-pairs have to be defined:

```JSON
{
    "broker_host": "127.0.0.1",
    "broker_port": 1883,
    "handler_type": "geringer",
    "handler_id": "HTO92-20F",
    "device_ids": ["SCT-81-1F"],
    "site_layout": [[0, 0]],
    "loglevel": 10
}
```

* `broker_host` defines the ip address of the mqtt broker.
* `broker_port` defines the prot of the mqtt broker.
* `handler_type` defines the type of the handler. The type is used to communicate with the handler. At the moment only type _geringer_ is supported.
* `handler_id` the handler id is used to form unique MQTT topics.
* `device_ids` defines a list of test systems connected to the handler. A handler may steer more than one test system, i.e.test systems that test some Devices by different temperatures.
* `site_layout` defines the site layout of the different test sites.
* `loglevel` defines the log-level of the control application

## Starting the Handler Application

We assume that the semi-ate-handler-app package has been installed in the current python environment. Further the configuration file **handler_config_file.json** is located in the current folder.

**IMPORTANT**: The configuration file has to be named **handler_config_file.json**

```Console
(environment)> launch_handler 1234
```

The parameter after the `launch_handler` command is the serial port number that is used to communicate with the handler over a serial interface. In order to define the serial interface in more details the following optional parameters are supported:

```Console
--baudrate BAUDRATE  set bautrate
--timeout TIMEOUT    set timeout
--parity PARITY      set parity
--bytesize BYTESIZE  set bytesize
--stopbits STOPBITS  set stopbits
```
