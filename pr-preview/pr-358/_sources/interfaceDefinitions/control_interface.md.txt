# Control

## Daten die von Control erzeugt werden

### Statusinfo

Topic: \<device-id>/Control/status/site\<SiteId>/
|Feld| Bedeutung/Zulässige Werte   |
|----|------------------------------|
|type| „status“                    |
|interface_version|Version,  der Schnittstelle Control -> Test|
|softwareversion| Softwareversion der Controlapplikation
|payload| Nutzdaten des Pakets      |

Inhalt der Nutzdaten (Bsp!):
```json
{
  "state": "ready",
  "message": "some message"
}
```

## Daten die von Control konsumiert werden

Control konsumiert Statusinformationen aus den Topics:

* \<device-id>/Master/status
* \<device-id>/Testapp/status

## Befehle die von Control verstanden werden

Topic: \<device-id>/Control/cmd/

### Load

|Feld| Bedeutung/Zulässige Werte   |
|----|------------------------------|
|Command| „loadTest“              |
|testapp_params | information über das testprogram (Path, Argumente, etc...) |
|sites| sites die das testprogram laden müssen|
Der Loadbefehl weist Control an ein gegebenes Testprogramm zu laden.
kann das Test Program nicht gestartet werden, geht der Control in dem 'error' Zustand,
error Nachrichten werden direkt im Log-File geschrieben.

__Hinweis__ Master prüft, ob sich die Testapp anmeldet. Sollte das nicht innerhalb von !TBD! Sekunden nach dem Start passieren, so geht sie in den softerror 'Zustand' über.

