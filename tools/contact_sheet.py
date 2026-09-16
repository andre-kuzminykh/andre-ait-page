# -*- coding: utf-8 -*-
"""Контактный лист кадров лекции: вся колода на нескольких картинках.

    python3 tools/lecture_check.py kadry 4 v1      # снять кадры
    python3 tools/contact_sheet.py v1 pc           # → build/lecture-frames/v1/pc-sheet-1.png

Зачем. П9 требует смотреть на каждое изменение глазами, а 43 слайда по
одному — это 43 открытых картинки. Контактный лист собирает их в сетку 4x3,
и колода просматривается за три листа.
"""
import os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS, ROWS, TW = 4, 3, 520          # 12 кадров на лист


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    tag, form = sys.argv[1], sys.argv[2]
    src = os.path.join(ROOT, "build", "lecture-frames", tag, form)
    files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
    if not files:
        sys.exit("нет кадров в %s" % src)
    made = []
    per = COLS * ROWS
    for page in range((len(files) + per - 1) // per):
        chunk = files[page * per:(page + 1) * per]
        thumbs = []
        for f in chunk:
            im = Image.open(os.path.join(src, f)).convert("RGB")
            th = TW / im.width
            thumbs.append((f, im.resize((TW, int(im.height * th)))))
        cw = TW + 8
        ch = max(t[1].height for t in thumbs) + 8
        sheet = Image.new("RGB", (cw * COLS, ch * ROWS), (235, 235, 235))
        for i, (f, im) in enumerate(thumbs):
            x, y = (i % COLS) * cw + 4, (i // COLS) * ch + 4
            sheet.paste(im, (x, y))
        out = os.path.join(src, "..", "%s-sheet-%d.png" % (form, page + 1))
        out = os.path.normpath(out)
        sheet.save(out)
        made.append((out, chunk[0], chunk[-1]))
    for out, a, b in made:
        print("%s  (%s … %s)" % (out, a, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
