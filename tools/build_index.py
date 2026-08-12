# -*- coding: utf-8 -*-
"""Страница графики поверх видео по слайдам 22–30 («Зачем нужен ИИ-индекс
зрелости», семь измерений индекса и «Что делать с ИИ-индексом»).

Берём страницу прошлого ролика — в ней вся машинерия: покадровый рендер,
шапка, обложка, субтитры, скрипт сборки, — и меняем ТОЛЬКО сцены: их CSS
и разметку. Каждая замена обязана сработать, поэтому подмена() с assert:
молчаливый промах уже один раз оставлял старую раскладку.

Ролик-список: семь блоков идут один за другим, и сцена у каждого одна и
та же — крупный круг с названием и ряд коротких «чипов», которые выходят
ровно на своих словах. Однообразие тут в плюс: зритель понимает форму с
первого блока и дальше читает только содержание.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "automation", "1", "overlay-transform", "index.html")
DST = os.path.join(ROOT, "automation", "1", "overlay-index", "index.html")
PH = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ph.json"),
                    encoding="utf-8"))
# Ширину заголовка меряем по метрикам шрифта: от неё зависит, сколько
# места остаётся значкам по бокам. У «Исследований и разработок» его
# почти нет, и значки улетали за край кадра.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ttf_width import Шрифт

ШРИФТ = Шрифт(os.path.join(ROOT, "automation", "1", "overlay-index",
                           "fonts", "Montserrat-Black.ttf"))
КЕГЛЬ_ЗАГОЛОВКА = 54


def запас(подпись):
    """Сколько пикселей от края заголовка до края кадра."""
    голая = подпись.replace("&amp;", "&")
    return (1080 - ШРИФТ.ширина(голая, КЕГЛЬ_ЗАГОЛОВКА)) / 2.0 - 56


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


подмена("<title>Три трансформации бизнеса — анимированная графика поверх видео</title>",
        "<title>ИИ-индекс зрелости — анимированная графика поверх видео</title>",
        "заголовок")

# ── CSS сцен ─────────────────────────────────────────────────────────
css_start = html.index("/* ── Общее для этого ролика")
css_end = html.index("/* ── Обложка: первые секунды готового ролика.")
CSS = """/* ── Общее для этого ролика ─────────────────────────────────────────
   Ролик-список: семь измерений индекса. У каждого блока одна и та же
   раскладка — крупный круг сверху, ряд коротких чипов снизу. Линия с
   стрелкой нужна только в финальной дорожной карте. */
.stage{position:relative;width:100%;display:flex;flex-direction:column;align-items:center}
.stage .row{position:relative;z-index:1}
.link{position:absolute;left:0;top:0;width:100%;pointer-events:none;z-index:0;overflow:visible}
.link line,.link polyline,.link path{
    fill:none;stroke:rgba(255,255,255,.30);stroke-width:3;stroke-linecap:round;
    stroke-linejoin:round;stroke-dasharray:1400;stroke-dashoffset:1400;
}
.link polygon{fill:rgba(255,255,255,.30);opacity:0;transition:opacity .5s var(--ease) .5s}
/* .el сдвигает элемент при появлении — линии это не нужно, она чертится. */
.link.el,.link.el.on{transform:none;opacity:1}
.link.el line,.link.el polyline,.link.el path{stroke-dashoffset:1400}
.link.el.on line,.link.el.on polyline,.link.el.on path{animation:drawLink 1.4s var(--ease) forwards}
.link.el.on polygon{opacity:1}
@keyframes drawLink{to{stroke-dashoffset:0}}
.item .slot{position:relative;z-index:1}

