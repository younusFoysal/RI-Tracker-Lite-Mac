[Setup]
AppName=RI Tracker
AppVersion=1.0.9
DefaultDirName={pf}\RI Tracker
DefaultGroupName=RI Tracker
OutputDir=dist
OutputBaseFilename=RI_Tracker_Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico  

[Files]
Source: "dist\\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion  

[Icons]
; Start Menu shortcut
Name: "{group}\\RI Tracker"; Filename: "{app}\\main.exe"; IconFilename: "{app}\\icon.ico"

; Desktop shortcut
Name: "{commondesktop}\\RI Tracker"; Filename: "{app}\\main.exe"; IconFilename: "{app}\\icon.ico"

; Uninstaller
Name: "{group}\\Uninstall RI Tracker"; Filename: "{uninstallexe}"
