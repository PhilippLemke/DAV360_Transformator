# DAV360_Transformator
-> Dieses Repository basiert auf einem Fork von matmuc/DAV360_Transformator

Konvertiert Touren- und Veranstaltungs-Eingabeformulare (Excel) für den Import in das DAV360 PIMCORE Redaktionstool.

# Voraussetzungen
- Git installiert, z.B. für Windows hier downloaden: https://git-scm.com/install/windows
- Python 3.7 oder höher

# Setup

```bash
git clone https://github.com/PhilippLemke/DAV360_Transformator.git
cd DAV360_Transformator
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

# Transformator ausführen

```bash
python transformator.py <typ> --variante <variante> <eingabedatei.xlsx>
```

- `<typ>`: `touren` oder `veranstaltungen`
- `<variante>`: welches Eingabeformular verwendet wurde - `msf`, `tr` oder `gruppen`

Beispiele mit den mitgelieferten Beispieldatensätzen:

```bash
python transformator.py touren --variante msf dummy_daten/touren_msf_beispiel.xlsx
python transformator.py touren --variante tr dummy_daten/touren_tr_beispiel.xlsx
python transformator.py veranstaltungen --variante msf dummy_daten/veranstaltungen_msf_beispiel.xlsx
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

# Tests (optional)

```bash
pip install -r requirements-dev.txt
pytest
```

# Virtuelle Umgebung deaktivieren
```bash
deactivate
```
