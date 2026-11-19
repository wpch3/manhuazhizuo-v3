# 被拒绝的 NTR 老师

第 1 话：**我画的女生，从来不看我**

> 竖屏第一人称漫画系列。画风延续 `wpch3/shi-pin-zhizuo-v2` 的暖纸色可爱风格，
> 排版规范与气泡几何延续 `wpch3/shi-pin-zhizuo`（v1）。

## 一句话概念

一个专门画 NTR、靠"让读者生气"涨粉的漫画作者，
接连被现实里温柔、清醒的女孩子礼貌地拒绝，最后单身到老。

## 核心原则

1. **第一人称**：镜头即主角的眼睛，读者就是"他"。
2. **刀刃对准他，不对准女生**：所有女生都清醒、温柔、有礼貌，拒绝干净利落。
3. **他爱的是"被抢走"这件事**，不是人。这是他真正的病。
4. **尺度**：全部角色成年；无露骨内容；只用台词与镜头暗示"抢夺"梗。
5. **每话一句最狠的台词**，留给读者截图。

## 目录

```
art/lv1/            原画（WebP，生图产物，不含任何文字）
art/lv1/ref/        角色基准图（锁定画风与五官）
docs/LV1_剧本与分镜.md     剧本、逐页台词、删掉的备选台词
docs/LV1_制作记录.md       画风锁定、逐页自查
docs/LV2_方案草案.md       下一话 5 个方向
scripts/comic_layout.py   排版引擎（椭圆气泡 + 真实文字测量）
scripts/build_lv1.py      LV1 构建（输出 PNG 与 PDF）
deliverables/lv1/    成品页面 1440×1920（WebP q95）
```

## 构建

```bash
pip install --break-system-packages Pillow numpy
python3 scripts/build_lv1.py
```

输出：`deliverables/lv1/*.webp` 与 `deliverables/LV1_第1话_试读.pdf`（12 页）

## 字体与许可

- `assets/fonts/NotoSansCJKsc-*.otf`：SIL Open Font License（见 `OFL.txt`）。
- `scripts/speech_bubble_geometry.py`：改编自 splargdotcom/speechbubble（MIT，见
  `assets/licenses/speechbubble-MIT.txt`）。

## 体积规范

见 `docs/仓库体积规范.md`。要点：
- 原画与成品统一 WebP（原画 q92、成品 q95），单张 < 1 MB；
- 无损母版放 `art/lv1/master/`（已 gitignore），不重复入库；
- 试读 PDF 以 JPEG q95 内嵌，整本 < 15 MB；
- 每话结束检查 `du -sh art deliverables` 与 `git count-objects -vH`。
