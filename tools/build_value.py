# -*- coding: utf-8 -*-
"""Страница графики поверх видео по слайдам 13–16 («Модель создания ценности»,
«Процессная архитектура», «ИИ как нервная система», «Где ИИ создаёт ценность»).

Берём готовую страницу прошлого ролика — в ней вся машинерия: покадровый
рендер, шапка, обложка, субтитры, скрипт сборки, — и меняем ТОЛЬКО сцены:
их CSS и разметку. Каждая замена обязана сработать, поэтому подмена() с
assert: молчаливый промах уже один раз оставлял старую раскладку.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "automation", "1", "overlay-ai-first", "index.html")
DST = os.path.join(ROOT, "automation", "1", "overlay-value", "index.html")
# Иконки Phosphor лежат рядом со сборщиком: те же глифы, что на слайдах.
PH = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ph.json"),
                    encoding="utf-8"))


def ico(name):
    return '<svg viewBox="0 0 256 256" fill="currentColor">%s</svg>' % PH[name]


def circle(name, colour, size):
    return ('<div class="circle %s ico" style="width:%dpx;height:%dpx">%s</div>'
            % (colour, size, size, ico(name)))


html = open(SRC, encoding="utf-8").read()


def подмена(старое, новое, имя):
    global html
    assert старое in html, "не нашёл кусок для замены: " + имя
    html = html.replace(старое, новое, 1)


# ── заголовок страницы ───────────────────────────────────────────────
подмена("<title>Эволюция ИИ и AI-First — анимированная графика поверх видео</title>",
        "<title>Где ИИ создаёт ценность — анимированная графика поверх видео</title>",
        "заголовок")

# ── CSS сцен ─────────────────────────────────────────────────────────
css_start = html.index("/* ── СЦЕНА 1 · таймлайн четырёх эпох")
css_end = html.index("/* ── Обложка: первые секунды готового ролика.")
CSS = """/* ── СЦЕНА 1 · арка RUN → CHANGE → DISRUPT ──────────────────────────
   Форма новая: три круга по дуге, дуга прочерчивается слева направо —
   «путь от стабильности к прорыву». Диаметры одинаковые (правило
   владельца), подписи снаружи дуги: у боковых снизу, у верхнего сверху,
   чтобы ничего не сталкивалось. */
#s1 .arc{position:relative;width:940px;height:360px}
#s1 .node{position:absolute;display:flex;flex-direction:column;align-items:center;text-align:center}
#s1 .n1{left:0;bottom:6px}
#s1 .n2{left:50%;transform:translateX(-50%);top:0}
#s1 .n3{right:0;bottom:6px}
#s1 .n1.el,#s1 .n3.el{transform:translateY(18px) scale(.96)}
#s1 .n1.el.on,#s1 .n3.el.on{transform:none}
#s1 .n2.el{transform:translate(-50%,18px) scale(.96)}
#s1 .n2.el.on{transform:translateX(-50%)}
#s1 .label{font-size:40px;letter-spacing:.02em}
#s1 .n1 .label,#s1 .n3 .label{margin-top:16px}
#s1 .n2 .label{margin-bottom:16px;order:-1}
#s1 .role{
    font-size:26px;font-weight:800;color:#FFD9BE;margin-top:8px;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6);opacity:0;
    transition:opacity .5s var(--ease),transform .5s var(--ease);transform:translateY(8px);
}
#s1 .role.on{opacity:1;transform:none}
#s1 .n2 .role{color:#DCC9FF}
/* Дуга: тонкая линия, прочерченная от левого круга к правому. */
#s1 svg.curve{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}
#s1 svg.curve path{
    fill:none;stroke:rgba(255,255,255,.30);stroke-width:3;stroke-linecap:round;
    stroke-dasharray:1200;stroke-dashoffset:1200;
}
#s1.on svg.curve path{animation:drawCurve 1.6s var(--ease) .15s forwards}
@keyframes drawCurve{to{stroke-dashoffset:0}}
/* «Бизнес-прорыв» — ниже подписи CHANGE: на 58% они пересекались. */
#s1 .core{
    position:absolute;left:50%;top:72%;transform:translate(-50%,-50%);
    font-size:50px;font-weight:900;color:#fff;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}
#s1 .core.el{transform:translate(-50%,calc(-50% + 18px)) scale(.96)}
#s1 .core.el.on{transform:translate(-50%,-50%)}

/* ── СЦЕНА 2 · три типа процессов, цель ИИ вторым слоем ─────────────
   Ряд из трёх, но подписи приходят в два захода: сначала сам процесс,
   потом под ним цель ИИ — ровно тогда, когда её называют. */
