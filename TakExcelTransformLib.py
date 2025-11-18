# Excel Transformator for DAV TAK
# Matthias Vogt, Februar 2024
# GNU General Public License v3.0

# Dies ist die Library für die gemeinsam genutzten Funktionen
# benötigt die Keys.xlsx Datei!

import pandas, openpyxl, re
from datetime import datetime


def readTechnik():
    global Technik
    Technik = {}
    df = pandas.read_excel('Keys.xlsx', 'Technik')
    for sID, name in df.values:
        Technik[name] = sID


def readKategorie():
    global Kategorie
    Kategorie = {}
    global KategorieShort
    KategorieShort = {}
    df = pandas.read_excel('Keys.xlsx', 'Kategorie')
    for sID, name, sc in df.values:
        Kategorie[name] = sID
        KategorieShort[name] = sc


def readAusdauer():
    global Ausdauer
    Ausdauer = {}
    df = pandas.read_excel('Keys.xlsx', 'Ausdauer')
    for sID, name in df.values:
        Ausdauer[name] = sID


def readSaison():
    global Saison
    Saison = {}
    df = pandas.read_excel('Keys.xlsx', 'Saison')
    for sID, name in df.values:
        Saison[name] = sID


def readEventart():
    global Eventart
    Eventart = {}
    df = pandas.read_excel('Keys.xlsx', 'Eventart')
    for sID, name in df.values:
        Eventart[name] = sID


def readKlassifizierung():
    global Klassifizierung
    Klassifizierung = {}
    df = pandas.read_excel('Keys.xlsx', 'Klassifizierung')
    for sID, name in df.values:
        Klassifizierung[name] = sID


def readTourenfuehrer():
    global Tourenfuehrer
    Tourenfuehrer = {}
    df = pandas.read_excel('Keys.xlsx', 'Tourenführer')
    for ID, fullpath, firstName, lastName in df.values:
        name = firstName + ' ' + lastName
        Tourenfuehrer[name] = {}
        Tourenfuehrer[name]['ID'] = ID
        Tourenfuehrer[name]['name'] = name
        Tourenfuehrer[name]['fullpath'] = fullpath
        Tourenfuehrer[name]['firstName'] = firstName
        Tourenfuehrer[name]['lastName'] = lastName


def readGruppen():
    global Gruppen
    Gruppen = {}
    df = pandas.read_excel('Keys.xlsx', 'Gruppen')
    for Gruppe, fullpath, ShortCode in df.values:
        Gruppen[Gruppe] = {}
        Gruppen[Gruppe]['fullpath'] = fullpath
        Gruppen[Gruppe]['ShortCode'] = ShortCode


def getTourenfuehrer(Name):
    for tf in Tourenfuehrer:
        if Tourenfuehrer[tf]['name'] == Name:
            return Tourenfuehrer[tf]
    return None


# Key für Touren
def getKey(Titel, Kategorie, Datum):
    global KategorieShort
    Titel = re.sub(r"\(.*\)", "", Titel)
    Titel = Titel.replace(" ", "")
    Kategorie = KategorieShort[Kategorie]
    return Datum.strftime("%y%m") + Kategorie + Titel


# Key für Gruppenveranstaltungen/Touren'
def getKeyGroups(Titel, Gruppe, Datum):
    global KategorieShort
    Titel = re.sub(r"\(.*\)", "", Titel)
    Titel = Titel.replace(" ", "")
    return Gruppe + Datum.strftime("%y%m") + Titel


def getBookingcode(Titel, Kategorie, Datum):
    Titel = Titel.replace(" ", "")
    if (Kategorie == 'Trailrunning / Berglauf'):
        Kategorie = 'Trailrunning'
    if (Kategorie == 'Senior*innen'):
        Kategorie = 'Senioren'
    return Datum.strftime("%y%m%d") + "_" + Kategorie + "_" + Titel


def getDatefromStr(datestr: str) -> datetime:
    m = re.match(r"[a-zA-Z]{2}\ ([0-9]{2}\.[0-9]{2})\.*$", datestr)
    if m:
        d = datetime.strptime(m.group(1), "%d.%m")
        d.replace(year=datetime.now().year)
        return d


