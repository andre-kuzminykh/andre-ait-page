# -*- coding: utf-8 -*-
"""Сборка automation/3/practice/index.html из шаблона + данных кейсов и промтов."""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cases import CASES, CLASSDEFS
from prompts import PROMPTS

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P2 = open(os.path.join(ROOT, "automation/2/practice/index.html"), encoding="utf-8").read()
OUT = os.path.join(ROOT, "automation/3/practice/index.html")
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
NBH = "‑"


def I(name):
    return '<svg class="ic" aria-hidden="true"><use href="#i-%s" xlink:href="#i-%s"></use></svg>' % (name, name)


def esc(s):
    # «лимит 3» не рвём: одинокая цифра на новой строке читается как опечатка
    return re.sub(r"лимит (\d)", "лимит\u00a0\\1", html.escape(s, quote=False))


# ── CSS практики 2 — дословно ────────────────────────────────────────────
css2 = P2.split("<style>", 1)[1].split("</style>", 1)[0].strip("\n")
tpl = tpl.replace("/*@CSS2*/", css2)

# ── источники графов ──────────────────────────────────────────────────────
srcs, tabs, infos = [], [], []
keys = [c["key"] for c in CASES]
for c in CASES:
    code = c["graph"].replace("@CLASSDEFS", CLASSDEFS)
    c["code"] = code
    srcs.append('      <pre class="mmd-src" id="src-%s">%s</pre>' % (c["key"], esc(code)))
    tabs.append('        <button class="v-tab" role="tab" data-key="%s" aria-selected="%s">%s %s</button>'
                % (c["key"], "true" if c["key"] == "consult" else "false", I(c["icon"]), c["tab"]))


def lis(items):
    return "".join("<li>%s</li>" % esc(x) for x in items)


def json_html(s):
    e = esc(s)
    return re.sub(r'(&quot;|")([a-z_]+)(&quot;|")(\s*:)', r'<span class="k">"\2"</span>\4', e)


# Названия сценариев — словами владельца из текста задания: «обычном,
# неоднозначном, с нехваткой данных и с ошибкой внешнего сервиса».
TEST_KINDS = [("s-ok", "check-circle", "Обычный"), ("s-amb", "question", "Неоднозначный"),
              ("s-miss", "puzzle-piece", "С нехваткой данных"), ("s-err", "cloud-warning", "С ошибкой внешнего сервиса")]

