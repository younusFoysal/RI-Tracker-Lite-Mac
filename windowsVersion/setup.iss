; installer.iss - RI Tracker Installer
[Setup]
AppId={{B8F9C4E2-1234-5678-9ABC-DEF012345678}
AppName=RI Tracker
AppVersion=1.0.15
AppVerName=RI Tracker 1.0.15
DefaultDirName={autopf}\RI Tracker
DefaultGroupName=RI Tracker
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=RI_Tracker_Installer_v1.0.15
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\main.exe
LicenseFile=license.txt
WizardImageFile=wizard_image.bmp
WizardSmallImageFile=wizard_small.bmp
AppPublisher=RemoteIntegrity LLC
AppPublisherURL=https://remoteintegrity.com
AppSupportURL=https://remoteintegrity.com/support
AppUpdatesURL=https://remoteintegrity.com/downloads
AppCopyright=Copyright (C) 2025 RemoteIntegrity LLC
VersionInfoVersion=1.0.15.0
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\RI Tracker"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
; Optional desktop shortcut
Name: "{commondesktop}\RI Tracker"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Start RI Tracker automatically when Windows starts"; GroupDescription: "Startup options:"

[Run]
Filename: "{app}\main.exe"; Description: "Launch RI Tracker"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "RI Tracker"; ValueData: """{app}\main.exe"""; Flags: uninsdeletevalue; Tasks: startupicon