; Build using Inno Setup 6.7.3 or later. SourceDir must be a privacy-checked runtime.
#ifndef SourceDir
  #error SourceDir must point to a clean AquaSync runtime
#endif
#ifndef OutputDir
  #error OutputDir must be specified
#endif
#define AppVersion "2.0"

[Setup]
AppId={{BA47F53A-1666-4FCB-9348-C74DDA57EE20}
AppName=AquaSync
AppVersion={#AppVersion}
AppVerName=AquaSync {#AppVersion}
AppPublisher=AquaSync
DefaultDirName={code:DefaultInstallDir}
UsePreviousAppDir=yes
DisableDirPage=no
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir={#OutputDir}
OutputBaseFilename=AquaSync-{#AppVersion}-Setup
SetupIconFile={#SourceDir}\_internal\data\report_assets\aquasync.ico
UninstallDisplayIcon={app}\AquaSync.exe
WizardStyle=modern
Compression=lzma2/fast
SolidCompression=yes
DiskSpanning=no
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
UninstallDisplayName=AquaSync {#AppVersion}
VersionInfoVersion=2.0.0.0

[Languages]
Name: "chinesesimplified"; MessagesFile: "ChineseSimplified.isl"

[Messages]
chinesesimplified.SelectDirDesc=请选择 AquaSync 的安装位置
chinesesimplified.SelectDirLabel3=建议选择非系统盘且当前用户可写的文件夹。程序、个人成绩和日志默认保存在此目录；请勿选择 Program Files 或 Windows 目录。
chinesesimplified.FinishedLabel=已安装 AquaSync。桌面快捷方式已创建。%n%n卸载程序会保留个人成绩、配置和日志；更新前请先关闭 AquaSync。

[Files]
Source: "{#SourceDir}\AquaSync.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Retire only bundled artwork/dependencies replaced by the compact runtime.
; User covers and personal records live in user-data, outside these paths.
Type: files; Name: "{app}\_internal\data\report_assets\archive\*.png"
Type: files; Name: "{app}\_internal\data\report_assets\covers\*.png"
Type: filesandordirs; Name: "{app}\_internal\PIL"

[Icons]
Name: "{param:SHORTCUTDIR|{userdesktop}}\AquaSync"; Filename: "{app}\AquaSync.exe"; WorkingDir: "{app}"; IconFilename: "{app}\AquaSync.exe"

[Run]
Filename: "{app}\AquaSync.exe"; Description: "启动 AquaSync"; Flags: nowait postinstall skipifsilent

[Code]
function GetDriveType(lpRootPathName: String): Cardinal;
  external 'GetDriveTypeW@kernel32.dll stdcall';

function DefaultInstallDir(Param: String): String;
var
  Drive: String;
  Letter: Integer;
begin
  Drive := ExtractFileDrive(ExpandConstant('{src}'));
  if (CompareText(Drive, ExpandConstant('{sd}')) <> 0) and
     (GetDriveType(Drive + '\') = 3) then begin
    Result := Drive + '\AquaSync';
    exit;
  end;
  for Letter := Ord('D') to Ord('Z') do begin
    Drive := Chr(Letter) + ':';
    if DirExists(Drive + '\') and (GetDriveType(Drive + '\') = 3) then begin
      Result := Drive + '\AquaSync';
      exit;
    end;
  end;
  Result := ExpandConstant('{sd}\AquaSync');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  SelectedDir: String;
begin
  Result := True;
  if CurPageID = wpSelectDir then begin
    SelectedDir := AddBackslash(ExpandFileName(WizardDirValue));
    if (Pos(Lowercase(AddBackslash(ExpandConstant('{win}'))), Lowercase(SelectedDir)) = 1) or
       (Pos(Lowercase(AddBackslash(ExpandConstant('{commonpf32}'))), Lowercase(SelectedDir)) = 1) or
       (Pos(Lowercase(AddBackslash(ExpandConstant('{commonpf64}'))), Lowercase(SelectedDir)) = 1) then begin
      MsgBox('请选择当前用户可写的独立文件夹，例如 D:\AquaSync。', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Only explicitly installed program files are removed. No recursive deletion of
// {app}: user-data, AquaSync-desktop.json and logs must survive uninstall/update.