#s2 .label{font-size:28px;margin-top:18px}
#s2 .sub{
    font-size:24px;font-weight:800;color:rgba(255,255,255,.72);margin-top:6px;
    text-shadow:0 3px 16px rgba(10,4,24,.6);
}
#s2 .goal{
    font-size:27px;font-weight:900;color:#FFB380;margin-top:14px;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6);opacity:0;transform:translateY(10px);
    transition:opacity .5s var(--ease),transform .5s var(--ease);
}
#s2 .goal.on{opacity:1;transform:none}

/* ── СЦЕНЫ 3 и 5 · сеть: ядро AI и четыре узла ──────────────────────
   Узлы равноудалены от ядра (радиус один на все), линии прочерчиваются
   от центра. В пятой сцене по тем же линиям бегут импульсы. */
.net{position:relative;width:880px;height:360px}
.net .hub{
    position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
    display:flex;flex-direction:column;align-items:center;z-index:2;
}
.net .hub.el{transform:translate(-50%,calc(-50% + 18px)) scale(.96)}
.net .hub.el.on{transform:translate(-50%,-50%)}
.net .hub .label{font-size:30px;margin-top:10px;white-space:nowrap}
.net .nd{
    position:absolute;display:flex;flex-direction:column;align-items:center;z-index:2;
    transform:translate(-50%,-50%);
}
.net .nd .label{font-size:26px;margin-top:8px;white-space:nowrap}
.net .nd.el{opacity:0}
.net .nd.el.on{opacity:1}
.net svg.wires{position:absolute;inset:0;width:100%;height:100%;overflow:visible;pointer-events:none}
.net svg.wires line{
    stroke:rgba(255,255,255,.28);stroke-width:3;stroke-linecap:round;
    stroke-dasharray:400;stroke-dashoffset:400;
}
.scene.on .net svg.wires line{animation:drawWire 1s var(--ease) forwards}
.scene.on .net svg.wires line:nth-child(2){animation-delay:.12s}
.scene.on .net svg.wires line:nth-child(3){animation-delay:.24s}
.scene.on .net svg.wires line:nth-child(4){animation-delay:.36s}
@keyframes drawWire{to{stroke-dashoffset:0}}
/* Импульс — светлая точка, бегущая от ядра к узлу по той же линии. */
.net .pulse{
    position:absolute;left:50%;top:50%;width:16px;height:16px;border-radius:50%;
    margin:-8px 0 0 -8px;background:#fff;box-shadow:0 0 18px 6px rgba(196,181,253,.9);
    opacity:0;
}
.scene.on .net .pulse{animation:run 1.8s linear infinite}
.scene.on .net .pulse.p2{animation-delay:.45s}
.scene.on .net .pulse.p3{animation-delay:.9s}
.scene.on .net .pulse.p4{animation-delay:1.35s}
@keyframes run{
    0%{opacity:0;transform:translate(0,0) scale(.6)}
    12%{opacity:1}
    88%{opacity:1}
    100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.6)}
}
#s5 .verdict{
    font-size:34px;font-weight:900;color:#fff;white-space:nowrap;margin-top:24px;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}

/* ── СЦЕНА 4 · «как было раньше»: цепочка с разрывами ───────────────
   Единственный кадр ролика, где элементы намеренно приглушены: это
   прошлое, а не рабочая схема. Соседи при этом не гаснут по ходу сцены —
   приглушены сразу все и одинаково. */
#s4 .row{gap:30px;justify-content:center;align-items:flex-start}
#s4 .item{flex:0 1 auto}
#s4 .slot{height:112px}
#s4 .label{font-size:30px;margin-top:16px;white-space:nowrap}
#s4 .circle{filter:saturate(.35);opacity:.86}
#s4 .gap{
    flex:0 0 auto;width:52px;height:52px;margin-top:30px;
    color:rgba(255,255,255,.42);font-size:44px;font-weight:900;text-align:center;
    text-shadow:0 3px 16px rgba(10,4,24,.6);
}
#s4 .warn{
    font-size:34px;font-weight:900;color:#FFB380;white-space:nowrap;margin-top:44px;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}

/* Обёртка сияния: сам .glow не может быть .el — у .el.on стоит
   transform:none, он сносит центрирующий translate сияния. */
.halo{position:absolute;inset:0;pointer-events:none}

/* ── СЦЕНА 6 · финал блока: цифровая нервная система ────────────────── */
#s6 .row{justify-content:center}
#s6 .slot{height:158px}
#s6 .label{font-size:44px;margin-top:20px;position:relative;z-index:1;line-height:1.14}
#s6 .glow{width:880px;height:350px}

