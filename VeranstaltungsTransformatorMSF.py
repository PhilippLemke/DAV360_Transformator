# Excel Transformator for DAV Trier
# Matthias Vogt, Februar 2024
# Berenike Meyer, Mai 2026
# GNU General Public License v3.0

# Transformiert eine "DAV-Trier Eingabeformular Wanderungen - eintägig.xlsx" bzw.
# übergebene Excel Datei von Microsoft-Forms in das Format für den Pimcore Import (PimcoreOut.xlsx)
# Es müssen die Spalten Lfd-Nr. und Kategorie (Zeilen immer Veranstaltung) ergänzt werden
# benötigt dazu auch die Datei Keys.xlsx die die Umschlüsselungen enthält.
# benötigt TakExcelTransformLib.py
# Doku der verwendeten Libs zum lesen und schreiben der xlsx Dateien:
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
# https://openpyxl.readthedocs.io/en/latest/api/openpyxl.html

import pandas, openpyxl, re, sys, os, TakExcelTransformLib
from datetime import datetime

if __name__ == "__main__":
    TakExcelTransformLib.init()

    if len(sys.argv) > 1:
        inFileVeranstaltungen = sys.argv[1]
    else:
        inFileVeranstaltungen = "DAV-Trier Eingabeformular Wanderungen - eintägig.xlsx"
    if not os.path.exists(inFileVeranstaltungen):
        print(f"ERROR: given file {inFileVeranstaltungen} does not exist! -> Exit")
        os._exit(os.EX_NOINPUT)
    else:
        print(f"using Input file {inFileVeranstaltungen}")
    Season = "Sommer"
    if (
        datetime.today().month > 6
    ):  # Wenn Juli oder später ausgeführt wird es wohl das Winterprogramm sein
        Season = "Winter"
    ProgramYear = datetime.today().year
    if Season == "Winter":
        ProgramYear = (
            datetime.today().year
        ) + 1  # Winterprogramm wird für das Folgejahr erstellt
    SeasonID = Season + "" + str(ProgramYear)
    print("SeasonID: " + SeasonID)
    outDir = "export" if os.path.isdir("export") else "."
    outFile = os.path.join(outDir, "DAV_Veranstaltungsexport_" + SeasonID + ".xlsx")

    #
    # write Output by OpenPYXL
    #
    VeranstaltungenFormIn = pandas.read_excel(inFileVeranstaltungen)
    VeranstaltungenFormIn = (
        VeranstaltungenFormIn.reset_index()
    )  # make sure indexes pair with number of rows

    wbOut = openpyxl.Workbook()
    sheetOut = wbOut.active
    sheetOut.title = "Veranstaltungen"

    ColumnsVeranstaltungen = {
        "key": 1,
        "bookingCode": 2,
        "title": 3,
        "subtitlr": 4,
        "description": 5,
        "Termine": 6,
        "datesAlternativeText": 7,
        "assignedGroups": 8,
        "locations": 9,
        "leaders": 10,
        "destination": 11,
        "images": 12,
        "maxNumberOfParticipants": 13,
        "bookingState": 14,
        "prices": 15,
        "previewDiscussion": 16,
        "registerStart": 17,
        "registerEnd": 18,
        "registration": 19,
        "enquiryForm": 20,
        "meetingPoint": 21,
        "arrivalHints": 22,
        "isPublicTransportAvailable": 23,
        "teaserTitle": 24,
        "teaserSubtitle": 25,
        "teaserAbstract": 26,
        "teaserImage": 27,
    }
    ci = 1
    for col in ColumnsVeranstaltungen:
        sheetOut.cell(row=1, column=ci).value = col
        ci = ci + 1
    ri = 2
    for index, inFormRow in VeranstaltungenFormIn.iterrows():
        titel = inFormRow["Bezeichnung/Titel"]
        kategorie = inFormRow["Kategorie"]
        gruppe = inFormRow["Gruppe"]
        # date = TakExcelTransformLib.getDatefromStr(inFormRow['Termin (Start)'])
        date = inFormRow["Termin (Datum)"]
        time = inFormRow["Startzeit (bitte angeben im Format HH:MM)"]
        # enddate = inFormRow["Termin (Ende)"]
        print(
            f"Processing Veranstaltung: {titel}, von {date} "
        )  # hier {kategorie}: vor {titel} un bis {enddate} nach {date} gelöscht
        # Anmeldeschluss = inFormRow["Anmeldeschluss"]
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["key"]).value = (
            TakExcelTransformLib.getKey(titel, inFormRow["Kategorie"], date)
        )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen['assignedGroups']).value = '/264 - Sektion Trier/Gruppen/Allgemein'
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["assignedGroups"]).value = (
            TakExcelTransformLib.Gruppen[gruppe].get("fullpath", "")
        )
        # sheetOut.cell(row=ri, column=Columns['bookingCode']).value = getBookingcode(row['Titel'],row['Kategorie'],date)
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen['bookingCode']).value = 'T' + str(ProgramYear) + '_' + str(inFormRow['ID'])
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["bookingCode"]).value = (
            inFormRow["Lfd-Nr."]
        )
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["title"]).value = titel
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["category"]).value = (
        #     TakExcelTransformLib.Kategorie[kategorie]
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["technique"]).value = (
        #     TakExcelTransformLib.Technik[inFormRow["Schwierigkeit"]]
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["stamina"]).value = (
        #     TakExcelTransformLib.Ausdauer[inFormRow["Kondition"]]
        # )
        Profil = str(inFormRow["Profil"])
        Dauer = str(inFormRow["Dauer"])
        Beschreibung = str(inFormRow["Beschreibung"])
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["description"]).value = (
            TakExcelTransformLib.makeHTML(Beschreibung + " Profil: " + Profil + ", Dauer: " + Dauer)
        )
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["Termine"]).value = (
            TakExcelTransformLib.getDates(date, time)
        )
        sheetOut.cell(
            row=ri, column=ColumnsVeranstaltungen["datesAlternativeText"]
        ).value = "<p>&nbsp;</p>"
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["leaders"]).value = (
            TakExcelTransformLib.getLeaders(inFormRow["Leitung/Organisation"])
        )
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["destination"]).value = (
            TakExcelTransformLib.makeHTML(inFormRow["Schlusseinkehr"])
        )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["season"]).value = (
        #     TakExcelTransformLib.Saison[Season]
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["characteristic"]).value = (
        #     TakExcelTransformLib.Eventart[inFormRow["Klassifizierung"]]
        # )  # Achtung das ist im Formular verdreht
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["classification"]).value = (
        #    TakExcelTransformLib.Klassifizierung[inFormRow["Tourenart"]]
        # )  # Achtung das ist im Formular verdreht
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["requirements"]).value = (
        #     "<p>&nbsp;</p>"
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["maxNumberOfParticipants"]).value = (
        #     TakExcelTransformLib.getMaxNumberOfParticipants(
        #         str(inFormRow["max. Zahl der Teilnehmenden"])
        #     )
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["bookingState"]).value = ""
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["registerEnd"]).value = (
        #     TakExcelTransformLib.getDate(Anmeldeschluss)
        # )
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["meetingPoint"]).value = (
        #     TakExcelTransformLib.makeHTML("")
        # )
        # Entfernung = str(inFormRow["Anfahrt km"])
        # Ausgangsort = str(inFormRow["Ausgangsort"])
        # sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["arrivalHints"]).value = (
        #     TakExcelTransformLib.makeHTML(
        #         "Ausgangsort: " + Ausgangsort + ", Entfernung: " + Entfernung + "km"
        #     )
        # )
        sheetOut.cell(row=ri, column=ColumnsVeranstaltungen["arrivalHints"]).value = (
            TakExcelTransformLib.makeHTML(inFormRow["Treffpunkt"])
        )
        # sheetOut.cell(
        #     row=ri, column=ColumnsVeranstaltungen["isPublicTransportAvailable"]
        # ).value = TakExcelTransformLib.getEinsNull(inFormRow["Öffentliche Anreise"])
        ri = ri + 1
    wbOut.save(outFile)
    print("wrote: " + outFile)
