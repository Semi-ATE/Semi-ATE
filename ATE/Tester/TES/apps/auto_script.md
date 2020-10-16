auto_script is a development script, that is mainly used to generate config files for master and control, beside the user is also
able to start multiple control


## Control

### generate control configuration file
```
python auto_script.py control #device_id -conf
```

* the output will be a json file format: "control_config_file.json"


### start multiple control
```
python auto_script.py control #device_id -num_apps #num_of_required_apps
```

## Master

#### generate master configuration file
```
python auto_script.py master #device_id -conf
```

#### generate master configuration file for multiple sites
```
python auto_script.py master #device_id -conf -num_apps #num_of_required_apps
```

* the output will be a json file format: "master_config_file.json"


