"""
Premiere Pro Settings Migrator - Core Logic
Windows / Mac cross-platform support
"""
import os
import sys
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional

TOOL_VERSION = "1.0.0"

CATEGORY_NAMES = {
    "mogrt":     "Motion Graphics Templates",
    "preset":    "エフェクトプリセット",
    "shortcuts": "キーボードショートカット",
    "layouts":   "ワークスペースレイアウト",
}

# ─────────────────────────────────────────────
# Platform helpers
# ─────────────────────────────────────────────

def get_platform() -> str:
    return "windows" if sys.platform == "win32" else "mac"


def _appdata() -> Path:
    """Return %APPDATA% on Windows or ~/Library/Preferences on Mac."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return Path.home() / "Library" / "Preferences"


def _app_support() -> Path:
    """Return ~/Library/Application Support on Mac, %APPDATA% on Windows."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    return Path.home() / "Library" / "Application Support"


# ─────────────────────────────────────────────
# Premiere Pro path detection
# ─────────────────────────────────────────────

def get_premiere_doc_base() -> Optional[Path]:
    """Documents/Adobe/Premiere Pro  (both platforms)."""
    docs = Path.home() / "Documents" / "Adobe" / "Premiere Pro"
    return docs if docs.exists() else None


def find_premiere_versions() -> list:
    """Scan for installed Premiere Pro versions (by profile folder names)."""
    base = get_premiere_doc_base()
    if not base:
        return []
    versions = [
        item.name for item in base.iterdir()
        if item.is_dir() and item.name[:2].isdigit()
    ]
    return sorted(versions, reverse=True)


def find_profile_dir(version: str) -> Optional[Path]:
    """Return the Profile-* directory for the given version."""
    base = get_premiere_doc_base()
    if not base:
        return None
    ver_dir = base / version
    if not ver_dir.exists():
        return None
    for item in ver_dir.iterdir():
        if item.is_dir() and item.name.startswith("Profile"):
            return item
    return None


def get_mogrt_dir() -> Optional[Path]:
    """User-level MOGRT folder."""
    path = _app_support() / "Adobe" / "Common" / "Motion Graphics Templates"
    return path if path.exists() else None


def get_layouts_dir(version: str) -> Optional[Path]:
    """Workspace layouts folder for the given version."""
    base = _appdata() / "Adobe" / "Premiere Pro" / version
    if not base.exists():
        return None
    for item in base.iterdir():
        if item.is_dir() and item.name.startswith("Profile"):
            layouts = item / "Layouts"
            if layouts.exists():
                return layouts
    return None


# ─────────────────────────────────────────────
# File collection
# ─────────────────────────────────────────────

def collect_files(version: str, include: dict) -> dict:
    """
    Returns {category: {"source_dir": str, "files": [str, ...]}}
    for each enabled category.
    """
    result = {}
    profile_dir = find_profile_dir(version)

    if include.get("mogrt"):
        d = get_mogrt_dir()
        if d:
            files = [str(f) for f in d.rglob("*.mogrt") if f.is_file()]
            result["mogrt"] = {"source_dir": str(d), "files": files}

    if include.get("preset") and profile_dir:
        files = [str(f) for f in profile_dir.glob("*.prfpset")]
        if files:
            result["preset"] = {"source_dir": str(profile_dir), "files": files}

    if include.get("shortcuts") and profile_dir:
        # Windows: Profile-*/Win/*.kys  / Mac: Profile-*/Mac/*.kys
        subdir = "Win" if sys.platform == "win32" else "Mac"
        kys_dir = profile_dir / subdir
        if kys_dir.exists():
            files = [str(f) for f in kys_dir.glob("*.kys")]
        else:
            # Fallback: search directly in profile dir
            files = [str(f) for f in profile_dir.glob("*.kys")]
        if files:
            result["shortcuts"] = {
                "source_dir": str(kys_dir if kys_dir.exists() else profile_dir),
                "files": files,
            }

    if include.get("layouts") and profile_dir:
        layouts_dir = profile_dir / "Layouts"
        if layouts_dir.exists():
            files = [str(f) for f in layouts_dir.rglob("*") if f.is_file()]
            if files:
                result["layouts"] = {"source_dir": str(layouts_dir), "files": files}

    return result


def count_files(version: str, include: dict) -> dict:
    """Return {category: count} for UI preview."""
    data = collect_files(version, include)
    return {cat: len(v["files"]) for cat, v in data.items()}


# ─────────────────────────────────────────────
# Export
# ─────────────────────────────────────────────

