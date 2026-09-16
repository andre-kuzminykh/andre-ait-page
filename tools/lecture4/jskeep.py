# -*- coding: utf-8 -*-
"""Пометить ряды класса js-keep: они остаются рядами и на телефоне.

    python3 build/l4/jskeep.py 13 29 33        # пометить в этих слайдах
    python3 build/l4/jskeep.py --show 13       # только показать кандидатов

Зачем. Скрипт лекции (annotate) складывает В СТОЛБИК любой элемент с классом
flex-row без md:flex-row, у которого три и более ребёнка:

    if (cl.indexOf(' flex-row ') !== -1 && cl.indexOf('md:flex-row') === -1 &&
        el.children.length >= 3){ el.classList.add('js-stack'); }

а .js-stack на телефоне — это flex-direction:column. Поэтому «поставить панели
рядом» для ряда из трёх и более элементов молча не работает: высота слайда
остаётся прежней, подгонщик ужимает текст, кегль падает ниже нормы.

Ряд, который обязан остаться рядом, помечается js-keep — annotate такие
пропускает. Класс чисто служебный, стилей у него нет, в собранный CSS ему
попадать не нужно.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def rows(html):
    """Все элементы с flex-row без md:flex-row и с >= 3 детьми-тегами."""
    found = []
    for m in re.finditer(r'<div class="([^"]*\bflex-row\b[^"]*)"[^>]*>', html):
        cls = m.group(1)
        if "md:flex-row" in cls or "js-keep" in cls:
            continue
        # считаем детей первого уровня
        depth, i, kids = 0, m.end(), 0
        while i < len(html):
            nxt = re.search(r"<(/?)(\w+)[^>]*?(/?)>", html[i:])
            if not nxt:
                break
            tag, close, selfclose = nxt.group(2), nxt.group(1), nxt.group(3)
            pos = i + nxt.end()
            if close:
                if depth == 0:
                    break
                depth -= 1
            elif not selfclose and tag not in ("br", "img", "input", "hr", "meta"):
                # <i> тоже парный: если не считать его вложенность, </i>
                # уводит глубину в минус и ряд «теряет» детей.
                if depth == 0:
                    kids += 1
                depth += 1
            elif depth == 0:
                kids += 1
            i = pos
        if kids >= 3:
            found.append((m.start(), m.group(0), kids))
    return found


def main():
    show = "--show" in sys.argv
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not ids:
        sys.exit(__doc__)
    for sid in ids:
        path = os.path.join(OUT, "slide-%02d.html" % sid)
        html = io.open(path, encoding="utf-8").read()
        found = rows(html)
        if show:
            print("слайд %d: рядов-кандидатов %d" % (sid, len(found)))
            for _, tag, kids in found:
                print("   детей %d  %s" % (kids, tag[:110]))
            continue
        for start, tag, kids in reversed(found):
            html = html[:start] + tag.replace('class="', 'class="js-keep ', 1) + html[start + len(tag):]
        io.open(path, "w", encoding="utf-8").write(html)
        print("слайд %d: помечено рядов %d" % (sid, len(found)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
