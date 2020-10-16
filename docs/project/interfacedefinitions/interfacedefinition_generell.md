# Interfacedefinitionen Micronas ATE

## Grundsätzliches

* Sämtliche Daten werden immer als Json zwischen den Komponenten verschickt
* Alle Json Strukturen müssen mindestens folgende Felder beinhalten:
* type: Bezeichnet den Typ des Datensatzes als string.
* Zusätzliche Daten sind Datensatzspezifisch
* Alle Feldnamen in den Json Daten sind als camelCase anzulegen.
* In diesem Dokument bezeichnen „erzeugte Daten“ Daten, die beim Betrieb anfallen (z.B. Testresultate, Statusinformationen), aber keine Steuerbefehle sind.
* In diesem Dokument bezeichnen „konsumierte Daten“ Daten, die von einer Applikation verwendet werden, aber nicht direkt Aktionen einer Applikation auslösen (z.B. Statusinformationen, die nur angezeigt werden)
* In diesem Dokument bezeichnen „Befehle“ Daten, die eine Applikation dazu veranlassen eine bestimmte Aktion durchzuführen (z.B. Test starten).

Ein Json Datensatz sieht demzufolge aus wie folgt:

```json
{
    "type": "<Type>"
}
```

## Topics

Grundsätzlich werden alle Topics nach Ursprung gegliedert. Für jede Teilapplikation, bei der es mehrere Instanzen geben kann, gibt es folgende Topics:

* \<device-id>/\<AppName>/status/ site\<siteId>
* \<device-id>/\<AppName>/cmd
Das \<device-id> ermöglicht es eine bessere Aufteilung, wenn sich mehrere Geräte in der gleichen Netzwerk befinden.
Teilapplikationen, von denen immer nur eine Instanz läuft Pverwenden die Topics ohne sitespezifisches Untertopic, also:
* \<device-id>/\<AppName>/status/site\<siteId>
* \<device-id>/\<AppName>/cmd
Diese Aufeilung ermöglicht es dem Master mit einer Subscription z.B. auf TestApp/status/# die Statusinformationen alle Testapps zu bekommen, ohne wissen zu müssen, welche Testapps nun gerade laufen.
Beispiel:
Ein Gerät mit 2 Sites hätte damit folgende Topics:
* \<device-id>/Master/status
* \<device-id>/Master/cmd
* \<device-id>/Control/status/site0
* \<device-id>/Control/status/site1
* \<device-id>/Control/cmd
* \<device-id>/TestApp/cmd
* \<device-id>/TestApp/status/site0
* \<device-id>/TestApp/status/site1
* ...

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



