; Script Inno Setup pour Smart Sorter v4.2 - Version Simplifiée
; Crée un installateur Windows professionnel

#define MyAppName "Smart Sorter"
#define MyAppVersion "4.2.0"
#define MyAppPublisher "Smart Sorter Team"
#define MyAppExeName "SmartSorter_v4.2.exe"

[Setup]
; Informations de base
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=SmartSorter_v4.2_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_EXE.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "FINAL_v4.2.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "EXE_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Guide d'utilisation"; Filename: "{app}\README_EXE.txt"
Name: "{group}\Documentation complète"; Filename: "{app}\FINAL_v4.2.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
