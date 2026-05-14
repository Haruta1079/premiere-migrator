"""
アイコン生成スクリプト (CI / ローカルビルド共用)
- Windows: assets/icon.ico
- Mac:     assets/icon.icns  (iconutil が必要 = macOS のみ)
"""
import sys
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path("assets")
ASSETS.mkdir(exist_ok=True)


def make_frame(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 角丸の青い背景
    r = max(size // 6, 2)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill="#4A9EFF")

    # 中央に "P" の文字
    fs = max(int(size * 0.52), 8)
    font = None
    candidates = [
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
        # macOS (CI)
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        # Linux (GitHub Actions ubuntu)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, fs)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    d.text((size / 2, size / 2), "P", fill="white", anchor="mm", font=font)
    return img


# ── Windows .ico ──────────────────────────────
ico_path = ASSETS / "icon.ico"
sizes = [16, 32, 48, 256]
frames = [make_frame(s) for s in sizes]
frames[0].save(
    ico_path,
    format="ICO",
    sizes=[(s, s) for s in sizes],
    append_images=frames[1:],
)
print(f"Created {ico_path}")


# ── macOS .icns ───────────────────────────────
if sys.platform == "darwin":
    iconset = Path(tempfile.mkdtemp()) / "AppIcon.iconset"
    iconset.mkdir()

    for s in [16, 32, 64, 128, 256, 512]:
        make_frame(s).save(iconset / f"icon_{s}x{s}.png")
        make_frame(s * 2).save(iconset / f"icon_{s}x{s}@2x.png")

    icns_path = ASSETS / "icon.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
        check=True,
    )
    print(f"Created {icns_path}")
else:
    print("Skipped icon.icns (macOS only)")
