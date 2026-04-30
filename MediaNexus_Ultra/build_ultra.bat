@echo off
echo ========================================
echo MediaNexus Ultra - Power Build System
echo ========================================
echo.
echo Mise a jour de l'environnement...
pip install -r requirements.txt

echo.
echo Compilation de l'executable Ultra...
pyinstaller --onefile --windowed --name="MediaNexus_Ultra" --icon="app_icon.ico" --clean main.py

echo.
echo ========================================
echo BUILD REUSSI !
echo Votre application est dans 'dist/MediaNexus_Ultra.exe'
echo ========================================
pause
