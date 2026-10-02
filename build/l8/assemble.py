# -*- coding: utf-8 -*-
"""Сборка automation/8/index.html из каркаса лекции 7 и слайдов build/l8/out.

    python3 build/l8/assemble.py

Каркас берётся у лекции 7 целиком: в ней самый свежий канон владельца, а
общие блоки (portal-fit, slide-polish, radial-fig, notes-panel-*) обязаны
совпадать побайтово со всеми лекциями — любая ручная правка здесь развалит
test_shared_blocks_identical. Меняется только то, что у лекции своё: превью,
слайды, число слайдов, ролики, тест, панель «Текст» и константы формы.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L8 = os.path.join(ROOT, "build", "l8")
SRC = os.path.join(ROOT, "automation", "7", "index.html")
DST = os.path.join(ROOT, "automation", "8", "index.html")

DESC = ("Вы научитесь считать экономику ИИ-трансформации: юнит и исходная точка процесса, будущая модель "
        "и трудоёмкость, полная стоимость сотрудника, прямая экономия, предотвращённые расходы и ценность "
        "высвобождённого времени, качество и выручка, TCO, ROI, окупаемость и сценарии — "
        "и соберёте историю для демо-дня: процесс, агент, человек, метрики и решение.")
TITLE = "Модуль 8 — Оценка эффективности и экономического эффекта"
OLD_TITLE = "Модуль 7 — Управление изменениями в компании"


def slides():
    out = os.environ.get("L8_OUT") or os.path.join(L8, "out")
    files = sorted(f for f in os.listdir(out) if re.match(r"slide-\d+\.html$", f))
    got = {}
    for f in files:
        html = io.open(os.path.join(out, f), encoding="utf-8").read().rstrip() + "\n"
        m = re.search(r'id="slide-(\d+)"', html)
        got[int(m.group(1))] = html
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
    html = html.replace("<title>Автоматизация - Модуль 7 - Управление изменениями в компании</title>",
                        "<title>Автоматизация - Модуль 8 - Оценка эффективности и экономического эффекта</title>", 1)
    old_desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    html = html.replace(old_desc, DESC)
    html = html.replace(OLD_TITLE, TITLE)
    html = html.replace('content="https://andre.technology/automation/7/"',
                        'content="https://andre.technology/automation/8/"', 1)
    html = html.replace('<link rel="stylesheet" href="/assets/lecture-7.css">',
                        '<link rel="stylesheet" href="/assets/lecture-8.css">', 1)

    # ── 2. Слайды ────────────────────────────────────────────────────────
    start = html.index('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-100')
    end = html.index("    <!-- Модальное окно теста -->")
    html = html[:start] + "\n".join(body) + "\n" + html[end:]

    # ── 3. Число слайдов и ролики ────────────────────────────────────────
    html = re.sub(r"const totalSlides = \d+;", "const totalSlides = %d;" % total, html, count=1)
    html = re.sub(r"const videoIds = \[.*?\];[^\n]*",
                  "const videoIds = [];   // роликов к лекции 8 ещё нет: кружок не показывается",
                  html, count=1, flags=re.S)

    # ── 4. Тест ──────────────────────────────────────────────────────────
    quiz_path = os.path.join(L8, "quiz.json")
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
        block = "\n".join(lines)
        html = re.sub(r"        const quizQuestions = \[.*?\n        \];", lambda m: block, html,
                      count=1, flags=re.S)
        html = re.sub(r'(<p id="quiz-progress"[^>]*>Вопрос 1 из )\d+(</p>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)
        html = re.sub(r'(<span class="text-xl md:text-3xl font-black text-white/40"> / )\d+(</span>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)

    # ── 5. Панель «Текст» ────────────────────────────────────────────────
    notes_dir = os.environ.get("L8_NOTES") or os.path.join(L8, "notes")
    data = {}
    if os.path.isdir(notes_dir):
        for f in sorted(os.listdir(notes_dir)):
            m = re.match(r"slide-(\d+)\.json$", f)
            if not m:
                continue
            data[str(int(m.group(1)))] = json.load(io.open(os.path.join(notes_dir, f), encoding="utf-8"))
    dump = json.dumps({k: data[k] for k in sorted(data, key=int)}, ensure_ascii=False, indent=1)
    html = re.sub(r'(<script id="slide-notes" type="application/json">\n).*?(\n</script>)',
                  lambda m: m.group(1) + dump + m.group(2), html, count=1, flags=re.S)

    # ── 6. Константы формы ───────────────────────────────────────────────
    floor_path = os.path.join(L8, "floor.json")
    if os.path.isfile(floor_path):
        f = json.load(io.open(floor_path, encoding="utf-8"))
        html = re.sub(r"window\.__FLOOR = \{pc:[\d.]+,mob:[\d.]+\};",
                      "window.__FLOOR = {pc:%s,mob:%s};" % (f["pc"], f["mob"]), html, count=1)

    dst = os.environ.get("L8_DST") or DST
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    io.open(dst, "w", encoding="utf-8").write(html)
    print("собрана лекция 8: %s" % dst)
    print("   слайдов: %d, строк: %d" % (total, html.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
