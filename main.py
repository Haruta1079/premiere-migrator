"""
Premiere Pro Settings Migrator
エントリーポイント
"""
import sys

def check_dependencies():
    missing = []
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    if missing:
        print("必要なライブラリが不足しています。以下のコマンドを実行してください:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

check_dependencies()

from ui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
