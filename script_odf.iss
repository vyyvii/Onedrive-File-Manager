[Setup]
AppId={{GUID-UNIQUE}}
AppName=OneDrive Duplicate Finder
AppVersion=1.0
AppVerName=OneDrive Duplicate Finder v1.0
AppPublisher=Victor Defauchy
AppPublisherURL=https://duplicatefinder.fr
AppSupportURL=https://duplicatefinder.fr
AppUpdatesURL=https://duplicatefinder.fr
DefaultDirName={autopf}\OneDrive Duplicate Finder
DefaultGroupName=OneDrive Duplicate Finder
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=OneDrive_Duplicate_Finder_Setup
SetupIconFile=content\onedrive_logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\OneDrive_Duplicate_Finder.exe
UninstallDisplayName=OneDrive_Duplicate_Finder_Uninstall

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminLoggedOn

[Files]
Source: "dist\OneDrive_Duplicate_Finder.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "content\*"; DestDir: "{app}\content"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config.cfg"; DestDir: "{app}"; Flags: ignoreversion
Source: "source_code_odf.zip"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\OneDrive Duplicate Finder"; Filename: "{app}\OneDrive_Duplicate_Finder.exe"
Name: "{group}\{cm:UninstallProgram,OneDrive Duplicate Finder}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\OneDrive Duplicate Finder"; Filename: "{app}\OneDrive_Duplicate_Finder.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\OneDrive Duplicate Finder"; Filename: "{app}\OneDrive_Duplicate_Finder.exe"; Tasks: quicklaunchicon

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\save"
Type: files; Name: "{app}\*.db"
Type: files; Name: "{app}\*.log"