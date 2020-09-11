# Interfacedefinitionen Micronas ATE

## Grundsätzliches
•	Sämtliche Daten werden immer als Json zwischen den Komponenten verschickt
•	Alle Json Strukturen müssen mindestens folgende Felder beinhalten:
o	type: Bezeichnet den Typ des Datensatzes als string.
•	Zusätzliche Daten sind Datensatzspezifisch
•	Alle Feldnamen in den Json Daten sind als camelCase anzulegen.
•	In diesem Dokument bezeichnen „erzeugte Daten“ Daten, die beim Betrieb anfallen (z.B. Testresultate, Statusinformationen), aber keine Steuerbefehle sind.
•	In diesem Dokument bezeichnen „konsumierte Daten“ Daten, die von einer Applikation verwendet werden, aber nicht direkt Aktionen einer Applikation auslösen (z.B. Statusinformationen, die nur angezeigt werden)
•	In diesem Dokument bezeichnen „Befehle“ Daten, die eine Applikation dazu veranlassen eine bestimmte Aktion durchzuführen (z.B. Test starten).

Ein Json Datensatz sieht demzufolge aus wie folgt:
```json
{
	„type“: „<Type>“
}
``` 

## Topics
Grundsätzlich werden alle Topics nach Ursprung gegliedert. Für jede Teilapplikation, bei der es mehrere Instanzen geben kann, gibt es folgende Topics:
•	\<device-id>/\<AppName>/status/ site\<siteId>
•	\<device-id>/\<AppName>/cmd
Das \<device-id> ermöglicht es eine bessere Aufteilung, wenn sich mehrere Geräte in der gleichen Netzwerk befinden.
Teilapplikationen, von denen immer nur eine Instanz läuft Pverwenden die Topics ohne sitespezifisches Untertopic, also:
•	\<device-id>/\<AppName>/status/site\<siteId>
•	\<device-id>/\<AppName>/cmd
Diese Aufeilung ermöglicht es dem Master mit einer Subscription z.B. auf TestApp/status/# die Statusinformationen alle Testapps zu bekommen, ohne wissen zu müssen, welche Testapps nun gerade laufen.
Beispiel:
Ein Gerät mit 2 Sites hätte damit folgende Topics:
•	\<device-id>/Master/status
•	\<device-id>/Master/cmd 
•	\<device-id>/Control/status/site0
•	\<device-id>/Control/status/site1
•	\<device-id>/Control/cmd
•	\<device-id>/TestApp/cmd
•	\<device-id>/TestApp/status/site0
•	\<device-id>/TestApp/status/site1

## Befehle
Befehle weisen die einzelnen Systemkomponenten an definierte Aktionen durzuchführen. Es gilt, dass jeder Befehl folgende Form hat:
```json
{
	type: „cmd“,
	command: „<cmdname>“,
}
```
Befehle, die an eine oder meherere Testapps gesendet werden haben zusätzlich noch ein Feld mit einem Array von Sites für die der Befehl gültig werden, z.B.:
```json
{
	type: „cmd“,
	command: „<cmdname>“,
	sites: [1,2,3]
}
```

Dieser Befehl würde von den Sites 1, 2 und 3 ausgeführt. Etwaige andere vorhandene Sites ignorieren den Befehl. Es wird an dieser Stelle darauf verzichtet, für jede Testapp ein eigenes Befehlstopic zu verwenden, da Befehle i.D. immer an alle Testapps gesendet werden müssen.

## Master
### Daten die vom Master erzeugt werden
#### Statusinfo
Topic: \<device-id>/Master/status
|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command|	status                  |
|alive | 0 oder 1                   |
|interface_version| Bezeichnet die Version der Schnittstelle Master -> TestApp, die von dieser Version des Masters implementiert wird. |

Gültige Werte für alive:
•	0 = Masterapplikation hat sich beendet (unbeabsichtigt/Fehler), 
•	1 = Masterapplikation aktiv

Beispiel:
```json
{
	„type“: „status“,
	„alive“: „1“,
	„interface_version“: „1“
}
```

#### Job
Topic: \<device-id>/Master/job
In diesem Topic findet sich eine Reihe von Key-Value Paaren, die die Konfiguration für den aktuellen Testjob darstellen. Der Master ermittelt sie anhand der Losnummer und einer kofigurierten Quelle (z.B. Networkshare für Job.xml).

