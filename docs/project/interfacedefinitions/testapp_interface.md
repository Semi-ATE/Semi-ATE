## TestApp

### Daten die von der Testapp erzeugt werden

#### Statusinfo

Topic: \<device-id>/Testapp/status/site\<SiteId>

|Feld| Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type| „status“                    |
|alive | 0, 1, 2, 3                 |
|framework_version|Version des Frameworks, die verwendet wurde im die Testapp zu bauen|
|test_version|Version des Testprogramms|

Bedeutungen der Werte des Felds alive:

* 0 = Testapp hat sich beendet (unbeabsichtigt/Fehler),
* 1 = Testapp aktiv,
* 2 = Testapp wurde beendet („graceful shutdown)
* 3 = Testapp aktiv, Selbsttest fehlgeschlagen. Details im Logfile der Testapp

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

|Feld| Bedeutung/Zulässige Werte             |
|----|----------------------------------------|
|command| "next"                              |

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

