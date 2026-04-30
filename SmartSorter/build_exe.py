# Script de Packaging - Créer un .exe installable
# =================================================

"""
Ce script utilise PyInstaller pour créer un exécutable Windows
de l'application Organisateur de Fichiers.

Installation de PyInstaller :
    pip install pyinstaller

Utilisation :
    python build_exe.py
"""

import os
import subprocess
import sys
from pathlib import Path


def check_pyinstaller():
    """Vérifie si PyInstaller est installé."""
    try:
        import PyInstaller
        print("✓ PyInstaller est installé")
        return True
    except ImportError:
        print("✗ PyInstaller n'est pas installé")
        print("\nInstallation de PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installé avec succès")
            return True
        except subprocess.CalledProcessError:
            print("✗ Erreur lors de l'installation de PyInstaller")
            return False


def create_icon():
    """Crée un fichier icône simple (optionnel)."""
    # Pour l'instant, on n'utilise pas d'icône personnalisée
    # Vous pouvez ajouter un fichier .ico dans le dossier si vous le souhaitez
    pass


def build_exe(modern=False):
    """
    Construit l'exécutable avec PyInstaller.
    
    Args:
        modern: Si True, compile la version moderne, sinon la version classique
    """
    script_name = "file_organizer_modern.py" if modern else "file_organizer.py"
    exe_name = "Organisateur_Fichiers_Modern" if modern else "Organisateur_Fichiers"
    
    print(f"\n{'='*60}")
    print(f"Construction de l'exécutable: {exe_name}")
    print(f"{'='*60}\n")
    
    # Vérifier que le script existe
    if not Path(script_name).exists():
        print(f"✗ Erreur: {script_name} n'existe pas")
        return False
    
    # Options PyInstaller
    options = [
        script_name,                    # Script source
        f"--name={exe_name}",          # Nom de l'exécutable
        "--onefile",                    # Un seul fichier exe
        "--windowed",                   # Pas de console (GUI uniquement)
        "--clean",                      # Nettoyer avant de construire
        f"--distpath=dist",            # Dossier de sortie
        f"--workpath=build",           # Dossier de travail
        f"--specpath=build",           # Dossier des specs
    ]
    
    # Ajouter une icône si elle existe
    if Path("icon.ico").exists():
        options.append("--icon=icon.ico")
    
    # Métadonnées Windows
    options.extend([
        "--version-file=version_info.txt",  # Si le fichier existe
    ])
    
    print("Options PyInstaller:")
    for opt in options:
        print(f"  {opt}")
    print()
    
    # Exécuter PyInstaller
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller"] + options)
        print(f"\n{'='*60}")
        print(f"✓ Exécutable créé avec succès!")
        print(f"{'='*60}")
        print(f"\nEmplacement: {Path('dist') / f'{exe_name}.exe'}")
        print(f"Taille: {(Path('dist') / f'{exe_name}.exe').stat().st_size / 1024 / 1024:.2f} MB")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Erreur lors de la construction: {e}")
        return False


def create_version_info():
    """Crée un fichier de métadonnées de version pour Windows."""
    version_info = """# UTF-8
#
# For more details about fixed file info:
# https://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Organisateur de Fichiers'),
        StringStruct(u'FileDescription', u'Application de tri automatique de fichiers'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'FileOrganizer'),
        StringStruct(u'LegalCopyright', u'© 2026'),
        StringStruct(u'OriginalFilename', u'Organisateur_Fichiers.exe'),
        StringStruct(u'ProductName', u'Organisateur de Fichiers'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    print("✓ Fichier version_info.txt créé")


def create_installer_script():
    """Crée un script Inno Setup pour créer un installateur Windows."""
    inno_script = """
; Script Inno Setup pour Organisateur de Fichiers
; ================================================

#define MyAppName "Organisateur de Fichiers"
#define MyAppVersion "2.0"
#define MyAppPublisher "Organisateur de Fichiers"
#define MyAppExeName "Organisateur_Fichiers_Modern.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=Organisateur_Fichiers_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis:"

[Files]
Source: "dist\\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent
"""
    
    with open("installer_script.iss", "w", encoding="utf-8") as f:
        f.write(inno_script)
    
    print("✓ Script Inno Setup créé: installer_script.iss")
    print("\nPour créer l'installateur:")
    print("1. Téléchargez Inno Setup: https://jrsoftware.org/isdl.php")
    print("2. Ouvrez installer_script.iss avec Inno Setup")
    print("3. Cliquez sur 'Build' > 'Compile'")


def clean_build_files():
    """Nettoie les fichiers de build temporaires."""
    import shutil
    
    dirs_to_clean = ['build', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ Nettoyé: {dir_name}/")
    
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"✓ Supprimé: {file}")


def main():
    """Fonction principale."""
    print("="*60)
    print("CONSTRUCTION DE L'EXÉCUTABLE WINDOWS")
    print("="*60)
    print()
    
    # Vérifier PyInstaller
    if not check_pyinstaller():
        print("\n✗ Impossible de continuer sans PyInstaller")
        return
    
    print()
    
    # Créer les fichiers de métadonnées
    create_version_info()
    
    print()
    
    # Demander quelle version compiler
    print("Quelle version voulez-vous compiler ?")
    print("1. Version classique (file_organizer.py)")
    print("2. Version moderne (file_organizer_modern.py)")
    print("3. Les deux")
    
    choice = input("\nVotre choix (1/2/3) [2]: ").strip() or "2"
    
    print()
    
    success = True
    
    if choice == "1":
        success = build_exe(modern=False)
    elif choice == "2":
        success = build_exe(modern=True)
    elif choice == "3":
        success = build_exe(modern=False) and build_exe(modern=True)
    else:
        print("✗ Choix invalide")
        return
    
    if success:
        print("\n" + "="*60)
        print("CRÉATION DU SCRIPT D'INSTALLATION")
        print("="*60)
        print()
        create_installer_script()
        
        print("\n" + "="*60)
        print("NETTOYAGE")
        print("="*60)
        print()
        
        clean = input("Nettoyer les fichiers temporaires ? (o/N): ").strip().lower()
        if clean == 'o':
            clean_build_files()
        
        print("\n" + "="*60)
        print("✓ PROCESSUS TERMINÉ")
        print("="*60)
        print("\nVos fichiers sont dans le dossier 'dist/'")
        print("Vous pouvez maintenant distribuer l'exécutable !")


if __name__ == "__main__":
    main()
