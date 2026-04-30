; Script Inno Setup pour Smart Sorter v5.0 PRO
#define MyAppName "Smart Sorter PRO"
#define MyAppVersion "5.0.3"
#define MyAppPublisher "Smart Sorter Team"
#define MyAppExeName "SmartSorter_v5.0_PRO.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer
OutputBaseFilename=SmartSorter_PRO_Setup_v5.0.3
SetupIconFile=app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; IMPORTANT: Vérifiez que le fichier existe bien dans .\dist\ après le build PyInstaller
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_EXE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "FINAL_v4.2.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Raccourci Bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Guide
Name: "{group}\Guide d'utilisation"; Filename: "{app}\README_EXE.txt"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Smart Sorter PRO"; Flags: nowait postinstall skipifsilent