for n, c in enumerate(CASES):
    prev_c = CASES[(n - 1) % len(CASES)]
    next_c = CASES[(n + 1) % len(CASES)]
    h = []
    h.append('      <div class="case-info" id="info-%s"%s>' % (c["key"], "" if n == 0 else " hidden"))
    # Значок и строка «почему так» (FR-SITE79): у ИИ-воркфлоу — схема потока,
    # у воркфлоу с зоной агента — робот. Строка отвечает на вопрос владельца
    # «а где здесь агенты?»: пяти процессам хватает воркфлоу, одному нужен агент.
    agent = c["kind"] == "agent"
    h.append('        <div class="agent-head rv-item">')
    h.append('          <span class="agent-ico%s">%s</span>' % (" is-agent" if agent else "", I("robot" if agent else "flow-arrow")))
    h.append('          <div>')
    h.append('            <span class="kicker">%s</span>' % esc(c["kicker"]))
    h.append('            <h3>%s</h3>' % esc(c["name"]))
    h.append('            <p class="from">%s</p>' % esc(c["frm"]))
    h.append('          </div>')
    h.append('        </div>')
    h.append('        <p class="verdict%s rv-item">%s<span><b>%s</b> %s</span></p>'
             % (" is-agent" if agent else "", I("robot" if agent else "flow-arrow"),
                "Воркфлоу с агентом." if agent else "ИИ-воркфлоу.", esc(c["why"])))
    h.append('        <div class="spec">')
    for ic, lbl, key in (("user-focus", "Роль", "role"), ("target", "Цель и критерий успеха", "goal"),
                         ("database", "Входные данные", "inp"), ("seal-check", "Ожидаемый результат", "out")):
        h.append('          <div class="rv-item"><span class="lbl">%s %s</span><p>%s</p></div>' % (I(ic), lbl, esc(c[key])))
    h.append('        </div>')
    # Заголовки карточки — фразами из текста задания владельца: «какие данные
    # ему нужны, что он должен помнить между шагами и где проходят границы
    # его автономности», «когда … завершает работу, когда передаёт задачу
    # человеку и в каком формате возвращает результат». «Агент» там заменён на
    # «воркфлоу»: даже в разборе инцидента агент — лишь один узел воркфлоу.
    h.append('        <h4 class="rv-item">%sКонтекст: какие данные ему нужны</h4>' % I("database"))
    h.append('        <ul class="ctx rv-item">')
    for what, src in c["ctx"]:
        h.append('          <li><span>%s</span><span class="src-tag">%s %s</span></li>' % (esc(what), I("database"), esc(src)))
    h.append('        </ul>')
    h.append('        <h4 class="rv-item">%sИнструменты — узкие функции с параметрами</h4>' % I("plugs"))
    h.append('        <ul class="tools rv-item">')
    for nm, sig, what in c["tools"]:
        h.append('          <li><b>%s</b><code>%s</code><span>%s</span></li>' % (esc(nm), esc(sig), esc(what)))
    h.append('        </ul>')
    # У агента свой контекст — входные данные, как у любого ИИ-шага, — и ещё
    # свой набор инструментов (слова владельца, FR-SITE79): из общего списка
    # видно, какие функции вызывает он сам, а какие — воркфлоу.
    ag = c.get("agent")
    if ag:
        h.append('        <h4 class="rv-item">%sАгент: контекст и набор инструментов</h4>' % I("robot"))
        h.append('        <div class="auto agent-box rv-item">')
        h.append('          <div><span class="lbl">%s Вход — контекст</span><ul>%s</ul></div>' % (I("database"), lis(ag["inp"])))
        h.append('          <div><span class="lbl">%s Инструменты</span><ul>%s</ul></div>'
                 % (I("plugs"), "".join("<li><code>%s</code></li>" % esc(t) for t in ag["tools"])))
        h.append('          <div><span class="lbl">%s Лимит и выход</span><ul>%s</ul></div>' % (I("flag-checkered"), lis(ag["out"])))
        h.append('        </div>')
    h.append('        <h4 class="rv-item">%sСостояние: что он должен помнить между шагами</h4>' % I("hard-drives"))
    h.append('        <ul class="state rv-item">')
    for f, what in c["state"]:
        h.append('          <li><code>%s</code>%s</li>' % (esc(f), esc(what)))
    h.append('        </ul>')
    h.append('        <p class="mem rv-item">%s<span>%s</span></p>' % (I("brain"), esc(c["mem"])))
    h.append('        <h4 class="rv-item">%sГде проходят границы его автономности</h4>' % I("shield-check"))
    h.append('        <div class="auto rv-item">')
    h.append('          <div class="a-self"><span class="lbl">%s Решает сам</span><ul>%s</ul></div>' % (I("check-circle"), lis(c["self_"])))
    h.append('          <div class="a-prop"><span class="lbl">%s Только предлагает</span><ul>%s</ul></div>' % (I("chats-circle"), lis(c["prop"])))
    h.append('          <div class="a-conf"><span class="lbl">%s После подтверждения</span><ul>%s</ul></div>' % (I("user"), lis(c["conf"])))
    h.append('        </div>')
    h.append('        <p class="forbid rv-item">%s<span><b>Запрещено:</b> %s</span></p>' % (I("prohibit"), esc(c["forbid"])))
    h.append('        <h4 class="rv-item">%sКогда воркфлоу завершает работу и когда передаёт задачу человеку</h4>' % I("flag-checkered"))
    h.append('        <div class="finish rv-item">')
    h.append('          <div class="a-done"><span class="lbl">%s Завершает работу, когда</span><ul>%s</ul></div>' % (I("flag-checkered"), lis(c["done"])))
    h.append('          <div class="a-hand"><span class="lbl">%s Передаёт человеку, когда</span><ul>%s</ul></div>' % (I("user-switch"), lis(c["hand"])))
    h.append('        </div>')
    h.append('        <p class="json-cap rv-item">%s В каком формате возвращает результат — структурированный вывод</p>' % I("brackets-curly"))
    h.append('        <pre class="code rv-item">%s</pre>' % json_html(c["json"]))
    h.append('        <h4 class="rv-item">%sПроверка на четырёх сценариях</h4>' % I("flask"))
    h.append('        <div class="tests">')
    for (cls, ic, title), (sit, exp, route) in zip(TEST_KINDS, c["tests"]):
        h.append('          <article class="%s rv-item"><span class="tt">%s %s</span><p><b>Вход:</b> %s</p><p><b>Ожидаем:</b> %s</p><code class="case-path">%s</code></article>'
                 % (cls, I(ic), title, esc(sit), esc(exp), esc(route)))
    h.append('        </div>')
    h.append('        <div class="case-nav rv-item">')
    h.append('          <button class="prev" type="button" data-go="%s">%s %s</button>' % (prev_c["key"], I("arrow-left"), esc(prev_c["tab"])))
    h.append('          <button class="next" type="button" data-go="%s">%s %s</button>' % (next_c["key"], esc(next_c["tab"]), I("arrow-right")))
    h.append('        </div>')
    h.append('      </div>')
    infos.append("\n".join(h))

