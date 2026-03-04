@echo off
set SCRIPT_PATH=%~dp0scheduler.py
set VBS_PATH=%~dp0start_voltaire.vbs

:: Créer un script VBS pour lancer le Python en arrière-plan (sans fenêtre noire)
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_PATH%"
echo WshShell.Run "pythonw.exe " ^& Chr(34) ^& "%SCRIPT_PATH%" ^& Chr(34), 0, False >> "%VBS_PATH%"

:: Ajouter au dossier de démarrage de Windows
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%VBS_PATH%" "%STARTUP_FOLDER%\start_voltaire.vbs"

echo.
echo [SUCCES] Le planificateur Projet Voltaire a ete ajoute a votre dossier de demarrage Windows.
echo Il se lancera desormais automatiquement en arriere-plan a chaque ouverture de session.
pause
