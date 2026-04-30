; Script Inno Setup pour Smart Sorter v4.2 - Version Ultra Simplifiée
#define MyAppName "Smart Sorter"
#define MyAppVersion "4.2.0"
#define MyAppPublisher "Smart Sorter Team"
#define MyAppExeName "SmartSorter_v4.2.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=SmartSorter_Setup_v4.2
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Privilèges utilisateur normal
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; IMPORTANT: Vérifiez que le fichier existe bien dans .\dist\
Source: "dist\SmartSorter_v4.2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_EXE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "FINAL_v4.2.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Raccourci Bureau (Toujours créé dans cette version pour éviter l'erreur Tasks)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Guide
Name: "{group}\Guide d'utilisation"; Filename: "{app}\README_EXE.txt"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Smart Sorter"; Flags: nowait postinstall skipifsilent
