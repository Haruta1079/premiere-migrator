# Premiere Pro Settings Migrator

Premiere Proの設定を丸ごとエクスポートして、別のPCやMac↔Windows間で一括インポートできるツールです。

## 対応ファイル

| カテゴリ | ファイル |
|---|---|
| Motion Graphics Templates | `.mogrt` |
| エフェクトプリセット | `.prfpset` |
| キーボードショートカット | `.kys` |
| ワークスペースレイアウト | `.xml` |

---

## インストール方法

### Windows
1. [Releases](../../releases/latest) から `PremiereMigrator.exe` をダウンロード
2. ダブルクリックで起動（インストール不要）

> SmartScreenの警告が出た場合: 「詳細情報」→「実行」をクリック

### Mac
1. [Releases](../../releases/latest) から `PremiereMigrator.dmg` をダウンロード
2. DMGを開き、アプリをApplicationsフォルダへドラッグ

> 「開発元を確認できません」と表示された場合: Controlキーを押しながらアプリをクリック→「開く」

---

## 使い方

### 設定をエクスポートする

1. アプリを起動し「エクスポート」タブを開く
2. Premiere Proのバージョンが自動検出される（複数バージョンがある場合はドロップダウンで選択）
3. 移行したい項目にチェックを入れる
4. 「ファイル数を確認」ボタンで検出された数を確認
5. 保存先のZIPファイルパスを指定して「エクスポート」をクリック

### 設定をインポートする

1. 「インポート」タブを開く
2. エクスポートしたZIPファイルを選択
3. 作成日時・元のOS・Premiere Proバージョンがプレビュー表示される
4. インストール先のバージョンを選択
5. 必要に応じて「既存ファイルを上書きする」にチェック
6. 「インポート」をクリック

---

## Mac ↔ Windows 間の移行について

- MOGRTファイルはそのまま移行できます
- キーボードショートカットは **Mac（Command）と Windows（Ctrl）でキーが異なる** ため、インポート後に一部のショートカットを手動で調整してください
- ワークスペースレイアウトは基本的にそのまま使えます

---

## 開発者向け: ソースから実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 起動
python main.py
```

### ビルド（EXE/DMGの作成）

```bash
# 依存関係
pip install pyinstaller pillow

# ビルド
pyinstaller premiere_migrator.spec

# Windows: dist/PremiereMigrator.exe
# Mac:     dist/PremiereMigrator.app
```

### リリースの作成

```bash
git tag v1.0.0
git push origin v1.0.0
```

タグをpushすると GitHub Actions が自動でWindows/Macのビルドを行い、Releasesページにファイルが添付されます。

---

## ライセンス

MIT License
