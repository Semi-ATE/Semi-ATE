# Test Interface

The Test structure is auto generated based on some UI configuration. It provides functions to read & write parameters and to interact with extern tools.

## Test Entry Point

The tests are written in python.
The following is an example of a generated test based on the configuration of one input parameter and one output parameter:

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

The `do` function is the main spot where test code should be located which will be automatically executed by the test program.

__note__: `do` should not be renamed oder removed as the test program will try to call this function on each associated test instance.

The test contains also some comments with some information of available parameter and some hints how to use the logger. As we go further, we will learn more about other utility the test provides.

In the following sections will cover all other interfaces that are provided by the test.

## Input Parameter

The current parameter value by the test program could be extracted as follow:

```python
temperature_value = self.ip.Temperature()
```

The `temperature_value` variable contains the value of the temperature set by the corresponding test program.

> __note__: input parameters are read only parameters that shall not be overridden in code.

## output Parameter

Output parameter on the other hand are more likely to change

```python
self.new_parameter1.default()
self.new_parameter1.write(1.0)
output_param_value = self.new_parameter1.get_measurement()
```

To operate on output parameter there are several options.
As seen above, the output parameter has a 'default' function with which a default value will be assigned to it.

__note__: the value assigned with the `default` function will always be in the defined range and will always pass the test.

The `write` function shall assign the output parameter a value specified by the user or read from external source such as reading the output voltage of an analog channel that the tester provides.

The `get_measurement` function gets the value assigned to the output parameter.

__note__: in case the `mpr` flag is set, the `write` function could be called multiple times and the value will be appended to a list. Calling the `get_parameter` function shall return a list of all written values

> __note__: output parameters must be assigned with a value before the test execution ends, otherwise an exception will be raised

## Context

The Context is part of the test and could be used as follow.

```python
self.context.<...>
```

The Context is a special object which provides the test with all required tools, tools are those configured in the `hardwaresetup` section such as e.g tester, instrument and actuator.

The context could be seen as a container that manages all the tools and provides the test with the available interfaces to interact with it's environment

### Tester

The Tester is a plugin instance which shall be used to operate on the real tester hardware and execute such operations like setting relays, reading channels, etc...

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

## Some Hints

* Writing tests in an IDE such as Spyder IDE will simplify using the tools (e.g. tester, instrument, etc...) as it provides the user with a full auto-completion support feature with which the provided interfaces could be explored easily.
