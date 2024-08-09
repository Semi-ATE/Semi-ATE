## TestApp

### Daten die von der Testapp erzeugt werden

#### Statusinfo

Topic: \<device-id>/Testapp/status/site\<SiteId>

|Feld| Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type| „status“                    |
|framework_version|Version des Frameworks, die verwendet wurde im die Testapp zu bauen|
|test_version|Version des Testprogramms|
|payload| Nutzdaten des Pakets      |

Inhalt der Nutzdaten (Bsp!):
```json
{
  "state": "ready",
  "message": "some message"
}
```


#### Testresultat

Topic: \<device-id>/Testapp/testresult/site\<SiteId>

|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|type| „testresult“                          |
|payload | restresult in json format          |
|testdata| Unterstruktur mit binären Testdaten|

Die Testdaten sind ggf. je nach Testtyp anders, weshalb hier keine allgemeingültige Form angegeben werden kann.

### Daten die von der Testapp konsumiert werden

Die Testapp konsumiert Statusinformationen aus den Topics:

* \<device-id>/Master/status
* \<device-id>/Control/status/site\<SiteId>
Befehle die von der Testapp verstanden werden

Topic: \<device-id>/TestApp/cmd

#### Init

Der Initbefehl weist die Testapplikation an einen Selbsttest durchzuführen.
|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "init"                              |

#### Next

Der Nextbefehl weist die Testapplikation einen neuen Testlauf zu starten. Der Testbefehl muss für jedes Bauteil, das von der Applikation getestet werden soll erneut geschickt werden

|Feld    | Bedeutung/Zulässige Werte           |
|------- |-------------------------------------|
|command | "next"                              |
|sites   | list of sites that should test      |
|job_data| all information needed to test      |

__example__:
```json
{
  "type": "cmd",
  "command": "next",
  "sites": [
    "0"
  ],
  "job_data": {
    "stop_on_fail": {
      "active": false,
      "value": -1
    },
    "single_step": {
      "active": false,
      "value": -1
    },
    "stop_on_test": {
      "active": false,
      "value": -1
    },
    "trigger_on_test": {
      "active": false,
      "value": -1
    },
    "trigger_on_fail": {
      "active": false,
      "value": -1
    },
    "trigger_site_specific": {
      "active": false,
      "value": -1
    },
    "sites_info": [
                  {
                    "siteid": "0",
                    "partid": "12346",
                    "binning": -1,
                    "logflag": 2,
                    "additionalinfo": 0
                  }
                  ]
  },
  "test_sequence": []
}
```

* **tests**(optinal): Liste von test-instances Namen, die ausgeführt werden sollen

#### Terminate

Der Terminatebefehl weist die Testapplikation an sich zu beenden.

|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "terminate"                         |

#### Setloglevel

Der setloglevel Befehl weist die Testapplikation an, dass sie ihr loglevel update muss

|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "setloglevel"                         |
|level| \<level>|
\<level>:

* Debug
* Info
* Warning
* Error

#### Setting

Der setting Befehl weist die Testapplikation an, dass sie die angeforderten settings schicken soll

|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "setting"                         |
|name| setting-name bzw. -type

Beispiel: name == "binsettings"


#### SetParameter 
Mit Hilfe dieses Befehls kann man Input Parameter setzten bzw. updaten. Dies wird benötigt, wenn man shmoo tests ausführen möchte.


```json
{
    "type": "cmd",
    "command": "setparameter",
    "parameters":
    [
        {
            "parametername": "<name>",
            "value": "<value>", 
        },
    ]
}
```

* **parametername**: ist eine Kombination von test instance Name und Inputparamter Name (wie im test definiert ist) (<test_instance_name>.<parameter_name>)
* **value**: der neue Wert, der das Inputparameter einnehmen soll