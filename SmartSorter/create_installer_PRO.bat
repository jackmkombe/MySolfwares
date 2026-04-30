@echo off
REM Script pour créer l'installateur Smart Sorter v5.0 PRO
REM Utilise Inno Setup pour compiler le script .iss

echo ========================================
echo Smart Sorter v5.0 PRO - Création Installateur
echo ========================================
echo.

REM Vérifier que l'exe existe
if not exist "dist\SmartSorter_v5.0_PRO.exe" (
    echo ERREUR: dist\SmartSorter_v5.0_PRO.exe n'existe pas
    echo Veuillez d'abord compiler l'exe avec PyInstaller
    echo.
    pause
    exit /b 1
)

REM Vérifier que l'icône existe
if not exist "app_icon.ico" (
    echo ERREUR: app_icon.ico manquant
    pause
    exit /b 1
)

REM Vérifier les fichiers de docs
if not exist "README_EXE.txt" (
    echo ERREUR: README_EXE.txt manquant
    pause
    exit /b 1
)

echo Tous les fichiers requis (EXE + Icône + Docs) sont présents.
echo.

if not exist "installer" mkdir installer

set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%INNO_PATH%" (
    echo ERREUR: Inno Setup n'est pas installé.
    pause
    exit /b 1
)

echo Compilation de l'installateur PRO avec l'icône...
"%INNO_PATH%" SmartSorter_PRO_Setup.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCÈS ! L'installateur PRO est prêt.
    echo ========================================
    echo Emplacement : installer\SmartSorter_PRO_Setup_v5.0.3.exe
) else (
    echo.
    echo ERREUR lors de la compilation Inno Setup.
)

pause
