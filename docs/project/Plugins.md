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
A given plugin publishes its functionality by means of Importers/Exporters/Actuators/Instruments/Equipments/Testers. Each of these can be queried by means of a "get_x_names" function where x is the name of the respective functionality. The returnvalue of the get_x_names functions is always a list of dictionaries, where each dictionary has the following layout:
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


#### Instruments
An instrument is a piece of hardware, that is used to measure a given aspect of the DUT. It is usually used in a lab context.

```
    get_instrument_names() -> []
```

#### General Purpose Functions
General Purpose Functions are plugin functionality that needs to be available to tests, but that is not tied to a specific usage scenario. 

```
get_general_purpose_function_names() -> []
```

The complete layout of the results of this function is:
```
{
    display_name: "Display Name"
    version: "Object Version"
    name: "Object Name"
}
```

### Tester
The following function returns all installed testers use to be run beyond the MiniSCT, which will be used by the testprogram to synchronize the test execution
```
get_tester_names() -> []
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

### Instruments
```
get_instrument(instrument_name) -> InstrumentInstance
get_instrument_proxy(instrument_name) -> InstrumentInstance
```
This hook shall return an instance of a given instrument. The returned instance has no specified interface. This hook is intended for use in tests only.

If the plugin is unable to resolve the instrument name it shall *immediatly* throw an exception containing the missing instrument's name. Do not return None in this case as it makes diagnostics harder than a well thought out error string.


### General Purpose Functions
General Purpose Functions are plugin functionality that needs to be available to tests, but that is not tied to a specific usage scenario. 

```
get_general_purpose_function(func_name) -> FunctionInstance
```

Note that a "Function" in this context denotes an object that can have an arbitrary interface. The runtime environment will make an instance of the object available for each test program and test

### Tester
```
get_tester(tester_name) -> TesterInstance
```
This hook shall return an instance of a tester with the given name.

A tester is expected to have the following interface:
```
get_sites_count() -> int
def do_request(self, site_id: int, timeout: int) -> bool
def test_in_progress(site_id: int)
def test_done(site_id: int, timeout: int)
```

```
get_tester_master(tester_name) -> TesterInstance
```

This hook shall return an instance of a tester master type with the given name.

A tester master is expected to have the following interface:
```
get_sites_count() -> int
def get_site_states(self) -> list
def release_test_execution(self, sites: list)
def get_strategy_type(self)
```


## Configuration
Pluginobjects may provide configuration data in the form of key-value pairs. Each plugin shall provide a list of configuration options for a given object when the function:

```
get_configuration_options(object_name) -> List[String]
```

is called. It is up to the runtime to use the data (e.g. for creating a configuartion dialog). All objects shall support the
function:
```
set_configuration_values(Dict[String, String])
```
to apply a given set of configuration options. Each object shall be implemented such, that it is able to use the provided values on the fly.

Note: The configuration values are plain strings and have no notion of types.


## Complete Hookspec

```
get_plugin_identification() -> plugin_ident
get_importer_names() -> []
get_exporter_names() -> []
get_equipment_names() -> []
get_devicepin_importer_names() -> []
get_instrument_names() -> []
get_general_purpose_function_names() -> []
get_tester_names() -> []

get_importer(importer_name) -> Importer
get_exporter(exporter_name) -> Exporter
get_equipment(equipment_name) -> EquipmentInstance
get_devicepin_importer(importer_name) -> Importer

get_instrument(instrument_name) -> InstrumentInstance
get_instrument_proxy(required_capability) -> InstrumentProxy

get_tester(tester_name) -> TesterInstance
get_tester_master(tester_name) -> TesterInstance

get_general_purpose_function(func_name) -> FunctionInstance

get_configuration_options(object_name) -> List[String]]
```

The hookspecmarker is "ate.org"


### As basic example plugin
The example in this chapter containes the most basic plugin possible.

__File__: PluginSrc\PluginB\\_\_init__.py
```
import pluggy
from ATE.semiateplugins.hookspec import hookimpl

class ThePlugin(object):

    @hookimpl
    def get_plugin_identification() -> dict:
        return {}

    @hookimpl
    def get_importer_names() -> []:
        return []

    @hookimpl
    def get_exporter_names() -> []:
        return []

    @hookimpl
    def get_equipment_names() -> []:
        return []

    @hookimpl
    def get_devicepin_importer_names() -> []:
        return []

    @hookimpl
    def get_instrument_names() -> []:
        return []

    @hookimpl
    def get_tester_names() -> []:
        return []

    @hookimpl
    def get_importer(importer_name) -> Importer:
        raise NotImplementedError

    @hookspec.ate.hookimpl
    def get_exporter(exporter_name) -> Exporter:
        raise NotImplementedError

    @hookimpl
    def get_equipment(equipment_name) -> EquipmentInstance:
        raise NotImplementedError

    @hookimpl
    def get_devicepin_importer(importer_name) -> Importer:
        raise NotImplementedError

    @hookimpl
    def get_instrument(instrument_name) -> InstrumentInstance:
        raise NotImplementedError

    @hookimpl
    def get_instrument_proxy(instrument_name) -> InstrumentInstance:
        raise NotImplementedError

    @hookimpl
    def get_tester(tester_name) -> TesterInstance:
        raise NotImplementedError

    @hookimpl
    def get_tester_master(tester_name) -> TesterInstance:
        raise NotImplementedError

    @hookimpl
    def get_general_purpose_function(function_name) -> FunctionInstance:
        raise NotImplementedError

    @hookimpl
    def get_configuration_options(object_name) -> []:
        raise NotImplementedError
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
