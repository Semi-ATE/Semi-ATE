# ATE.org Plugins
This document describes the Plugin Api (or "hookspec" in pluggy terms) of an ATE.org plugin.

Each ATE.org Plugin provides means to access its contents in different forms. Most notably:
- Identification of contents
- Instances of contents

## Design Rationale
The API Design in this document tries to take into account the way the IDE is structured as well as the way Pluggy works. We focus on the following points:
* Ease of integration
* Flexibility
* Extensibility

## Identification
We use the "identification" functions to discover the functionality provided by a given plugin. The plugin shall provide a number of functions, that allow us to query that functionality.

### Plugin
```
get_plugin_identification() -> plugin_ident
```
This hook shall return a dictionary with the following layout:

```
    name: "Plugin Name"
    version: "Plugin Version"
```

### Plugin Functionality
A given plugin publishes its functionality by means of Importers/Exporters/Actuators/Instruments/Equipments. Each of these can be queried by means of a "get_x_names" function where x is the name of the respective functionality. The returnvalue of the get_x_names functions is always a list of dictionaries, where each dictionary has the following layout:
```
    display_name: "Display Name"
    version: "Object Version"
    name: "Object Name"
```
Where:
* display_name denotes the string, that is used to display the the object in the ATE.org UI.
* Version denotes the Version of the code, that is used for the respective object
* Name: Denotes the actual internal name by which the object is identified within the plugin. The plugin must be able to return an instance of the object when the get_x hook is called with the string name as x_name parameter. Note that the object name must be unqique across all plugins. Therefore it is advisable to prefix the objectname with the pluginname. E.g:
* Plugin: TDK.Micronas
* Object: CSVFileImporter
* Name: TDK.Micronas.CSVFileImporter



#### Importers
An importer is an object that is able to import a wafermap from a given (importer-specific) datasource and in a given format. E.g. ther might be an importer that imports data as .CSV value from a database.

```
    get_importer_names() -> []
```

#### Exporters
An exporter is an object that is able to export a wafermap from to a given (exporter-specific) datasink and in a given format. E.g. ther might be an exporter that export to .CSV.

```
    get_exporter_names() -> []
```

#### Equipments
An equipment object is used to access the specific functionality of prober or handler.
```
    get_equipment_names() -> []
```

#### Devicepin Importer
A devicepin importer is used to import the pinset, that is accessible for a given device.
```
    get_devicepin_importer_names() -> []
```


#### Actuators
An actuator is a piece of hardware, that controls some aspect of the test environment (e.g. magenetic field). In addition to the common layout as specified above, each actator will also return a list of "services", that actuator provides. These services are plain strings and are used by the ATE runtime to resolve an actuator that can modify a defined aspect of the testenvironment.

```
    get_actuator_names() -> []
```

The complete layout of the results of this function is:
```
{
    display_name: "Display Name"
    version: "Object Version"
    name: "Object Name"
    capabilities: ("MagField", "Temperature")
}
```

#### Instruments
An instrument is a piece of hardware, that is used to measure a given aspect of the DUT. It is usually used in a lab context.

```
    get_instrument_names() -> []
```

## Instances
All hooks that deal with the instanciation of objects are provided the name of the plugin that should actually create the instance. The reason is, that pluggy will call each hook for all registered plugins, so a call to "get_importer" will be executed for each plugin, using the same parameter. Since we want to avoid nameclashes of objects we must uniquely identify the actual type of object we want created. See the section on object names for this.

A note on dependencies:
Importers and exporters are allowed to depend on PyQt to provide their own UI, if necessary. Actuators, Instruments and Equiments should not depend on PyQt - these objects are created by testcases and usually used in a headless environment (i.e. the tester itself!)

### Importers

```
get_importer(importer_name) -> Importer
```

This hook shall return an instance of an importer with the given name.
An importer is expected to have the following interface:

```
    do_import() -> data
    get_abort_reason() -> string
```

The importer shall show it's own import dialog (which may well be just a file chooser!), perform the import and return the imported data in an - as of now - not yet specified format. If the import fails/is canceled do_import() shall not propagate any exception to the application, but instead return "None". The plugin shall expose the reason, why no data was returned when get_abort_reason is called.

### Exporters
```
get_exporter(exporter_name) -> Exporter
```
This hook shall return an instance of an exporter with the given name.

