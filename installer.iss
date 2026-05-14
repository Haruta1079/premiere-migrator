#define MyAppName      "Premiere Migrator"
#define MyAppVersion   GetEnv("APP_VERSION")
#define MyAppURL       "https://github.com/Haruta1079/premiere-migrator"
#define MyAppExeName   "PremiereMigrator.exe"

[Setup]
AppId={{F3A2B1C4-D5E6-4789-ABCD-012345678901}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; インストール先に書き込み権限があれば管理者不要で動作
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=dist
OutputBaseFilename=PremiereMigratorSetup
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; インストール後にアプリを起動するオプション
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "デスクトップにショートカットを作成(&D)"; \
  GroupDescription: "追加アイコン:"; \
  Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

[Icons]
; スタートメニュー
Name: "{group}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName}をアンインストール"; \
  Filename: "{uninstallexe}"
; デスクトップ（タスクで選択した場合のみ）
Name: "{autodesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{#MyAppName}を起動する"; \
  Flags: nowait postinstall skipifsilent
