#define AppName "NOVA Player"
#define AppVersion "1.10.0"
[Setup]
AppId={{B8E57B76-7541-4B59-97B4-0AA34D9A7101}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\NOVA Player
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
DefaultGroupName={#AppName}
AppPublisher=Nayan Patel
SetupIconFile=..\assets\nova-player.ico
UninstallDisplayIcon={app}\NOVAPlayer.exe
OutputDir=..\dist
OutputBaseFilename=NOVA-Player-Setup
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
[Files]
Source: "..\dist\NOVAPlayer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\NOVA Player"; Filename: "{app}\NOVAPlayer.exe"; IconFilename: "{app}\NOVAPlayer.exe"
Name: "{autodesktop}\NOVA Player"; Filename: "{app}\NOVAPlayer.exe"; IconFilename: "{app}\NOVAPlayer.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

