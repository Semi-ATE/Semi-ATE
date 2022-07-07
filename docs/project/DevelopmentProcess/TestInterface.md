# Test Interface

Tests provides a public interface to read & write the corresponding parameters. This document will cover all those public functions.

## Test Entry Point

Tests are auto-generated and all parameters defined via the IDE will be available as python objects that may be used to read and write those parameter.

The following is an example of a generated test based on configuring one input parameter and one output parameter:

```python
class contact(contact_BC):

    '''
    for debug purposes, a logger is available to log infomration and porpagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    


    Input Parameter | Shmoo | Min | Default | Max | Unit | fmt
    ----------------+-------+-----+---------+-----+------+----
    ip.Temperature  |  Yes  | -40 |   25    | 170 | °C   | .0f

    Parameter         | MPR | LSL | (LTL) |  Nom  | (UTL) | USL  | Unit | fmt
    ------------------+-----+-----+-------+-------+-------+------+------+----
    op.new_parameter1 | No  |  -∞ |  (-∞) | 0.000 | (+∞)  | +∞   | ˽    | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for test."""
        self.op.new_parameter1.default()
```

The `do` function is the spot where test code should be located to be executed by the test program.

Even though, the test contains some comments with some information of the parameter available and some logging hint there still not enough to write complex tests, such as using instrument, actuators or operating on the tester hardware.

Therefore, the following sections will cover all other interfaces that are provided to the test.
All input & output parameters are listed in the comment section above the `do` function.

## Input Parameter

The current parameter value set by the test program could be extracted as follow:

```python
temperature_value = self.ip.Temperature()
```

The `temperature_value` now variable contains the value of the temperature set by the corresponding test program.

> __note__: input parameters are read only parameters that shall not be overridden in code.

## output Parameter

Output parameter on the other side provide more are more likely to change

```python
self.new_parameter1.default()
self.new_parameter1.write(1.0)
output_param_value = self.new_parameter1.get_measurement()
```

To operate on output parameter there are several options.
As seen above, the output parameter has a 'default' function with which a default value will be assigned to it.

__note__: the value assigned with the `default` function will always be in the defined range and will always pass the test

The `write` function shall assign the output parameter a value specified by the user or read from external source such as reading the output voltage of an analog channel that the tester provides

The `get_measurement` function gets the value assigned to the output parameter.

__note__: in case the `mpr` flag is set, the `write` function could be called multiple times, the assigned values will be appended a measurement list. Further, calling the `get_parameter` function shall return a list of all written values

> __note__: output parameters must be assigned with a value after each test execution, otherwise an exception will be raised

## Context

The Context is part of the test and could be used as follow.

```python
self.context.<...>
```

The Context is a special object which provides the tester with all tools required & configured in the different stages of setting up the project e.g the instrument and actuator selected in the `hardwaresetup` section, the selected tester, ...

The context could be seen as a container that manages all the tools to provide the test with different interfaces to interact with it's environment

### Tester

The Tester is the interface to operate on the real tester hardware such that operation like setting relays, reading channels, etc..., are possible.

```python
self.context.tester.<function>
```

The tester interface is not part of this document and shall be provided by the tester hardware developers.

> proposal to simplify accessing the tester
>
> ```python
> self.tester.<function>
> ```
>
> not implemented yet

__note__: the tester is a plugin and shall be installed separately.

### Instrument & Actuator

Using Instruments or Actuator defined in the `hardwaresetup` section shall be done via the context.

```python
self.context.<any-defined-instrument-or-actuator-name>.<function>
```

## Review All

* Writing tests in an IDE such as Spyder IDE will simplify using the tools (e.g. tester, instrument, etc...) as it provides the user with a full auto-completion support feature with which the provided interfaces could explored easily.
