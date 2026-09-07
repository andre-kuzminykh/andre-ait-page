# -*- coding: utf-8 -*-
"""Правка терминов в данных семинара: слова, которые не должны звучать в
учебной речи, заменяются на принятые русские.

Отдельным шагом, а не руками по двенадцати файлам: агенты-составители тянут
из первоисточника его собственный словарь («домен», «оператор»), а на слайдах
и в озвучке курс говорит «направление» и «человек».

    python3 tools/seminar_lint.py          # показать, что будет заменено
    python3 tools/seminar_lint.py --apply  # заменить в tools/seminar/*.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "tools", "seminar")

# Порядок важен: длинные формы раньше коротких, иначе «домены» станет
# «направлениы» — замена по основе испортит окончание.
RULES = [
    (r"\bдоменах\b", "направлениях"), (r"\bдоменам\b", "направлениям"),
    (r"\bдоменов\b", "направлений"), (r"\bдомены\b", "направления"),
    (r"\bдомена\b", "направления"), (r"\bдомену\b", "направлению"),
    (r"\bдоменом\b", "направлением"), (r"\bдомене\b", "направлении"),
    (r"\bдомен\b", "направление"),
    (r"\bДоменах\b", "Направлениях"), (r"\bДоменов\b", "Направлений"),
    (r"\bДомены\b", "Направления"), (r"\bДомена\b", "Направления"),
    (r"\bДомен\b", "Направление"),
    (r"\bкапабилити\b", "умений"),
    # Согласование после замены: «домен» мужского рода, «направление» —
    # среднего, поэтому местоимения и указательные слова рядом надо поправить.
    (r"\bэтот направление\b", "это направление"),
    (r"\bсам направление\b", "само направление"),
    (r"направление стоит именно здесь: он ", "направление стоит именно здесь: оно "),
    # «Оператор подтверждает…» — только в начале фразы: в отделе продаж и
    # поддержки «оператор» это живая человеческая должность, её не трогаем.
    (r"^Оператор\b", "Человек"),
]


def walk(node, fn):
    if isinstance(node, str):
        return fn(node)
    if isinstance(node, list):
        return [walk(v, fn) for v in node]
    if isinstance(node, dict):
        return {k: (v if k in ("en", "icon", "key") else walk(v, fn)) for k, v in node.items()}
    return node


def normalize(apply):
    """Привести реплики к одному виду: {n, ru, text}.

    Составители иногда отдают items простым списком строк — тогда имя
    сотрудника теряется, а панель «Текст» показывает реплику без подписи.
    Имя берём из соседнего data-файла по порядку.
    """
    fixed = 0
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.startswith("speech-") or not name.endswith(".json"):
            continue
        key = name[len("speech-"):-len(".json")]
        data_path = os.path.join(DATA_DIR, "data-%s.json" % key)
        if not os.path.exists(data_path):
            continue
        path = os.path.join(DATA_DIR, name)
        with open(path, encoding="utf-8") as f:
            sp = json.load(f)
        with open(data_path, encoding="utf-8") as f:
            tiles = json.load(f)["tiles"]
        items = sp.get("items") or []
        if items and all(isinstance(x, str) for x in items) and len(items) == len(tiles):
            sp["items"] = [{"n": t["n"], "ru": t["ru"], "text": x}
                           for t, x in zip(tiles, items)]
            fixed += 1
            print("%s: реплики приведены к виду {n, ru, text}" % name)
            if apply:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(sp, f, ensure_ascii=False, indent=1)
    return fixed


def main():
    apply = "--apply" in sys.argv
    normalize(apply)
    hits = 0
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.endswith(".json") or name == "icons.json":
            continue
        path = os.path.join(DATA_DIR, name)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        found = []

        def fix(s):
            nonlocal found
            out = s
            for pat, rep in RULES:
                if re.search(pat, out):
                    found.append((re.search(pat, out).group(0), rep))
                    out = re.sub(pat, rep, out)
            return out

        fixed = walk(data, fix)
        if found:
            hits += len(found)
            print("%s: %d замен — %s" % (name, len(found),
                  ", ".join(sorted({"%s→%s" % (a, b) for a, b in found}))))
            if apply:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(fixed, f, ensure_ascii=False, indent=1)
    print(("заменено" if apply else "к замене") + ": %d" % hits)


if __name__ == "__main__":
    main()
