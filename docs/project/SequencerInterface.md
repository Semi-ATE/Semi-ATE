# ATE Sequencer Specification

## Intro
The sequencer is a piece of software that controls how a given set of tests ("testprogram") is executed within the ATE runtime. The sequencer serves as the entrypoint into the ATE testharness, i.e. it synchronizes with the other members of the system.

## API as seen by the ATE Runtime
The sequencer is visible to two parts of the ATE Runtime: Control and Master.

### Control
Control will launch the testprogram (and with that the sequencer) using the following commandline options:

* '--device_id', containing the device ID of the device on which the programm is started
* '--site_id', containing the site_id for the site (in case of a standalone MiniSCT this is always 0)
* '--broker_host', containing the IP address of the associated MQTT broker
* '--broker_port', containing the port of the MQTT broker
* '--parent-pid', containing the process ID of the MQTT broker

The testprogram shall pass all these parameters to the sequencer and the sequencer shall do the following:
* Connect to the broker on the provided IP/Port
* Subscribe to the topic \<device-id>/TestApp/cmd
* Post a statusmessage to \<device-id>/TestApp/status/site\<site-id> containing status "idle"

### Master
After the master has received the "idle" state it will assume that the testprogram is ready to do it's duty. As soon as the master receives a test command (by means beyond the scope of this document) it will post a "Next" command to the TestApp/cmd topic, This message contains the sites that are supposed to do the actual testing as well as test options. The sequencer shall:
* Check if it is supposed to execute a test by means of checking the "sites" list for its own site-id.
* Emit a statusmessage containing the status "testing"
* Start the test using the provided parameters.

### Testoptions
Whenever the master emits a "Next" command it will append any usersettings to the command as a Key-Value dataset. These settings include
* Trigger On Test#
* Stop On Fail Setting
* Trigger On Fail Setting

and more. The master expects the testprogram to pay heed to these settings. Since the master sends these settings with every "Next" the testprogram/sequencer must be able to deal with "suddenly" changing settings.

## The Runtime as seen by the sequencer
Each and every instrument/actuator is either controlled by the TCC or the master.

### Proxies/Shims
All additional devices will usually be either controlled by the master or by an instance even higher up in the hierarchy. This means, that the testprogram will usually not be able to directly influence the behavior of such a device, instead it will have to send requests to the master which will - depending on the peripheral in question - either control the peripheral or relay the request to the next higher instance (i.e. TCC). In order to provide a readable and ergonomic interface for the test each peripheralimplementation shall come in two flavours:
* A proxy class that provides an easy to use interface for the test, but will - in the background - translate methodcalls to mqtt requests and block until the request has been fulfilled
* A concrete implementation, that will actually implement the interface to the peripheral.

The proxy will be instanciated for each testprogramm (common.py), whereas the actual implementation will run on the master.

Example:
Suppose we have an object called the "K2000", which can be activated or deactivated. In the test we'd like an interface similar to the following:

```
k2000 = pluggy.get_proxy("k2000")
k2000.activate()
```

The proxy side of the activate method would be as follows:

```
activate(self):
    mqttclient.send("{cmd:activate"})
    mqttclient.wait_response("activate")
```

Whereas the code on the master would be:

```
resource = pluggy.get_instance("k2000")
resource.activate()


class k2000(object):
    activate(self):
        hdl = open("dev/tty0/")
        write(hdl, "do stuff)
```

To enable this behavior the hookspec for an ATE.org Plugin is changed as follows:
```
get_plugin_identification() -> plugin_ident
get_importer_names() -> []
get_exporter_names() -> []
get_equipment_names() -> []
get_devicepin_importer_names() -> []
get_actuator_names() -> []
get_instrument_names() -> []

get_importer(plugin_name, importer_name) -> Importer
get_exporter(plugin_name, exporter_name) -> Exporter
get_equipment(plugin_name, equipment_name) -> EquipmentInstance
get_devicepin_importer(plugin_name, importer_name) -> Importer

get_actuator(plugin_name, actuator_name) -> ActuatorInstance
get_actuator_proxy(plugin_name, actuator_name) -> ActuatorProxy

get_instrument(plugin_name, instrument_name) -> InstrumentInstance
get_instrument_proxy(plugin_name, instrument_name) -> InstrumentProxy
```

The get_xx_proxy implementations shall be used by the testprogram to obtain a proxy implementation, whereas the get_xx implementations shall be used by the controlling instance (i.e. the master) to obtain actual implementations when the testprogram sends a request by proxy.
Note: Structuring the hookspec this way allows use to also use concrete implementations of actuators/instruments in the tests, should the need arise. In fact, one could go as far as to only generate testcode that uses proxies for hardwaresetups where parallelism is > 1.

### Testresults & Testend
The sequencer is free to send testresult as fragments at any time during a testrun. Sending a testresult is archieved by posting an mqtt message to "ate/\<device-id>/TestApp/stdf/sitesite\<site-id>" containing the STDF data encoded as Base64 string.

After the complete testprogram has run its course, i.e. all tests for the dut in question have either passed or the testing was stopped due to a test failing, the testprogramm shall change its state to "idle", indicating, that it is ready to test the next dut.

Note: As soon as the sequencer changes its state from "testing" to "idle" the master may begin to process the testresults received by that point. Any testresults emitted after this statetransition will cause a system error (this is by design, as it hints at a testprogram that does not behave as expected!).

Also Note: The sequencer is expected to deliver a testresult within 15 seconds. This is currently not a configurable value.

## Errorhandling & Teardowns
The runtime employs several layers of errorhandling, which are applied differently depending on the concrete situation.

### Teardowns
The sequencer can use two different usersupplied teardown functions.
* Testprogramteardown: This callback is called right before the testprogram terminates. Signature:
``` def program_teardown(ctx: Context) ```
* Aftercycleteardown: This callback is called after each testcycle, i.e. everytime a DUT has finished testing. Signature:
``` def cycle_teardown(ctx: Context, has_error: bool) ```

__Note__: A testprogram generated by the the sammy buildtool will always be accompanied by a file called *\<testprogramname>_teardown.py* which already contains blank implementations for the two teardowns. These implementations are automatically wired into the testprogram by the buildtool.

### During startup
Any exception triggered during startup will cause the sequencer to report an error to the master, resulting in the master entering the error state. Afterwards the sequencer will call the testprogram teardown and terminate.

### During testexecution
The sequencer will catch all exceptions that are thrown by tests. A test that raises an exception will be treated as failed.
If an error is so severe, that the testprogram crashes altogether (e.g. a segfault in a nativ library), the master will enter the error state and execute the Ioctl "Teardown" for all actuators. 

__Note__: In case of a segfault no teardown code will be called, as the operating system will most likely terminate the python interpreter right away. Caught exceptions will trigger the sequencer to notify the Afercycleteardown with the "has_error" flag set to true.

### Batch End
The master may - at any time when no testing is in progress - send a "Terminate" command. The testprogram/sequencer shall cease execution and exit upon receiving this command. The sequencer will call the testprogramteardown callback. It will further advertise a clean shutdown by publishing the state "Shutdown", after the teardowncode for the running testprogram has been executed.

The master will execute the Ioctl "Teardown" for all actuators after all testprograms have terminated
