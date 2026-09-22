# -*- coding: utf-8 -*-
"""Сборка automation/5/index.html из каркаса лекции 4 и слайдов build/l5/out.

    python3 tools/lecture5/assemble.py

Каркас берётся у лекции 4 целиком: общие блоки (portal-fit, slide-polish,
radial-fig, notes-panel-*) обязаны совпадать побайтово со всеми лекциями, и
любая ручная правка здесь развалит test_shared_blocks_identical. Меняется
только то, что у лекции своё: превью, слайды, число слайдов, ролики, тест,
панель «Текст» и константы формы.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L5 = os.path.join(ROOT, "build", "l5")
SRC = os.path.join(ROOT, "automation", "4", "index.html")
DST = os.path.join(ROOT, "automation", "5", "index.html")

DESC = ("Вы пройдёте путь от идеи до работающего ИИ-сервиса: описание продукта, "
        "пользовательские истории и сценарии, требования и архитектура, разбиение "
        "на задачи, тесты и оценка качества ИИ, генерация кода, отладка и "
        "трассировка, работа с данными и надёжность рабочей системы.")
TITLE = "Модуль 5 — Продвинутые техники разработки ИИ-сервисов"


def slides():
    out = os.environ.get("L5_OUT") or os.path.join(L5, "out")
    got = {}
    for f in sorted(os.listdir(out)):
        if not re.match(r"slide-\d+\.html$", f):
            continue
        html = io.open(os.path.join(out, f), encoding="utf-8").read().rstrip() + "\n"
        got[int(re.search(r'id="slide-(\d+)"', html).group(1))] = html
    if not got:
        sys.exit("нет слайдов в %s" % out)
    missing = [i for i in range(max(got) + 1) if i not in got]
    if missing:
        sys.exit("не хватает слайдов: %s" % missing)
    return [got[i] for i in sorted(got)]


def main():
    html = io.open(SRC, encoding="utf-8").read()
    body = slides()
    total = len(body)

    # ── 1. Превью и заголовки ────────────────────────────────────────────
    html = html.replace("<title>Автоматизация - Модуль 4 - От одного агента к системе агентов</title>",
                        "<title>Автоматизация - Модуль 5 - Продвинутые техники разработки ИИ-сервисов</title>", 1)
    old_desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    html = html.replace(old_desc, DESC)
    html = html.replace("Модуль 4 — От одного агента к системе агентов", TITLE)
    html = html.replace('content="https://andre.technology/automation/4/"',
                        'content="https://andre.technology/automation/5/"', 1)
    html = html.replace('<link rel="stylesheet" href="/assets/lecture-4.css">',
                        '<link rel="stylesheet" href="/assets/lecture-5.css">', 1)

    # ── 2. Слайды ────────────────────────────────────────────────────────
    start = html.index('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-100')
    end = html.index("    <!-- Модальное окно теста -->")
    html = html[:start] + "\n".join(body) + "\n" + html[end:]

    # ── 3. Число слайдов и ролики ────────────────────────────────────────
    html = re.sub(r"const totalSlides = \d+;", "const totalSlides = %d;" % total, html, count=1)
    html = re.sub(r"const videoIds = \[\].*",
                  "const videoIds = [];   // роликов к лекции 5 ещё нет: кружок не показывается",
                  html, count=1)

    # ── 4. Тест ──────────────────────────────────────────────────────────
    quiz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.json")
    quiz = json.load(io.open(quiz_path, encoding="utf-8"))
    lines = ["        const quizQuestions = ["]
    for q in quiz:
        lines.append("            {")
        lines.append("                q: %s," % json.dumps(q["q"], ensure_ascii=False))
        lines.append("                options: [")
        for i, o in enumerate(q["options"]):
            lines.append("                    %s%s" % (json.dumps(o, ensure_ascii=False),
                                                       "," if i < len(q["options"]) - 1 else ""))
        lines.append("                ],")
        lines.append("                correct: %d," % q["correct"])
        lines.append("                explanation: %s" % json.dumps(q["explanation"], ensure_ascii=False))
        lines.append("            },")
    lines.append("        ];")
    html = re.sub(r"        const quizQuestions = \[.*?\n        \];", "\n".join(lines), html,
                  count=1, flags=re.S)
    html = re.sub(r'(<p id="quiz-progress"[^>]*>Вопрос 1 из )\d+(</p>)',
                  r"\g<1>%d\g<2>" % len(quiz), html, count=1)
    html = re.sub(r'(<span class="text-xl md:text-3xl font-black text-white/40"> / )\d+(</span>)',
                  r"\g<1>%d\g<2>" % len(quiz), html, count=1)

    # ── 5. Панель «Текст» ────────────────────────────────────────────────
    notes_dir = os.environ.get("L5_NOTES") or os.path.join(L5, "notes")
    data = {}
    for f in sorted(os.listdir(notes_dir)):
        m = re.match(r"slide-(\d+)\.json$", f)
        if m:
            data[str(int(m.group(1)))] = json.load(io.open(os.path.join(notes_dir, f), encoding="utf-8"))
    if not data:
        sys.exit("нет текстов панели в %s" % notes_dir)
    dump = json.dumps({k: data[k] for k in sorted(data, key=int)}, ensure_ascii=False, indent=1)
    html = re.sub(r'(<script id="slide-notes" type="application/json">\n).*?(\n</script>)',
                  lambda m: m.group(1) + dump + m.group(2), html, count=1, flags=re.S)

    # ── 6. Комментарий, привязанный к НОМЕРУ слайда лекции 4 ─────────────
    #    В головном <style> лекции 4 остался комментарий про её #slide-20.
    #    В лекции 5 под этим номером стоит другой слайд — убираем, чтобы
    #    следующая лекция не унаследовала неверное объяснение.
    a = html.find("    /* Слайд «Уровни зрелости бизнес-модели» (#slide-20)")
    if a < 0:
        sys.exit("не найден комментарий лекции 4 — проверь, что каркас не уехал")
    b = html.index("\n", html.index("«ширина слайда", a))
    html = html[:a] + html[b + 1:]

    # ── 7. Константы формы ───────────────────────────────────────────────
    floor_path = os.path.join(L5, "floor.json")
    if os.path.isfile(floor_path):
        f = json.load(io.open(floor_path, encoding="utf-8"))
        html = re.sub(r"window\.__FLOOR = \{pc:[\d.]+,mob:[\d.]+\};",
                      "window.__FLOOR = {pc:%s,mob:%s};" % (f["pc"], f["mob"]), html, count=1)

    dst = os.environ.get("L5_DST") or DST
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    io.open(dst, "w", encoding="utf-8").write(html)
    print("собрана лекция 5: %s" % dst)
    print("   слайдов: %d, текстов панели: %d, вопросов теста: %d, строк: %d"
          % (total, len(data), len(quiz), html.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
