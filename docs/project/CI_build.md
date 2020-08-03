# CI build

## GitLab Runner

__________

Typen:

* Specific GitLab Runner
* Sahred GitLab Runner
* Group GitLab Runner

**Konfigurationsdateien:**

* **config.toml**: 

  * Diese Datei befindet sich auf dem GitLab Server
  * Enthält die Konfiguration für die einzelnen GitLab Runner

* **.gilab-ci.yml**:

  * Diese Datei befindet sich standardmäßig im Root-Ordner des Git-Repositories
  * Enthält die einzelnen Jobs die ausgeführt werden, wenn das Repository durch einen git-push aktualisiert wird.

### Beispiel config.toml

``` toml
concurrent = 8
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "clean"
  url = "https://git.awinia.lan/"
  token = "8BUky95eUg4x411kXhp7"
  limit = 8
  executor = "shell"
  shell = "powershell"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
```

Beschreibung:

* **concurrent**: (global) Definiert über alle existierenden GitLab Runner hinweg die maximale Anzahl der parallel ausgeführten Jobs
* **token**: eindeutig für jeder GitLab Runner. token und url können von der GitLab Webseite entnommen werden.
* **limit**: definiert die maximale Anzahle an Jobs, die von einem GitLab Runner parallel gestartet werden können.

## Beispiel .gitlab-ci.yml

``` yml
variables:
    GIT_CLEAN_FLAGS: -f -d -x

cache:
  paths:
    - name_of_to_cached_file

stages:
    - build
    - test
    - deploy

before_script:
    - >
      function Build-Linux-Target {
          """ do build """
      }

    - >
      function Build-Win-Target {
          """ do build """
      }

    - >
      function Run-Tests {
          """ do test """
      }
    - >
      function Deploy {
          """ do test """
      }

job1:
  stage: build
  artifacts:
    expire_in: '10 mins'
    paths:
      - artifact_name
  script:
    """ do build """
    - Build-Linux-Target

job2:
  stage: build
  script:
    """ do build """
    - Build-Win-Target

job3:
  stage: test
  script:
    """ do tests """
   - Run-Tests
  dependencies:
   - artifact_name

job4:
  stage: deploy
  script:
    """ do stuff """
    - Deploy
  dependencies:
   - artifact_name
```

**Beschreibung**:

* **Stages** dienen der Gruppierung und Bestimmung der Ausführungsreihenfolge von Jobs. So gibt es in unserem Beispiel 3 Stages (build, test, und deploy). Alle werden im Schlüssel stages zu Beginn der yml-Datei angelegt. Die hier angegebene Reihenfolge legt fest, dass als erstes alle Jobs der Stage build ausgeführt werden müssen, bevor ein Job der Stage test ausgeführt wird

* **Jobs** müssen immer zu einer Stage gehören - bewschrieben durch den Schlüssel stage. Jobs beinhalten die einzelnen Schritte - beschrieben mittels des Schlüssels script - die in diesem Job ausgeführt werden.
Gehören mehrere Jobs zu einer Stage können diese prinzipiell parallel ausgeführt werden. Vorausgesetzt die Gitlab Runner Konfiguration ist entsprechend so konfiguriert (concurrent und limit)
* **cache**: mit Hilfe von Caching kann man vermeiden, dass vorhandene Pakete wiederholt installiert werden.
* **artifacts**: Durch diesen Schlüssel werden die Artefakte eines Jobs 
definiert. Ein Artefakt (Ordner bzw. Dateien), dass in einer Stage von einem Job hergestellt worden ist, kann so von einer zukünftigen Stage weiter verwendet werden. D.h. das Artefakt braucht nur einmal erzeugt zu werden. Neben der klareren Struktur ergibt sich auch hier eine Zeitersparnis, denn das Artefakt braucht nicht erneut generiert zu werden.
* **dependencies**: Hat ein Job eine Abhängigkeit zu einem Artefakt, so kann er nur erfolgreich ausgeführt werden, wenn das Artefakt auch wirklich existiert bzw. generiert worden ist. Mit dem Schlüssel dependencies wird klargestellt, dass ein Job von der Ausführung eines oder mehreren Jobs einer vorher ausgeführten Stage abhängt.
