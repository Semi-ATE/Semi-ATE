# Semi-Ate.org Actuator Control

* An actuator is always controlled by a program, that listens to a given mqtt Topic. 
* We can have multiple instances of the program. 
* Each instance shall use slightly different topics.

Use Case I: A single actuator
We have a single actuator of a given type in our testcell. The tester will use this actuator to control environmental aspects
of the testcell. 

Use Case II: Multiple actuators
We have multiple actuators of different types in our testcell. The tester will use these actuators to control different environmental aspects
of the testcell. 


Use Case III: Mutliple actuators of the same type.
We have multiple actuators of the same type in our testcell. Each tester has its own set of actuators.
Note, that we do not need multiple actuators of the same type per teststation/tester.


## The IOCtl Protocol
The Master <-> Testprogram interface for actuators is based on controlcodes with parameters, such as:

```json
{
    "type": "io-control-request",
    "periphery_type": "fluxcompensator",
    "ioctl_name": "set_output",
    "parameters": {
        "param0": 100,
        "timeout": 5.0
    }
}
```

The masterapplication synchronizes access to actuators among all members of the same testergroup, i.e. The actuator will only
be controlled, once all testers have sent the same of the IOCtl they want to use. Once the this has happened the master shall
post the io-control-request as received from the sites to the topic:

ATE/\<deviceid>/fluxcompensator/io-control/request

-> Each running actuator service shall be aware of the device id it caters to. As soon as it receives a request on the mentioned
topic it shall perform the required action and send the result on the topic:
ATE/\<deviceid>/fluxcompensator/io-control/response

The response shall have the following form:

```json
{
    "type": "io-control-response",
    "ioctl_name": "set_output",
    "result": {
        /* Data */
    }
}
```

The result field shall *at least* contain the following two fields:
* status: Encodes wether or not the call was successful. In case of success this field shall always have the value "ok" and "timeout" if the operation timed out. Other values (i.e. errors!) are implementation defined.
* error_message: The error message shall contain a human readable reason why a call failed. This field is optional, if status is "ok"
* Note, that the master will not relay the result of the io-control back to the testprogram. The testprogram itself must watch the actuator's responsetopic!

### Startup & shutdown
During startup the actuator shall observer the master application's statustopic and send a message advertising its existence
to ATE/<deviceid>/<actuatortype>/status as soon as it receives a status message from the master.
with the following form:
```json
{
    "status": "available"
}
```

Further: The actuator shall instruct the broker to post a last-will message of the following form:
```json
{
    "status": "crashed"
}
```
__Note__ This message is used to automatically notify the master in case of a crash of the actuator application. If the
actuator shuts down gracefully (however that happens!), if shall replace the last-will message with:
```json
{
    "status": "terminated"
}
```

The master will - as soon as it receives any of the previous two messages - no longer allow any tests to commence.

## IOControl Codes
All actuator classes define their own set of controlcodes, depending on the type of service the actuator provides. 

### Generic
Apart from these codes, each actuator shall implement the following IOControl codes:

#### Dry Call
The "Dry Call" represents a sanity check, in as far as that the sending program asks the actuatorimplementation, wether or not
it is able to perform a call with a given set of parameters. This functionality can be used to check wether a given testprogram
can be executed in a meaningful way on a given setup. E.g.: If a testprogram requires an actuator to produce 500 mA of current,
but the actuator can only produce 250 mA this testprogram would be incompatible with the respective environment. Upon receiving
a drycall request, the actuatorimplementation shall check if the parameters and the provided ioctl could be made into an actual
call. Note that the actuator shall *not* perform that call.

```json
{
    "type": "io-control-drycall",
    // These lines are the same, as with the actual call
    "ioctl_name": "set_field",
    "parameters": {
        "millitesla": 100,
        "timeout": 5.0
    }
}
```

Response: 
```json
{
    "type": "io-control-drycall-response",
    "ioctl_name": "set_field",
    "result": {
        "status": {"ok" | "bad_ioctl | missing_parameter |badparamvalue | error"},
        <optional> "error_message": "some string"
    }
}
```
Explaination of status codes:
* done: Magfield set to the specified value.
* badioctl: The iocl_name is not supported by the actuator
* badparamvalue: At least one of the given parameters is in some way invalid. The actuator implementation shall provide an errormessage indicating the bad parameter.
* error: An unspecified error has occured. The actuatorimplementation shall provide an errormessage indicating the source of the error.