/* ── СЦЕНА 7 · узкие места и точки решений ──────────────────────────── */
#s7 .row{gap:70px;justify-content:center;align-items:flex-start}
#s7 .item{flex:0 1 auto}
#s7 .slot{height:138px}
#s7 .label{font-size:36px;margin-top:18px;white-space:nowrap}
#s7 .sub{
    font-size:25px;font-weight:800;color:rgba(255,255,255,.75);margin-top:10px;
    line-height:1.25;text-shadow:0 3px 16px rgba(10,4,24,.6);
    opacity:0;transform:translateY(10px);
    transition:opacity .5s var(--ease),transform .5s var(--ease);
}
#s7 .sub.on{opacity:1;transform:none}
#s7 .row{position:relative}
#s7 .glow{width:880px;height:340px;top:42%}

/* ── СЦЕНА 8 · карусель функций ─────────────────────────────────────
   Шесть функций в один ряд не влезают: их называют за 7 секунд подряд,
   поэтому они сменяют друг друга по одной — каждая ровно на своём слове
   (у элементов есть data-out). */
#s8 .row{justify-content:center}
#s8 .item{flex:0 1 auto;position:absolute;left:50%;transform:translateX(-50%)}
#s8 .item.el{transform:translate(-50%,18px) scale(.96)}
#s8 .item.el.on{transform:translateX(-50%)}
#s8 .stack{position:relative;width:100%;height:230px}
#s8 .slot{height:150px}
#s8 .label{font-size:44px;margin-top:18px;white-space:nowrap}
#s8 .all{
    font-size:44px;font-weight:900;color:#fff;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}

/* ── СЦЕНА 9 · финал: три метрики ───────────────────────────────────── */
#s9 .row{gap:40px;justify-content:center}
#s9 .item{flex:0 1 auto}
#s9 .slot{height:124px}
#s9 .label{font-size:34px;margin-top:16px;white-space:nowrap}
#s9 .row{position:relative}
#s9 .glow{width:900px;height:340px;top:44%}