/* Фраза-вывод: крупная строка по центру сцены, цвет чередуется. */
.cores{position:relative;width:100%;height:44px}
.cores .core{position:absolute;left:0;right:0;top:0}
.core{
    font-size:36px;font-weight:900;color:#fff;white-space:nowrap;text-align:center;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}
.core.solar{color:#C9B2FF}
.core.ember{color:#FFB380}
.core .glow{width:780px;height:210px;top:50%}
/* Подпись второго слоя — то, что говорят про элемент отдельно. */
.sub{
    font-size:25px;font-weight:800;color:rgba(255,255,255,.78);margin-top:10px;
    line-height:1.25;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6);
    opacity:0;transform:translateY(10px);
    transition:opacity .5s var(--ease),transform .5s var(--ease);
}
.sub.on{opacity:1;transform:none}
/* Обёртка сияния: сам .glow не может быть .el — у .el.on стоит
   transform:none, он сносит центрирующий translate сияния. */
.halo{position:absolute;inset:0;pointer-events:none}

/* Два элемента в кадре стоят ШИРОКО: каждый над своей картиной (центры
   235 и 820 по кадру), середина свободна — там голова. */
.scene .row.duo{justify-content:space-between;gap:0}
.scene .row.duo>.item{flex:0 0 400px}
.duo .label{font-size:34px;margin-top:16px;white-space:nowrap}

/* ── Блок индекса: одно слово, сияние и разлёт значков ──────────────
   Владелец: «давай только заголовки — Данные / Модели и т.д., без
   иконок, а оранжевым / фиолетовым сзади свечением и эмодзи слева
   справа, как ты уже делал». Круг с иконкой убран совсем: якорем стало
   само слово, цвет держит сияние за ним, а значки вылетают из-за краёв
   слова влево и вправо — по букве они не проходят.
   Кегль 54: «Исследования и разработки» на 64 занимает 1029px и в кадр
   шириной 988 не помещается (замерено по метрикам шрифта). */
.block{display:flex;flex-direction:column;align-items:center;width:100%}
.block .head{position:relative;display:flex;align-items:center;justify-content:center}
.block .title{
    font-size:54px;font-weight:900;color:#fff;white-space:nowrap;
    position:relative;z-index:1;letter-spacing:-.01em;
    text-shadow:0 3px 18px rgba(10,4,24,.65),0 1px 4px rgba(10,4,24,.8);
}
/* Фиолетовое сияние на фиолетовой стене почти не читается, поэтому у
   заголовков центр облака взят светлее обычного — оно работает светом,
   а не цветом. Оранжевому этого не нужно, стена не оранжевая. */
.block .head .glow{
    width:880px;height:300px;
    background:radial-gradient(closest-side,rgba(226,210,255,.95),rgba(152,102,250,.42) 52%,rgba(136,84,243,0) 74%);
}
.block .head .glow.glow-ember{
    background:radial-gradient(closest-side,rgba(249,140,60,.82),rgba(249,115,22,.30) 55%,rgba(249,115,22,0) 74%);
}
/* Чипы — просто слова: круги под ними и были теми «иконками», от
   которых владелец отказался. Подсветка тут не кольцо, а цвет и лёгкий
   подрост; соседи при этом НЕ гаснут — они остаются белыми. */
.block .chips{display:flex;gap:34px;justify-content:center;margin-top:34px}
.block .chip{
    font-size:28px;font-weight:800;color:rgba(255,255,255,.92);white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
    transition:opacity .5s var(--ease),transform .5s var(--ease),color .45s var(--ease);
}
.block .chip.on.cur{transform:scale(1.09)}
.block .chip.solar.on.cur{color:#C9B2FF}
.block .chip.ember.on.cur{color:#FFB380}
.block .cores{margin-top:26px}

/* Значки вылетают из-за краёв заголовка — влево из левого края, вправо
   из правого. Это Phosphor того же набора, а не эмодзи: эмодзи рисуются
   системным шрифтом, которого на чужой машине может не быть. */
.fly{position:absolute;top:50%;width:0;height:0;pointer-events:none;z-index:0}
.fly.l{left:-4px}
.fly.r{right:-4px}
.fly i{
    position:absolute;left:-20px;top:-20px;display:block;width:40px;height:40px;
    opacity:0;color:#fff;
}
.fly svg{width:100%;height:100%;fill:currentColor}
.fly.solar i{filter:drop-shadow(0 0 10px rgba(136,84,243,.95)) drop-shadow(0 2px 6px rgba(10,4,24,.6))}
.fly.ember i{filter:drop-shadow(0 0 10px rgba(249,115,22,.95)) drop-shadow(0 2px 6px rgba(10,4,24,.6))}
.scene.on .fly.on i{animation:flyOut 3s ease-out infinite}
@keyframes flyOut{
    0%{opacity:0;transform:translate(0,0) scale(.4) rotate(0deg)}
    22%{opacity:.95}
    58%{opacity:.8}
    100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1.05) rotate(var(--rot))}
}

/* ── Семь блоков сеткой 4 + 3 ───────────────────────────────────────
   В один ряд семь подписей не влезают: на колонку осталось бы 140px, а
   «Инфраструктура» кеглем 24 занимает 212. Поэтому 4 сверху и 3 снизу. */
.grid7{display:flex;flex-direction:column;gap:24px;width:100%}
.grid7 .row{gap:20px}
.grid7 .row.bottom{justify-content:center}
.grid7 .row.bottom .item{flex:0 0 232px}
.grid7 .slot{height:90px}
.grid7 .label{font-size:24px;margin-top:9px;white-space:nowrap}
#s12 .cores{margin-top:18px}

/* ── Дорожная карта: три шага в ряд, линия со стрелкой ─────────────── */
#s13 .steps{position:relative;width:100%}
#s13 .link{height:112px}
#s13 .row{gap:40px;position:relative;z-index:1}
#s13 .label{font-size:32px;margin-top:14px;white-space:nowrap}
#s13 .cores{margin-top:22px}

/* ── Пилоты: единственный намеренно тусклый кадр ролика ─────────────── */
#s2 .row{gap:120px;justify-content:center}
#s2 .item{flex:0 1 auto}
#s2 .label{font-size:30px;margin-top:14px;white-space:nowrap}
#s2 .item .circle{filter:saturate(.3);opacity:.78}
#s2 .item .label{color:rgba(255,255,255,.72)}
#s2 .cores{margin-top:30px}

/* ── Первая сцена: сам индекс ───────────────────────────────────────── */
#s1 .slot{height:150px}
#s1 .label{font-size:44px;margin-top:16px;position:relative;z-index:1;white-space:nowrap}
#s1 .glow{width:840px;height:330px}
#s1 .cores{margin-top:26px}
#s3 .cores{margin-top:26px}

"""
html = html[:css_start] + CSS + html[css_end:]

# ── разметка сцен ────────────────────────────────────────────────────
m_start = html.index('<div id="layer">')
m_start = html.index("\n", m_start) + 1
m_end = html.index('    </div>\n\n    <div id="cover">')

L = []
A = L.append


def атрибуты(in_, out=None, cur=None):
    a = ' data-in="%s"' % in_
    if out:
        a += ' data-out="%s"' % out
    if cur:
        a += ' data-cur="%s"' % cur
    return a


def item(in_, icon, colour, size, label, cur=None, out=None, extra="", halo="", cls="item"):
    return ('                <div class="%s el"%s>%s%s<p class="label">%s</p>%s</div>\n'
            % (cls, атрибуты(in_, out, cur), halo,
               '<div class="slot">%s</div>' % circle(icon, colour, size), label, extra))


def core(in_, текст, цвет, out=None):
    return ('                <p class="core %s el"%s>%s</p>\n'
            % (цвет, атрибуты(in_, out), текст))


def cores(*строки):
    return '            <div class="cores">\n%s            </div>\n' % "".join(строки)


def halo(цвет, in_):
    return ('<div class="halo el" data-in="%s"><div class="glow %s"></div></div>'
            % (in_, "glow-ember" if цвет == "ember" else ""))


# Семь измерений индекса: значок, подпись и цвет — один и тот же набор в
# обзорной сетке, в блоках и в финальном профиле.
БЛОКИ = [
    ("compass-tool", "Стратегия", "solar"),
    ("users-three", "Люди", "ember"),
    ("cpu", "Инфраструктура", "solar"),
    ("database", "Данные", "ember"),
    ("brain", "Модели", "solar"),
    ("gear-six", "Внедрение", "ember"),
    ("lightbulb", "R&amp;D", "solar"),
]


def сетка7(времена, cur=None):
    """4 + 3: в один ряд семь подписей не помещаются."""
    out = ['            <div class="grid7">\n                <div class="row">\n']
    for i, ((icon, label, colour), t) in enumerate(zip(БЛОКИ, времена)):
        if i == 4:
            out.append('                </div>\n                <div class="row bottom">\n')
        out.append(item(t, icon, colour, 78, label, cur=cur))
    out.append('                </div>\n            </div>\n')
    return "".join(out)


# Куда летят значки из-за краёв слова: влево и вправо, врассыпную по
# высоте, с разными задержками — строем они читались бы как одна деталь.
РАЗЛЁТ = [(104, -50, -14, 0.00), (166, 12, 12, 0.70), (214, -24, -8, 1.40)]
# Когда заголовок широкий и вбок лететь некуда, значки уходят вверх —
# над словом место есть всегда, зона начинается заметно выше строки.
ВВЕРХ = [(38, -74, -14, 0.00), (72, -108, 12, 0.70), (26, -132, -8, 1.40)]


def fly(in_, цвет, значок, сторона, место):
    знак = -1 if сторона == "l" else 1
    доля = max(0.0, min(1.0, место / 214.0))
    траектории = РАЗЛЁТ if доля >= 0.55 else ВВЕРХ
    куски = []
    for dx, dy, rot, задержка in траектории:
        if траектории is РАЗЛЁТ:
            dx = int(dx * доля)
        куски.append('<i style="--dx:%dpx;--dy:%dpx;--rot:%ddeg;animation-delay:%.2fs">%s</i>'
                     % (знак * dx, dy, знак * rot, задержка, ico(значок)))
    return ('<span class="fly %s %s el" data-in="%s">%s</span>'
            % (цвет, сторона, in_, "".join(куски)))


def блок(sid, in_, out_, icon, colour, подпись, шапка, шапка_cur, чипы, фразы=""):
    """Одна и та же раскладка на все семь измерений: слово, сияние за
    ним, значки по бокам и ряд коротких слов снизу."""
    цвета = ["ember" if colour == "solar" else "solar", colour]
    т = ['        <!-- ══ %s ══ -->\n' % подпись,
         '        <section class="scene" id="%s" data-in="%s" data-out="%s">\n' % (sid, in_, out_),
         '            <div class="block">\n',
         '                <div class="head el"%s>'
         '<div class="halo"><div class="glow %s"></div></div>%s'
         '<p class="title">%s</p>%s</div>\n'
         % (атрибуты(шапка, cur=шапка_cur), "glow-ember" if colour == "ember" else "",
            fly(шапка, colour, icon, "l", запас(подпись)), подпись,
            fly(шапка, colour, icon, "r", запас(подпись))),
         '                <div class="chips">\n']
    for i, (t, _, текст, окно) in enumerate(чипы):
        т.append('                    <p class="chip %s el"%s>%s</p>\n'
                 % (цвета[i % 2], атрибуты(t, cur=окно), текст))
    т.append('                </div>\n')
    if фразы:
        т.append(фразы)
    т.append('            </div>\n        </section>\n\n')
    return "".join(т)


# ── СЦЕНА 1 · зачем нужен индекс ────────────────────────────────────
A('        <!-- ══ СЦЕНА 1 · слайд 22 · зачем нужен ИИ-индекс ══ -->\n')
A('        <section class="scene" id="s1" data-in="0.9" data-out="7.5">\n')
A('            <div class="row">\n')
A('                <div class="item el" data-in="1.51" data-cur="1.51 3.36">'
  '<div class="halo"><div class="glow"></div></div>'
  '<div class="slot">%s</div><p class="label">ИИ-индекс зрелости</p></div>\n'
  % circle("target", "solar", 140))
A('            </div>\n')
A(cores(core("4.25", "Без измерения не управлять", "ember")))
A('        </section>\n\n')

# ── СЦЕНА 2 · пилоты без системного эффекта ─────────────────────────
A('        <!-- ══ СЦЕНА 2 · слайд 22 · разрозненные пилоты ══ -->\n')
A('        <section class="scene" id="s2" data-in="7.6" data-out="13.5">\n')
A('            <div class="row">\n')
for t in ("8.37", "8.80", "9.20"):
    A(item(t, "rocket", "ember", 92, "Пилот"))
A('            </div>\n')
A(cores(core("9.91", "Без системного эффекта", "ember")))
A('        </section>\n\n')

# ── СЦЕНА 3 · что показывает индекс ─────────────────────────────────
A('        <!-- ══ СЦЕНА 3 · слайд 22 · где ограничения и как их снять ══ -->\n')
A('        <section class="scene" id="s3" data-in="13.6" data-out="16.4">\n')
A('            <div class="row duo">\n')
A(item("13.93", "warning", "ember", 108, "Ограничения", cur="13.93 14.89"))
A(item("14.89", "wrench", "solar", 108, "Как их снять", cur="14.89 16.36"))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 4 · семь блоков ───────────────────────────────────────────
A('        <!-- ══ СЦЕНА 4 · слайд 22 · семь измерений индекса ══ -->\n')
A('        <section class="scene" id="s4" data-in="16.5" data-out="25.5">\n')
A(сетка7(["18.33", "19.63", "21.30", "21.80", "22.77", "23.19", "24.59"]))
A('        </section>\n\n')

# ── СЦЕНЫ 5–11 · семь измерений по очереди ──────────────────────────
A(блок("s5", "25.6", "47.2", "compass-tool", "solar", "Стратегия и управление",
       "25.81", "25.81 31.17",
       [("32.55", "target", "Цели", "32.55 34.05"),
        ("34.05", "chart-line-up", "Метрики", "34.05 35.61"),
        ("38.21", "user-gear", "Руководство", "38.21 40.59")],
       cores(core("43.55", "Иначе ИИ не масштабируется", "ember"))))

A(блок("s6", "47.4", "63.4", "users-three", "ember", "Люди и культура",
       "48.23", "48.23 49.19",
       [("50.21", "check-circle", "Готовность", "50.21 52.35"),
        ("57.45", "graduation-cap", "Компетенции", "57.45 58.55"),
        ("60.33", "users", "Культура", "60.33 63.23")]))

A(блок("s7", "63.5", "83.9", "cpu", "solar", "Инфраструктура",
       "64.51", "64.51 65.85",
       [("67.71", "buildings", "Фундамент", "67.71 70.19"),
        ("74.31", "database", "Доступ", "74.31 75.65"),
        ("76.60", "lifebuoy", "Безопасность", "76.60 77.33"),
        ("77.33", "plugs-connected", "Стабильность", "77.33 78.39")],
       cores(core("79.67", "Быстро запускать и масштабировать", "ember"))))

A(блок("s8", "84.0", "104.4", "database", "ember", "Данные",
       "85.07", "85.07 85.69",
       [("89.43", "star", "Актив", "89.43 90.45"),
        ("93.15", "check-circle", "Качество", "93.15 94.03"),
        ("94.03", "plugs-connected", "Доступность", "94.03 94.85"),
        ("94.85", "steering-wheel", "Управляемость", "94.85 95.53")],
       cores(core("102.33", "Без данных ИИ не работает", "solar"))))

A(блок("s9", "104.6", "123.5", "brain", "solar", "Модели",
       "105.39", "105.39 105.89",
       [("109.01", "sparkle", "Интеллект", "109.01 110.25"),
        ("113.93", "rocket", "Продакшен", "113.93 114.69"),
        ("117.63", "trend-up", "Масштаб", "117.63 118.63"),
        ("122.55", "eye", "Мониторинг", "122.55 123.29")]))

A(блок("s10", "123.7", "141.1", "gear-six", "ember", "Внедрение ИИ",
       "124.51", "124.51 125.51",
       [("126.53", "arrows-merge", "В процессах", "126.53 128.83"),
        ("131.71", "calendar-check", "Каждый день", "131.71 133.27"),
        ("136.35", "chart-pie-slice", "Доля процессов", "136.35 137.89"),
        ("139.95", "users", "Клиенты", "139.95 140.85")]))

A(блок("s11", "141.3", "158.3", "lightbulb", "solar", "Исследования и разработки",
       "142.01", "142.01 143.37",
       [("144.47", "wrench", "Свои решения", "144.47 146.07"),
        ("147.19", "shopping-bag", "Не только готовые", "147.19 148.19"),
        ("152.49", "trend-up", "Развивать", "152.49 154.09")],
       cores(core("155.41", "Формирует рынок, а не догоняет", "ember"))))

# ── СЦЕНА 12 · профиль по семи блокам ───────────────────────────────
A('        <!-- ══ СЦЕНА 12 · слайд 30 · профиль по семи блокам ══ -->\n')
A('        <section class="scene" id="s12" data-in="158.5" data-out="164.9">\n')
A(сетка7(["158.89"] * 7))
A(cores(core("162.17", "Сильные и слабые стороны", "solar")))
A('        </section>\n\n')

# ── СЦЕНА 13 · дорожная карта ───────────────────────────────────────
A('        <!-- ══ СЦЕНА 13 · слайд 30 · дорожная карта ══ -->\n')
A('        <section class="scene" id="s13" data-in="165.0" data-out="174.6">\n')
A('            <div class="steps">\n')
A('                <div class="link el" data-in="167.73">'
  '<svg viewBox="0 0 988 112" preserveAspectRatio="none">'
  '<line x1="259" y1="56" x2="781" y2="56"/>'
  '<polygon points="817,56 779,39 779,73"/></svg></div>\n')
A('            <div class="row">\n')
A(item("167.73", "clock", "solar", 100, "Сейчас", cur="167.73 169.27"))
A(item("169.27", "calendar-blank", "ember", 100, "Среднесрок", cur="169.27 171.13"))
A(item("172.19", "rocket", "solar", 100, "AI-first", cur="172.19 174.12"))
A('            </div>\n')
A('            </div>\n')
A(cores(core("166.15", "Дорожная карта", "ember")))
A('        </section>\n\n')

html = html[:m_start] + "".join(L) + html[m_end:]

# ── длина ролика ─────────────────────────────────────────────────────
подмена("var DURATION = 181.0;                     // дорожка 179.7 c + хвост под шапку",
        "var DURATION = 176.0;                     // дорожка 174.1 c + хвост под шапку",
        "длина")

os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8").write(html)
print("страница собрана:", DST, len(html), "байт")
