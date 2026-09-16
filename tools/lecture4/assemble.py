# -*- coding: utf-8 -*-
"""Сборка automation/4/index.html из каркаса лекции 3 и слайдов build/l4/out.

    python3 build/l4/assemble.py

Каркас берётся у лекции 3 целиком: общие блоки (portal-fit, slide-polish,
radial-fig, notes-panel-*) обязаны совпадать побайтово со всеми лекциями, и
любая ручная правка здесь развалит test_shared_blocks_identical. Меняется
только то, что у лекции своё: превью, слайды, число слайдов, ролики, тест,
панель «Текст», телефонный блок и константы формы.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L4 = os.path.join(ROOT, "build", "l4")
SRC = os.path.join(ROOT, "automation", "3", "index.html")
DST = os.path.join(ROOT, "automation", "4", "index.html")

DESC = ("Вы разберёте, как агент рассуждает и когда останавливается, как строится "
        "поиск по знаниям компании, зачем нужны MCP и A2A, как из агентов собирается "
        "система ролей и как она описывается графом и живёт распределённо.")
TITLE = "Модуль 4 — От одного агента к системе агентов"


def slides():
    out = os.environ.get("L4_OUT") or os.path.join(L4, "out")
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
    html = html.replace("<title>Автоматизация - Модуль 3 - Инженерия ИИ-агентов</title>",
                        "<title>Автоматизация - Модуль 4 - От одного агента к системе агентов</title>", 1)
    old_desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    html = html.replace(old_desc, DESC)
    html = html.replace("Модуль 3 — Инженерия ИИ-агентов", TITLE)
    html = html.replace('content="https://andre.technology/automation/3/"',
                        'content="https://andre.technology/automation/4/"', 1)
    html = html.replace('<link rel="stylesheet" href="/assets/lecture-3.css">',
                        '<link rel="stylesheet" href="/assets/lecture-4.css">', 1)

    # ── 2. Слайды ────────────────────────────────────────────────────────
    start = html.index('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-100')
    end = html.index("    <!-- Модальное окно теста -->")
    html = html[:start] + "\n".join(body) + "\n" + html[end:]

    # ── 3. Число слайдов и ролики ────────────────────────────────────────
    html = re.sub(r"const totalSlides = \d+;", "const totalSlides = %d;" % total, html, count=1)
    html = re.sub(r"const videoIds = \[.*?\];",
                  "const videoIds = [];   // роликов к лекции 4 ещё нет: кружок не показывается",
                  html, count=1, flags=re.S)

    # ── 4. Тест ──────────────────────────────────────────────────────────
    quiz_path = os.path.join(L4, "quiz.json")
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
        html = re.sub(r"        const quizQuestions = \[.*?\n        \];", block, html,
                      count=1, flags=re.S)
        # счётчик вопросов в модалке
        html = re.sub(r'(<p id="quiz-progress"[^>]*>Вопрос 1 из )\d+(</p>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)
        html = re.sub(r'(<span class="text-xl md:text-3xl font-black text-white/40"> / )\d+(</span>)',
                      r"\g<1>%d\g<2>" % len(quiz), html, count=1)

    # ── 5. Панель «Текст» ────────────────────────────────────────────────
    notes_dir = os.environ.get("L4_NOTES") or os.path.join(L4, "notes")
    if os.path.isdir(notes_dir):
        data = {}
        for f in sorted(os.listdir(notes_dir)):
            m = re.match(r"slide-(\d+)\.json$", f)
            if not m:
                continue
            data[str(int(m.group(1)))] = json.load(io.open(os.path.join(notes_dir, f), encoding="utf-8"))
        if data:
            dump = json.dumps({k: data[k] for k in sorted(data, key=int)},
                              ensure_ascii=False, indent=1)
            html = re.sub(r'(<script id="slide-notes" type="application/json">\n).*?(\n</script>)',
                          lambda m: m.group(1) + dump + m.group(2), html, count=1, flags=re.S)

    # ── 6. Телефонный блок: правила лекции 3 к лекции 4 отношения не имеют ─
    a = html.find("/* \u2500\u2500 \u0414\u0432\u0430 \u043f\u043b\u043e\u0442\u043d\u044b\u0445 \u0441\u043b\u0430\u0439\u0434\u0430")
    if a < 0:
        sys.exit("не найден телефонный блок лекции 3 — проверь, что каркас не уехал")
    b = html.index("\n", html.index("#slide-23 .content-z > p{", a))
    html = html[:a].rstrip(" ") + html[b + 1:]

    # ── 6б. Правила, привязанные к НОМЕРАМ слайдов лекции 3 ──────────────
    #    В головном <style> у лекции 3 висят точечные правила #slide-1,
    #    #slide-14, #slide-19, #slide-20. В лекции 4 под этими номерами стоят
    #    совсем другие слайды, и правило «оранжевую плашку наверх» или «убрать
    #    боковые поля» сработало бы на случайном слайде. Вырезаем.
    killed = 0
    for rule in ('#slide-1 .content-z ul { width: fit-content; margin-left: auto; margin-right: auto; }',
                 '#slide-14 .content-z [class~="bg-solar"] { order: -1; }',
                 '#slide-19 .content-z ul { width: fit-content; margin-left: auto; margin-right: auto; }',
                 '#slide-20 { padding-left: 2rem; padding-right: 2rem; }',
                 '#slide-20 .content-z { padding-left: 0 !important; padding-right: 0 !important; }'):
        i = html.find(rule)
        if i < 0:
            continue
        j = html.index("\n", i)
        html = html[:html.rfind("\n", 0, i) + 1] + html[j + 1:]
        killed += 1
    if killed < 5:
        sys.exit("ожидалось 5 правил по номерам слайдов лекции 3, вырезано %d" % killed)

    # ── 7. Константы формы ───────────────────────────────────────────────
    floor_path = os.path.join(L4, "floor.json")
    if os.path.isfile(floor_path):
        f = json.load(io.open(floor_path, encoding="utf-8"))
        html = re.sub(r"window\.__FLOOR = \{pc:[\d.]+,mob:[\d.]+\};",
                      "window.__FLOOR = {pc:%s,mob:%s};" % (f["pc"], f["mob"]), html, count=1)

    dst = os.environ.get("L4_DST") or DST
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    io.open(dst, "w", encoding="utf-8").write(html)
    print("собрана лекция 4: %s" % dst)
    print("   слайдов: %d, строк: %d" % (total, html.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
