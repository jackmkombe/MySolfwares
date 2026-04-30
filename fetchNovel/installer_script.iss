; Script Inno Setup optimisé pour FetchNovel (Windows 11)
[Setup]
AppId={{D4B53A22-8B12-4C92-A8E2-9F123ABC456D}
AppName=FetchNovel
AppVersion=1.0
AppPublisher=FetchNovel Studio
DefaultDirName={autopf}\FetchNovel
DefaultGroupName=FetchNovel
AllowNoIcons=yes
; Style moderne Windows 11
WizardStyle=modern
Compression=lzma
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Setup_FetchNovel_Win11
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\dist\FetchNovel.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\FetchNovel"; Filename: "{app}\FetchNovel.exe"
Name: "{autodesktop}\FetchNovel"; Filename: "{app}\FetchNovel.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\FetchNovel.exe"; Description: "{cm:LaunchProgram,FetchNovel}"; Flags: nowait postinstall skipifsilent
