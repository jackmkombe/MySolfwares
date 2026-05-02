@echo off
echo ========================================
echo Compilation de l'installateur FetchNovel
echo ========================================
echo.

REM Vérification si Inno Setup est installé
where iscc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Inno Setup n'est pas installé!
    echo.
    echo Veuillez installer Inno Setup depuis:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Choisissez la version "QuickStart Pack" qui inclut le compilateur.
    echo.
    pause
    exit /b 1
)

echo [OK] Inno Setup détecté
echo.

REM Vérification des fichiers requis
if not exist "dist\FetchNovel.exe" (
    echo [ERREUR] Fichier dist\FetchNovel.exe introuvable!
    echo Veuillez d'abord compiler l'application avec:
    echo python setup_installer.py build
    pause
    exit /b 1
)

if not exist "installer_script.iss" (
    echo [ERREUR] Script installer_script.iss introuvable!
    pause
    exit /b 1
)

echo [OK] Fichiers requis trouvés
echo.

REM Compilation
echo Compilation de l'installateur...
iscc "installer_script.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCES] Installateur créé avec succès!
    echo Fichier disponible dans: dist\Setup_FetchNovel_Win11_v1.0.exe
    echo.
    echo Taille estimée: ~30MB
    echo.
    start "" "dist"
) else (
    echo.
    echo [ERREUR] Erreur lors de la compilation!
    echo Vérifiez le script installer_script.iss
)

pause