#### PeripheryState
Topic: \<device-id>/Master/peripherystate

Im diesem Topic teilt der Master den Zustand von Peripheriegeräten mit, die durch den Master kontrolliert werden, d.h. solche für die nur eine Instanz existiert. Die konkret verwendeten Peripheriegeräte sind noch offen. Die Daten in diesem Topic werden wie folgt organisiert:
"\<PeripheryName>.\<Attribute>" : \<Value>
Somit besteht die Möglichkeit sowohl einfache "an/aus" Zustände als auch komplexere Zustände zu modellieren.

### Befehle die vom Master verstanden werden
Der Master empfängt Befehle im Topic Master/Cmd. 

#### Geteilte Peripherie steuern
|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command|	„togglesharedperiphery“ |
|peripheryType | < name >           |
|param<0-n>| Parameter für Peripherie|

Weist den Master an ein Stück Peripherie anzusteuern, das
für alle Testprogramme gleich ist (z.B. Magnetfeldgenerator).
Der Master meldet Vollzug, indem das korrespondierende Feld im Topic "\<device-id>/Master/peripherystate" auf den geforderten Wert gesetzt wird. Das Parameterfeld ist als Beispiel zu verstehen. Je nach konkreter Peripherie werden unterschiedliche Parameter gebraucht. Hierzu muss eine seperate Dokumentation geschrieben werden.

__Beispiel__:
Im Test wird gefordert, dass der Fluxkompensator auf 100 bozos geschaltet wird. 

Der aktuelle Peripheriestatus ist:
```json
{
	"fluxcompensator": 0,
	"pulseout0": 0,
	...
}
```

TestApp postet:
```json
{
	type: "command",
	command: "togglesharedperiphery",
	peripheryType: "fluxcompensator",
	param0: 100
}
```

Nach Empfang der Nachricht der Testapp steuert der Master den Fluxkompensator an. Sobald diese geschehen ist wechselt der Peripheriestatus auf:
```json
{
	"fluxcompensator": 100,
	"pulseout0": 0,
	...
}
```

:information_source:: Der Master stellt sicher, dass die angeforderte Peripherie im korrekten Zustand ist, wenn der Vollzug meldet, d.h. etwaige Einschwingzeiten sind vom Testprogramm nicht seperat zu berücksichtigen, sondern wurden zum Zeitpunkt der Vollzugsmeldung durch den Master bereits berückstichtigt.

:information_source:: Im Peripheriestatus ist immer der Zustand aller für den Master konfigurierten Peripherien zu sehen, auch solche die zuletzt nicht angesteuert werden. Es handelt sich um eine retained Message, sodass alle Applikationen im System immer in der Lage sind den letzten gültigen Peripheriestatus abzufragen.

:warning:: Wird eine Ressource angefordert, die nicht existiert, so geht der Master in den Fehlerzustand.

:warning:: Erhält der Master verschiedene Befehle für die gleiche Peripherie (z.B. Site A fordert "Magnetfeld an", Site B fordert "Magnetfeld aus"), während noch eine Zustandsänderung pendent ist, so geht er in den Fehlerzustand über.

:warning:: Der Master synchronisiert den Zugriff auf die geteilten Peripherien derart, dass eine Änderung erst durchgeführt wird, wenn dieselbe Anfrage von allen aktiven Sites gesendet wurde. Es wird davon ausgegangen, dass auf allen Sites dasselbe Programm läuft und demnach auch immer zum gleichen Zeitpunkt während des Testablaufs von allen Sites dieselbe gemeinsame Ressource verwendet wird. Derzeit sind noch keine Timeouts für diesen Vorgang definiert.

### Daten die vom Masterkonsumiert werden
Der Master konsumiert Statusinformationen aus den Topics:
•	\<device-id>/Control/status
•	\<device-id>/TestApp/status
•	\<device-id>/Webserver/status

## Control
### Daten die von Control erzeugt werden

#### Statusinfo
Topic: \<device-id>/Control/status/site\<SiteId>/
|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type|	„status“                    |
|alive | 0, 1                       |
|interface_version|Version,  der Schnittstelle Control -> Test|
|softwareversion| Softwareversion der Controlapplikation
Gültige Werte für alive:
•	 0 = Controlapplikation hat sich beendet (unbeabsichtigt/Fehler)
•	 1 = Controlapplikation aktiv


