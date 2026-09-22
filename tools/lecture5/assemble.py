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
L5 = os.path.join(ROOT, "build", os.environ.get("L5_DIR", "l5"))
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
                        'content="%s"' % os.environ.get("L5_URL", "https://andre.technology/automation/5/"), 1)
    html = html.replace('<link rel="stylesheet" href="/assets/lecture-4.css">',
                        '<link rel="stylesheet" href="%s">' % os.environ.get("L5_CSS", "/assets/lecture-5.css"), 1)

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

    # ── 5б. Экран результата теста ───────────────────────────────────────
    #    Тексты уровней достались каркасу от лекции 3 и говорят про AS-IS,
    #    TO-BE и режимы участия человека H0-H3 — материал ЧУЖОЙ лекции.
    #    Человек проходит тест лекции 5 и получает совет пересмотреть слайды,
    #    которых в ней нет. Ставим свои.
    for was, now in (
        ("Вы мыслите процессами: видите AS-IS без прикрас, находите точки автоматизации "
         "и понимаете, где в контуре остаётся человек.",
         "Вы держите в голове весь путь: от описания продукта и поведения системы "
         "до тестов, генерации кода и надёжности готового сервиса."),
        ("Вы уверенно разбираетесь в процессном подходе: AS-IS, точки решений, TO-BE. "
         "Остались небольшие пробелы — пересмотрите спорные моменты.",
         "Вы уверенно отличаете продукт от автоматизации и понимаете, где нужен ИИ, "
         "а где обычный код. Остались небольшие пробелы — пересмотрите спорные моменты."),
        ("Основы вы уловили, но ключевые вещи — ограничение потока, реестр точек "
         "автоматизации и матрица «Ценность — Сложность» — требуют повторения.",
         "Основы вы уловили, но ключевые вещи — сценарии использования, критерии "
         "готовности и оценка качества ИИ — требуют повторения."),
        ("Пересмотрите слайды про AS-IS, детерминированные и вероятностные операции "
         "и режимы участия человека H0–H3 — и попробуйте снова.",
         "Пересмотрите слайды про описание поведения системы, разделение обычного кода "
         "и ИИ и надёжность рабочего сервиса — и попробуйте снова."),
    ):
        if was not in html:
            sys.exit("не найден текст уровня результата: %s..." % was[:44])
        html = html.replace(was, now, 1)

    # ── 6. Комментарии, привязанные к слайдам ЧУЖИХ лекций ───────────────
    #    В головном <style> каркаса остались объяснения про слайды лекций 3-4
    #    («Уровни зрелости бизнес-модели» #slide-20, оранжевый знак «нервной
    #    системы», списки data-driven). В лекции 5 таких слайдов нет.
    #
    #    Резать НАДО ЦЕЛИКОМ, от «/*» до «*/». Первый заход снял только начало
    #    комментария, и его хвост остался в <style> голым текстом: парсер CSS
    #    принимал этот текст за селектор и съедал вместе с ним следующий
    #    @media-блок. Сейчас блоки пустые, поэтому на вид ничего не менялось —
    #    но первое же правило, добавленное туда, молча не сработало бы.
    #    Проверка: число правил и @media в головном <style> должно совпадать
    #    с лекцией 4 (32 и 7).
    killed = 0
    for head in ("    /* Слайд «Уровни зрелости бизнес-модели» (#slide-20)",
                 "    /* Мобильная форма: оранжевый знак «нервной системы»",
                 "        /* Пункты в карточках «Мир делится»"):
        a = html.find(head)
        if a < 0:
            continue
        b = html.index("*/", a) + 2
        while b < len(html) and html[b] in " \t":
            b += 1
        if b < len(html) and html[b] == "\n":
            b += 1
        html = html[:a] + html[b:]
        killed += 1
    if killed != 3:
        sys.exit("ожидалось 3 чужих комментария в головном <style>, вырезано %d" % killed)

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