An importer is expected to have the following interface:
```
    do_export(data) -> bool
    get_abort_reason() -> string
```
The exporter shall show it's own export dialog (which may well be just a file chooser!) and perform the export. If the export fails/is canceled do_export() shall not propagate any exception to the application, but instead return ```False```. The plugin shall expose the reason, why no data was exported when get_abort_reason is called.

### Equipments
```
get_equipment(equipment_name) -> EquipmentInstance
```
This hook shall return an instance of a given equipment. The returned instance has no specified interface. This hook is intended for use in tests only.

If the plugin is unable to resolve the equipment name it shall *immediatly* throw an exception containing the missing equipment's name. Do not return None in this case as it makes diagnostics harder than a well thought out error string.

### Devicepins
```
get_devicepin_importer(importer_name) -> Importer
```
This hook shall return an instance of a given importer. The returned instance has no specified interface. This hook is intended for use in tests only.

If the plugin is unable to resolve the importer name it shall *immediatly* throw an exception containing the missing importer's name. Do not return None in this case as it makes diagnostics harder than a well thought out error string.

An importer is expected to have the following interface:
```
    do_import() -> data
    get_abort_reason() -> string
```

The importer shall show it's own import dialog (which may well be just a file chooser!), perform the import and return the imported data in an - as of now - not yet specified format. If the import fails/is canceled do_import() shall not propagate any exception to the application, but instead return "None". The plugin shall expose the reason, why no data was returned when get_abort_reason is called.

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




### Instruments
```
get_instrument(instrument_name) -> InstrumentInstance
get_instrument_proxy(instrument_name) -> InstrumentInstance
```
This hook shall return an instance of a given instrument. The returned instance has no specified interface. This hook is intended for use in tests only.

If the plugin is unable to resolve the instrument name it shall *immediatly* throw an exception containing the missing instrument's name. Do not return None in this case as it makes diagnostics harder than a well thought out error string.

## Configuration
At this point we assume, that no plugin will need any kind of central configuration and therefore no method of storing configuration data (e.g. in the project database) is specified for the plugin API.


## Complete Hookspec

```
get_plugin_identification() -> plugin_ident
get_importer_names() -> []
get_exporter_names() -> []
get_equipment_names() -> []
get_devicepin_importer_names() -> []
get_actuator_names() -> []
get_instrument_names() -> []

get_importer(importer_name) -> Importer
get_exporter(exporter_name) -> Exporter
get_equipment(equipment_name) -> EquipmentInstance
get_devicepin_importer(importer_name) -> Importer

get_actuator(required_capability) -> ActuatorInstance
get_actuator_proxy(required_capability) -> ActuatorProxy

get_instrument(instrument_name) -> InstrumentInstance
get_instrument_proxy(required_capability) -> InstrumentProxy
```

The hookspecmarker is "ate.org"


### As basic example plugin
The example in this chapter containes the most basic plugin possible.

__File__: PluginSrc\PluginB\\_\_init__.py
```
import pluggy
import hookspec.ate

class ThePlugin(object):

    @hookspec.ate.hookimpl
    def get_plugin_identification() -> dict:
        return {}

    @hookspec.ate.hookimpl
    def get_importer_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_exporter_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_equipment_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_devicepin_importer_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_actuator_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_instrument_names() -> []:
        return []

    @hookspec.ate.hookimpl
    def get_importer(importer_name) -> Importer:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_exporter(exporter_name) -> Exporter:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_equipment(equipment_name) -> EquipmentInstance:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_devicepin_importer(importer_name) -> Importer:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_actuator(required_capability) -> ActuatorInstance:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_actuator_proxy(required_capability) -> ActuatorInstance:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_instrument(instrument_name) -> InstrumentInstance:
        throw NotImplementedError

    @hookspec.ate.hookimpl
    def get_instrument_proxy(instrument_name) -> InstrumentInstance:
        throw NotImplementedError
```

### Plugin Installation
Plugins are installed by means of setuptools (Pluggy supports plugin discovery through setuptools entrypoints). For this to work we need a setup.py for each plugin:

__File__: PluginSrc\setup.py
```
from setuptools import setup
setup(
    name="SomeAtePlugin",
    install_requires="ate.org",
    entry_points={"ate.org": ["plug = PluginB:ThePlugin"]},
    py_modules=["PluginB"],
)
```