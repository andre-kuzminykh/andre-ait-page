# -*- coding: utf-8 -*-
"""Сверка видимого текста слайда до и после правки вёрстки.

    python3 tools/deck_textdiff.py 1 7        # лекция 1, слайд 7
    python3 tools/deck_textdiff.py 1          # все слайды лекции 1

Сравнивает build/l<N>/out/slide-NN.html с базовой копией build/l<N>/base/
(её кладёт `tools/deck_split.py extract` в DECK_OUT=build/l<N>/base перед
правками). Владелец: «текст и сами инфографики по смыслу там ок» — правка
вёрстки не имеет права потерять, добавить или переписать слово. Сравнение
идёт по словам после нормализации: теги и комментарии сняты, сущности
раскрыты, неразрывные пробел и дефис приравнены к обычным, мягкий перенос
убран — поэтому <br>, whitespace-nowrap и &nbsp; расхождением не считаются.

Код выхода 0 — текст тот же, 1 — есть расхождения (печатаются).
"""
import difflib
import html
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def words(markup):
    s = re.sub(r"<!--.*?-->", " ", markup, flags=re.S)
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace(" ", " ").replace("‑", "-").replace("­", "").replace("​", "")
    return s.split()


def compare(n, k):
    base = os.path.join(ROOT, "build", "l%s" % n, "base", "slide-%02d.html" % k)
    cur = os.path.join(ROOT, "build", "l%s" % n, "out", "slide-%02d.html" % k)
    a = words(io.open(base, encoding="utf-8").read())
    b = words(io.open(cur, encoding="utf-8").read())
    if a == b:
        return []
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append("%s: «%s» → «%s»" % (op, " ".join(a[i1:i2]), " ".join(b[j1:j2])))
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    n = sys.argv[1]
    folder = os.path.join(ROOT, "build", "l%s" % n, "base")
    ks = [int(sys.argv[2])] if len(sys.argv) > 2 else sorted(
        int(re.search(r"\d+", f).group()) for f in os.listdir(folder) if f.startswith("slide-"))
    bad = 0
    for k in ks:
        d = compare(n, k)
        if d:
            bad += 1
            print("слайд %d: текст изменился" % k)
            for line in d:
                print("   " + line)
    if not bad:
        print("текст тот же: %s" % (", ".join(map(str, ks)) if len(ks) < 6 else "%d слайдов" % len(ks)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
