# Master
## Daten die vom Master erzeugt werden

### Statusinfo

Topic: \<device-id>/Master/status
|Feld| Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command| status                  |
|interface_version| Bezeichnet die Version der Schnittstelle Master -> TestApp, die von dieser Version des Masters implementiert wird. |


Beispiel:

```json
{
    "type": "status",
    "interface_version": "1",
    "payload": {"state": "idle", "message": ""}
}
```

## Job

Topic: \<device-id>/Master/job
In diesem Topic findet sich eine Reihe von Key-Value Paaren, die die Konfiguration für den aktuellen Testjob darstellen. Der Master ermittelt sie anhand der Losnummer und einer kofigurierten Quelle (z.B. Networkshare für Job.xml).

## PeripheryState
**ToDo: Überarbeiten, gilt so nicht mehr!**

Topic: \<device-id>/Master/peripherystate

Im diesem Topic teilt der Master den Zustand von Peripheriegeräten mit, die durch den Master kontrolliert werden, d.h. solche für die nur eine Instanz existiert. Die konkret verwendeten Peripheriegeräte sind noch offen. Die Daten in diesem Topic werden wie folgt organisiert:
"\<PeripheryName>.\<Attribute>" : \<Value>
Somit besteht die Möglichkeit sowohl einfache "an/aus" Zustände als auch komplexere Zustände zu modellieren.

**Ende Todo**

## Befehle die vom Master verstanden werden

Der Master empfängt Befehle im Topic Master/command. Alle Befehle, auf die eine Antwort geschickt wird postet der Master im Topic Master/response

### Geteilte Peripherie steuern

**TODO - Abschnitt überarbeiten**
|Feld | Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command| „togglesharedperiphery“ |
|peripheryType | < name >           |
|param<0-n>| Parameter für Peripherie|


Weist den Master an ein Stück Peripherie anzusteuern, das
für alle Testprogramme gleich ist (z.B. Magnetfeldgenerator).
Der Master meldet Vollzug, indem das korrespondierende Feld im Topic "\<device-id>/Master/peripherystate" auf den geforderten Wert gesetzt wird. Das Parameterfeld ist als Beispiel zu verstehen. Je nach konkreter Peripherie werden unterschiedliche Parameter gebraucht. Hierzu muss eine seperate Dokumentation geschrieben werden.

**Ende ToDo**

__Beispiel__:
Im Test wird gefordert, dass der Fluxkompensator auf 100 bozos geschaltet wird.

Der aktuelle Peripheriestatus ist:

```json
{
    "fluxcompensator": 0,
    ...
}
```

TestApp postet:

```json
{
    "type": "io-control-request",
    "periphery_type": "fluxcompensator",
    "ioctl_name": "set_output",
    "parameters": 
    {
        "param0": 100,
        "timeout": 5.0
    }
}
```

Nach Empfang der Nachricht der Testapp steuert der Master den Fluxkompensator an.

:information_source: Der Master stellt sicher, dass die angeforderte Peripherie im korrekten Zustand ist, wenn der Vollzug meldet, d.h. etwaige Einschwingzeiten sind vom Testprogramm nicht seperat zu berücksichtigen, sondern wurden zum Zeitpunkt der Vollzugsmeldung durch den Master (bzw. das Plugin, welches die Ressourcensteuerung implementiert!) bereits berückstichtigt.

:warning: Wird eine Ressource angefordert, die nicht existiert, so geht der Master in den Fehlerzustand.

:warning: Erhält der Master verschiedene Befehle für die gleiche Peripherie (z.B. Site A fordert "Magnetfeld an", Site B fordert "Magnetfeld aus"), während noch eine Zustandsänderung pendent ist, so geht er in den Fehlerzustand über.

:warning: Zu einem Zeitpunkt kann nur genau eine Ressourcenanforderung aktiv sein. Werden zwei verschiedene Ressourcen angefordert, so geht der Master in den Fehlerzustand über.

:warning: Der Master synchronisiert den Zugriff auf die geteilten Peripherien derart, dass eine Änderung erst durchgeführt wird, wenn dieselbe Anfrage von allen aktiven Sites gesendet wurde. Es wird davon ausgegangen, dass auf allen Sites dasselbe Programm läuft und demnach auch immer zum gleichen Zeitpunkt während des Testablaufs von allen Sites dieselbe gemeinsame Ressource verwendet wird. Derzeit sind noch keine Timeouts für diesen Vorgang definiert.

__Auflösen von geteilten Peripherien__: Der Master verwendet Pluggy um für geteilte Peripherien das richtige Businessobjekt zu ermitteln, dabei wird der Peripherytype als Aktuatorfähigkeit interpretiert. Der Master instanziert sich ein Aktuatorobjekt mit dem Call "get_actuator" aus den installierten Plugins. Er verwendet die erste Implementierung, die gemeldet wird. Das bedeutet, dass mehrere Aktuatorimplementierungen für denselben Aktuator (die durchaus aus verschiedenen Plugins kommen können!) zu unvorhersehbarem Verhalten führen.


### Handlerbefehle

Topic: \<device-id>/Master/cmd
|Feld| Bedeutung/Zulässige Werte    |
|----|------------------------------|
|type| \<command_type>              |
|value | \<payload>                 |

payload kann mehere key paramters haben. Dies im Falle von load lot
informationen über das zu ladene lot (Losnumber, Temperature, etc..). Viele Befehle werden mit dem Zustand des Master quittiert, d.h. die interne Zustandsmaschine des Masters wechselt den Zustand aufgrund eines Befehls, was auf dem Master/status Topic zu beobachten ist. Dementsprechend muss eine Handlersteuerung dieses Topic überwachen.


Unterstützte Befehle