Attention: The actuatorimplementation can never guarantee, that a given call will be successful, as such, a drycall can only verify, that the provided parameters are within the expected bounds and that the call is probably legal with respect to the actual actuator implementation.

### MagField

#### Set Field
The set field command shall enable the magnetic field and set its strength to the given value. Setting the strangth to 0 millitesla shall not disable the device but instead use it to create a "true" 0 millitesla field (taking into account earths magnetic field!)


```json
{
    "type": "io-control-request",
    "ioctl_name": "set_field",
    "parameters": {
        "millitesla": 100,
        "timeout": 5.0
    }
}
```

Response: 
```json
{
    "type": "io-control-response",
    "ioctl_name": "set_field",
    "result": {
        "status": {"ok" | "badfieldstrength"},
        <optional> "error_message": "some string"
    }
}
```

Explaination of status codes:
* done: Magfield set to the specified value.
* badfieldstrength: The provided fieldstrength denotes a value that is either invalid or cannot be produced by the concrete actuator.

#### Disable Field
The disable field command shall physically disable the magnetic field (i.e. the powersource shall be disabled).

```json
{
    "type": "io-control-request",
    "ioctl_name": "disable",
    "parameters": {
        "timeout": 5.0
    }
}
```

Response: 
```json
{
    "type": "io-control-response",
    "ioctl_name": "disable",
    "result": {
        "status": {"ok" | "error"},
        <optional> "error_message": "some string"
    }
}
```

Explaination of status codes:
* done: Magfield was disabled.
* error: An unspecified error has occured. In this case the error_message field shall be present to provide context. *Attention* : If an error occured the actuator might not have been able to disable the field.


#### Program Curve
The program curve io command shall instruct the actuator to store a given curve of field strengths. The curve is presented as array of tuples, where the first value of the tuple denotes the field strength and the second value denotes the time for which this strength should be kept.

```json
{
    "type": "io-control-request",
    "periphery_type": "magfield",
    "ioctl_name": "program_curve",
    "parameters": {
        "id": 0,
        "hull": [{val0, duration0},{val1, duration1}],
        "timeout": 5.0
    }
}
```

Result:

```json
{
    "type": "io-control-response",
    "ioctl_name": "program_curve",
    "result": {
        "status": {"ok" | "invalidid" | "error"},
        <optional> "error_message": "some string"
    }
}
```

Explaination of status codes:
* done: The curve has been stored
* invalidid: The provided curve id is invalid (depending on the actuator implementation it might be outside of the range of permitted ids)
* error: An unspecified error has occured. In this case the error_message field shall be present to provide context.



#### Play curve
The play curve command shall instruct the actuator (or the softwareimplementation) to playback a previously programmed curve. This function has no overridable timeout, but shall instead only timeout 2 seconds after the curve should have completed.

```json
{
    "type": "io-control-request",
    "ioctl_name": "play_curve",
    "parameters": {
        "id": 0
    }
}
```

Result:

```json
{
    "type": "io-control-response",
    "ioctl_name": "play_curve",
    "result": {
        "status": {"ok" | "unknown"}
    }
}
```

Explaination of status codes:
* done: The requested curve has been played back. The magfield is now switched off
* unknown: The requested curve id is unknown.

Notes:
* After a curve has been played the actuator shall always disable the magnetic field.

#### Play curve stepwise
The play curve stepwise function shall instruct the actuator to playback a previously defined curve, while waiting for explicit instructions to switch between different points of the curve. When a curve is played using this function the duration value for each curvepoint shall be ignored.

```json
{
    "type": "io-control-request",
    "ioctl_name": "play_curve_stepwise",
    "parameters": {
        "id": 0
    }
}
```


Result:

```json
{
    "type": "io-control-response",
    "ioctl_name": "play_curve_stepwise",
    "result": {
        "status": {"ok" | "unknown"}
    }
}
```

Explaination of status codes:
* ok: The requested curve has been started, the first curve point has been applied.
* unknown: The requested curve id is unknown.

#### Curve step
The curvestep function shall instruct to move to the next curvepoint in a currently running stepwise playback. The step shall be performed immediately and shall ignore any timing settings of the curve.

```json
{
    "type": "io-control-request",
    "ioctl_name": "curve_step",
    "parameters": { }
}
```

Result:

```json
{
    "type": "io-control-response",
    "ioctl_name": "curve_step",
    "result": {
        "status": {"ok" | "done" | "notplaying"}
    }
}
```

Explaination of status codes:
* ok: The step was performed, the curve has further steps.
* done: The curve has playe back its last point and can not proceed any further. Magfield is now switched off.
* notplaying: There is currently no playback active.