def export_to_zip(version: str, include: dict, output_path: str) -> tuple:
    """
    Export selected items into a zip archive.
    Returns (success: bool, message: str)
    """
    try:
        file_data = collect_files(version, include)
        if not file_data:
            return False, "エクスポートするファイルが見つかりませんでした"

        manifest = {
            "tool_version": TOOL_VERSION,
            "premiere_version": version,
            "platform": get_platform(),
            "created": datetime.now().isoformat(),
            "items": list(file_data.keys()),
        }

        total = 0
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json",
                        json.dumps(manifest, indent=2, ensure_ascii=False))
            for category, data in file_data.items():
                source_dir = Path(data["source_dir"])
                for fp_str in data["files"]:
                    fp = Path(fp_str)
                    if not fp.exists():
                        continue
                    rel = fp.relative_to(source_dir)
                    # Use forward slashes inside the archive for cross-platform safety
                    arcname = f"{category}/{rel.as_posix()}"
                    zf.write(fp, arcname)
                    total += 1

        if total == 0:
            return False, "エクスポートできるファイルがありませんでした"
        return True, f"{total} 個のファイルをエクスポートしました\n保存先: {output_path}"

    except Exception as e:
        return False, f"エラー: {e}"


# ─────────────────────────────────────────────
# Preview zip
# ─────────────────────────────────────────────

def preview_zip(zip_path: str) -> dict:
    """
    Returns:
      {"manifest": {...}, "items": {category: [filename, ...]}, "error": None}
      or {"error": "message"}
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                return {"error": "このファイルはPremiere Migratorで作成されたzipではありません"}
            manifest = json.loads(zf.read("manifest.json"))

            items: dict = {}
            for name in zf.namelist():
                if name == "manifest.json" or name.endswith("/"):
                    continue
                parts = name.split("/", 1)
                if len(parts) == 2:
                    cat, fname = parts
                    items.setdefault(cat, []).append(fname)

            return {"manifest": manifest, "items": items, "error": None}
    except zipfile.BadZipFile:
        return {"error": "有効なzipファイルではありません"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Import
# ─────────────────────────────────────────────

def _get_dest_dir(category: str, version: str) -> Optional[Path]:
    if category == "mogrt":
        d = get_mogrt_dir()
        if d is None:
            # Create the default location
            d = _app_support() / "Adobe" / "Common" / "Motion Graphics Templates"
        return d
    if category == "preset":
        return find_profile_dir(version)
    if category == "shortcuts":
        profile = find_profile_dir(version)
        if profile is None:
            return None
        subdir = "Win" if sys.platform == "win32" else "Mac"
        kys_dir = profile / subdir
        kys_dir.mkdir(parents=True, exist_ok=True)
        return kys_dir
    if category == "layouts":
        profile = find_profile_dir(version)
        if profile is None:
            return None
        layouts = profile / "Layouts"
        layouts.mkdir(parents=True, exist_ok=True)
        return layouts
    return None


def import_from_zip(zip_path: str, version: str,
                    overwrite: bool = False) -> tuple:
    """
    Import from a zip archive into the current platform's Premiere paths.
    Returns (success: bool, summary: str, log_lines: list[str])
    """
    log = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                return False, "有効なMigratorファイルではありません", []

            manifest = json.loads(zf.read("manifest.json"))
            src_platform = manifest.get("platform", "unknown")
            categories = manifest.get("items", [])

            if src_platform != get_platform():
                log.append(
                    f"⚠ プラットフォーム変換: {src_platform} → {get_platform()}\n"
                    "  キーボードショートカットは一部のキーが異なる場合があります"
                )

            imported_total = 0
            skipped_total = 0

            for category in categories:
                dest_dir = _get_dest_dir(category, version)
                if dest_dir is None:
                    log.append(f"✗ {CATEGORY_NAMES.get(category, category)}: "
                               "インストール先が見つかりません（Premiere Proが未インストール？）")
                    continue

                dest_dir = Path(dest_dir)
                dest_dir.mkdir(parents=True, exist_ok=True)

                cat_files = [n for n in zf.namelist()
                             if n.startswith(f"{category}/") and not n.endswith("/")]

                count = 0
                skipped = 0
                for arc_name in cat_files:
                    rel = arc_name[len(category) + 1:]
                    dest_file = dest_dir / Path(rel)
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    if dest_file.exists() and not overwrite:
                        skipped += 1
                        skipped_total += 1
                        continue

                    data = zf.read(arc_name)
                    dest_file.write_bytes(data)
                    count += 1
                    imported_total += 1

                msg = f"✓ {CATEGORY_NAMES.get(category, category)}: {count} 個をインポート"
                if skipped:
                    msg += f" ({skipped} 個スキップ)"
                log.append(msg)

        summary = f"完了: {imported_total} 個をインポート"
        if skipped_total:
            summary += f"、{skipped_total} 個スキップ（上書きしない設定）"
        return True, summary, log

    except Exception as e:
        return False, f"エラー: {e}", log