#### Ladestatus
Topic: \<device-id>/Control/loadstate/site\<SiteId>/
|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type|	„loadstate“                 |
|success |	Fehlercode, siehe unten |

•	0 = Job XML wurde geladen, Testapp wurde geladen
•	1 = Fehlerhaftes Job XML (XML konnte nicht geparsed werden)
•	2 = Fehlerhaftes Job XML (Inhalt)
•	3 = Testapp konnte nicht geladen werden (nicht gefunden)
•	4 = Testapp konnte nicht geladen werden (Netzwerkfehler ?)
•	5 = Testapp konnte nicht gestartet werden


### Daten die von Control konsumiert werden
Control konsumiert Statusinformationen aus den Topics:
•	\<device-id>/Master/status
•	\<device-id>/Testapp/status

### Befehle die von Control verstanden werden
Topic: \<device-id>/Control/cmd/
#### Load
|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command|	„loadTest“              |
|XML |	Inhalt des JobXML           |
Der Loadbefehl weist Control an ein gegebenes Testprogramm zu laden. Control soll in diesem Fall
den Inhalt von /Master/job verwenden um das korrekte Testprogramm zu ermitteln
Der Loadbefehl weist Control an ein gegebenes Testprogramm anhand eines mitgelieferten Job.xml zu laden. Control interpretiert den XML Inhalt des Befehls und lädt im Anschluss das im XML referenzierte Testprogram. Hierbei muss es sich um ein Programm handeln, das dass TestApp Interface implementiert bzw. sich wie eine Testapp verhält.
__Achtung__: Möglicherweise reicht es aus, wenn Control einfach darauf achtet, was
im job Topic passiert. In diesem Fall benötigt es keinen expliziten Befehl.

__Hinweis__ Control prüft, ob sich die Testapp anmeldet. Sollte das nicht innerhalb von !TBD! Sekunden nach dem Start passieren, so geht sie in den Zustand 5 über.

## TestApp
### Daten die von der Testapp erzeugt werden

#### Statusinfo
Topic: \<device-id>/Testapp/status/site\<SiteId>

|Feld|	Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type|	„status“                    |
|alive | 0, 1, 2, 3                 |
|framework_version|Version des Frameworks, die verwendet wurde im die Testapp zu bauen|
|test_version|Version des Testprogramms|

Bedeutungen der Werte des Felds alive:
•	0 = Testapp hat sich beendet (unbeabsichtigt/Fehler), 
•	1 = Testapp aktiv, 
•	2 = Testapp wurde beendet („graceful shutdown)
•	3 = Testapp aktiv, Selbsttest fehlgeschlagen. Details im Logfile der Testapp

#### Testresultat
Topic: \<device-id>/Testapp/testresult/site\<SiteId>

|Feld|	Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|type|	„testresult“                          |
|pass | 1 oder 0 für pass/fail                |
|testdata| Unterstruktur mit binären Testdaten|

Die Testdaten sind ggf. je nach Testtyp anders, weshalb hier keine allgemeingültige Form angegeben werden kann. Achtung: Derzeit ist noch nicht klar, ob das "pass" Attribut beibehalten wird.

### Daten die von der Testapp konsumiert werden
Die Testapp konsumiert Statusinformationen aus den Topics:
•	\<device-id>/Master/status
•	\<device-id>/Control/status/site\<SiteId>
Befehle die von der Testapp verstanden werden

Topic: \<device-id>/TestApp/cmd

#### Init
Der Initbefehl weist die Testapplikation an einen Selbsttest durchzuführen.
|Feld|	Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "init"                              |

#### Next
Der Nextbefehl weist die Testapplikation einen neuen Testlauf zu starten. Der Testbefehl muss für jedes Bauteil, das von der Applikation getestet werden soll erneut geschickt werden

|Feld|	Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "next"                              |


#### Terminate
Der Terminatebefehl weist die Testapplikation an sich zu beenden.
*Offen: Soll Terminate etwaige laufende Tests ebenfalls abbrechen?*

|Feld|	Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "terminate"                         |


## Webserver
### Daten die vom Webserver erzeugt werden

### Daten die vom Webserver konsumiert werden
Der Webserver konsumiert Statusinformationen aus den Topics:
•	\<device-id>/Testapp/status/#
•	\<device-id>/Control/status
•	\<device-id>/Testapp/status
