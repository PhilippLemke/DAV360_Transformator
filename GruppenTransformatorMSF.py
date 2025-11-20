# Excel Transformator for DAV TAK - Gruppenveranstatungen
# Matthias Vogt, Februar 2024
# GNU General Public License v3.0

# Transformiert eine "TAK Gruppen Eingabeformular.xlsx"* von Microsoft-Forms in das Format für den Pimcore Import (PimcoreOut.xlsx)
#    *bzw. eine Datei welche als erstes Argument übergeben wurde
# benötigt dazu auch die Datei Keys.xlsx die die Umschlüsselungen enthält.
# benötigt TakExcelTransformLib.py
# Doku der verwendeten Libs zum lesen und schreiben der xlsx Dateien:
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
# https://openpyxl.readthedocs.io/en/latest/api/openpyxl.html

import pandas, openpyxl, os, sys, re, TakExcelTransformLib
from datetime import datetime

if __name__ == '__main__':
    TakExcelTransformLib.init()

    useSeperateFiles = True # entweder die Touren und Veranstaltungen in separate Blätter in eine Datei (False), oder in separate Files (True)

    if len( sys.argv ) > 1:
        inFileGruppen = sys.argv[1]
    else:
        inFileGruppen = "TAK Gruppen Eingabeformular.xlsx"
    if not os.path.exists(inFileGruppen):
        print(f"ERROR: given file {inFileGruppen} does not exist! -> Exit")
        os._exit(os.EX_NOINPUT)
    else:
        print(f"using Input file {inFileGruppen}")
    
    Season = 'Sommer'
    if(datetime.today().month > 6): #Wenn Juli oder später ausgeführt wird es wohl das Winterprogramm sein
        Season = 'Winter'
    ProgramYear = datetime.today().year
    if( Season == 'Winter'):
        ProgramYear = (datetime.today().year) +1    # Winterprogramm wird für das Folgejahr erstellt
    SeasonID = Season+''+str(ProgramYear)
    print('SeasonID: '+SeasonID)
    if useSeperateFiles:
        outFileTouren = 'DAV_GruppenexportTouren_'+SeasonID+'.xlsx'
        outFileEvents = 'DAV_GruppenexportEvents_'+SeasonID+'.xlsx'
    else:
        outFileTouren = 'DAV_GruppenexportEventsTouren_'+SeasonID+'.xlsx'

    #
    # write Output by OpenPYXL
    #
    GruppenFormIn = pandas.read_excel(inFileGruppen)
    GruppenFormIn = GruppenFormIn.reset_index()  # make sure indexes pair with number of rows

    wbOutTouren = openpyxl.Workbook()
    sheetTouren = wbOutTouren.active
    sheetTouren.title = "Touren"
    sheetVeranstaltungen = None
    
    if useSeperateFiles:
        wbOutEvents = openpyxl.Workbook()
        sheetVeranstaltungen = wbOutEvents.active
        sheetVeranstaltungen.title = "Veranstaltungen"
        
    else:
        wbOutEvents = wbOutTouren       
        wbOutEvents.create_sheet('Veranstaltungen')
        sheetVeranstaltungen = wbOutTouren["Veranstaltungen"]


    ColumnsTouren = {'key': 1, 'bookingCode': 2, 'title': 3, 'subtitle': 4, 'category': 5, 'technique': 6, 'stamina': 7,
               'description': 8, 'Termine': 9, 'datesAlternativeText': 10, 'assignedGroups': 11,
               'geographicRegions': 12, 'locations': 13, 'leaders': 14, 'destination': 15, 'season': 16,
               'characteristic': 17, 'classification': 18, 'altitude': 19, 'distance': 20, 'stageDuration': 21,
               'requirements': 22, 'equipment': 23, 'attachments': 24, 'images': 25, 'maxNumberOfParticipants': 26,
               'bookingState': 27, 'prices': 28, 'previewDiscussion': 29, 'registerStart': 30, 'registerEnd': 31,
               'registration': 32, 'enquiryForm': 33, 'meetingPoint': 34, 'arrivalHints': 35,
               'isPublicTransportAvailable': 36, 'teaserTitle': 37, 'teaserSubtitle': 38, 'teaserAbstract': 39,
               'teaserImage': 40}
    ci = 1
    for col in ColumnsTouren:
        sheetTouren.cell(row=1, column=ci).value = col
        ci = ci+1

    ColumnsEvents ={'key': 1, 'bookingCode': 2, 'title': 3, 'subtitle': 4, 'description': 5, 'Termine': 6, 'datesAlternativeText': 7,
                    'assignedGroups': 8, 'locations': 9, 'leaders': 10, 'destination': 11, 'images': 12, 'maxNumberOfParticipants': 13,
                    'bookingState': 14, 'prices': 15, 'previewDiscussion': 16, 'registerStart': 17, 'registerEnd': 18, 'registration': 19,
                    'enquiryForm': 20, 'meetingPoint': 21, 'arrivalHints': 22, 'isPublicTransportAvailable': 23, 'teaserTitle': 24,
                    'teaserSubtitle': 25, 'teaserAbstract': 26, 'teaserImage': 27}
    ci = 1
    for col in ColumnsEvents:
        sheetVeranstaltungen.cell(row=1, column=ci).value = col
        ci = ci+1

    riTour = 2
    riEvent = 2
    for index, inFormRow in GruppenFormIn.iterrows():
        Kategorie = inFormRow['Kategorie']
        Gruppe = inFormRow['Gruppe']
        #print("Gruppe: ", Gruppe)
        GrouppeShort = TakExcelTransformLib.GetGroup(Gruppe)['ShortCode']
        date = inFormRow['Termin (Start)']
        enddate = inFormRow['Termin (Ende)']
        Anmeldeschluss = inFormRow['Anmeldeschluss']
        Titel = inFormRow['Bezeichnung/Titel']
        Entfernung = str(inFormRow['Anfahrt km'])
        Ausgangsort = str(inFormRow['Ausgangsort'])

        # Touren und Veranstaltungen in zwei Blätter/Reiter in die Ausgabedatei schreiben. oder in getrennte Dateien.
        
        if(Kategorie == 'Tour'):
            print("Processing Tour: ", inFormRow['Kategorie'], ":", Titel)
            sheetTouren.cell(row=riTour, column=ColumnsTouren['key']).value = TakExcelTransformLib.getKeyGroups(Titel, GrouppeShort, date)
            sheetTouren.cell(row=riTour, column=ColumnsTouren['assignedGroups']).value = TakExcelTransformLib.GetGroup(Gruppe)['fullpath']
            sheetTouren.cell(row=riTour, column=ColumnsTouren['bookingCode']).value = 'T_' +GrouppeShort+'_'+ str(ProgramYear) + '_' + str(inFormRow['ID'])
            #sheetTouren.cell(row=riTour, column=ColumnsTouren['bookingCode']).value = inFormRow['Lfd.Nr.']
            sheetTouren.cell(row=riTour, column=ColumnsTouren['title']).value = Titel
            sheetTouren.cell(row=riTour, column=ColumnsTouren['category']).value = TakExcelTransformLib.getKategorieForGruppe(Gruppe)
            sheetTouren.cell(row=riTour, column=ColumnsTouren['technique']).value = TakExcelTransformLib.Technik[inFormRow['Schwierigkeit']]
            sheetTouren.cell(row=riTour, column=ColumnsTouren['stamina']).value = TakExcelTransformLib.Ausdauer[inFormRow['Kondition']]
            sheetTouren.cell(row=riTour, column=ColumnsTouren['description']).value = TakExcelTransformLib.makeHTML(inFormRow['Beschreibung'])
            sheetTouren.cell(row=riTour, column=ColumnsTouren['Termine']).value = TakExcelTransformLib.getDates(date, enddate)
            sheetTouren.cell(row=riTour, column=ColumnsTouren['datesAlternativeText']).value = '<p>&nbsp;</p>'
            sheetTouren.cell(row=riTour, column=ColumnsTouren['leaders']).value = TakExcelTransformLib.getLeaders(inFormRow['Tourenleitung/Organisation'])
            sheetTouren.cell(row=riTour, column=ColumnsTouren['destination']).value = TakExcelTransformLib.makeHTML(inFormRow['Gebirgsgruppe/Region/Ort'])
            sheetTouren.cell(row=riTour, column=ColumnsTouren['season']).value = TakExcelTransformLib.Saison[Season]
            sheetTouren.cell(row=riTour, column=ColumnsTouren['characteristic']).value = TakExcelTransformLib.Eventart[inFormRow['Klassifizierung']] #Achtung das ist im Formular verdreht
            sheetTouren.cell(row=riTour, column=ColumnsTouren['classification']).value = TakExcelTransformLib.Klassifizierung['Gemeinschaftstour']
            sheetTouren.cell(row=riTour, column=ColumnsTouren['requirements']).value = '<p>&nbsp;</p>'
            sheetTouren.cell(row=riTour, column=ColumnsTouren['maxNumberOfParticipants']).value = TakExcelTransformLib.getMaxNumberOfParticipants(str(inFormRow['max. Zahl der Teilnehmenden']))
            sheetTouren.cell(row=riTour, column=ColumnsTouren['bookingState']).value = ''
            sheetTouren.cell(row=riTour, column=ColumnsTouren['registerEnd']).value = TakExcelTransformLib.getDate(Anmeldeschluss)
            sheetTouren.cell(row=riTour, column=ColumnsTouren['meetingPoint']).value = TakExcelTransformLib.makeHTML('')
            sheetTouren.cell(row=riTour, column=ColumnsTouren['arrivalHints']).value = TakExcelTransformLib.makeHTML('Ausgangsort: ' + Ausgangsort + ', Entfernung: ' + Entfernung + 'km')
            sheetTouren.cell(row=riTour, column=ColumnsTouren['isPublicTransportAvailable']).value = TakExcelTransformLib.getEinsNull(inFormRow['Öffentliche Anreise'])
            riTour = riTour + 1
        if (Kategorie == 'Veranstaltung'):
            print("Processing Veranstaltung: ", inFormRow['Kategorie'], ":", Titel)
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['key']).value = TakExcelTransformLib.getKeyGroups(Titel, GrouppeShort, date)
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['bookingCode']).value = 'V_' +GrouppeShort+'_'+str(ProgramYear) + '_' + str(inFormRow['ID'])
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['title']).value = Titel
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['subtitle']).value = ''
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['description']).value = TakExcelTransformLib.makeHTML(inFormRow['Beschreibung'])
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['Termine']).value = TakExcelTransformLib.getDates(date, enddate)
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['datesAlternativeText']).value = '<p>&nbsp;</p>'
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['assignedGroups']).value = TakExcelTransformLib.GetGroup(Gruppe)['fullpath']
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['leaders']).value = TakExcelTransformLib.getLeaders(inFormRow['Tourenleitung/Organisation'])
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['maxNumberOfParticipants']).value = TakExcelTransformLib.getMaxNumberOfParticipants(str(inFormRow['max. Zahl der Teilnehmenden']))
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['registerEnd']).value = TakExcelTransformLib.getDate(Anmeldeschluss)
            sheetVeranstaltungen.cell(row=riEvent, column=ColumnsEvents['destination']).value = TakExcelTransformLib.makeHTML(inFormRow['Gebirgsgruppe/Region/Ort'])
            riEvent = riEvent + 1
    
    wbOutTouren.save(outFileTouren)
    print("wrote: "+outFileTouren)
    if useSeperateFiles:
        wbOutEvents.save(outFileEvents)
        print("wrote: "+outFileEvents)

    
