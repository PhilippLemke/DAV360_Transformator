# DAV360 Transformator - Transform-Funktionen
# GNU General Public License v3.0
#
# Diese Funktionen werden von transformator.py anhand des "transform:"
# Schlüssels in profiles.yaml aufgerufen. Sie sind bewusst als einfache,
# benannte Bausteine gehalten (kein generischer Ausdrucks-Interpreter),
# damit jede Transformation weiterhin normaler, lesbarer Python-Code bleibt.

import re

import pandas

# Spec-Schlüssel, deren Wert kein Spaltenname aus der Eingabedatei ist
# (sondern ein Literal, eine Tabellenreferenz o.ä.). Alles andere in einer
# Feld-Spec wird als benötigte Eingabespalte gewertet, siehe
# required_columns_for_field().
NON_COLUMN_SPEC_KEYS = {"transform", "value", "table", "wrap", "template", "mandatory", "label", "prefix"}


def required_columns_for_field(spec):
    """Ermittelt, welche Eingabespalten eine einzelne Feld-Spec aus profiles.yaml referenziert."""
    columns = []
    for key, val in spec.items():
        if key in NON_COLUMN_SPEC_KEYS:
            continue
        if isinstance(val, list):
            columns.extend(val)
        elif isinstance(val, str):
            columns.append(val)
    return columns


def required_columns_for_variant(variant_spec):
    """Ermittelt alle von einer Formular-Variante benötigten Eingabespalten (für einen Vorab-Check)."""
    columns = set()
    row_filter = variant_spec.get("filter")
    if row_filter is not None:
        columns.add(row_filter["column"])
    for spec in variant_spec.get("fields", {}).values():
        columns.update(required_columns_for_field(spec))
    return columns


def _clean(value):
    """Wandelt NaN/None/beliebige Werte robust in einen String um."""
    if value is None:
        return ""
    text = str(value)
    return "" if text == "nan" else text


def _strip_parentheses_and_spaces(titel):
    titel = re.sub(r"\(.*\)", "", str(titel))
    return titel.replace(" ", "")


def make_html(text):
    text = _clean(text)
    if len(text) == 0:
        return ""
    return "<p>" + text.replace("\n", "<br />").replace("\r", "") + "</p>"


def get_numbers_from_string(raw, label="_", mandatory=False):
    text = _clean(raw).strip()
    default = 99 if mandatory else 0
    if len(text) == 0:
        if mandatory:
            print(f'ERROR: Feld "{label}" ist leer, verwende {default}.')
        return default
    if text == "unbegrenzt":
        return 99
    match = re.compile(r"([\d,.]+)\s*(\w*)").match(text)
    if not match:
        print(f'WARNING: Konnte aus "{text}" keine Zahl lesen (Feld "{label}"), verwende {default}.')
        return default
    return match.group(1)


def get_max_participants(raw):
    return get_numbers_from_string(raw, "max. Zahl der Teilnehmenden", mandatory=True)


def get_ja_nein(text):
    text = _clean(text)
    if text == "ja":
        return 1
    if text == "nein":
        return 0
    return -1


_DATE_PARTS_RE = re.compile(r"^(\d{1,4})[./\-](\d{1,4})[./\-](\d{1,4})$")


def _parse_date(value, label="Datum"):
    """Wandelt einen Zellwert robust in ein datetime-Objekt um (oder None).

    Excel erkennt Zellen, die im amerikanischen Format (Monat.Tag.Jahr bzw.
    Monat/Tag/Jahr) eingetippt wurden, in einer deutsch formatierten Spalte
    (Tag.Monat.Jahr) oft nicht als Datum und legt sie als Text ab (z.B.
    "2.21.2027" für den 21. Februar 2027). pandas liest solche Zellen dann
    als Rohtext statt als Timestamp. Ist der zweite Teil eindeutig nur als
    Tag gültig (>12) und der erste nur als Monat (<=12), handelt es sich
    zweifelsfrei um das amerikanische Format - das wird hier automatisch
    erkannt und umgerechnet. In allen anderen Fällen (z.B. "5.1.2026") bleibt
    es beim üblichen deutschen Tag-zuerst-Format.
    """
    if value is None:
        return None
    if hasattr(value, "strftime"):
        return None if pandas.isna(value) else value
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None

    match = _DATE_PARTS_RE.match(text)
    if match:
        teil1, teil2, jahr = (int(teil) for teil in match.groups())
        if teil1 <= 12 and teil2 > 12:
            try:
                parsed = pandas.Timestamp(year=jahr, month=teil1, day=teil2)
            except ValueError:
                parsed = None
            if parsed is not None:
                print(
                    f'WARNING: Feld "{label}" enthält "{text}" im amerikanischen Datumsformat '
                    f'(Monat.Tag.Jahr statt Tag.Monat.Jahr), interpretiere automatisch als '
                    f'{parsed.strftime("%d.%m.%Y")}. Bitte in der Eingabedatei auf deutsches '
                    f'Format (Tag.Monat.Jahr) korrigieren.'
                )
                return parsed

    parsed = pandas.to_datetime(text, dayfirst=True, errors="coerce")
    if not pandas.isna(parsed):
        return parsed
    print(f'ERROR: Feld "{label}" enthält "{text}", das ist kein gültiges Datum.')
    return None


