@echo off
echo ========================================
echo MediaNexus Ultra PRO - Global Build
echo ========================================
echo.
echo Verification des dependances...
pip install -r requirements.txt

echo.
echo Compilation de l'exécutable PRO v2.0.0...
pyinstaller --onefile --windowed --name="MediaNexus_Ultra_PRO" --icon="app_icon.ico" --clean main.py

echo.
echo ========================================
echo TERMINE ! Version PRO dans 'dist/'
echo ========================================
pause
