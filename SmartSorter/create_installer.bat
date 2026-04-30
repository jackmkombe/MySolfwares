@echo off
REM Script pour créer l'installateur Smart Sorter v4.2
REM Utilise Inno Setup pour compiler le script .iss

echo ========================================
echo Smart Sorter v4.2 - Création Installateur
echo ========================================
echo.

REM Vérifier que l'exe existe
if not exist "dist\SmartSorter_v4.2.exe" (
    echo ERREUR: dist\SmartSorter_v4.2.exe n'existe pas
    echo Veuillez d'abord compiler l'exe avec PyInstaller
    echo.
    pause
    exit /b 1
)

REM Vérifier que les fichiers de documentation existent
if not exist "README_EXE.txt" (
    echo ERREUR: README_EXE.txt manquant
    pause
    exit /b 1
)

if not exist "FINAL_v4.2.md" (
    echo ERREUR: FINAL_v4.2.md manquant
    pause
    exit /b 1
)

if not exist "LICENSE" (
    echo ERREUR: LICENSE manquant
    pause
    exit /b 1
)

echo Tous les fichiers requis sont présents
echo.

REM Créer le dossier installer s'il n'existe pas
if not exist "installer" mkdir installer

REM Chercher Inno Setup
set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%INNO_PATH%" (
    echo ERREUR: Inno Setup n'est pas installé
    echo Téléchargez-le depuis: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Compilation de l'installateur avec Inno Setup...
echo.

REM Compiler le script
"%INNO_PATH%" SmartSorter_Setup.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCÈS !
    echo ========================================
    echo.
    echo L'installateur a été créé avec succès:
    echo installer\SmartSorter_v4.2_Setup.exe
    echo.
    echo Taille: ~15 MB
    echo.
    echo Vous pouvez maintenant:
    echo 1. Tester l'installateur
    echo 2. Distribuer SmartSorter_v4.2_Setup.exe
    echo.
) else (
    echo.
    echo ========================================
    echo ERREUR !
    echo ========================================
    echo.
    echo La compilation a échoué
    echo Vérifiez le fichier SmartSorter_Setup.iss
    echo.
)

pause
