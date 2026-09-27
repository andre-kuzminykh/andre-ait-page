# -*- coding: utf-8 -*-
"""Колода лекции ↔ отдельные слайды: разрезать для правок и собрать обратно.

    python3 tools/deck_split.py extract 1     # automation/1/index.html → build/l1/out/slide-NN.html
    python3 tools/deck_split.py assemble 1    # build/l1/out → automation/1/index.html
    python3 tools/deck_split.py check 1       # разрезать и собрать в памяти: побайтово то же

Зачем. Лекции 1 и 2 сверстаны одним файлом, без сборщика, как у лекций 3–6.
Когда слайды правят несколько агентов сразу, правки одного большого файла
наступают друг на друга. Поэтому слайды режутся по файлу на слайд, правятся
по отдельности, меряются tools/deck_probe.py и собираются обратно в ту же
колоду: всё вне слайдов (голова, стили, тест, скрипты) остаётся побайтово
прежним.

Граница слайдов — от первого `<div class="slide-container` с отступом в четыре
пробела до комментария `<!-- Модальное окно теста -->`. Пустые строки после
слайда принадлежат ему, поэтому разрезать и собрать без правок = тот же файл
(это проверяет `check`).

Для замеров: DECK_OUT — другая папка слайдов, DECK_DST — другой файл колоды.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
END = "    <!-- Модальное окно теста -->"
START = re.compile(r'(?m)^(?=    <div class="slide-container)')
SID = re.compile(r'<div class="slide-container[^"]*" id="slide-(\d+)"')


def deck_path(n):
    return os.path.join(ROOT, "automation", str(n), "index.html")


def out_dir(n):
    return os.environ.get("DECK_OUT") or os.path.join(ROOT, "build", "l%s" % n, "out")


def split(html):
    """(голова, [слайды по порядку], хвост)."""
    m = START.search(html)
    if not m:
        raise SystemExit("в колоде нет слайдов")
    start, end = m.start(), html.index(END)
    parts = [p for p in START.split(html[start:end]) if p]
    ids = [int(SID.search(p).group(1)) for p in parts]
    if ids != list(range(len(parts))):
        raise SystemExit("слайды идут не по порядку: %s" % ids)
    return html[:start], parts, html[end:]


def read_slides(folder):
    got = {}
    for f in sorted(os.listdir(folder)):
        if re.match(r"slide-\d+\.html$", f):
            s = io.open(os.path.join(folder, f), encoding="utf-8").read()
            got[int(SID.search(s).group(1))] = s
    missing = [i for i in range(max(got) + 1) if i not in got]
    if missing:
        raise SystemExit("не хватает слайдов: %s" % missing)
    return [got[i] for i in sorted(got)]


def extract(n):
    head, parts, tail = split(io.open(deck_path(n), encoding="utf-8").read())
    folder = out_dir(n)
    os.makedirs(folder, exist_ok=True)
    for i, p in enumerate(parts):
        io.open(os.path.join(folder, "slide-%02d.html" % i), "w", encoding="utf-8").write(p)
    print("разрезана лекция %s: %d слайдов → %s" % (n, len(parts), folder))


def assemble(n):
    head, _, tail = split(io.open(deck_path(n), encoding="utf-8").read())
    parts = read_slides(out_dir(n))
    for i, p in enumerate(parts):
        if not p.endswith("\n"):
            parts[i] = p + "\n"
    dst = os.environ.get("DECK_DST") or deck_path(n)
    io.open(dst, "w", encoding="utf-8").write(head + "".join(parts) + tail)
    print("собрана лекция %s: %d слайдов → %s" % (n, len(parts), dst))


def check(n):
    html = io.open(deck_path(n), encoding="utf-8").read()
    head, parts, tail = split(html)
    same = head + "".join(parts) + tail == html
    print("лекция %s: %d слайдов, разрезать и собрать — %s"
          % (n, len(parts), "побайтово то же" if same else "РАСХОЖДЕНИЕ"))
    return 0 if same else 1


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("extract", "assemble", "check"):
        sys.exit(__doc__)
    cmd, n = sys.argv[1], sys.argv[2]
    sys.exit({"extract": extract, "assemble": assemble, "check": check}[cmd](n) or 0)
