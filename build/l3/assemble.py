# -*- coding: utf-8 -*-
"""Сборка automation/3/index.html из каркаса лекции 4 и слайдов build/l3/out.

    python3 build/l3/assemble.py

Каркас берётся у лекции 4 целиком: общие блоки (portal-fit, slide-polish,
radial-fig, notes-panel-*) обязаны совпадать побайтово со всеми лекциями, а у
лекции 4 в голове нет правил под номера слайдов — у старой колоды лекции 3 они
были (#slide-14, #slide-20, #slide-23) и после пересборки ударили бы по чужим
слайдам. Своё у лекции 3: превью, слайды, ролики, кнопка «Задание» (практика
живёт рядом, как у лекции 2), переход с экрана результата теста на практику,
тест, панель «Текст» и константы формы.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L3 = os.path.join(ROOT, "build", "l3")
SRC = os.path.join(ROOT, "automation", "4", "index.html")
DST = os.path.join(ROOT, "automation", "3", "index.html")

TITLE_TAG = "Автоматизация - Модуль 3 - Инженерия ИИ-агентов"
TITLE = "Модуль 3 — Инженерия ИИ-агентов"
DESC = ("Вы научитесь проектировать процесс до автоматизации, отличать воркфлоу от агента, "
        "писать спецификацию агента, собирать промт, контекст и обвязку, тестировать "
        "поведение и выводить агента в работу.")

TASK_BTN = ('            <a class="lec-ctrl lec-task" href="https://andre.technology/automation/3/practice/" '
            'aria-label="Практическое задание" title="Практическое задание"><i class="ph-fill ph-clipboard-text"></i>'
            '<span>Задание</span></a>\n')


def slides():
    out = os.environ.get("L3_OUT") or os.path.join(L3, "out")
    got = {}
    for f in sorted(os.listdir(out)):
        if not re.match(r"slide-\d+\.html$", f):
            continue
        html = io.open(os.path.join(out, f), encoding="utf-8").read().rstrip() + "\n"
        got[int(re.search(r'id="slide-(\d+)"', html).group(1))] = html
    missing = [i for i in range(max(got) + 1) if i not in got]
    if missing:
        sys.exit("не хватает слайдов: %s" % missing)
    return [got[i] for i in sorted(got)]


def main():
    html = io.open(SRC, encoding="utf-8").read()
    body = slides()
    total = len(body)

    # ── превью и заголовки ───────────────────────────────────────────────
    html = html.replace("<title>Автоматизация - Модуль 4 - От одного агента к системе агентов</title>",
                        "<title>%s</title>" % TITLE_TAG, 1)
    old_desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    html = html.replace(old_desc, DESC)
    html = html.replace("Модуль 4 — От одного агента к системе агентов", TITLE)
    html = html.replace('content="https://andre.technology/automation/4/"',
                        'content="https://andre.technology/automation/3/"', 1)
    html = html.replace('<link rel="stylesheet" href="/assets/lecture-4.css">',
                        '<link rel="stylesheet" href="/assets/lecture-3.css">', 1)

    # ── шапка: «Задание» ведёт на практику, как у лекции 2 ───────────────
    anchor = '            <button id="lec-theme" class="lec-ctrl"'
    assert html.count(anchor) == 1
    html = html.replace(anchor, TASK_BTN + anchor, 1)

    # ── слайды ───────────────────────────────────────────────────────────
    start = html.index('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-100')
    end = html.index("    <!-- Модальное окно теста -->")
    html = html[:start] + "\n".join(body) + "\n" + html[end:]

    # ── число слайдов и ролики: videoIds[k] — ролик слайда k, файл k+1.mp4 ─
    html = re.sub(r"const totalSlides = \d+;", "const totalSlides = %d;" % total, html, count=1)
    vids = ",\n".join("            '/assets/video_l3/%d.mp4'" % (k + 1) for k in range(total))
    html = re.sub(r"const videoIds = \[.*?\];",
                  lambda m: "const videoIds = [\n%s\n        ];" % vids, html, count=1, flags=re.S)

    # ── экран результата теста ведёт на практику ─────────────────────────
    html = html.replace('<a class="quiz-next" href="/automation/bootcamp/">',
                        '<a class="quiz-next" href="https://andre.technology/automation/3/practice/">', 1)

    # ── тест ─────────────────────────────────────────────────────────────
    quiz_path = os.path.join(L3, "quiz.json")
    if os.path.isfile(quiz_path):
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
        html = re.sub(r"        const quizQuestions = \[.*?\n        \];", lambda m: "\n".join(lines), html,
                      count=1, flags=re.S)
        html = re.sub(r'(<p id="quiz-progress"[^>]*>Вопрос 1 из )\d+(</p>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)
        html = re.sub(r'(<span class="text-xl md:text-3xl font-black text-white/40"> / )\d+(</span>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)

    # ── панель «Текст» ───────────────────────────────────────────────────
    notes_dir = os.environ.get("L3_NOTES") or os.path.join(L3, "notes")
    data = {}
    for f in sorted(os.listdir(notes_dir)):
        m = re.match(r"slide-(\d+)\.json$", f)
        if m and int(m.group(1)) < total:
            data[str(int(m.group(1)))] = json.load(io.open(os.path.join(notes_dir, f), encoding="utf-8"))
    dump = json.dumps({k: data[k] for k in sorted(data, key=int)}, ensure_ascii=False, indent=1)
    html = re.sub(r'(<script id="slide-notes" type="application/json">\n).*?(\n</script>)',
                  lambda m: m.group(1) + dump + m.group(2), html, count=1, flags=re.S)

    # ── константы формы ──────────────────────────────────────────────────
    floor_path = os.path.join(L3, "floor.json")
    if os.path.isfile(floor_path):
        f = json.load(io.open(floor_path, encoding="utf-8"))
        html = re.sub(r"window\.__FLOOR = \{pc:[\d.]+,mob:[\d.]+\};",
                      "window.__FLOOR = {pc:%s,mob:%s};" % (f["pc"], f["mob"]), html, count=1)

    dst = os.environ.get("L3_DST") or DST
    io.open(dst, "w", encoding="utf-8").write(html)
    print("собрана лекция 3: %s" % dst)
    print("   слайдов: %d, строк: %d" % (total, html.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
