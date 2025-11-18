# Excel Transformator for DAV TAK
# Matthias Vogt, Februar 2024
# GNU General Public License v3.0

# Tranformiert eine "Toureneingabe.xlsx" bzw. übergebene Excel Datei von Microsoft-Forms in das Format für den Pimcore Import (PimcoreOut.xlsx)
# benötigt dazu auch die Datei Keys.xlsx die die Umschlüsselungen enthält.
# benötigt TakExcelTransformLib.py
# Doku der verwendeten Libs zum lesen und schreiben der xlsx Dateien:
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
# https://openpyxl.readthedocs.io/en/latest/api/openpyxl.html

import pandas, openpyxl, re, sys, os, TakExcelTransformLib
from datetime import datetime

if __name__ == '__main__':
    TakExcelTransformLib.init()
    
    if len( sys.argv ) > 1:
        inFileTouren = sys.argv[1]
    else:
        inFileTouren = "Toureneingabe.xlsx"
    if not os.path.exists(inFileTouren):
        print(f"ERROR: given file {inFileTouren} does not exist! -> Exit")
        os._exit(os.EX_NOINPUT)
    else:
        print(f"using Input file {inFileTouren}")
    Season = 'Sommer'
    if(datetime.today().month > 6): #Wenn Juli oder später ausgeführt wird es wohl das Winterprogramm sein
        Season = 'Winter'
    ProgramYear = datetime.today().year
    if( Season == 'Winter'):
        ProgramYear = (datetime.today().year) +1    # Winterprogramm wird für das Folgejahr erstellt
    SeasonID = Season+''+str(ProgramYear)
    print('SeasonID: ' + SeasonID)
    outFile = 'TAK_Tourenexport_'+SeasonID+'.xlsx'

    #
    # write Output by OpenPYXL
    #
    TourenFormIn = pandas.read_excel(inFileTouren)
    TourenFormIn = TourenFormIn.reset_index()  # make sure indexes pair with number of rows

    wbOut = openpyxl.Workbook()
    sheetOut = wbOut.active
    sheetOut.title = "Touren"

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
        sheetOut.cell(row=1, column=ci).value = col
        ci = ci+1
    ri=2
    for index, inFormRow in TourenFormIn.iterrows():
        titel = inFormRow['Bezeichnung/Titel']
        kategorie = inFormRow['Kategorie']
        #date = TakExcelTransformLib.getDatefromStr(inFormRow['Termin (Start)'])
        date = inFormRow['Termin (Start)']
        enddate = inFormRow['Termin (Ende)']
        print(f"Processing Tour: {kategorie}: {titel}, von {date} bis {enddate}")
        Anmeldeschluss = inFormRow['Anmeldeschluss']
        sheetOut.cell(row=ri, column=ColumnsTouren['key']).value = TakExcelTransformLib.getKey(titel, inFormRow['Kategorie'], date)
        sheetOut.cell(row=ri, column=ColumnsTouren['assignedGroups']).value = '/267 - Sektion Turner-Alpenkränzchen/Gruppen/Allgemein'
        #sheetOut.cell(row=ri, column=Columns['bookingCode']).value = getBookingcode(row['Titel'],row['Kategorie'],date)
        #sheetOut.cell(row=ri, column=ColumnsTouren['bookingCode']).value = 'T' + str(ProgramYear) + '_' + str(inFormRow['ID'])
        sheetOut.cell(row=ri, column=ColumnsTouren['bookingCode']).value = inFormRow['Lfd-Nr.']
        sheetOut.cell(row=ri, column=ColumnsTouren['title']).value = titel
        sheetOut.cell(row=ri, column=ColumnsTouren['category']).value = TakExcelTransformLib.Kategorie[kategorie]
        sheetOut.cell(row=ri, column=ColumnsTouren['technique']).value = TakExcelTransformLib.Technik[inFormRow['Schwierigkeit']]
        sheetOut.cell(row=ri, column=ColumnsTouren['stamina']).value = TakExcelTransformLib.Ausdauer[inFormRow['Kondition']]
        sheetOut.cell(row=ri, column=ColumnsTouren['description']).value = TakExcelTransformLib.makeHTML(inFormRow['Beschreibung'])
        sheetOut.cell(row=ri, column=ColumnsTouren['Termine']).value = TakExcelTransformLib.getDates(date, enddate)
        sheetOut.cell(row=ri, column=ColumnsTouren['datesAlternativeText']).value = '<p>&nbsp;</p>'
        sheetOut.cell(row=ri, column=ColumnsTouren['leaders']).value = TakExcelTransformLib.getLeaders(inFormRow['Tourenleitung/Organisation'])
        sheetOut.cell(row=ri, column=ColumnsTouren['destination']).value = TakExcelTransformLib.makeHTML(inFormRow['Gebirgsgruppe/Region'])
        sheetOut.cell(row=ri, column=ColumnsTouren['season']).value = TakExcelTransformLib.Saison[Season]
        sheetOut.cell(row=ri, column=ColumnsTouren['characteristic']).value = TakExcelTransformLib.Eventart[inFormRow['Klassifizierung']] #Achtung das ist im Formular verdreht
        sheetOut.cell(row=ri, column=ColumnsTouren['classification']).value = TakExcelTransformLib.Klassifizierung[inFormRow['Tourenart']] #Achtung das ist im Formular verdreht
        sheetOut.cell(row=ri, column=ColumnsTouren['requirements']).value = '<p>&nbsp;</p>'
        sheetOut.cell(row=ri, column=ColumnsTouren['maxNumberOfParticipants']).value = TakExcelTransformLib.getMaxNumberOfParticipants(str(inFormRow['max. Zahl der Teilnehmenden']))
        sheetOut.cell(row=ri, column=ColumnsTouren['bookingState']).value = ''
        sheetOut.cell(row=ri, column=ColumnsTouren['registerEnd']).value = TakExcelTransformLib.getDate(Anmeldeschluss)
        sheetOut.cell(row=ri, column=ColumnsTouren['meetingPoint']).value = TakExcelTransformLib.makeHTML('')
        Entfernung = str(inFormRow['Anfahrt km'])
        Ausgangsort = str(inFormRow['Ausgangsort'])
        sheetOut.cell(row=ri, column=ColumnsTouren['arrivalHints']).value = TakExcelTransformLib.makeHTML('Ausgangsort: ' + Ausgangsort + ', Entfernung: ' + Entfernung + 'km')
        sheetOut.cell(row=ri, column=ColumnsTouren['isPublicTransportAvailable']).value = TakExcelTransformLib.getEinsNull(inFormRow['Öffentliche Anreise'])
        ri = ri+1
    wbOut.save(outFile)
    print("wrote: "+outFile)
