## Setup

### Presumed network:

![image](https://user-images.githubusercontent.com/3516972/197995910-c7597d2f-8ab4-49ec-bb0e-c23ff92f3da4.png)

### Installation on system level

Goto `https://github.com/Semi-ATE/STIL-Tools/releases` and download the latest `.deb` file (sct8-stil-loader_VERSION_arm64.deb) to the home directory of the `sct` user

```
(base)~$ sudo apt install mosquitto
...
(base)~$ sudo dpkg -i sct8-stil-loader_VERSION_arm64.deb
...
```

### Installation on (conda) environment level

```
(base)~$ mamba create -n Semi-ATE python=3.9 spyder=5.3.0
(base)~$ conda activate Semi-ATE
(Semi-ATE)~$ mkdir -p ~/repos/Semi-ATE
(Semi-ATE)~$ cd ~/repos/Semi-ATE
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/Semi-ATE.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/TCC_actuators.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/SCT8-ML.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/STIL-Tools.git
(Semi-ATE)~/repos/Semi-ATE$ cd Semi-ATE
(Semi-ATE)~/repos/Semi-ATE/Semi-ATE$ python scripts/package_tool.py --change-env cicd
...
(Semi-ATE)~/repos/Semi-ATE/Semi-ATE$ cd src/ATE_spyder/ate_spyder_lab_control 
(Semi-ATE) sct@sct8:~/repos/Semi-ATE/Semi-ATE/src/ATE_spyder/ate_spyder_lab_control$ pip install -e .
... 
(Semi-ATE) sct@sct8:~/repos/Semi-ATE/Semi-ATE/src/ATE_spyder/ate_spyder_lab_control$ cd ~/repos/Semi-ATE/TCC_actuators
(Semi-ATE)~/repos/Semi-ATE/TCC_actuators$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/TCC_actuators$ cd ../SCT8-ML
(Semi-ATE)~/repos/Semi-ATE/SCT8-ML$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/SCT8-ML$ cd STIL-Tools
(Semi-ATE)~/repos/Semi-ATE/STIL-Tools$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/SCT8-ML$ mamba install semi-ate-stil
...
(Semi-ATE)~/repos/Semi-ATE/STIL-Tools$ mamba install h5py 
...

```

Note: you should have your personal access token from github handy (you will need it)

# Setup (optional - if Semi-control can do what master does -)

```
(base)~$ mkdir master_control
(base)~$ cd master_control
(base)~/master_control$  echo "{
        "broker_host": "127.0.0.1",
        "broker_port": 1883,
        "device_id": "SCT-81-1F",
        "sites": [
                "0"
        ],
        "Handler": "HTO92-20F",
        "environment": "F1",
        "webui_host": "192.168.1.2",
        "webui_port": "8081",
        "webui_root_path": "./msct-webui",
        "jobsource": "filesystem",
        "jobformat": "xml.semi-ate",
        "skip_jobdata_verification": false,
        "filesystemdatasource_path": ".",
        "filesystemdatasource_jobpattern": "le123456000.xml",
        "enable_timeouts": true,
        "user_settings_filepath": "master_user_settings.json",
        "site_layout": [[0, 0]],
        "tester_type": "DummyMasterSingleTester",
        "loglevel": 10,
        "develop_mode": true
}" > master_config_file.json

```
then download the ZIP file from : https://github.com/Semi-ATE/MSCT-WebUI/releases (msct-webui-x.y.z.zip)
unpack the zip file and move the directory `msct-webui` to the `~/master_control` directory.


# Running (in Spyder)

### 1. Start Master

```
C:> ssh sct@sct8
(base)~$ conda activate Semi-ATE
(Semi-ATE)~$ cd master_control
(Semi-ATE)~/master_control$ launch_master
...
```

### 2. Start the TCC_actuator

```
C:> ssh sct@sct8
(base)~$ conda activate Semi-ATE
(Semi-ATE)~$ magfield-stl 192.168.1.2 1883 developmode 192.168.1.1 21324
```
Note :  192.168.1.2 = broker IP address

### 3. Start Spyder

use GWSL to connect to the sct8 (with X forwarding) then :

```
(Semi-ATE)~$ spyder
```
