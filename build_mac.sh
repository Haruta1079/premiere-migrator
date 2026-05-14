#!/bin/bash
echo "=== Premiere Migrator - Mac ビルド ==="

# PyInstallerがなければインストール
pip show pyinstaller > /dev/null 2>&1 || pip install pyinstaller

CTXK_PATH=$(python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))")

pyinstaller \
  --onefile \
  --windowed \
  --name "PremiereMigrator" \
  --add-data "$CTXK_PATH:customtkinter" \
  main.py

echo ""
echo "ビルド完了! dist/PremiereMigrator を確認してください"