#### site-layout
Der site-layout Befehl teilt dem Master mit welches physische Layout die Sites des Testers zueinander haben. 
Der Master ermittelt anhand dieses Layouts, welche Pingpong Konfiguration zu verwenden ist. 
```json
{
    "type": "site-layout",
    "payload": 
        {
            "sites": [
                [0, 1],
                [1, 0]
            ]
        }
}
```


* [0, 1] are the x and y coordinates
* the index of the tuple (x and y) is the sideid
from the example above:
    - siteid 0 ==>  (x: 0, y: 1)


* Für jede Site des Testers wird ein Eintrag im "sites" Array erwartet.
* Die Positionen müssen mit den Positionen, die im Master hinterlegt sind übereinstimmen.

Positionen der Sites im Master:
* Der Master speichert die Sitepositionen als vielfaches der Größe einer Site, mit dem 0 Punkt links oben.
* Es gibt keine negativen Koordinaten für Sites.
* Der Master erlaubt einen Versatz vom 0-Punkt von maximal <Anzahl Sites> - 1, d.h. bei 4 Sites ist die Maximale X Koordinate 3.
* Es gibt keine Bruchteile von Schritten, sondern nur ganze Zahlen.

Der Nutzer des Interface ist dafür verantwortlich die Sitekoordinaten mittels einer geeigneten Transformation in das Masterkoordinatensystem zu überführen.

Randbedingungen: 
- Der Master akzeptiert dieses Paket nur, solange noch kein Testprogramm geladen ist.
- Sollte ein Testprogramm geladen werden, bevor dieses Paket geladen wurde, so verwendet der Master eine in seiner  Konfigurationsdatei hinterlegtes Layout. Hierbei handelt es sich um einen Fallback um es weiterhin zu ermöglichen Lose über das WebUI zu ermöglichen wenn kein Handler verfügbar ist.

#### load
Der Loadbefehl weist die Masterapplikation an ein Los zu laden.
Bei Erfolg wechselt der Master in den Zustand XXX

```json
{
    "type": "load",
    "payload": 
        {
            "lotnumber": "", 
            "sublotnumber": "", 
            "devicetype": "", 
            "measurementtemperature": ""
        }
}
```

Der Loadbefehl weist die Masterapplikation an ein Los zu laden

* **lotnumber**: Losnummer
* sublotnumer: Sublosnummer / Wafernummer
* devicetype: Device Type
* measurementtemperature: Eingestellte Test-Temperatur

Bei Erfolg wechselt der Master in den Zustand XXX

#### next
Der Nextbefehl weist die Masterapplikation die Tests für eine gegebene Menge von Sites zu starten. Der Master wechselt während die Tests laufen in den Zustand XXX und nach Testabschluss in den Zustand YYY. Die Handlerapplikation darf keinen neuen Testbefehl schicken, solange der Zustand XXX nicht erreicht wurde, selbst dann nicht, wenn der Master bereits Testergebnisse publiziert hat.

```json
{
    "type": "next",
    "payload": 
        {
            "sites": [
                {
                    "siteid": "site-id",
                    "partid": "", 
                    "binning": "", 
                    "logflag": "", 
                    "additionalinfo": "",
                },
                (mehr sites)
            ]
        }
}
```

* **siteid**: Siteid einer Site, auf der getestet werden soll. Diese Siteid muss mit einer Site übereinstimmen, die beim Master angemeldet ist.
* **partid**: Bauteilnummer
* **binning**: Bin Ergebnis einer vorherigen Teststation für das Bauteil
* **logflag**:  LOG FLAG
* **additionalinfo**: Informationen die Zwischen meherere Tester ausgetauscht werden

**Fehlerfälle**:
Wird ein Testbefehl für eine Unbekannte Site erzeugt, so wechselt der Master in den Zustand "Error".

#### end lot
Der Endlotbefehl weist die Masterapplikation ihre Testapplikation zu beenden. Bei Erfolg wechselt der Master in den Zustand XXX

```json
{
    "type": "endlot",
    "payload": {}
}
```


#### identify
Der identifybefehl weist die Masterapplikation sein ID(Name) zu schicken. Die Antwort ist:

```json
{
    "type": "identify",
    "payload": {}
}
```


```json
{
    "type": "identify",
    "payload": {"name": ""}
}
```


#### get-state
Der get-state Befehl weist die Masterapplikation seinen Zustand zu schicken. Der Master published daraufhin seinen aktuellen Zustand im status Topic.

```json
{
    "type": "get-state",
    "payload": {}
}
```

Antwort durch den Master

```json
{
    "type": "get-state",
    "payload": {"state": "",
                "message": ""
               }
 }
```


**ToDo: Hier sollten nur die Statemachinezustände des Masters stehen. Der Handler muss sehen, wie er damit klarkommt.**

* BUSY
* LOT = loading
* INIT
* OK
* ERR
* CHECKSUM = checksum error
* NOT_IMPL
* INVAL_LOT
* NO_LOT
* HAVE_LOT
* UN_ERR = unrecorverable error


#### get-host
Der get-host Befehl weist die Masterapplikation seinen host information zu schicken. Diese werden verwendet, um auf dem Master WebUI zugreifen zu können.
Der Master published daraufhin die information in seinem response topic.

```json
{
    "type": "get-state",
    "payload": {}
}
```

Antwort durch den Master

```json
{
    "type": "get-state",
    "payload":
    {
        "host": "",
        "port": /<port-num/>
    }
 }
```

## Daten die vom Master konsumiert werden

Der Master konsumiert Statusinformationen aus den Topics:

* \<device-id>/Control/status
* \<device-id>/TestApp/status
* \<device-id>/Periphery/status

* \<handler-id>/Handler/status
