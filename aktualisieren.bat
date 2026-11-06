@echo off
rem Holt die neueste Version des Transformators.
rem Setzt vorher die Beispieldateien in dummy_daten zurueck, damit git pull
rem nicht an versehentlich gespeicherten Excel-Dateien scheitert.
cd /d "%~dp0"
git checkout -- dummy_daten
git pull
pause