def get_dates(termin1, termin2, label_start="Termin (Start)", label_end="Termin (Ende)"):
    termin1 = _parse_date(termin1, label_start)
    if termin1 is None:
        print(f'ERROR: Feld "{label_start}" enthält kein gültiges Datum, "Termine" bleibt leer.')
        return ""
    start = termin1.strftime("%Y-%m-%d")
    termin2 = _parse_date(termin2, label_end)
    if termin2 is None:
        print(f'WARNING: Feld "{label_end}" enthält kein gültiges Datum, verwende "{label_start}" auch als Ende.')
        ende = start
    else:
        ende = termin2.strftime("%Y-%m-%d")
    return f"[dates]{start} 00:00:00 bis {ende} 23:59:59"


def get_date(termin1, label="Datum"):
    termin1 = _parse_date(termin1, label)
    if termin1 is None:
        print(f'WARNING: Feld "{label}" enthält kein gültiges Datum, verwende leeren Wert.')
        return ""
    return termin1.strftime("%Y-%m-%d")


def get_dates_with_time(datum, zeit_str, label="Termin (Datum)"):
    datum = _parse_date(datum, label)
    if datum is None:
        print(f'ERROR: Feld "{label}" enthält kein gültiges Datum, "Termine" bleibt leer.')
        return ""
    zeit_str = _clean(zeit_str).strip()
    try:
        stunde, minute = (int(teil) for teil in zeit_str.split(":")[:2])
    except ValueError:
        print(f'WARNING: Konnte aus "{zeit_str}" keine Uhrzeit lesen, verwende 00:00.')
        stunde, minute = 0, 0
    tag = datum.strftime("%Y-%m-%d")
    start = f"{tag} {stunde:02d}:{minute:02d}:00"
    ende = f"{tag} 23:59:59"
    return f"[dates]{start} bis {ende}"


def get_leaders(text, tourenfuehrer):
    text = _clean(text)
    text = (
        text.replace(" und ", ",")
        .replace(" & ", ",")
        .replace("Dr. med.", "")
        .replace("Dr.med.", "")
        .replace("Dr.", "")
    )
    fullpaths = []
    for leader in text.split(","):
        name = leader.strip()
        if not name:
            continue
        entry = tourenfuehrer.get(name)
        if entry is None:
            print(f'ERROR: Tourenführer "{name}" ist nicht in mapping.yaml (tourenfuehrer) bekannt.')
        else:
            fullpaths.append(entry["fullpath"])
    return ",".join(fullpaths)


def lookup_id(mapping, table_name, key_name):
    table = getattr(mapping, table_name)
    entry = table.get(key_name)
    if entry is None:
        print(f'WARNING: Wert "{key_name}" nicht in mapping.yaml ({table_name}) gefunden.')
        return ""
    if isinstance(entry, dict):
        return entry.get("id", "")
    return entry


def get_kategorie_short_code(mapping, kategorie_name):
    entry = mapping.kategorie.get(kategorie_name)
    if entry is None:
        print(f'WARNING: Kategorie "{kategorie_name}" nicht in mapping.yaml (kategorie) gefunden.')
        return ""
    return entry.get("short_code", "")


def get_key(mapping, titel, kategorie_name, datum, label="Datum"):
    titel_clean = _strip_parentheses_and_spaces(titel)
    short_code = get_kategorie_short_code(mapping, kategorie_name)
    datum = _parse_date(datum, label)
    if datum is None:
        print(f'ERROR: Feld "{label}" enthält kein gültiges Datum, "key" ist unvollständig.')
        return short_code + titel_clean
    return datum.strftime("%y%m") + short_code + titel_clean


