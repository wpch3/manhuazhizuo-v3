"""LV1《被拒绝的 NTR 老师》第 1 话《我画的女生，从来不看我》排版构建。

用法：python3 scripts/build_lv1.py
输出：deliverables/lv1/*.png + deliverables/LV1_第1话_试读.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import comic_layout as L  # noqa: E402

ART = ROOT / "art/lv1"
OUT = ROOT / "deliverables/lv1"
OUT.mkdir(parents=True, exist_ok=True)


def cover(layer):
    L.caption(layer, (60, 40), ["第 1 话"], size=28, pad=(22, 12), radius=4, bold=False)
    L.caption(layer, (56, 96), ["被拒绝的", "NTR 老师"], size=76, pad=(36, 26), radius=6)
    L.caption(layer, (60, 392), ["我画的女生，从来不看我"], size=36,
              pad=(28, 18), radius=4, bold=False)


def p01(layer):
    # 「我二十四岁，是……」致敬 B 站「24 岁，是学生」句式（池沼梗）
    L.caption(layer, (44, 52), ["我二十四岁，", "是……画 NTR 的。"], size=44, pad=(30, 22))
    L.caption(layer, (44, 262), ["笔名「夜画」，四年没露过脸。",
                                 "读者只认我的笔，不认我的脸。"], size=38, pad=(30, 22))
    L.caption(layer, (930, 1640), ["今天要画完的，", "是女主被抢走那一页。"], size=38,
              pad=(28, 20), bold=False)


def p02(layer):
    L.caption(layer, (44, 56), ["我赚钱的公式，只有一句话："], size=44, pad=(30, 22))
    L.caption(layer, (140, 1676), ["「原本属于我的人，被抢走了。」",
                                   "越痛，越好看。",
                                   "这是我唯一会画的东西。"], size=34, pad=(30, 22))


def p03(layer):
    # 新构图：过肩远景，她在中景窗边看书，脸很小
    L.caption(layer, (628, 74), ["然后，我在咖啡店看见了她。"], size=40, pad=(30, 22))
    L.caption(layer, (70, 1700), ["我站了一会儿，才敢走过去。"], size=34, pad=(26, 18),
              bold=False)


def p04(layer):
    # 新构图：她刚从稿子上抬头，眼睛还在纸上
    L.caption(layer, (74, 72), ["我忘了，", "把打印稿收起来。"], size=34, pad=(28, 20), bold=False)
    L.speech(layer, (316, 700), ["这个分镜……", "是你画的吧？"], size=42,
             target=(612, 900), tail_len=58)


def p05(layer):
    # 新构图：她坐直、平视，单侧嘴角，不笑
    L.caption(layer, (72, 74), ["她说，她关注我很久了。", "每一话都看。"], size=36,
              pad=(30, 22))
    L.speech(layer, (318, 856), ["那我说实话", "可以吗？"], size=44,
             target=(700, 762), tail_len=92)
    L.caption(layer, (930, 1712), ["我点头点得太快了。"], size=32, pad=(24, 16), bold=False)


def p06(layer):
    # 新构图：速写本平放桌面，她抬眼。两句连续话：第一泡有尾，第二泡无尾紧随
    L.speech(layer, (1052, 408), ["老师，你画的那些", "「被抢走」的女孩子……"], size=36,
             target=(686, 566), tail_len=104)
    L.speech(layer, (1052, 612), ["好像都没有", "自己喜欢的东西。"], size=36, target=None)
    L.caption(layer, (60, 1706), ["那一瞬间，我竟然有点想反驳。"], size=32, pad=(24, 16),
              bold=False)


def p07(layer):
    # rev.6 新原画：全页近景、她前倾，嘴闭不笑。左上角teal墙 + 左臂上叠放气泡，尾尖指向脸
    L.speech(layer, (255, 300), ["你笔下的女生，好像", "只有「被爱」和", "「被抢走」两种状态。"],
             size=33, target=(610, 780), tail_len=96)
    L.speech(layer, (255, 545), ["可是我们其实会——"], size=34, target=None)
    L.speech(layer, (255, 760), ["挑自己喜欢的伞。", "记得朋友不吃香菜。", "下雨天，也会突然想吃甜的。"],
             size=26, target=None)
    # rev.8 定稿：反射旁白按LTR阅读顺序移到右缘 y≈1010（三泡之后），不再抢在前面
    L.caption(layer, (1120, 1010), ["她说得很轻，", "像在替谁道歉。"], size=30, pad=(24, 16), bold=False)


def p08(layer):
    # rev.6 新构图：窗外她与围巾男生并肩，收敛的笑（眼弯、头微侧），全话唯一松弛的笑
    L.caption(layer, (62, 68), ["那天下午，我在窗边坐到天黑。"], size=36, pad=(28, 20))
    # 她隔着玻璃说话，属于"画外音"，不画尾巴（v1 铁律：说话者不在同一空间不画尾）
    L.speech(layer, (1258, 264), ["走吧，", "回家了。"], size=34, target=None)
    L.caption(layer, (742, 1666), ["她从来不属于谁。", "她只是她自己。"], size=40,
              pad=(32, 22))


def p09(layer):
    """第 9 页：他的解释（新画布）。旁白放顶部暗墙留白，不压手与数位板。"""
    L.caption(layer, (150, 66), ["我又新建了一个空白文件。"], size=40, pad=(30, 22))
    L.caption(layer, (150, 158), ["那部连载，后来没画完。"], size=34, pad=(26, 18), bold=False)
    L.caption(layer, (150, 228), ["不是因为没时间。"], size=34, pad=(26, 18), bold=False)
    L.caption(layer, (150, 298), ["是因为画不下去。"], size=34, pad=(26, 18), bold=False)


def p10(layer):
    # rev.6 新原画：右上空墙叠三块（四十年后/他还在画/爷爷画外音），无尾
    L.caption(layer, (852, 74), ["四十年后。"], size=46, pad=(32, 24))
    L.caption(layer, (852, 204), ["我还在画。", "不过现在，我画的是纯爱。"], size=34,
              pad=(28, 20), bold=False)
    L.speech(layer, (1175, 560), ["爷爷，", "这一段真好看。"], size=34, target=None)


PAGES = [
    ("page-00-cover", "cover", cover, 0, None),
    ("page-01-desk", "p01", p01, 1, None),
    ("page-02-manuscript", "p02", p02, 2, None),
    ("page-03-cafe", "p03", p03, 3, None),
    ("page-04-lookup", "p04", p04, 4, None),
    ("page-05-standing", "p05", p05, 5, None),
    ("page-06-notebook", "p06", p06, 6,
     [(150, 120, 260, 250), (1256, 130, 270, 270)], None),
    ("page-07-touch", "p07", p07, 7, None),
    ("page-08-girl-noon", "p08", p08, 8, None),
    ("page-09-newpage", "p09", p09, 9, None),
    ("page-10-old-man", "p10", p10, 10, None),
]


def main():
    made = []
    for name, tag, fn, seed, soften, *rest in PAGES:
        art = ART / f"{name}.png"
        if not art.exists():
            art = ART / f"{name}.webp"
        if not art.exists():
            print(f"[skip] {name} 缺原画")
            continue
        out = OUT / f"{tag}.webp"
        L.compose(art, fn, seed=seed, out=out, erase=soften,
                  fade=(rest[0] if rest else None))
        made.append(out)
        print(f"[ok] {out.relative_to(ROOT)}")
    if made:
        pdf = ROOT / "deliverables/LV1_第1话_试读.pdf"
        tmp = []
        for i, p in enumerate(made):
            j = ROOT / "art/lv1/master/_pdf" / f"{i:02d}.jpg"
            j.parent.mkdir(parents=True, exist_ok=True)
            Image.open(p).convert("RGB").save(j, "JPEG", quality=95, subsampling=0,
                                             optimize=True)
            tmp.append(j)
        imgs = [Image.open(p).convert("RGB") for p in tmp]
        imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=150.0)
        print(f"[ok] {pdf.relative_to(ROOT)}  {len(imgs)} 页 "
              f"{pdf.stat().st_size/1e6:.1f} MB")
        for p in tmp:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
