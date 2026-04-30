@echo off
REM ============================================
REM Lanceur pour Organisateur de Fichiers
REM ============================================

echo.
echo ========================================
echo  Organisateur de Fichiers et Dossiers
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte
python --version
echo.

REM Lancer l'application
echo Lancement de l'application...
echo.
python file_organizer.py

REM Si l'application se ferme avec une erreur
if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est terminee avec une erreur
    echo.
    pause
)
