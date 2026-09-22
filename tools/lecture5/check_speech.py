# -*- coding: utf-8 -*-
"""Сверка колоды с озвучкой: слайд N несёт ровно свою тему.

Владелец: «чтобы соответствовало озвучке, чтобы на каждом слайде было ровно
то, о чём говорится». Темы 1–40 речи лежат в speech.json и отвечают слайдам
2–41; слайд 0 — обложка, 1 — содержание, 42 — заключение.

Сканер лексический: он считает, какая доля значимых слов темы стоит прямо
на слайде, а какая ушла в статью панели. Совпадение слов — не доказательство
(слайд вправе пересказать тему своими словами), поэтому сканер НЕ приговор,
а указатель: слайд с низким покрытием надо перечитать глазами рядом с темой.

    python3 tools/lecture5/check_speech.py build/l5/out build/l5/notes
    python3 tools/lecture5/check_speech.py build/l5v2/out build/l5v2/notes
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Служебные слова: встречаются в любой теме и ничего не доказывают.
STOP = set("""который которая которые когда чтобы потому этого этому этот эта эти
такой такая такие также можно нужно надо будет become только самый самая более менее
каждый каждая каждое всего вместе вместо через после перед между внутри вокруг
становится становятся делает делают работает работают нужны нужен значит например
разных разные разное одного одной одном одним целом целиком просто сразу сначала
затем потом здесь тогда очень много мало часто редко обычно именно ровно почти
дальше далее выше ниже своей своих свою свои этой этих иначе либо даже сама само
сами себя быть есть было были будут может могут должен должна должны""".split())


def words(s):
    return [w for w in re.findall(r"[а-яёa-z]{5,}", s.lower()) if w not in STOP]


def visible(html):
    html = re.sub(r"&shy;", "", html)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def article(path):
    d = json.load(io.open(path, encoding="utf-8"))
    s = d["title"]
    for b in d["blocks"]:
        v = b["v"]
        if b["t"] == "cards":
            s += " " + " ".join(c["h"] + " " + c["p"] for c in v)
        elif isinstance(v, list):
            s += " " + " ".join(v)
        else:
            s += " " + v
    return s


def main():
    out = os.path.join(ROOT, sys.argv[1] if len(sys.argv) > 1 else "build/l5/out")
    notes = os.path.join(ROOT, sys.argv[2] if len(sys.argv) > 2 else "build/l5/notes")
    topics = json.load(io.open(os.path.join(ROOT, "tools/lecture5/speech.json"),
                               encoding="utf-8"))
    rows, thin = [], []
    for k in sorted(topics, key=int):
        n = int(k)
        slide = visible(io.open(os.path.join(out, "slide-%02d.html" % n),
                                encoding="utf-8").read()).lower()
        panel = article(os.path.join(notes, "slide-%02d.json" % n)).lower()
        need = set(words(topics[k]))
        # Достаточно корня: «требование» покрывает «требования», «требований».
        def seen(w, hay):
            return w[:6] in hay
        on_slide = {w for w in need if seen(w, slide)}
        anywhere = {w for w in need if seen(w, slide) or seen(w, panel)}
        cov = 100.0 * len(on_slide) / max(1, len(need))
        rows.append((n, cov, 100.0 * len(anywhere) / max(1, len(need))))
        if cov < 40:
            thin.append((n, cov, sorted(need - on_slide)[:6]))
    print("тем сверено: %d (слайды 2–41)" % len(topics))
    print("покрытие темы слайдом: в среднем %.0f%%; слайдом или панелью: %.0f%%"
          % (sum(r[1] for r in rows) / len(rows), sum(r[2] for r in rows) / len(rows)))
    if thin:
        print("\nПЕРЕЧИТАТЬ ГЛАЗАМИ — на слайде меньше 40%% слов темы:")
        for n, c, g in thin:
            print("  слайд %2d: %.0f%% — не на слайде: %s" % (n, c, ", ".join(g)))
    else:
        print("слайдов со слабым покрытием нет")
    return 0


if __name__ == "__main__":
    sys.exit(main())