Notes:
* Emitting a curve_step command, after receiving status "done" shall cause the actuator implementation to return status "notplaying"
* Emitting a curve_step command, after receiving status "notplaying" shall cause the actuator implementation to return status "notplaying".
* Reaching the "done" state shall cause the actuator to disable the magfield.


#### Curve stop
The curve_stop function shall abort a stepwise playback of a curve and disable the magfield.
```json
{
    "type": "io-control-request",
    "ioctl_name": "curve_stop",
    "parameters": { }
}
```

Result:

```json
{
    "type": "io-control-response",
    "ioctl_name": "curve_stop",
    "result": {
        "status": {"ok" | "notplaying"}
    }
}
```

Explaination of status codes:
* ok: The curve playback was aborted and the magfield is now disabled
* notplaying: There is currently no playback active.


## Former part of plugin spec -> rework

### Actuators
```
get_actuator(required_capability) -> ActuatorInstance
get_actuator_proxy(required_capability) -> ActuatorInstance
```

This hook shall return an instance of an actuator that provides the required capability. This hook is intended for use in tests only. If the environment cannot resolve the service (e.g. because none is available) it shall *immediatly* throw an exception containing the missing capability. Do not return None in this case as it makes diagnostics harder than a well thought out error string.

A note on actuator capabilities: The capabilities are stored by the runtime environment. If a test asks for an actuator that provides a given capability, the test environemt shall find actuator that best matches this request, taking into account:
* The physical hardware on which the test is running
* The available actuators
* The physical location & connection of the actuators

The master application uses the ```get_actuator``` hook to obtain an actuator providing the required capability. It assumes
the following interface for the returned object:
```
    init(mqtt_client)
    async device_io_control(ioctl_name, data) -> Option[Data]
    close()
```

The masterapplication will lazily initialize an actuator, when it is first required, by calling init. Whenever an iocontrol
request is sent by one of the connected testprograms the master will wait until all testprograms have sent the same request.
Once this happend, it will call device_io_control for the actuator in question, using the parameters sent with the first call
as ```data``` parameter and returning any non-none value to the callers.

__Attention__ device_io_control is required to be a python __async__ function and the master app will await on this function. This means, that
device_io_control must *never* block, as this will cause the masterapp's mqtt connection to stall forever. 
A canonical way to implement a device_io_control that does not return immediately and waits for *something* to happen would be:
```
class peripheral:
    def __init__(self):
        self.event = asyncio.Event()

    def init(self, mqtt_client):
        pass

    async def device_io_control(self, ioctl_name, data):
        await self.event.wait()
        return "Done"

    def on_event_happened(self):
        self.event.set()
```

implementing the client side of an actuator is similar to the masterside, as it also involves async code. The codegenerator
assumes, that all actuatorproxies provide a set_mqtt_client function through which a reference to the testprogram's mqtt client
can be set.

#### Using mqtt in actuators
If the actuator implementation needs to use mqtt it should use the __init__ call to subscribe to any relevant topics. For the internal routing to work correctly the peripheral will have to call "register_route" as well.

__Note__: Actuators will only be unloaded, once an unload command is issued to the master application. The masterapp will call close on all actuators, that were previously loaded. The peripheral is expected to unsubscribe from mqtt and to deregister all routes.

Example
```
    class mqtt_peripheral():
        def __init__(self):
            self.event = asyncio.Event()
            # Always store the actual lambda/callback to use for registration
            # and unregistration. Don' use ad-hoc lambdas as this will
            # always create a new lambda and cause the instance of the peripheral
            # to never be released due to it being kept alive by the lambdas.
            self.message_cb = lambda topic, payload: self.on_message_received
        
        def init(self, mqtt_client):
            self.mqtt_client = mqtt_client
            mqtt_client.subscribe("SomePeripheral/command")
            mqtt_client.register_route("SomePeripheral/command", self.message_cb)
        
        def on_message_received(self, topic, payload):
            # This code is called whenever a message arrives on "SomePeripheral/command"
            self.event.set()
        
        async def device_io_control(self, ioctl_name, data):
            await self.event.wait()
            return "Done"

        def unload(self):
            self.mqtt_client.unsubscribe("SomePeripheral/command")
            mqtt_client.unregister_route("SomePeripheral/command",self.message_cb)
  
```


## The IOCtl Protocol Master <-> Testprogram
ATE/\<deviceid>/TestApp/peripherystate/<siteid>/request
