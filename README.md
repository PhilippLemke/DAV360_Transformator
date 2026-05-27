# DAV360_Transformator
-> Dieses Repository basiert auf einem Fork von matmuc/DAV360_Transformator

Konvertiere Touren und Gruppenveranstaltungen für den Import in DAV360 PIMCORE Redaktionstool.

Das System unterscheidet zwischen Touren, Veranstaltungen und Kursen.

# Input
Die Inputdateien können z.B. durch Microsoft&reg; Forms&trade; Formulare erzeugt werden, in die die Touren und Veranstaltungen eingetragen werden.
Es wird dabei zwischen "normalen" Touren und Touren durch Gruppen unterschieden. Gruppen haben zudem auch Veranstaltungen, die ein anderes Format haben.

Viele Attribute werden in DAV360 über IDs referneziert, die Zuordnung zwischen IDs und Werten ist in der Datei keys.xlsx. Diese muss Sektionsspezifisch angepasst werden.

# Hinweise:
- Es waren bei einem Import ID-Pfade doppelt, daher konnte es nicht importiert werden.
- Beim Import durch DAV des Winterporgramms kam es 2024 zu einem Fehler dass die Uhrzeiten um 1h falsch waren, vermutlich weil in dem Zeitbereich die Uhrumstellung war, 2025 habe ich darauf hingwewiesen und es hat alles gepasst.

# Transformator starten

## Voraussetzungen
- Git Installiert für Windows z.B. hier downloaden https://git-scm.com/install/windows
- Python 3.7 oder höher


## Setup

### 1. Github Repository auf dem eigenen Rechner auschecken / clonen
Eingabeaufforderung / CMD Terminal öffnen und folgenden Befehle eingeben:

```bash
git clone https://github.com/PhilippLemke/DAV360_Transformator.git
cd DAV360_Transformator
```

### 2. Virtuelle Python-Umgebung erstellen
```bash
python3 -m venv venv
```

### 3. Virtuelle Umgebung aktivieren
#### macOS / Linux:
```bash
source venv/bin/activate
```

#### Windows:
```bash
venv\Scripts\activate
```

### 4. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

## Transformator ausführen

Beispiel für 
### Touren:
```bash
python TourenTransformatorMSF.py dummy_daten/TAK_Touren.xlsx
```
### Veranstaltungen:
```bash
python VeranstaltungsTransformatorMSF.py dummy_daten/DAV-Trier_Eingabeformular_Wanderungen_eintaegig.xlsx
```

### Gruppenveranstaltungen:

```bash
python GruppenTransformatorMSF.py "TAK Gruppen Eingabeformular.xlsx"
```
## Exportierte Dateien
Diese werden automatisch im  Ordner 📂 export abglegt.


## Virtuelle Umgebung deaktivieren
```bash
deactivate
```