def getDates(Termin1, Termin2):
    try:
        return '[dates]' + Termin1.strftime("%Y-%m-%d") + ' 00:00:00 bis ' + Termin2.strftime("%Y-%m-%d") + ' 23:59:59'
    except:
        return '[dates]' + Termin1.strftime("%Y-%m-%d") + ' 00:00:00 bis ' + Termin1.strftime("%Y-%m-%d") + ' 23:59:59'


def getDate(Termin1):
    return Termin1.strftime("%Y-%m-%d")


def getEinsNull(text):
    if (text == 'ja'):
        return 1
    if (text == 'nein'):
        return 0
    return -1


# Extract the Leaders as Array from Text
def getLeaders(LeadersTxt):
    global Tourenfuehrer  # aus Keys.xlsx
    LeadersOut = ''
    LeadersTxt = LeadersTxt.replace(" und ", ",").replace(" & ", ",") \
        .replace("Dr. med.", "").replace("Dr.med.", "").replace("Dr.", "")
    Leaders = LeadersTxt.split(',')
    for leader in Leaders:
        leader = leader.strip()
        leaderCor = leader
        if leader == "Eri Köhnke":
            leaderCor = "Erika Köhnke"
        tf = getTourenfuehrer(leaderCor)
        if tf is None:
            print(f"ERROR: Tourenführer {leader} ist nicht in der Liste bekannter Tourenführer. (tried: {leaderCor})")
        else:
            if len(LeadersOut) > 2:
                LeadersOut = LeadersOut + ','
            LeadersOut = LeadersOut + tf['fullpath']
    return LeadersOut


def GetGroup(Gruppe):
    global Gruppen
    return Gruppen[Gruppe]


def getKategorieForGruppe(Gruppe):
    match Gruppe:
        case "Mountainbike":
            return Kategorie['Mountainbike']
        case "Mankeis":
            return Kategorie['Familien']
        case "Jugendklettergruppe":
            return Kategorie['Sportklettern']
        case "Familiengruppe":
            return Kategorie['Familien']
        case "Klettertreff":
            return Kategorie['Sportklettern']
        case "Seniorengruppe":
            return Kategorie['Senior*innen']
        case _:
            return ""


def makeHTML(text):
    text = str(text)
    if text == "nan":
        text = ""
    if len(text) == 0:
        return ""
    return "<p>" + text.replace("\n", "<br />").replace("\r", "") + "</p>"


def getMaxNumberOfParticipants(inStr) -> int:
    num = getNumbersFromString(inStr, "getMaxNumberOfParticipants", True)
    if num == 0:
        print("WARNING Number of max Participants is 0, using 99!")
        return 99
    return num


def getNumbersFromString(inStr, Field='_', mandatory=False) -> int:
    inStr = inStr.strip()
    default = 0
    if mandatory:
        default = 99
    if (len(inStr) == 0):
        if mandatory:
            print("ERROR String is empty! Field: \"" + Field + "\"")
        return default
    if inStr == "nan":
        if mandatory:
            print("ERROR String is empty (NaN)! Field: \"" + Field + "\"")
        return default
    elif inStr == "unbegrenzt":
        return 99
    p = re.compile(r'([\d,.]+)\s*(\w*)')
    num = p.match(inStr).group(1)
    return num


def getSesonID():
    Season = 'Sommer'
    if (datetime.today().month > 6):  # Wenn Juli oder später ausgeführt wird es wohl das Winterprogramm sein
        Season = 'Winter'
    ProgramYear = datetime.today().year
    if (Season == 'Winter'):
        ProgramYear = (datetime.today().year) + 1  # Winterprogramm wird für das Folgejahr erstellt
    SeasonID = Season + '' + str(ProgramYear)
    return SeasonID

# Einlesen aller Daten aus der Keys.xlsx
def init():
    readTechnik()
    readKategorie()
    readAusdauer()
    readSaison()
    readEventart()
    readKlassifizierung()
    readTourenfuehrer()
    readGruppen()
