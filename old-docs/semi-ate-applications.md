# Semi-ATE in Production

This document describes how you can install the semi-ate applications to run test-programs in production mode. You will be guided how to install the required *conda packages*, to configure the applications and to generate a job-file.

We assume the following:

* You have [maxiconda](https://www.maxiconda.org/) installed
* You are running *Windows 10 64Bit*
* You have already downloaded or generated some test program - via spyder - in folder *C:\\%UserProfile%\project\src\HW0\PR\project_HW0_PR_die_production_prod.py*. The underlying hardware used when creating the semi-ate test project was *Semi-ATE Single Tester*.
* All provided commands are executed in a **PowerShell**.
* The windows user's name is **test_user**, i.e. variable `$env:Username` is pointing to **test_user**. The user name is used to build paths. These paths are defined in the later mentioned configuration and job files. You have to adapt it to match your environment.

## Requirements

* [Generate a fresh *mamba environment*](#create-mamba-environment)
* [Install and Start MQTT-Broker](#mqtt-broker)
* [Install Semi-ATE applications and Testers](#semi-ate-applications-and-testers):
  * Download and unzip web user interface aka. [*msct_webui*](#download-web-user-interface)
  * master application and a suitable configuration file (*master_config_file.json*)
  * control application and a suitable configuration file (*control_config_file.json*)
  * test application
* [JOB-File](#create-xml-job-file)

### Create Mamba Environment

* Creation `mamba create -n _app_py39_ python=3.9 -y`
* Environment Activation `conda activate _app_py39_`

### MQTT-Broker

* Environment Activation `conda activate _app_py39_`
* Installation `mamba install -c conda-forge mosquitto -y`
* Running Mosquitto-Broker `&(Join-Path $env:USERPROFILE maxiconda\envs\_app_py39_\Library\sbin\mosquitto) -v`

### Semi-ATE Applications and Testers

* Environment Activation `conda activate _app_py39_`
* Installation `mamba install -c conda-forge semi-ate-master-app semi-ate-control-app semi-ate-test-app semi-ate-testers -y`

#### Download Web-User-Interface

On [MSCT-WebUI-Releases](https://github.com/Semi-ATE/MSCT-WebUI/releases) download *msct-webui-X.X.X.zip*. Unzip the archive. It should create a folder named *msct-webui*.

#### Configurations

Create the following files:

1. master_config_file.json:

  ```JSON
  {
    "broker_host": "127.0.0.1",
    "broker_port": 1883,
    "device_id": "SCT",
    "sites": [
        "0"
    ],
    "Handler": "Handler",
    "environment": "F1",
    "webui_host": "127.0.0.1",
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
    "tester_type": "Semi_ATE Master Single Tester",
    "loglevel": 10
  }
  ```

2. control_config_file.json:

  ```JSON
  {
    "broker_host": "127.0.0.1",
    "broker_port": 1883,
    "device_id": "SCT",
    "site_id": "0",
    "loglevel": 10
  }
  ```

### Create XML Job File

Create the job file *le123456000.xml* with the following content:

```XML
<PROBE_FINAL_TEST>
    <MAIN>
        <MATCHCODE>DMSENSOR3FHRFUZ7U</MATCHCODE>
        <LOTNUMBER>123456.000</LOTNUMBER>
        <PACKAGEID_SHORT>UZ</PACKAGEID_SHORT>
    </MAIN>
    <CLUSTER>
        <TESTER>SCT</TESTER>
        <TESTER_ALIAS>SCT_1</TESTER_ALIAS>
        <HANDLER_PROBER>Handler</HANDLER_PROBER>
        <HANDLER_PROBER_ALIAS></HANDLER_PROBER_ALIAS>
        <NADELKARTE></NADELKARTE>
        <PINELEKTRONIK></PINELEKTRONIK>
        <RUESTSATZ></RUESTSATZ>
    </CLUSTER>
    <TESTPROGRAM>
        <EXEC_OPTIONS></EXEC_OPTIONS>
    </TESTPROGRAM>
    <HANDLERSECTION>
        <TEMP1></TEMP1>
    </HANDLERSECTION>
    <PAT>
        <PAT_RECIPE></PAT_RECIPE>
    </PAT>
    <STATION>
        <STATION1>
            <USERTEXT1>F1N</USERTEXT1>
            <TEMP1>25</TEMP1>
            <TESTERPRG1>825A</TESTERPRG1>
            <!-->
            Adapt the value of the next XML tag in such a way that it points to the desired test program
            <-->
            <PROGRAM_DIR1>C:\Users\test_user\project\src\HW0\PR\project_HW0_PR_die_production_prod.py</PROGRAM_DIR1>
            <TESTER1>SCT</TESTER1>
            <TESTER_ALIAS1>SCT_1</TESTER_ALIAS1>
            <BINTABLE1>
            <ENTRY SBIN="1"     HBIN="1"  SBINNAME="SB_GOOD1"     GROUP="BT_PASS"           DESCRIPTION="Our best choice"/>
            <ENTRY SBIN="12"    HBIN="12" SBINNAME="SB_CONT_OPEN" GROUP="BT_FAIL_CONT"      DESCRIPTION="Open Contacts"/>
            <ENTRY SBIN="20"    HBIN="13" SBINNAME="SB_IDD"       GROUP="BT_FAIL_ELECTRIC"  DESCRIPTION="Current Consumption"/>
            <ENTRY SBIN="22"    HBIN="42" SBINNAME="SB_THD"       GROUP="BT_FAIL_ELECTRIC"  DESCRIPTION="Total Harmonic Distortion"/>
            <ENTRY SBIN="60000" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="60001" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="13"    HBIN="12" SBINNAME="SB_THD"       GROUP="BT_FAIL_ELECTRICA" DESCRIPTION="Total Harmonic Distortion"/>
            <ENTRY SBIN="11"    HBIN="12" SBINNAME="SB_THD"       GROUP="BT_FAIL_ELECTRICA" DESCRIPTION="Total Harmonic Distortion"/>
            <ENTRY SBIN="60001" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="60002" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="60003" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="60004" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            <ENTRY SBIN="60005" HBIN="0"  SBINNAME="SB_SMU_ALARM" GROUP="BT_ALARM"          DESCRIPTION="SMU Compliance Warning"/>
            </BINTABLE1>
        </STATION1>
    </STATION>
    <DIEELEMENT_COUNT>1</DIEELEMENT_COUNT>
    <DIEELEMENT>
        <DIEELEMENT_NUMBER>1</DIEELEMENT_NUMBER>
    </DIEELEMENT>
</PROBE_FINAL_TEST>
```

## Starting the Applications

In order to successfully run the applications we assume that all previous sections of this document have been applied:

1. Activate the conda environment `conda activate _app_py39_`
2. Make sure that the current location contains the following files and folders:
    * Master application configuration *master_config_file.json*, refer to [Configurations](#configurations)
    * Control appliation configuration *control_config_file.json*, refer to [Configurations](#configurations)
    * The job file *le123456000.xml*, refer to [Create XML Job File](#create-xml-job-file)
    [Configurations](#configurations)
    * The web-ui folder *msct-webui*, refer to [Download Web-User-Interface](#download-web-user-interface)
3. Make sure that some MQTT-Broker is running, refer to [MQTT-Broker](#mqtt-broker)
4. Run master application by doing the following:

    ```Powershell
    > launch_master
    ======== Running on http://127.0.0.1:8081 ========
    (Press CTRL+C to quit)
    master   |22/06/2022 11:10:02 AM |INFO    |mqtt connected
    master   |22/06/2022 11:10:02 AM |INFO    |Master state is connecting
    ```

5. Run master control application by doing the following:

    ```Powershell
    > launch_control
    control 0|22/06/2022 11:11:20 AM |INFO    |mqtt connected
    control 0|22/06/2022 11:11:20 AM |INFO    |control state is: idle
    ```

6. Open some web browser and navigate to [http://127.0.0.1:8081](http://127.0.0.1:8081)
7. In the browser navigate to the control tab and load the lot by providing the number **123456.000** in the load lot handling control.
8. Next you can click on button *Start DUT-Test* in the Header.
