## TES: Test Executive Software

In this step we will configure the software components as if they were run on a Mini SCT device.
From Semi-ATE root navigate to ATE/TES/apps.

current directory: Semi-ATE

```Console
cd ATE/TES/apps
```

The files ```master_config_file_template.json``` and
```control_config_file_template.json``` serve as the basic configuration for our system. Copy these two files adjust them, so that:

- The broker_host address points to the host, where your mqtt broker is running
- Both files have the same device id (this is required, so that master and control application can "find" each other).
- Leave the rest of the file contents as is.
- Rename the files to ```master_config_file.json``` and ```control_config_file.json``` respectively.

## Master Config File

```json
{
    "broker_host": "127.0.0.1", // mqtt broker
    "broker_port": 1883,        // mqtt port
    "device_id": "SCT-81-1F",   // unique device id
    "sites": [                  // list of site_ids (these are control applications with the respective id)
        "0"
    ],
    "webui_host": "127.0.0.1",
    "webui_port": 8081,
    "webui_root_path": ".",
    // the following fields are information to simulate a test-program execition
    "Handler": "HTO92-20F",
    "environment": "F1",
    "jobsource": "filesystem",
    "jobformat": "xml.semi-ate",
    "filesystemdatasource_path": ".",
    "filesystemdatasource_jobpattern": "le306426001_template.xml",
    "enable_timeouts": true,
    "skip_jobdata_verification": false,
    "user_settings_filepath": "master_user_settings.json"
}
```

:warning: if no mqtt broker is available, mosquitto could be installed
<https://mosquitto.org/downloadconfigure>

## Control Config File

```json
{
    "broker_host": "127.0.0.1",  // mqtt broker
    "broker_port": 1883,         // mqtt port
    "device_id": "SCT-81-1F",    // unique device_id (should match the one configured in master)
    "site_id": "0"               // site_id which should be in the master sites list
}
```

These configurations are valid once the comments are removed.

## Launch applications

From within the apps folder execute the following commands (you'll need two open two terminals to do this, and you'll have to activate the environment for both terminals):

```Console
python launch_master.py
```

```Console
python launch_control.py
```

### Interacting with the applications

When both applications are running, the web-ui is reachable on:
<http://localhost:8081>

localhost = "127.0.0.1"  -> configured with the webui_host setting in "master_config_file.json"

8081 -> configured with the webui_port setting in "master_config_file.json"

## XML configuration

inside apps folder there will be also an xml file template that could be configured as follow:

### CLUSTER section

- TESTER should match the device-id name configured via configuration file
- HANDLER_PROBER should match the Handler name configured via configuration file

### STATION section

- TESTER# should also match the device-id already configured
- PROGRAM_DIR# best if it is an absolute path of the test-program file (.py)

if the config files template are taken then the only thing that should be adapted is the PROGRAM_DIR#

if other checks are missing or other information should also be checked from the xml file, please be free to report !
