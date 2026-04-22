# DAV360_Transformator
Konvertiere Touren und Gruppenveranstaltungen für den Import in DAV360

Die Inputdateien werden bei uns durch zwei Microsoft&reg; Forms&trade; Formulare erzeugt, in die die Touren und Veranstaltungen eingetragen werden.
Es wird dabei zwischen "normalen" Touren und Touren durch Gruppen unterschieden. Gruppen haben zudem auch Veranstaltungen, die ein anderes Format haben.

Viele Attribute werden in DAV360 über IDs referneziert, die Zuordnung zwischen IDs und Werten ist in der Datei keys.xlsx. Diese muss Sektionsspezifisch angepasst werden.

# Hinweise:
- Es waren bei einem Import ID-Pfade doppelt, daher konnte es nicht importiert werden.
- Beim Import durch DAV des Winterporgramms kam es 2024 zu einem Fehler dass die Uhrzeiten um 1h falsch waren, vermutlich weil in dem Zeitbereich die Uhrumstellung war, 2025 habe ich darauf hingwewiesen und es hat alles gepasst.

# Transformator starten

## Voraussetzungen
- Python 3.7 oder höher

## Setup

### 1. Github Repository auf dem eigenen Rechner auschecken / clonen
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

```bash
python TourenTransformatorMSF.py "Toureneingabe.xlsx"
```

oder für Gruppenveranstaltungen:

```bash
python GruppenTransformatorMSF.py "TAK Gruppen Eingabeformular.xlsx"
```

## Virtuelle Umgebung deaktivieren
```bash
deactivate
```