@echo off
echo === Premiere Migrator - Windows ビルド ===

:: PyInstallerがなければインストール
pip show pyinstaller >nul 2>&1 || pip install pyinstaller

:: customtkinterのデータファイルを含めてビルド
pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PremiereMigrator" ^
  --add-data "%LOCALAPPDATA%\Programs\Python\Python312\Lib\site-packages\customtkinter;customtkinter" ^
  main.py

echo.
echo ビルド完了! dist\PremiereMigrator.exe を確認してください
pause
