; Script Inno Setup optimisé pour FetchNovel (Fluent Edition)
; Basé sur les dernières modifications de app.py et scraper.py

[Setup]
; Identification de l'application
AppId={{D4B53A22-8B12-4C92-A8E2-9F123ABC456D}
AppName=FetchNovel
AppVersion=1.0
AppVerName=FetchNovel 1.0 (Fluent Edition)
AppPublisher=FetchNovel Studio
AppPublisherURL=https://github.com/fetchnovel
AppSupportURL=https://github.com/fetchnovel/support
AppUpdatesURL=https://github.com/fetchnovel/updates

; Paramètres d'installation
DefaultDirName={autopf}\FetchNovel
DefaultGroupName=FetchNovel
AllowNoIcons=yes
AllowRootDirectory=no
DisableDirPage=no
DisableProgramGroupPage=no
PrivilegesRequired=admin
MinVersion=10.0
UninstallDisplayIcon={app}\FetchNovel.exe

; Style moderne Windows 11
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Setup_FetchNovel_Win11_v1.0

; Architecture 64-bit
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
french.BeveledLabel=FetchNovel - Modern Novel Scraper (Fluent Edition)
english.BeveledLabel=FetchNovel - Modern Novel Scraper (Fluent Edition)

[CustomMessages]
french.LaunchProgram=Lancer FetchNovel
english.LaunchProgram=Launch FetchNovel
french.CreateDesktopIcon=Créer une icône sur le bureau
english.CreateDesktopIcon=Create a desktop icon
french.AdditionalIcons=Icônes supplémentaires
english.AdditionalIcons=Additional icons
french.FileAssoc=Associer les fichiers .novel avec FetchNovel
english.FileAssoc=Associate .novel files with FetchNovel

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "fileassoc"; Description: "{cm:FileAssoc}"; GroupDescription: "Associations"; Flags: unchecked

[Files]
; IMPORTANT: On utilise la sortie de cx_Freeze (onedir) pour garantir que toutes les bibliothèques sont présentes
; (customtkinter, deep-translator, requests, etc.)
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\build\exe.win-amd64-3.13\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\BUILD_README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "LISEZ-MOI.md"

; Documentation et exemples
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "c:\Users\etoun\Documents\Logiciel\fetchNovel\examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Dirs]
Name: "{app}\logs"
Name: "{app}\temp"
Name: "{app}\cache"

[Icons]
; Menu Démarrer
Name: "{group}\FetchNovel"; Filename: "{app}\FetchNovel.exe"; Comment: "Modern Novel Scraper with Translation"
Name: "{group}\Lisez-moi"; Filename: "{app}\LISEZ-MOI.md"; Comment: "Documentation"
Name: "{group}\Désinstaller"; Filename: "{uninstallexe}"; Comment: "Désinstaller FetchNovel"

; Bureau
Name: "{autodesktop}\FetchNovel"; Filename: "{app}\FetchNovel.exe"; Tasks: desktopicon; Comment: "Modern Novel Scraper"

[Registry]
; Enregistrement du chemin d'installation
Root: HKLM; Subkey: "SOFTWARE\FetchNovel"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\FetchNovel"; ValueType: string; ValueName: "Version"; ValueData: "1.0"; Flags: uninsdeletekey

; Association de fichiers .novel (si activé)
Root: HKCR; Subkey: ".novel"; ValueType: string; ValueData: "FetchNovel.File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "FetchNovel.File"; ValueType: string; ValueData: "FetchNovel Novel File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "FetchNovel.File\DefaultIcon"; ValueType: string; ValueData: "{app}\FetchNovel.exe,0"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCR; Subkey: "FetchNovel.File\shell\open\command"; ValueType: string; ValueData: """{app}\FetchNovel.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: fileassoc

[Run]
; Lancement après installation
Filename: "{app}\FetchNovel.exe"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\temp"
Type: filesandordirs; Name: "{app}\cache"
Type: filesandordirs; Name: "{app}\logs"

[Code]
// Code Pascal pour un installateur premium

function InitializeSetup: Boolean;
begin
  Result := True;
end;

// Note: Dans WizardStyle=modern, on évite UpdateReadyMemo car le résumé est automatique.
// Mais pour satisfaire le besoin de visibilité des fonctionnalités, on peut ajouter
// un message d'information sur la page de succès.

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedLabel.Caption := 
      'L''installation de FetchNovel 1.0 est terminée.' + #13#10 + #13#10 +
      'Fonctionnalités prêtes :' + #13#10 +
      '• Interface Windows 11 Fluent Edition' + #13#10 +
      '• Scraper robuste avec sélecteurs CSS personnalisés' + #13#10 +
      '• Support de la traduction via Google Translate' + #13#10 +
      '• Export multi-formats (DOCX & PDF)' + #13#10 +
      '• Mode furtif avec délais aléatoires';
  end;
end;