"""
html = html[:css_start] + CSS + html[css_end:]

# ── разметка сцен ────────────────────────────────────────────────────
m_start = html.index('<div id="layer">')
m_start = html.index("\n", m_start) + 1
m_end = html.index('    </div>\n\n    <div id="cover">')


def node(cls, in_, icon, colour, size, label, cur=None, extra=""):
    a = ' data-in="%s"' % in_
    if cur:
        a += ' data-cur="%s"' % cur
    return ('<div class="%s el"%s>%s<p class="label">%s</p>%s</div>'
            % (cls, a, '<div class="slot">%s</div>' % circle(icon, colour, size),
               label, extra))


def item(in_, icon, colour, size, label, cur=None, out=None, extra=""):
    a = ' data-in="%s"' % in_
    if out:
        a += ' data-out="%s"' % out
    if cur:
        a += ' data-cur="%s"' % cur
    return ('                <div class="item el"%s>%s<p class="label">%s</p>%s</div>\n'
            % (a, '<div class="slot">%s</div>' % circle(icon, colour, size), label, extra))


L = []
A = L.append

# ── СЦЕНА 1 · арка RUN → CHANGE → DISRUPT ───────────────────────────
A('        <!-- ══ СЦЕНА 1 · слайд 13 · RUN → CHANGE → DISRUPT ══ -->\n')
A('        <section class="scene" id="s1" data-in="7.0" data-out="43.9">\n')
A('            <div class="arc">\n')
A('                <div class="halo el" data-in="36.30"><div class="glow" style="top:62%"></div></div>\n')
A('                <svg class="curve" viewBox="0 0 940 360" preserveAspectRatio="none">'
  '<path d="M 60 250 Q 470 40 880 250"/></svg>\n')
A('                <div class="node n1 el" data-in="7.16" data-cur="7.16 16.90">'
  + circle("gear-six", "solar", 96) +
  '<p class="label">RUN</p><p class="role el" data-in="12.76" data-out="36.30">Автоматизация рутины</p></div>\n')
A('                <div class="node n2 el" data-in="17.38" data-cur="17.38 26.16">'
  + circle("arrows-merge", "ember", 96) +
  '<p class="label">CHANGE</p><p class="role el" data-in="24.74" data-out="36.30">Решения</p></div>\n')
A('                <div class="node n3 el" data-in="26.76" data-cur="26.76 35.76">'
  + circle("rocket", "solar", 96) +
  '<p class="label">DISRUPT</p><p class="role el" data-in="31.66" data-out="36.30">Новые продукты</p></div>\n')
A('                <p class="core el" data-in="36.30" data-cur="36.30 43.90">Бизнес-прорыв</p>\n')
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 2 · три типа процессов ────────────────────────────────────
A('        <!-- ══ СЦЕНА 2 · слайд 14 · три типа процессов и цели ИИ ══ -->\n')
A('        <section class="scene" id="s2" data-in="50.5" data-out="81.5">\n')
A('            <div class="row">\n')
A(item("50.90", "star", "solar", 96, "Основные",
       cur="50.90 55.12 76.02 77.82",
       extra='<p class="sub">Создают ценность</p>'
             '<p class="goal el" data-in="76.02">Рост выручки</p>'))
A(item("55.72", "lifebuoy", "ember", 96, "Поддерживающие",
       cur="55.72 64.96 72.86 75.46",
       extra='<p class="sub">HR, финансы, IT</p>'
             '<p class="goal el" data-in="72.86">Снижение затрат</p>'))
A(item("65.48", "scales", "solar", 96, "Управленческие",
       cur="65.48 69.10 78.18 81.46",
       extra='<p class="sub">Планирование и контроль</p>'
             '<p class="goal el" data-in="78.18">Качество решений</p>'))
A('            </div>\n')
A('        </section>\n\n')


def net(scene_id, hub_in, hub_cur, nodes, wires_extra="", pulses=False):
    """Сеть: ядро в центре, четыре узла на одном радиусе, линии от центра."""
    out = []
    out.append('            <div class="net">\n')
    out.append('                <svg class="wires" viewBox="0 0 880 360">')
    for x, y in [(132, 74), (748, 74), (132, 286), (748, 286)]:
        out.append('<line x1="440" y1="180" x2="%d" y2="%d"/>' % (x, y))
    out.append('</svg>\n')
    if pulses:
        for i, (dx, dy) in enumerate([(-308, -106), (308, -106), (-308, 106), (308, 106)], 1):
            out.append('                <span class="pulse p%d" style="--dx:%dpx;--dy:%dpx"></span>\n'
                       % (i, dx, dy))
    out.append('                <div class="hub el" data-in="%s"%s>%s'
               '<p class="label">ИИ</p></div>\n'
               % (hub_in, (' data-cur="%s"' % hub_cur) if hub_cur else "",
                  circle("brain", "solar", 132)))
    for (in_, icon, colour, label, left, top) in nodes:
        out.append('                <div class="nd el" data-in="%s" style="left:%d%%;top:%d%%">%s'
                   '<p class="label">%s</p></div>\n'
                   % (in_, left, top, circle(icon, colour, 76), label))
    out.append('            </div>\n')
    return "".join(out)


# ── СЦЕНА 3 · сеть ──────────────────────────────────────────────────
A('        <!-- ══ СЦЕНА 3 · слайд 15 · ИИ соединяет всё в единый контур ══ -->\n')
A('        <section class="scene" id="s3" data-in="82.4" data-out="92.9">\n')
A(net("s3", "82.40", "82.40 87.78", [
    ("88.98", "briefcase", "ember", "Функции", 15, 22),
    ("89.66", "arrows-merge", "solar", "Процессы", 85, 22),
    ("90.32", "database", "ember", "Данные", 15, 78),
    ("90.90", "users", "solar", "Люди", 85, 78),
]))
A('        </section>\n\n')

# ── СЦЕНА 4 · как было раньше ───────────────────────────────────────
A('        <!-- ══ СЦЕНА 4 · слайд 15 · раньше: письма, согласования, встречи ══ -->\n')
A('        <section class="scene" id="s4" data-in="96.6" data-out="102.6">\n')
A('            <div class="row">\n')
A(item("96.78", "envelope-simple", "solar", 92, "Письма"))
A('                <div class="gap el" data-in="97.20">···</div>\n')
A(item("97.50", "calendar-check", "ember", 92, "Согласования"))
A('                <div class="gap el" data-in="97.90">···</div>\n')
A(item("98.18", "users-three", "solar", 92, "Встречи"))
A('            </div>\n')
A('            <p class="warn el" data-in="100.14" data-cur="100.14 102.60">'
  'Задержки и ошибки</p>\n')
A('        </section>\n\n')

# ── СЦЕНА 5 · импульсы ──────────────────────────────────────────────
A('        <!-- ══ СЦЕНА 5 · слайд 15 · ИИ убирает разрывы: импульсы по связям ══ -->\n')
A('        <section class="scene" id="s5" data-in="103.2" data-out="120.9">\n')
A(net("s5", "103.18", "103.18 105.34", [
    ("105.34", "briefcase", "ember", "Функции", 15, 22),
    ("105.34", "arrows-merge", "solar", "Процессы", 85, 22),
    ("105.34", "database", "ember", "Данные", 15, 78),
    ("105.34", "users", "solar", "Люди", 85, 78),
], pulses=True))
A('            <p class="verdict el" data-in="112.74" data-cur="112.74 120.90">'
  'Единая интеллектуальная система</p>\n')
A('        </section>\n\n')

# ── СЦЕНА 6 · цифровая нервная система ──────────────────────────────
A('        <!-- ══ СЦЕНА 6 · слайд 15 · AI-First как организм ══ -->\n')
A('        <section class="scene" id="s6" data-in="121.6" data-out="128.8">\n')
A('            <div class="row">\n')
A('                <div class="item el" data-in="121.62" data-cur="121.62 128.80">'
  '<div class="glow"></div>'
  '<div class="slot">%s</div>'
  '<p class="label">Цифровая<br>нервная система</p></div>\n' % circle("network", "solar", 140))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 7 · узкие места и точки решений ───────────────────────────
A('        <!-- ══ СЦЕНА 7 · слайд 16 · узкие места и точки решений ══ -->\n')
A('        <section class="scene" id="s7" data-in="131.3" data-out="150.9">\n')
A('            <div class="row">\n')
A('                <div class="halo el" data-in="144.18"><div class="glow glow-ember"></div></div>\n')
A(item("131.50", "funnel", "ember", 120, "Узкие места",
       cur="131.50 133.00 134.30 138.66 146.90 148.60",
       extra='<p class="sub el" data-in="135.88">Время · Деньги<br>Ошибки</p>'))
A(item("132.66", "scales", "solar", 120, "Точки решений",
       cur="132.66 134.20 139.26 143.46 148.60 150.84",
       extra='<p class="sub el" data-in="141.72">Анализ данных<br>Лучший вариант</p>'))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 8 · карусель функций ──────────────────────────────────────
A('        <!-- ══ СЦЕНА 8 · слайд 16 · функции компании по одной ══ -->\n')
A('        <section class="scene" id="s8" data-in="151.5" data-out="158.9">\n')
A('            <div class="stack">\n')
карусель = [
    ("151.56", "154.26", "currency-dollar", "ember", "Финансы"),
    ("154.26", "155.38", "users", "solar", "HR"),
    ("155.38", "156.74", "megaphone", "ember", "Маркетинг"),
    ("156.74", "157.20", "chart-line-up", "solar", "Продажи"),
    ("157.20", "157.76", "headset", "ember", "Поддержка"),
    ("157.76", "158.90", "chart-pie-slice", "solar", "Аналитика"),
]
for in_, out_, icon, colour, label in карусель:
    A(item(in_, icon, colour, 130, label, out=out_))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 9 · финал: метрики ────────────────────────────────────────
A('        <!-- ══ СЦЕНА 9 · слайд 16 · метрики, ради которых всё ══ -->\n')
A('        <section class="scene" id="s9" data-in="159.4" data-out="167.0">\n')
A('            <div class="row">\n')
A('                <div class="halo el" data-in="159.46"><div class="glow glow-ember"></div></div>\n')
A(item("159.46", "lightning", "ember", 104, "Скорость", cur="164.78 165.90"))
A(item("159.46", "check-circle", "solar", 104, "Качество", cur="165.90 166.72"))
A(item("159.46", "piggy-bank", "ember", 104, "Прибыль", cur="166.72 167.00"))
A('            </div>\n')
A('        </section>\n\n')

html = html[:m_start] + "".join(L) + html[m_end:]

# ── элементы умеют исчезать: data-out ────────────────────────────────
подмена("""        el.__in = parseFloat(el.getAttribute('data-in'));""",
        """        el.__in = parseFloat(el.getAttribute('data-in'));
        /* data-out — элемент уходит: карусель функций в сцене 8 сменяет
           их по одному, шесть подписей в ряд не помещаются. */
        el.__out = parseFloat(el.getAttribute('data-out'));""",
        "разбор data-out")
подмена("""            var vis = vt >= el.__in;""",
        """            var vis = vt >= el.__in && (isNaN(el.__out) || vt < el.__out);""",
        "видимость по data-out")

# ── длина ролика ─────────────────────────────────────────────────────
подмена("var DURATION = 167.0;                     // дорожка 165.0 c + хвост под шапку",
        "var DURATION = 169.0;                     // дорожка 167.1 c + хвост под шапку",
        "длина")

os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8").write(html)
print("страница собрана:", DST, len(html), "байт")
