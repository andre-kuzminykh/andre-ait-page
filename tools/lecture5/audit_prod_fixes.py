# -*- coding: utf-8 -*-
"""Проверка, что правки владельца (круг 3, пункты 32–43) на месте.

Зачем. Вторая колода (build/l5v2) была отпочкована ДО этого круга правок,
и агенты переписывали слайды со старой версии — правки владельца могли
молча пропасть. Этот сканер держит их зафиксированными для любой колоды.

    python3 tools/lecture5/audit_prod_fixes.py build/l5/out
    python3 tools/lecture5/audit_prod_fixes.py build/l5v2/out

Нумерация владельца = индекс слайда + 1 (пункт 32 → slide-31).
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# слайд → список (метка пункта, «должно быть», «не должно быть»[, «только если»])
# «должно быть» — подстрока или (min_count, подстрока); «не должно» — подстрока.
# Четвёртый элемент — якорь: правка проверяется, только если он есть на слайде.
# Нужен для второй колоды, где ряды примеров сняты целиком и выравнивать нечего.
CHECKS = {
    31: [("32 убрать «и текущую основу»", None, "и текущую основу"),
         ("32 перенос в подзаголовке", " <br>", None),
         ("32 выровнять карточки", (4, "flex flex-col justify-center"), None)],
    33: [("34 цикл, не круг", "следующего цикла", "следующего круга")],
    34: [("35 подзаголовок в строчку", "хватает на основное, но нужна своя бизнес-логика", None),
         ("35 цикл доработки", "цикл доработки", "круг доработки")],
    35: [("36 плашки по центру", (8, "flex items-center justify-center"), None,
          "text-black/60 text-center")],
    36: [("36 карточки по центру", (5, "flex items-center justify-center"), None)],
    37: [("38 плашки по центру", (12, "flex items-center justify-center"), None)],
    38: [("39 Управление", "Управление", "Управляющий слой"),
         ("39 Сервисы", "Сервисы", "Внешние сервисы"),
         ("39 Агент-инструмент", "Агент-инструмент", "Агент как инструмент")],
    39: [("40 общаются", "общаются друг с другом", "говорят друг с другом"),
         ("40 модель сама выбирает", "Модель сама выбирает возможность",
          "Возможность, которую модель выбирает сама")],
    40: [("41 перенос «после подтверждения»", " <br>после подтверждения", None),
         ("41 карточки рисков по центру", (2, "text-center flex items-center justify-center"), None)],
    41: [("42 убрать 16:30", None, "16:30")],
    42: [("43 перенос «код выполняет»", " <br>код выполняет", None),
         ("43 убрать «а не удача»", None, "а не удача"),
         ("43 практика", "описание задачи или целого сервиса", None)],
}


def main():
    rel = sys.argv[1] if len(sys.argv) > 1 else "build/l5/out"
    out = os.path.join(ROOT, rel)
    bad = []
    for n in sorted(CHECKS):
        path = os.path.join(out, "slide-%02d.html" % n)
        if not os.path.exists(path):
            bad.append("slide-%02d: файла нет" % n)
            continue
        html = io.open(path, encoding="utf-8").read()
        for row in CHECKS[n]:
            label, need, forbid = row[0], row[1], row[2]
            if len(row) > 3 and row[3] not in html:
                continue  # ряда, к которому относилась правка, на слайде нет
            if need is not None:
                if isinstance(need, tuple):
                    k, sub = need
                    got = html.count(sub)
                    if got < k:
                        bad.append("slide-%02d · %s: «%s» %d из %d" % (n, label, sub, got, k))
                elif need not in html:
                    bad.append("slide-%02d · %s: нет «%s»" % (n, label, need))
            if forbid is not None and forbid in html:
                bad.append("slide-%02d · %s: осталось «%s»" % (n, label, forbid))
    total = sum(len(v) for v in CHECKS.values())
    if bad:
        print("НЕ НА МЕСТЕ (%d из %d проверок):" % (len(bad), total))
        for b in bad:
            print("  " + b)
        sys.exit(1)
    print("правки владельца 32–43 на месте: %d проверок, %s" % (total, rel))


if __name__ == "__main__":
    main()
