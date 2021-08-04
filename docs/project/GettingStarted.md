# Getting Started with ATE Dev

## Install Prerequisites

Install Python 3 (at least 3.7) and PIP

### MQTT

The components use MQTT for communication, so an MQTT server must
be available. The easiest solution is to use HBMQTT, which is a
Python based broker. It can be installed with PIP.

#### Conventions

- All static content (such as plain html and css files!) must be located in ./static
- Jinja2 must be located in ./template
- Create packages for all subfolders
- Don't use capital letters for packagenames!

## Tests

- All tests shall be put into the correspondings "/tests" folder for each subproject.
- We're using pytest, so we're bound by the conventions of pytest, i.e.:
  - All tests must be located in files prefixed with test_
  - All tests must start with test_, e.g. test_someFunction_does_something
- To run the tests "python -m pytest" in the root of the subproject.

## environment

## create new environment (conda)

```Console
conda init   // once you initialize conda in your custom terminal using
             // this command or
             // you are using conda terminal you don't need to run it again
conda create -n env_name python=3.7
```

## activate environment

```Console
conda activate env_name
conda config --append channels conda-forge
```

## deactivate environment

```Console
conda deactivate
```

## Installation Instructions

Semi-ATE has some external dependencies, that need to be installed beforehand. To install the requirements open a terminal
in the Semi-ATE root folder and activate the previously created environment.

## Install Requirements

```Console
conda install --file requirements/run.txt
```

if any of the required packages could not be installed via conda, an other package manager (pip) could be used

## Install Semi-ATE packages (ATE, TES)

At this point all components live in the same folder and can be installed as one package

```Console
python setup.py develop
```

## Install Reference Plugin

```Console
cd Plugins/TDKMicronas
python setup.py install
```

## Installing Spyder

We need a recent (5.x) version of Spyder. As of the time of writing(2020/08/21), only a beta version of the 5.x series exists,
which is not available via conda, therefore we need to clone from the Spyder github repository. This checkout should be done
into its own directory, seperate from the Semi-ATE directory.

Open a terminal and navigate to an empty folder. Then issue the following command:

```Console
git clone https://github.com/spyder-ide/spyder.git
```

## Install Spyder Dependencies

Activate the previously created environment

```Console
conda install spyder
```

## Running Spyder

To launch the Spyder IDE navigate to the Spyder folder and activate the previously created environment, then run the following
command:

```Console
cd spyder
python bootstrap.py
```

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
    // the following fields are information to simulate a test-program execition
    "Handler": "HTO92-20F",
    "environment": "F1",
    "jobsource": "filesystem",
    "jobformat": "xml.micronas",
    "filesystemdatasource.path": ".",
    "filesystemdatasource.jobpattern": "le306426001_template.xml",
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