tpl = tpl.replace("<!--@SOURCES-->", "\n".join(srcs))
tpl = tpl.replace("<!--@TABS-->", "\n".join(tabs))
tpl = tpl.replace("<!--@CASES-->", "\n".join(infos))

# ── промты ───────────────────────────────────────────────────────────────
pp = []
for pid, title, text, with_graph in PROMPTS:
    btns = '<button class="copy" type="button" data-copy="%s">%s копировать</button>' % (pid, I("copy"))
    if with_graph:
        btns += '\n          <button class="copy copy-code" type="button" data-copy="%s">%s копировать с графом из окна</button>' % (pid, I("sparkle"))
    pp.append("""      <details class="src">
        <summary>%s%s %s</summary>
        <div class="code-wrap">
          <pre class="code" id="%s">%s</pre>
          <div class="code-act">%s</div>
        </div>
      </details>""" % (I("caret-down").replace('class="ic"', 'class="ic caret"'), I("clipboard-text"), esc(title), pid, esc(text), btns))
tpl = tpl.replace("<!--@PROMPTS-->", "\n\n".join(pp))

# ── кружок: блок практики 2 побайтово, меняются только адреса ─────────────
b0 = P2.index("<!-- ГОВОРЯЩАЯ ГОЛОВА")
b1 = P2.rindex("</script>", 0, P2.index("</body>")) + len("</script>")
bubble = P2[b0:b1]
head_comment_end = bubble.index("-->") + 3
bubble = ("""<!-- ГОВОРЯЩАЯ ГОЛОВА (кружок): механика, размеры и разметка — те же, что в
     заданиях лекций 1 и 2, отличаются только ролик и обложка (первый кадр
     ролика практики, FR-SITE71). Кружок виден сразу с обложкой, как у лекций
     1 и 2: прежняя обёртка прятала его до loadeddata, пока ролика не было, —
     а на iPhone без звука кадры до play() не грузятся, и кружок так бы и не
     появился (приёмка роликов). -->""" + bubble[head_comment_end:])
bubble = bubble.replace('src="/assets/video_l2/40.mp4"', 'src="/assets/video_l3/practice.mp4"')
bubble = bubble.replace("/assets/video_sq/poster_practice_2.jpg", "/assets/video_l3/practice.jpg")
tpl = tpl.replace("<!--@BUBBLE-->", bubble)

