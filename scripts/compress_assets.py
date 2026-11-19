"""把 1440 宽母版图转成仓库友好的体积。

用法：
    python3 scripts/compress_assets.py            # 转换 art/ 与 deliverables/ 下的 PNG
    python3 scripts/compress_assets.py --dry-run  # 只看体积变化

规则见 docs/仓库体积规范.md：原画 WebP q92，成品 WebP q95；
已有 PNG 母版会被移动到 art/lv1/master/（gitignore），不删原文件。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "art/lv1/master"

JOBS = [
    (ROOT / "art/lv1", 92, 620),          # 原画
    (ROOT / "deliverables/lv1", 95, 950),  # 成品
]


def convert(path: Path, quality: int, cap_kb: int, dry: bool) -> tuple[int, int]:
    before = path.stat().st_size
    out = path.with_suffix(".webp")
    if dry:
        im = Image.open(path)
        arr = im.convert("RGB")
        tmp = Path("/tmp") / out.name
        arr.save(tmp, "WEBP", quality=quality, method=6)
        size = tmp.stat().st_size
        tmp.unlink(missing_ok=True)
        return before, size
    im = Image.open(path).convert("RGB")
    im.save(out, "WEBP", quality=quality, method=6)
    size = out.stat().st_size
    if size > cap_kb * 1024 and quality > 80:
        # 单次降质重试，避免超标文件进仓库
        im.save(out, "WEBP", quality=quality - 8, method=6)
        size = out.stat().st_size
    return before, size


def archive_master(path: Path) -> None:
    MASTER.mkdir(parents=True, exist_ok=True)
    target = MASTER / path.name
    if not target.exists():
        shutil.move(str(path), str(target))
    else:
        path.unlink()


def main() -> None:
    dry = "--dry-run" in sys.argv
    total_before = total_after = 0
    for folder, quality, cap in JOBS:
        if not folder.exists():
            continue
        for png in sorted(folder.glob("*.png")):
            before, after = convert(png, quality, cap, dry)
            total_before += before
            total_after += after
            print(f"{png.relative_to(ROOT)}: {before/1e6:.2f} -> {after/1e6:.2f} MB")
            if not dry:
                archive_master(png)
    if total_before:
        print(f"\n合计 {total_before/1e6:.1f} MB -> {total_after/1e6:.1f} MB "
              f"({after/total_before*100:.0f}%)" if total_before and total_after else "")


if __name__ == "__main__":
    main()
