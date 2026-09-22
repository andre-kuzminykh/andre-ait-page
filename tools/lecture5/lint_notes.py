# -*- coding: utf-8 -*-
"""Проверка текста панели «Текст к слайду» лекции 5.

    python3 tools/lecture5/lint_notes.py                      # все файлы notes/
    python3 tools/lecture5/lint_notes.py notes/slide-07.json
"""
import io, json, os, re, sys

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "build", "l5")
ICONS = set(io.open(os.path.join(HERE, "icons.txt"), encoding="utf-8").read().split())
BANNED = ("workflow", "reasoning", "retrieval", "fallback", "polling", "guardrail",
          "governance", "throughput", "human review", "backlog", "adoption",
          "baseline", "продакшен", "чекпоинт", "снапшот")
TYPES = ("p", "h", "ul", "ol", "note", "cards")


def check(path):
    name = os.path.basename(path)
    bad = []
    add = lambda m: bad.append("%s: %s" % (name, m))
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        return ["%s: не разбирается как JSON — %s" % (name, e)]
    if not isinstance(data, dict):
        return ["%s: на верхнем уровне должен быть объект {title, blocks}" % name]
    title = data.get("title", "")
    if not title or len(title) > 64:
        add("заголовок пустой или длиннее 64 знаков")
    blocks = data.get("blocks") or []
    if len(blocks) < 3:
        add("меньше трёх блоков — панель должна разбирать тему, а не дублировать слайд")
    kinds = set()
    for i, b in enumerate(blocks):
        t = b.get("t")
        kinds.add(t)
        if t not in TYPES:
            add("блок %d: неизвестный тип %r" % (i, t)); continue
        v = b.get("v")
        if not v:
            add("блок %d: пустой" % i); continue
        if t == "cards":
            if not isinstance(v, list) or not v:
                add("блок %d: карточки должны быть непустым списком" % i); continue
            for c in v:
                if not re.match(r"^ph-[a-z0-9-]+$", c.get("i", "")):
                    add("блок %d: плохое имя иконки %r" % (i, c.get("i")))
                elif c["i"] not in ICONS:
                    add("блок %d: несуществующая иконка %s" % (i, c["i"]))
                if not c.get("h") or not c.get("p"):
                    add("блок %d: карточка без названия или пояснения" % i)
        elif t in ("ul", "ol"):
            if not isinstance(v, list) or not v:
                add("блок %d: список должен быть непустым" % i)
        else:
            if not isinstance(v, str):
                add("блок %d: значение должно быть строкой" % i)
            elif t == "p" and len(v) > 1400:
                add("блок %d: абзац длиннее 1400 знаков" % i)
    if "p" not in kinds:
        add("нет ни одного обычного абзаца")
    if not ({"cards", "ul", "ol"} & kinds):
        add("нет ни одного перечисления (cards/ul/ol) — канон требует карточек для пунктов")

    blob = json.dumps(data, ensure_ascii=False)
    for w in BANNED:
        if re.search(re.escape(w), blob, re.I):
            add("англицизм: %s" % w)
    plain = re.sub(r"[A-Za-z-]*AI[A-Za-z-]*", lambda m: m.group(0), blob)
    if re.search(r"(?<![A-Za-z])AI(?![A-Za-z])", blob):
        add("«AI» вместо «ИИ»")
    if len(blob) < 900:
        add("текста слишком мало (%d знаков): панель — второй слой лекции" % len(blob))
    return bad


def main():
    files = sys.argv[1:] or sorted(
        os.path.join(HERE, "notes", f) for f in os.listdir(os.path.join(HERE, "notes"))
        if f.endswith(".json"))
    if not files:
        print("нет файлов"); return 1
    bad = []
    for f in files:
        bad += check(f)
    if bad:
        print("НАРУШЕНИЯ (%d):" % len(bad))
        for b in bad:
            print("  " + b)
        return 1
    print("чисто: %d файлов" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
