# Projektjournal für Runtime Framework (RTF)
Alle wichtigen Designentscheidungen werden in dieser Datei festgehalten

## 7.1.2020 Webserver + Websockets
- Es wurde festgelegt, dass die UI Applikation alle Daten auf dem Server zusammenstellt via Websockets zum Client überträgt. Damit entfällt der direkte Pfad zwischen Webclient und den anderen Komponenten.
- Festlegung für UI auf AioHttp statt Django:
    Libs:
    - aoihttp
    - aoihttp_jinja2
    - jinja2
    - pytest