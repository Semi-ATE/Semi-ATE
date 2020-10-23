# The Magnetic Field Actuator (STL DCS6K, single channel)

## Actuator Api

## Additional Api Functions
In addition to the standard API defined for a magnetic field actuator, the DCS6K supports additional io controls that are usable for setting up the magnetic field. The parameters are those, that are used in the examples of the reference manual chapter 3.3.5.2

### init_load

```json
{
    "type": "io-control-request",
    "ioctl_name": "init_load",
    "parameters": {
        "rref": 100,
        "lref": 5.0,
        "deltaRref": 0.05,
        "deltaLref": 0.05
    }
}
```

Initializes the load by:
* reading the reference impedance
* measureing the current impedance
* setting the reference impedance according to the given parameters
* performing an impedance test.

Will return 0 or 1 according to the manual of the DCS6K

### do_load_adaption

```json
{
    "type": "io-control-request",
    "ioctl_name": "do_load_adaption",
    "parameters": {
        "proportional_factor": 100,
        "integral_factor": 5.0,
        "slew_rate": 0.05,
    }
}
```

* initializes the PID
* sets the PID parameters for the "standard" pid

### setup_dcs6k

```json
{
    "type": "io-control-request",
    "ioctl_name": "do_load_adaption",
    "parameters": {}
}
```

* Sets the opration mode and startup mode to "analog"
* Sets the analog parameters to 1,standard,1,0.05
