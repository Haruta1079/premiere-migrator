"""
Premiere Pro Settings Migrator - UI (customtkinter)
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from datetime import datetime

import core


# ─────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#4A9EFF"
BG_CARD = "#2B2D30"
SUCCESS = "#4CAF50"
WARNING = "#FF9800"
ERROR   = "#F44336"


# ─────────────────────────────────────────────
# Helper widgets
# ─────────────────────────────────────────────

class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, text=text,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#AAAAAA", **kwargs)


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", BG_CARD)
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)


# ─────────────────────────────────────────────
# Version selector widget (shared)
# ─────────────────────────────────────────────

class VersionSelector(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        SectionLabel(self, "Premiere Pro バージョン").pack(anchor="w", pady=(0, 4))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        self._var = ctk.StringVar()
        self._combo = ctk.CTkComboBox(row, variable=self._var, width=200,
                                      state="readonly")
        self._combo.pack(side="left")

        ctk.CTkButton(row, text="再検出", width=80, command=self.refresh
                      ).pack(side="left", padx=(8, 0))

        self._info = ctk.CTkLabel(row, text="", text_color="#888888",
                                  font=ctk.CTkFont(size=11))
        self._info.pack(side="left", padx=(8, 0))

        self.refresh()

    def refresh(self):
        versions = core.find_premiere_versions()
        if versions:
            self._combo.configure(values=versions)
            self._combo.set(versions[0])
            self._info.configure(text=f"{len(versions)} バージョン検出")
        else:
            self._combo.configure(values=["（未検出）"])
            self._combo.set("（未検出）")
            self._info.configure(text="Premiere Proが見つかりません")

    @property
    def value(self) -> str:
        return self._var.get()

    def is_valid(self) -> bool:
        return self.value not in ("", "（未検出）")


# ─────────────────────────────────────────────
# Category checkbox group
# ─────────────────────────────────────────────

CATEGORIES = [
    ("mogrt",     "Motion Graphics Templates (.mogrt)"),
    ("preset",    "エフェクトプリセット (.prfpset)"),
    ("shortcuts", "キーボードショートカット (.kys)"),
    ("layouts",   "ワークスペースレイアウト"),
]


class CategorySelector(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._vars = {}
        self._counts = {}

        SectionLabel(self, "エクスポートする項目").pack(anchor="w", pady=(0, 6))

        for key, label in CATEGORIES:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", pady=2)

            var = ctk.BooleanVar(value=True)
            self._vars[key] = var

            chk = ctk.CTkCheckBox(row, text=label, variable=var,
                                   command=self._on_change)
            chk.pack(side="left")

            cnt = ctk.CTkLabel(row, text="", text_color="#888888",
                               font=ctk.CTkFont(size=11))
            cnt.pack(side="left", padx=(8, 0))
            self._counts[key] = cnt

    def _on_change(self):
        pass

    def get_selected(self) -> dict:
        return {k: v.get() for k, v in self._vars.items()}

    def update_counts(self, counts: dict):
        for key, label_w in self._counts.items():
            n = counts.get(key, 0)
            if n > 0:
                label_w.configure(text=f"({n} 個)", text_color="#888888")
            else:
                label_w.configure(text="(見つからず)", text_color=WARNING)


# ─────────────────────────────────────────────
# Log box
# ─────────────────────────────────────────────

class LogBox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("height", 150)
        kwargs.setdefault("state", "disabled")
        kwargs.setdefault("font", ctk.CTkFont(family="Consolas", size=12))
        super().__init__(master, **kwargs)

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

    def append(self, text: str, color: str | None = None):
        self.configure(state="normal")
        self.insert("end", text + "\n")
        self.configure(state="disabled")
        self.see("end")


# ─────────────────────────────────────────────
# Export tab
# ─────────────────────────────────────────────

class ExportTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        pad = {"padx": 20, "pady": 8}

        # ── Version
        self._version = VersionSelector(self)
        self._version.pack(fill="x", **pad)
        self._version._combo.configure(command=lambda _: self._refresh_counts())

        # ── Categories
        self._cats = CategorySelector(self)
        self._cats.pack(fill="x", **pad)
        # patch on_change to refresh counts
        for v in self._cats._vars.values():
            v.trace_add("write", lambda *_: self._refresh_counts())

        ctk.CTkButton(self, text="ファイル数を確認", command=self._refresh_counts,
                      fg_color="#555555", hover_color="#666666"
                      ).pack(anchor="w", padx=20, pady=(0, 4))

        # ── Output path
        card = Card(self)
        card.pack(fill="x", **pad)

        SectionLabel(card, "保存先").pack(anchor="w", padx=12, pady=(10, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))

        self._out_var = ctk.StringVar(value=self._default_path())
        ctk.CTkEntry(row, textvariable=self._out_var, width=360).pack(side="left")
        ctk.CTkButton(row, text="参照", width=70,
                      command=self._browse_out).pack(side="left", padx=(8, 0))

        # ── Export button
        self._btn = ctk.CTkButton(
            self, text="エクスポート", height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ACCENT, hover_color="#3080DD",
            command=self._do_export
        )
        self._btn.pack(fill="x", padx=20, pady=12)

        # ── Log
        SectionLabel(self, "ログ").pack(anchor="w", padx=20)
        self._log = LogBox(self, height=120)
        self._log.pack(fill="x", padx=20, pady=(4, 16))

    def _default_path(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return str(Path.home() / "Desktop" / f"premiere_settings_{ts}.zip")

    def _refresh_counts(self):
        if not self._version.is_valid():
            return
        counts = core.count_files(self._version.value, self._cats.get_selected())
        self._cats.update_counts(counts)

    def _browse_out(self):
        path = filedialog.asksaveasfilename(
            title="保存先を選択",
            defaultextension=".zip",
            filetypes=[("ZIP ファイル", "*.zip")],
            initialfile=Path(self._out_var.get()).name,
        )
        if path:
            self._out_var.set(path)

    def _do_export(self):
        if not self._version.is_valid():
            messagebox.showwarning("警告", "Premiere Pro のバージョンが選択されていません")
            return

        include = self._cats.get_selected()
        if not any(include.values()):
            messagebox.showwarning("警告", "エクスポートする項目を1つ以上選んでください")
            return

        out = self._out_var.get().strip()
        if not out:
            messagebox.showwarning("警告", "保存先を指定してください")
            return

        self._btn.configure(state="disabled", text="エクスポート中...")
        self.update()

        ok, msg = core.export_to_zip(self._version.value, include, out)

        self._btn.configure(state="normal", text="エクスポート")
        self._log.clear()
        self._log.append(msg)

        if ok:
            messagebox.showinfo("完了", msg)
            # Update default path for next export
            self._out_var.set(self._default_path())
        else:
            messagebox.showerror("エラー", msg)


# ─────────────────────────────────────────────
# Import tab
# ─────────────────────────────────────────────

class ImportTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        pad = {"padx": 20, "pady": 8}

        # ── Zip file selector
        card = Card(self)
        card.pack(fill="x", **pad)

        SectionLabel(card, "インポートするZIPファイル").pack(anchor="w", padx=12, pady=(10, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))

        self._zip_var = ctk.StringVar()
        self._zip_entry = ctk.CTkEntry(row, textvariable=self._zip_var, width=360,
                                       placeholder_text="ZIPファイルを選択してください")
        self._zip_entry.pack(side="left")
        ctk.CTkButton(row, text="参照", width=70,
                      command=self._browse_zip).pack(side="left", padx=(8, 0))

        # ── Preview area
        self._preview = Card(self)
        self._preview.pack(fill="x", **pad)
        SectionLabel(self._preview, "ZIPの中身").pack(anchor="w", padx=12, pady=(10, 4))
        self._preview_text = ctk.CTkTextbox(self._preview, height=130, state="disabled",
                                             font=ctk.CTkFont(family="Consolas", size=12))
        self._preview_text.pack(fill="x", padx=12, pady=(0, 10))

        # ── Destination version
        self._version = VersionSelector(self)
        self._version.pack(fill="x", **pad)

        # ── Overwrite option
        self._overwrite = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="既存ファイルを上書きする",
                        variable=self._overwrite
                        ).pack(anchor="w", padx=20, pady=4)

        # ── Import button
        self._btn = ctk.CTkButton(
            self, text="インポート", height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SUCCESS, hover_color="#3D8E40",
            command=self._do_import
        )
        self._btn.pack(fill="x", padx=20, pady=12)

        # ── Log
        SectionLabel(self, "結果").pack(anchor="w", padx=20)
        self._log = LogBox(self, height=130)
        self._log.pack(fill="x", padx=20, pady=(4, 16))

        # ── Watch for zip path changes
        self._zip_var.trace_add("write", lambda *_: self._load_preview())

    def _browse_zip(self):
        path = filedialog.askopenfilename(
            title="ZIPファイルを選択",
            filetypes=[("ZIP ファイル", "*.zip"), ("すべてのファイル", "*.*")],
        )
        if path:
            self._zip_var.set(path)

    def _load_preview(self):
        path = self._zip_var.get().strip()
        self._preview_text.configure(state="normal")
        self._preview_text.delete("1.0", "end")

        if not path or not Path(path).exists():
            self._preview_text.configure(state="disabled")
            return

        info = core.preview_zip(path)
        if info.get("error"):
            self._preview_text.insert("end", f"エラー: {info['error']}")
            self._preview_text.configure(state="disabled")
            return

        m = info["manifest"]
        lines = [
            f"作成日時 : {m.get('created', '?')[:19].replace('T', ' ')}",
            f"作成元OS : {'Windows' if m.get('platform') == 'windows' else 'Mac'}",
            f"PPro Ver : {m.get('premiere_version', '?')}",
            "",
            "含まれる項目:",
        ]
        for cat, files in info["items"].items():
            name = core.CATEGORY_NAMES.get(cat, cat)
            lines.append(f"  • {name}: {len(files)} 個")

        self._preview_text.insert("end", "\n".join(lines))
        self._preview_text.configure(state="disabled")

    def _do_import(self):
        zip_path = self._zip_var.get().strip()
        if not zip_path or not Path(zip_path).exists():
            messagebox.showwarning("警告", "ZIPファイルを選択してください")
            return

        if not self._version.is_valid():
            messagebox.showwarning("警告", "インストール先のバージョンを選択してください")
            return

        self._btn.configure(state="disabled", text="インポート中...")
        self.update()

        ok, summary, log_lines = core.import_from_zip(
            zip_path, self._version.value, self._overwrite.get()
        )

        self._btn.configure(state="normal", text="インポート")
        self._log.clear()
        for line in log_lines:
            self._log.append(line)

        if ok:
            messagebox.showinfo("完了", summary)
        else:
            messagebox.showerror("エラー", summary)


# ─────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Premiere Pro Settings Migrator")
        self.geometry("560x720")
        self.minsize(520, 620)
        self.resizable(True, True)

        # Header
        header = ctk.CTkFrame(self, fg_color="#1E1F22", corner_radius=0, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Premiere Pro Settings Migrator",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            header,
            text=f"v{core.TOOL_VERSION}  |  {core.get_platform().capitalize()}",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        ).pack(side="right", padx=20)

        # Tab view
        tabs = ctk.CTkTabview(self, anchor="nw")
        tabs.pack(fill="both", expand=True, padx=10, pady=10)

        tabs.add("エクスポート")
        tabs.add("インポート")

        # Scrollable frames inside each tab
        export_scroll = ctk.CTkScrollableFrame(tabs.tab("エクスポート"),
                                               fg_color="transparent")
        export_scroll.pack(fill="both", expand=True)

        import_scroll = ctk.CTkScrollableFrame(tabs.tab("インポート"),
                                               fg_color="transparent")
        import_scroll.pack(fill="both", expand=True)

        ExportTab(export_scroll).pack(fill="both", expand=True)
        ImportTab(import_scroll).pack(fill="both", expand=True)
