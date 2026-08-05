# -*- coding: utf-8 -*-
"""Разносит общие блоки лекции 1 по лекциям 2–8.

Стили и скрипты портала (подгонка слайда, панель текста, шапка, полировка)
у всех восьми лекций обязаны быть побайтово одинаковыми — это стережёт
`tests/test_lectures.py::test_shared_blocks_identical`. Правим лекцию 1 и
запускаем:

    python3 tools/sync_lecture_blocks.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "automation/1/index.html")
TARGETS = [os.path.join(ROOT, "automation/%d/index.html" % n) for n in range(2, 9)]

# (тег, id) — блоки, которые обязаны совпадать во всех лекциях
BLOCKS = [
    ("style", "lecture-chrome"),
    ("style", "portal-deck"),
    ("style", "slide-polish"),
    ("style", "radial-fig"),
    ("style", "notes-panel-style"),
    ("script", "portal-fit"),
    ("script", "notes-panel-script"),
]

# Куски разметки, которые тоже должны быть одинаковыми (кнопки шапки).
MARKUP = [
    re.compile(r'<button id="notes-toggle"[^>]*>.*?</button>', re.S),
]


def block(html, tag, ident):
    m = re.search(r'<%s id="%s">.*?</%s>' % (tag, ident, tag), html, re.S)
    return m.group(0) if m else None


def main():
    src = open(SOURCE, encoding="utf-8").read()
    pieces = []
    for tag, ident in BLOCKS:
        b = block(src, tag, ident)
        if b is None:
            print("в лекции 1 нет блока %s#%s — пропускаю" % (tag, ident))
            continue
        pieces.append((tag, ident, b))
    marks = []
    for rx in MARKUP:
        m = rx.search(src)
        if m:
            marks.append((rx, m.group(0)))

    changed = 0
    for path in TARGETS:
        if not os.path.exists(path):
            continue
        html = open(path, encoding="utf-8").read()
        before = html
        for tag, ident, b in pieces:
            old = block(html, tag, ident)
            if old is None:
                print("%s: нет блока %s#%s" % (os.path.relpath(path, ROOT), tag, ident))
                continue
            html = html.replace(old, b, 1)
        for rx, new in marks:
            html = rx.sub(lambda _m: new, html, count=1)
        if html != before:
            open(path, "w", encoding="utf-8").write(html)
            changed += 1
            print("обновлено:", os.path.relpath(path, ROOT))
    print("готово, файлов изменено:", changed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
