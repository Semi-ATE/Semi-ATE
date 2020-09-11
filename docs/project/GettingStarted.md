# Getting Started with ATE Dev

## Install Prerequisites
Install Python 3 (at least 3.7) and PIP, run setup.bat

### MQTT
The components use MQTT for communication, so an MQTT server must
be available. The easiest solution is to use HBMQTT, which is a
Python based broker. It can be installed with PIP.

### Command: pip install #package
### Master
### Control
- Install pytest
- Install pytest-mock
- Install paho-mqtt

### UI
- Install aoihttp
- Install aoihttp_jinja2
- Install pytest
- Install pytest-mock
- Install paho-mqtt

#### Conventions
- All static content (such as plain html and css files!) must be located in ./static
- Jinja2 must be located in ./template
- Create packages for all subfolders
- Don't use capital letters for packagenames!

# Tests
- All tests shall be put into the correspondings "/tests" folder for each subproject.
- We're using pytest, so we're bound by the conventions of pytest, i.e.:
    - All tests must be located in files prefixed with test_
    - All tests must start with test_, e.g. test_someFunction_does_something
- To run the tests "python -m pytest" in the root of the subproject. 

# Device Provisioning
## Install Prerequesites
## Configure Master
## Configure Control
## Configure UI