def get_group_entry(mapping, name):
    entry = mapping.gruppen.get(name)
    if entry is None:
        print(f'WARNING: Gruppe "{name}" nicht in mapping.yaml (gruppen) gefunden.')
    return entry or {}


def get_group_fullpath(mapping, name):
    return get_group_entry(mapping, name).get("fullpath") or ""


def get_group_image(mapping, name):
    return get_group_entry(mapping, name).get("image_path") or ""


def get_group_short_code(mapping, name):
    return get_group_entry(mapping, name).get("short_code") or ""


def get_key_groups(mapping, titel, gruppe_name, datum, label="Datum"):
    titel_clean = _strip_parentheses_and_spaces(titel)
    short_code = get_group_short_code(mapping, gruppe_name)
    datum = _parse_date(datum, label)
    if datum is None:
        print(f'ERROR: Feld "{label}" enthält kein gültiges Datum, "key" ist unvollständig.')
        return short_code + titel_clean
    return short_code + datum.strftime("%y%m") + titel_clean


def get_kategorie_for_gruppe(mapping, gruppe_name):
    kategorie_name = mapping.gruppe_kategorie.get(gruppe_name)
    if kategorie_name is None:
        return ""
    return lookup_id(mapping, "kategorie", kategorie_name)


def get_booking_code_gruppen(mapping, prefix, gruppe_name, row_id, program_year):
    short_code = get_group_short_code(mapping, gruppe_name)
    return f"{prefix}_{short_code}_{program_year}_{_clean(row_id)}"


def render_template(template, sources, row):
    rendered = template
    for column in sources:
        rendered = rendered.replace("{{" + column + "}}", _clean(row.get(column)))
    return rendered


def dispatch(spec, row, mapping, season_ctx):
    """Wertet eine einzelne Feld-Transformation aus profiles.yaml für eine Zeile aus."""
    transform = spec["transform"]

    if transform == "static":
        return spec["value"]

    if transform == "direct":
        return row.get(spec["source"])

    if transform == "html":
        return make_html(row.get(spec["source"]))

    if transform == "numbers":
        return get_numbers_from_string(row.get(spec["source"]), spec.get("label", spec["source"]), spec.get("mandatory", False))

    if transform == "max_participants":
        return get_max_participants(row.get(spec["source"]))

    if transform == "ja_nein":
        return get_ja_nein(row.get(spec["source"]))

    if transform == "date":
        return get_date(row.get(spec["source"]), spec["source"])

    if transform == "dates_range":
        return get_dates(row.get(spec["start"]), row.get(spec["end"]), spec["start"], spec["end"])

    if transform == "date_with_time":
        return get_dates_with_time(row.get(spec["date"]), row.get(spec["time"]), spec["date"])

    if transform == "leaders":
        return get_leaders(row.get(spec["source"]), mapping.tourenfuehrer)

    if transform == "lookup":
        key_name = spec["value"] if "value" in spec else row.get(spec["source"])
        return lookup_id(mapping, spec["table"], key_name)

    if transform == "key_touren":
        return get_key(mapping, row.get(spec["title"]), row.get(spec["kategorie"]), row.get(spec["date"]), spec["date"])

    if transform == "key_gruppen":
        return get_key_groups(mapping, row.get(spec["title"]), row.get(spec["gruppe"]), row.get(spec["date"]), spec["date"])

    if transform == "group_fullpath":
        return get_group_fullpath(mapping, row.get(spec["source"]))

    if transform == "group_image":
        return get_group_image(mapping, row.get(spec["source"]))

    if transform == "gruppe_kategorie":
        return get_kategorie_for_gruppe(mapping, row.get(spec["source"]))

    if transform == "booking_code_gruppen":
        return get_booking_code_gruppen(
            mapping,
            spec["prefix"],
            row.get(spec["gruppe"]),
            row.get(spec["id"]),
            season_ctx.program_year,
        )

    if transform == "season_id":
        return lookup_id(mapping, "saison", season_ctx.season_name)

    if transform == "template":
        rendered = render_template(spec["template"], spec["sources"], row)
        return make_html(rendered) if spec.get("wrap") == "html" else rendered

    raise ValueError(f'Unbekannte Transformation "{transform}" in profiles.yaml')
