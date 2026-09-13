# DAV360 Transformator - Transform-Funktionen
# GNU General Public License v3.0
#
# Diese Funktionen werden von transformator.py anhand des "transform:"
# Schlüssels in profiles.yaml aufgerufen. Sie sind bewusst als einfache,
# benannte Bausteine gehalten (kein generischer Ausdrucks-Interpreter),
# damit jede Transformation weiterhin normaler, lesbarer Python-Code bleibt.

import re


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


def get_dates(termin1, termin2):
    try:
        return (
            "[dates]"
            + termin1.strftime("%Y-%m-%d")
            + " 00:00:00 bis "
            + termin2.strftime("%Y-%m-%d")
            + " 23:59:59"
        )
    except AttributeError:
        return (
            "[dates]"
            + termin1.strftime("%Y-%m-%d")
            + " 00:00:00 bis "
            + termin1.strftime("%Y-%m-%d")
            + " 23:59:59"
        )


def get_date(termin1):
    return termin1.strftime("%Y-%m-%d")


def get_dates_with_time(datum, zeit_str):
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


def get_key(mapping, titel, kategorie_name, datum):
    titel_clean = _strip_parentheses_and_spaces(titel)
    short_code = get_kategorie_short_code(mapping, kategorie_name)
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


def get_key_groups(mapping, titel, gruppe_name, datum):
    titel_clean = _strip_parentheses_and_spaces(titel)
    short_code = get_group_short_code(mapping, gruppe_name)
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
        return get_date(row.get(spec["source"]))

    if transform == "dates_range":
        return get_dates(row.get(spec["start"]), row.get(spec["end"]))

    if transform == "date_with_time":
        return get_dates_with_time(row.get(spec["date"]), row.get(spec["time"]))

    if transform == "leaders":
        return get_leaders(row.get(spec["source"]), mapping.tourenfuehrer)

    if transform == "lookup":
        key_name = spec["value"] if "value" in spec else row.get(spec["source"])
        return lookup_id(mapping, spec["table"], key_name)

    if transform == "key_touren":
        return get_key(mapping, row.get(spec["title"]), row.get(spec["kategorie"]), row.get(spec["date"]))

    if transform == "key_gruppen":
        return get_key_groups(mapping, row.get(spec["title"]), row.get(spec["gruppe"]), row.get(spec["date"]))

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