# ── иконки ───────────────────────────────────────────────────────────────
tpl = re.sub(r"@I\(([a-z0-9-]+)\)", lambda m: I(m.group(1)), tpl)
used = sorted(set(re.findall(r'href="#i-([a-z0-9-]+)"', tpl)) | {"sun", "moon", "check-circle"})
p2sym = dict(re.findall(r'(?s)<symbol id="i-([a-z0-9-]+)"(.*?)</symbol>', P2))
sel = json.load(open(os.path.join(ROOT, "vendor/phosphor/src/fill/selection.json")))
selmap = {x["properties"]["name"]: x["icon"]["paths"] for x in sel["icons"]}
syms = []
for name in used:
    if name in p2sym:
        syms.append('    <symbol id="i-%s"%s</symbol>' % (name, p2sym[name]))
    else:
        paths = selmap.get(name + "-fill")
        if not paths:
            raise SystemExit("нет иконки " + name)
        syms.append('    <symbol id="i-%s" viewBox="0 0 1024 1024">%s</symbol>'
                    % (name, "".join('<path d="%s"/>' % p for p in paths)))
tpl = tpl.replace("<!--@ICONS-->", "\n".join(syms))

# ── появление при прокрутке: какие блоки проявляются (html.rv в CSS) ──────
# Крупные блоки страницы и пункты сеток; блоки карточки агента помечены выше.
for a, b in (('<div class="sec-head">', '<div class="sec-head rv-item">'),
             ('<article class="step">', '<article class="step rv-item">'),
             ('<div class="link" aria-hidden="true">', '<div class="link rv-item" aria-hidden="true">'),
             ('<div class="cta">', '<div class="cta rv-item">'),
             ('<div class="viewer" id="viewer">', '<div class="viewer rv-item" id="viewer">'),
             ('<details class="src">', '<details class="src rv-item">')):
    assert a in tpl, a
    tpl = tpl.replace(a, b)


def _rv_li(m):
    inner = re.sub(r'<li class="([^"]*)">', r'<li class="\1 rv-item">', m.group(4))
    inner = inner.replace('<li>', '<li class="rv-item">')
    return m.group(1) + inner + m.group(5)


tpl, n_rv = re.subn(r'(?s)(<(ul|ol) class="(criteria|flow|pmap)"[^>]*>)(.*?)(</\2>)', _rv_li, tpl)
assert n_rv == 3, n_rv

# ── неразрывный дефис в видимом тексте тела (не в коде и не в промтах) ───
NBSP = "\u00a0"


def typo(t):
    t = re.sub(r"(?<=[A-Za-zА-Яа-яЁё])-(?=[A-Za-zА-Яа-яЁё])", NBH, t)
    # Тире не открывает строку: пробел перед ним неразрывный. В новых блоках
    # FR-SITE79 строки начинались с «— ИИ-воркфлоу», «— системный промт».
    t = t.replace(" — ", NBSP + "— ")
    # «если — то» — одна формула: рвалась на «если —» и «то»
    t = t.replace("«если" + NBSP + "— то»", "«если" + NBSP + "—" + NBSP + "то»")
    # Однобуквенный предлог или союз не висит в конце строки («…нужен. У» / «каждой»)
    return re.sub(r"(?<![A-Za-zА-Яа-яЁё0-9\u2011-])([АВИКОСУЯавикосуя]) (?=\S)", "\\1" + NBSP, t)


head, body = tpl.split("<body>", 1)
parts = re.split(r"(?is)(<(pre|textarea|script|style|code)\b.*?</\2>)", body)
out = []
skip = False
for idx, part in enumerate(parts):
    # re.split с двумя группами: [текст, блок, имя_тега, текст, ...]
    if idx % 3 == 2:
        continue
    if idx % 3 == 1:
        out.append(part)
        continue
    # только текст между тегами, атрибуты не трогаем. Кусок текста в начале
    # и в конце части тоже текст: он примыкает к вырезанному <code>/<pre>.
    # Раньше он пропускался — «чек-лист» после <code>contract</code> в
    # карточке дизайна остался с обычным дефисом и мог разорваться.
    out.append(re.sub(r"(^|>)([^<]*)(?=<|$)", lambda m: m.group(1) + typo(m.group(2)), part))
body = "".join(out)
tpl = head + "<body>" + body

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(tpl)
print("written", OUT, len(tpl), "bytes;", len(syms), "icons")
