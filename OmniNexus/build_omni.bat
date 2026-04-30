@echo off
echo ========================================
echo OmniNexus Manager - Build System
echo ========================================
echo.
echo Installation des dependances...
pip install -r requirements.txt

echo.
echo Generation de l'executable avec icone...
pyinstaller --onefile --windowed --name="OmniNexus_Manager" --icon="app_icon.ico" --clean main.py

echo.
echo ========================================
echo BUILD TERMINE !
echo L'executable se trouve dans le dossier 'dist'
echo ========================================
pause
