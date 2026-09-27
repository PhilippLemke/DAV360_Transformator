# DAV360_Transformator
-> Dieses Repository basiert auf einem Fork von matmuc/DAV360_Transformator

Konvertiert Touren- und Veranstaltungs-Eingabeformulare (Excel) für den Import in das DAV360 PIMCORE Redaktionstool.

# Voraussetzungen
- Git installiert, z.B. für Windows hier downloaden: https://git-scm.com/install/windows
- Python 3.7 oder höher

# Setup

## Windows
Eingabeaufforderung (cmd):
```bat
git clone https://github.com/PhilippLemke/DAV360_Transformator.git
cd DAV360_Transformator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
In der PowerShell stattdessen `venv\Scripts\Activate.ps1` zum Aktivieren verwenden.
In Git Bash: `source venv/Scripts/activate`.

## Linux / Mac
```bash
git clone https://github.com/PhilippLemke/DAV360_Transformator.git
cd DAV360_Transformator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
# Transformator ausführen

```bash
python transformator.py <typ> --variante <variante> <eingabedatei.xlsx>
```

- `<typ>`: `touren`, `veranstaltungen` oder `kurse`
- `<variante>`: welches Eingabeformular verwendet wurde - je nach Typ `tak`, `tr` oder `gruppen`
  (`tak` = ursprüngliches Formular aus dem Fork-Original, `tr` = Sektion-Trier-eigenes Formular)
- `--zusatz-mapping <datei.yaml>` (optional): ergänzt bzw. überschreibt Einträge der Tabellen aus `mapping.yaml`.
  Gedacht für Stammdaten, die nicht ins Repo sollen, z.B. die Tourenführer:innen mit echten Namen. Die Datei
  hat denselben Aufbau wie `mapping.yaml` und braucht nur die Tabellen, die ergänzt werden sollen.

Beispiele mit den mitgelieferten Beispieldatensätzen:

```bash
python transformator.py touren --variante tak dummy_daten/touren_tak_beispiel.xlsx
python transformator.py touren --variante tr dummy_daten/touren_tr_beispiel.xlsx
python transformator.py veranstaltungen --variante tr dummy_daten/veranstaltungen_tr_beispiel.xlsx
```

Ein Gruppen-Eingabeformular enthält sowohl Touren als auch Veranstaltungen und wird deshalb zweimal aufgerufen (einmal je Typ):

```bash
python transformator.py touren --variante gruppen dummy_daten/gruppen_beispiel.xlsx
python transformator.py veranstaltungen --variante gruppen dummy_daten/gruppen_beispiel.xlsx
```

Die erzeugten Dateien landen automatisch im Ordner 📂 `export`.

# Konfiguration

- `mapping.yaml` - sektionsspezifische Stammdaten (Kategorien, Tourenführer, Gruppen, Pimcore-IDs). **Muss pro Sektion angepasst werden.**
- `config.yaml` - Tool-Verhalten (Output-Ordner, Season-Logik)
- `profiles.yaml` - Spalten-Zuordnung je Typ/Variante

# Hinweise
- Es waren bei einem Import ID-Pfade doppelt, daher konnte es nicht importiert werden.
- Beim Import durch DAV des Winterprogramms kam es 2024 zu einem Fehler, dass die Uhrzeiten um 1h falsch waren, vermutlich weil in dem Zeitbereich die Uhrumstellung war, 2025 habe ich darauf hingewiesen und es hat alles gepasst.
- Der Typ `kurse` (Variante `tr`, DAV-Trier Kurs-Eingabeformular) deckt noch nicht alle Zielfelder ab: `locations` (Pimcore-Objekt für den Veranstaltungsort) bleibt bewusst leer, der Veranstaltungsort landet als Freitext in `destination`. Betroffene Zeilen/Felder werden beim Ausführen mit `WARNING`/`ERROR` markiert, der Import selbst läuft aber durch.
- Bei Touren und Kursen (Variante `tr`) wird `assignedGroups` aus der Kategorie abgeleitet (`mapping.yaml`, `kategorie.*.gruppe`); die Formularspalte "Gruppen" wird nicht mehr gelesen. Kategorien ohne feste Gruppe (z.B. Ski) bleiben leer.
- `bookingState` wird bei Touren und Kursen (Variante `tr`) auf "wenige frei" gesetzt, wenn die *maximale* Teilnehmerzahl höchstens 10 beträgt. Sonst bleibt das Feld leer und wird weiterhin in Pimcore gepflegt.

# Tests (optional)

```bash
pip install -r requirements-dev.txt
pytest
```

# Virtuelle Umgebung deaktivieren
```bash
deactivate
```
