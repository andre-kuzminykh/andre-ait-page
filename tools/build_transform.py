# -*- coding: utf-8 -*-
"""Страница графики поверх видео по слайдам 17–21 («Эволюция операционных
моделей», «Agile-трансформация», «Цифровая трансформация», «ИИ-трансформация»,
«Уровни зрелости бизнес-модели»).

Берём готовую страницу прошлого ролика — в ней вся машинерия: покадровый
рендер, шапка, обложка, субтитры, скрипт сборки, — и меняем ТОЛЬКО сцены:
их CSS и разметку. Каждая замена обязана сработать, поэтому подмена() с
assert: молчаливый промах уже один раз оставлял старую раскладку.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "automation", "1", "overlay-value", "index.html")
DST = os.path.join(ROOT, "automation", "1", "overlay-transform", "index.html")
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


подмена("<title>Где ИИ создаёт ценность — анимированная графика поверх видео</title>",
        "<title>Три трансформации бизнеса — анимированная графика поверх видео</title>",
        "заголовок")

# ── CSS сцен ─────────────────────────────────────────────────────────
css_start = html.index("/* ── СЦЕНА 1 · арка RUN → CHANGE → DISRUPT")
css_end = html.index("/* ── Обложка: первые секунды готового ролика.")
CSS = """/* ── Общее для этого ролика ─────────────────────────────────────────
   Ролик про переходы: почти в каждой сцене есть линия, по которой одно
   состояние превращается в другое. Линия — общий класс, а не копия в
   каждой сцене. Круги лежат ПОВЕРХ линии (z-index) и закрывают её концы:
   иначе штрих торчит из-под иконки, это уже ловили в прошлом ролике. */
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

/* Фраза-вывод: крупная строка по центру сцены, цвет чередуется.
   Две фразы, которые сменяют друг друга, кладём в общий контейнер и
   абсолютом друг на друга: спрятанная строка (opacity:0) продолжает
   занимать место, и сцена вылезала из зоны на полсотни пикселей. */
.cores{position:relative;width:100%;height:46px}
.cores .core{position:absolute;left:0;right:0;top:0}
.core{
    font-size:38px;font-weight:900;color:#fff;white-space:nowrap;text-align:center;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75);
}
.core.solar{color:#C9B2FF}
.core.ember{color:#FFB380}
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

/* ── СЦЕНА 1 · три трансформации в ряд ──────────────────────────────
   Agile → Цифровая → AI. Круги одного размера на одной высоте, линия
   между ними прочерчивается вместе с их появлением. Под каждым — одно
   слово роли, и больше в кадре ничего, пока не пойдёт вывод. */
#s1 .link{height:112px}
#s1 .label{font-size:40px;margin-top:16px;letter-spacing:.01em}
#s1 .role{
    font-size:27px;font-weight:800;color:#FFD9BE;margin-top:8px;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6);opacity:0;
    transition:opacity .5s var(--ease),transform .5s var(--ease);transform:translateY(8px);
}
#s1 .role.on{opacity:1;transform:none}
#s1 .i2 .role{color:#DCC9FF}
#s1 .core{margin-top:42px}

/* ── СЦЕНА 2 · было: иерархия ───────────────────────────────────────
   Один круг сверху, три снизу, линии сверху вниз: решения принимаются
   наверху, задачи спускаются. Диаметры одинаковые — иерархию рисует
   расстановка, а не размер (правило владельца). */
#s2 .pyr{position:relative;width:720px;text-align:center}
#s2 .pyr .link{height:262px}
#s2 .top{display:flex;flex-direction:column;align-items:center;position:relative;z-index:1}
#s2 .down{display:flex;gap:120px;justify-content:center;margin-top:28px;position:relative;z-index:1}
#s2 .down .item{flex:none}
#s2 .slot{height:100px}
#s2 .down .slot{height:100px}
#s2 .label{font-size:30px;margin-top:12px;white-space:nowrap}
#s2 .down .label{font-size:0;margin:0}
#s2 .foot{font-size:30px;font-weight:900;color:#fff;margin-top:8px;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75)}
#s2 .core{font-size:34px}

/* ── СЦЕНА 3 · стало: матрица ───────────────────────────────────────
   Шесть кружков в два ряда, столбец = команда: в каждой разные функции.
   Линии внутри столбца и поперёк рядов — это и есть матрица. */
#s3 .matrix{position:relative;width:660px;text-align:center}
#s3 .matrix .link{height:214px}
#s3 .grid{
    display:grid;grid-template-columns:repeat(3,1fr);
    row-gap:36px;column-gap:70px;width:100%;position:relative;z-index:1;
}
#s3 .grid .item{flex:none}
#s3 .slot{height:88px}
#s3 .foot{font-size:30px;font-weight:900;color:#fff;margin-top:16px;white-space:nowrap;
    text-shadow:0 3px 16px rgba(10,4,24,.6),0 1px 4px rgba(10,4,24,.75)}
#s3 .core{font-size:32px}

/* ── СЦЕНА 4 · быстрые циклы и живая система ────────────────────────
   Кольцо с бегущей точкой: цикл виден движением, а не стрелкой. */
#s4 .cycle{position:relative;width:200px;height:200px}
#s4 .ring{
    position:absolute;inset:0;border-radius:50%;
    border:3px dashed rgba(255,255,255,.32);
}
.scene.on #s4 .spin,#s4 .spin{position:absolute;inset:0;animation:spin 4.2s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#s4 .dot{
    position:absolute;left:50%;top:-9px;width:18px;height:18px;margin-left:-9px;
    border-radius:50%;background:#fff;box-shadow:0 0 18px 6px rgba(196,181,253,.9);
}
#s4 .mid{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
#s4 .label{font-size:32px;margin-top:18px;white-space:nowrap}
#s4 .core{margin-top:22px}

/* ── СЦЕНА 5 · фундамент ────────────────────────────────────────────── */
#s5 .slot{height:148px}
#s5 .label{font-size:44px;margin-top:18px;position:relative;z-index:1}
#s5 .glow{width:820px;height:330px}
#s5 .core{margin-top:26px}

/* ── СЦЕНЫ 6 и 13 · переход одного состояния в другое ───────────────
   Два круга и стрелка между ними: слева было, справа стало. */
.pair{position:relative;width:760px}
.pair .link{height:112px}
.pair .row{gap:200px;justify-content:center}
.pair .item{flex:0 1 auto}
.pair .label{font-size:34px;margin-top:16px;white-space:nowrap}
#s13 .label{font-size:30px}
#s13 .core{margin-top:36px}
#s6 .core{margin-top:36px}

/* ── СЦЕНА 7 · что оцифровали ───────────────────────────────────────
   Четыре в ряд: на четыре колонки по 220px подписи в одну строку
   помещаются, если кегль 26 (замерено по метрикам шрифта). */
#s7 .slot{height:104px}
#s7 .label{font-size:26px;margin-top:14px;white-space:nowrap}

/* ── СЦЕНА 8 · цифровой след и новая нефть ──────────────────────────── */
#s8 .row{gap:150px;justify-content:center}
#s8 .item{flex:0 1 auto}
#s8 .label{font-size:34px;margin-top:16px;white-space:nowrap}

/* ── СЦЕНА 9 · интуиция против фактов ───────────────────────────────
   Единственный приглушённый круг ролика — это прошлое, а не схема.
   Соседи при этом НЕ гаснут: приглушена только сама интуиция. */
#s9 .row{gap:160px;justify-content:center}
#s9 .item{flex:0 1 auto}
#s9 .label{font-size:34px;margin-top:16px;white-space:nowrap}
#s9 .dim .circle{filter:saturate(.3);opacity:.8}
#s9 .dim .label{color:rgba(255,255,255,.72)}
#s9 .core{margin-top:38px}

/* ── СЦЕНА 10 · человек в центре решений ────────────────────────────── */
#s10 .row{gap:190px;justify-content:center}
#s10 .item{flex:0 1 auto}
#s10 .label{font-size:34px;margin-top:16px;white-space:nowrap}

/* ── СЦЕНА 11 · что дала цифра и где встала ─────────────────────────── */
#s11 .label{font-size:30px;margin-top:14px;white-space:nowrap}


/* ── СЦЕНА 12 · предел цифровой модели ──────────────────────────────── */
#s12 .row{gap:150px;justify-content:center}
#s12 .item{flex:0 1 auto}
#s12 .label{font-size:32px;margin-top:16px;white-space:nowrap}
#s12 .core{margin-top:40px}

/* ── СЦЕНА 14 · три уровня зрелости ─────────────────────────────────
   Здесь высота значит уровень, поэтому круги стоят ступенями — это
   единственная сцена, где они не на одной линии. Диаметр всё равно
   один: подрастает только тот, о ком говорят. */
#s14 .steps{position:relative;width:900px;height:330px}
#s14 .link{height:330px}
#s14 .st{position:absolute;display:flex;flex-direction:column;align-items:center;z-index:1}
#s14 .st1{left:0;bottom:0}
#s14 .st2{left:50%;transform:translateX(-50%);bottom:78px}
#s14 .st3{right:0;bottom:156px}
#s14 .st.el{transform:translateY(18px) scale(.96)}
#s14 .st.el.on{transform:none}
#s14 .st2.el{transform:translate(-50%,18px) scale(.96)}
#s14 .st2.el.on{transform:translateX(-50%)}
#s14 .label{font-size:34px;margin-top:14px;white-space:nowrap}
#s14 .sub{font-size:24px;margin-top:8px}
#s14 .core{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%)}
#s14 .core.el{transform:translate(-50%,calc(-50% + 18px)) scale(.96)}
#s14 .core.el.on{transform:translate(-50%,-50%)}

/* ── СЦЕНА 15 · финал ───────────────────────────────────────────────── */
#s15 .row{gap:170px;justify-content:center}
#s15 .item{flex:0 1 auto}
#s15 .label{font-size:32px;margin-top:16px;line-height:1.16}
#s15 .pair{width:820px}

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


def core(in_, текст, цвет, out=None, halo=False):
    # ВНУТРИ <p> только строчные теги: <div> браузер закрывает абзац
    # раньше времени, и фраза вываливалась из .core — «Предел цифровой
    # модели» вышел системным кеглем 16px вместо 38.
    гало = ('<span class="halo"><span class="glow %s"></span></span>'
            % ("glow-ember" if цвет == "ember" else "")) if halo else ""
    return ('            <p class="core %s el"%s>%s%s</p>\n'
            % (цвет, атрибуты(in_, out), гало, текст))


def cores(mt, *строки):
    return ('            <div class="cores" style="margin-top:%dpx">\n%s            </div>\n'
            % (mt, "".join(строки)))


def sub(in_, текст):
    return '<p class="sub el" data-in="%s">%s</p>' % (in_, текст)


# ── СЦЕНА 1 · три трансформации ─────────────────────────────────────
A('        <!-- ══ СЦЕНА 1 · слайд 17 · Agile → Цифровая → AI ══ -->\n')
A('        <section class="scene" id="s1" data-in="0.9" data-out="40.25">\n')
A('            <div class="stage">\n')
A('                <div class="link el" data-in="3.85">'
  '<svg viewBox="0 0 940 112" preserveAspectRatio="none">'
  '<line x1="148" y1="56" x2="792" y2="56"/></svg></div>\n')
A('            <div class="row">\n')
A(item("3.85", "users-three", "solar", 104, "Agile",
       cur="3.74 4.90 6.86 11.53 11.78 17.39 36.54 40.25",
       extra='<p class="role el" data-in="10.08">Команды</p>', cls="item i1"))
A(item("4.62", "database", "ember", 104, "Цифровая",
       cur="4.62 6.34 17.88 26.74",
       extra='<p class="role el" data-in="18.92">Данные</p>', cls="item i2"))
A(item("5.30", "brain", "solar", 104, "AI",
       cur="5.30 6.69 26.74 32.73",
       extra='<p class="role el" data-in="30.60">Решения</p>', cls="item i3"))
A('            </div>\n')
A(core("32.92", "Новый этап эволюции", "ember"))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 2 · было: иерархия ────────────────────────────────────────
A('        <!-- ══ СЦЕНА 2 · слайд 18 · было: решения наверху, задачи вниз ══ -->\n')
A('        <section class="scene" id="s2" data-in="40.45" data-out="47.25">\n')
A('            <div class="pyr">\n')
A('                <div class="link el" data-in="42.10">'
  '<svg viewBox="0 0 720 262" preserveAspectRatio="none">'
  '<line x1="360" y1="96" x2="140" y2="186"/>'
  '<line x1="360" y1="96" x2="360" y2="186"/>'
  '<line x1="360" y1="96" x2="580" y2="186"/></svg></div>\n')
A('                <div class="top item el" data-in="40.66" data-cur="40.66 42.10">'
  '<div class="slot">%s</div><p class="label">Решения</p></div>\n'
  % circle("user-gear", "solar", 96))
A('                <div class="down">\n')
for i, t in enumerate(["42.30", "42.60", "42.90"]):
    A(item(t, "list-checks", "ember", 96, "", cur="42.96 44.37"))
A('                </div>\n')
A('                <p class="foot el" data-in="43.10" data-cur="42.96 44.37">Задачи</p>\n')
A(cores(18, core("44.46", "Контроль есть", "solar", out="45.74"),
        core("45.74", "Изменения — медленные", "ember")))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 3 · стало: матрица ────────────────────────────────────────
A('        <!-- ══ СЦЕНА 3 · слайд 18 · стало: кросс-функциональные команды ══ -->\n')
A('        <section class="scene" id="s3" data-in="47.4" data-out="56.9">\n')
A('            <div class="matrix">\n')
A('                <div class="link el" data-in="49.10">'
  '<svg viewBox="0 0 660 214" preserveAspectRatio="none">'
  '<line x1="66" y1="44" x2="66" y2="168"/>'
  '<line x1="330" y1="44" x2="330" y2="168"/>'
  '<line x1="594" y1="44" x2="594" y2="168"/>'
  '<line x1="66" y1="44" x2="594" y2="44"/>'
  '<line x1="66" y1="168" x2="594" y2="168"/></svg></div>\n')
A('                <div class="grid">\n')
матрица = [("47.90", "chart-line-up", "solar"), ("48.20", "code", "ember"),
           ("48.50", "megaphone", "solar"), ("48.80", "users", "ember"),
           ("49.10", "wrench", "solar"), ("49.40", "headset", "ember")]
for in_, icon, colour in матрица:
    A(item(in_, icon, colour, 76, "", cur="51.91 53.50"))
A('                </div>\n')
A('                <p class="foot el" data-in="51.91" data-cur="51.91 53.50">'
  'Кросс-функциональные команды</p>\n')
A(cores(14, core("53.50", "Сами решают", "solar", out="55.00"),
        core("55.00", "Отвечают за результат", "ember")))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 4 · циклы и живая система ─────────────────────────────────
A('        <!-- ══ СЦЕНА 4 · слайд 18 · быстрые циклы, живая система ══ -->\n')
A('        <section class="scene" id="s4" data-in="57.0" data-out="67.5">\n')
A('            <div class="cycle el" data-in="57.08" data-cur="57.08 60.79">\n')
A('                <div class="ring"></div>\n')
A('                <div class="spin"><span class="dot"></span></div>\n')
A('                <div class="mid">%s</div>\n' % circle("arrows-merge", "solar", 96))
A('            </div>\n')
A('            <p class="label el" data-in="57.84">Быстрые циклы</p>\n')
A('            <p class="sub el" data-in="59.14">Гипотезы · Адаптация</p>\n')
A(core("62.48", "Из механизма — в живую систему", "ember"))
A('        </section>\n\n')

# ── СЦЕНА 5 · фундамент ─────────────────────────────────────────────
A('        <!-- ══ СЦЕНА 5 · слайд 18 · гибкость как фундамент ══ -->\n')
A('        <section class="scene" id="s5" data-in="67.6" data-out="72.15">\n')
A('            <div class="row">\n')
A('                <div class="item el" data-in="67.82" data-cur="67.82 72.15">'
  '<div class="halo"><div class="glow"></div></div>'
  '<div class="slot">%s</div><p class="label">Гибкость</p></div>\n'
  % circle("lifebuoy", "solar", 132))
A('            </div>\n')
A(core("69.44", "Фундамент цифровой трансформации", "ember"))
A('        </section>\n\n')

# ── СЦЕНА 6 · процессы → данные ─────────────────────────────────────
A('        <!-- ══ СЦЕНА 6 · слайд 19 · от управления процессами к данным ══ -->\n')
A('        <section class="scene" id="s6" data-in="72.4" data-out="77.5">\n')
A('            <div class="pair">\n')
A('                <div class="link el" data-in="74.41">'
  '<svg viewBox="0 0 760 112" preserveAspectRatio="none">'
  '<line x1="250" y1="56" x2="486" y2="56"/>'
  '<polygon points="510,56 484,44 484,68"/></svg></div>\n')
A('            <div class="row">\n')
A(item("73.20", "arrows-merge", "ember", 104, "Процессы", cur="74.41 75.66"))
A(item("75.66", "database", "solar", 104, "Данные", cur="75.66 77.25"))
A('            </div>\n')
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 7 · что оцифровали ────────────────────────────────────────
A('        <!-- ══ СЦЕНА 7 · слайд 19 · оцифровали операции, клиентов, данные ══ -->\n')
A('        <section class="scene" id="s7" data-in="77.6" data-out="84.9">\n')
A('            <div class="row">\n')
A(item("78.52", "gear-six", "ember", 92, "Операции", cur="78.52 80.50"))
A(item("80.50", "users", "solar", 92, "Клиенты", cur="80.50 81.49"))
A(item("81.78", "database", "ember", 92, "Базы данных", cur="81.78 83.00"))
A(item("83.00", "chart-pie-slice", "solar", 92, "Аналитика", cur="83.00 84.67"))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 8 · цифровой след и новая нефть ───────────────────────────
A('        <!-- ══ СЦЕНА 8 · слайд 19 · цифровой след, данные как нефть ══ -->\n')
A('        <section class="scene" id="s8" data-in="85.0" data-out="91.0">\n')
A('            <div class="row">\n')
A(item("86.54", "graph", "solar", 108, "Цифровой след", cur="86.54 88.08"))
A(item("88.30", "currency-dollar", "ember", 108, "Новая нефть", cur="88.30 90.85",
       halo='<div class="halo el" data-in="88.30"><div class="glow glow-ember"></div></div>'))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 9 · интуиция → факты → data-driven ────────────────────────
A('        <!-- ══ СЦЕНА 9 · слайд 19 · решения по фактам, а не по интуиции ══ -->\n')
A('        <section class="scene" id="s9" data-in="91.1" data-out="98.7">\n')
A('            <div class="row">\n')
A(item("93.08", "lightbulb", "solar", 104, "Интуиция", cur="93.08 94.66", cls="item dim"))
A(item("94.66", "check-circle", "ember", 104, "Факты", cur="94.66 95.49"))
A('            </div>\n')
A(core("96.34", "Data-driven управление", "solar"))
A('        </section>\n\n')

# ── СЦЕНА 10 · человек в центре ─────────────────────────────────────
A('        <!-- ══ СЦЕНА 10 · слайд 19 · человек остаётся центром решений ══ -->\n')
A('        <section class="scene" id="s10" data-in="98.8" data-out="106.9">\n')
A('            <div class="row">\n')
A(item("99.00", "user-gear", "solar", 112, "Человек", cur="98.84 102.14",
       extra=sub("99.74", "Центр решений")))
A(item("102.14", "warning", "ember", 112, "Ограничение", cur="102.14 106.81",
       extra=sub("105.12", "Дальше — AI"),
       halo='<div class="halo el" data-in="102.14"><div class="glow glow-ember"></div></div>'))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 11 · что дала цифра ───────────────────────────────────────
A('        <!-- ══ СЦЕНА 11 · слайд 20 · данные есть, а решают всё равно люди ══ -->\n')
A('        <section class="scene" id="s11" data-in="107.4" data-out="120.9">\n')
A('            <div class="row">\n')
A(item("108.58", "database", "solar", 96, "Данные", cur="108.58 109.84"))
A(item("109.84", "eye", "ember", 96, "Прозрачность", cur="109.84 111.47"))
A(item("112.28", "target", "solar", 96, "Измеримость", cur="111.50 113.91"))
A('            </div>\n')
A(cores(40, core("114.16", "Данные сами не решают", "ember", out="117.62"),
        core("117.62", "Решает человек", "solar")))
A('        </section>\n\n')

# ── СЦЕНА 12 · предел цифровой модели ───────────────────────────────
A('        <!-- ══ СЦЕНА 12 · слайд 20 · предел: скорость мышления и внимание ══ -->\n')
A('        <section class="scene" id="s12" data-in="121.0" data-out="127.35">\n')
A('            <div class="row">\n')
A(item("121.60", "clock", "ember", 104, "Скорость мышления", cur="121.60 123.36"))
A(item("123.36", "eye", "solar", 104, "Масштаб внимания", cur="123.36 124.75"))
A('            </div>\n')
A(core("125.50", "Предел цифровой модели", "ember", halo=True))
A('        </section>\n\n')

# ── СЦЕНА 13 · data-driven → intelligence-driven ────────────────────
A('        <!-- ══ СЦЕНА 13 · слайд 20 · переход к intelligence-driven ══ -->\n')
A('        <section class="scene" id="s13" data-in="127.5" data-out="141.95">\n')
A('            <div class="pair">\n')
A('                <div class="link el" data-in="130.20">'
  '<svg viewBox="0 0 760 112" preserveAspectRatio="none">'
  '<line x1="250" y1="56" x2="486" y2="56"/>'
  '<polygon points="510,56 484,44 484,68"/></svg></div>\n')
A('            <div class="row">\n')
A(item("129.39", "chart-line-up", "ember", 104, "Data-driven", cur="129.39 130.92"))
A(item("130.92", "brain", "solar", 104, "Intelligence-driven", cur="130.92 133.13",
       extra=sub("133.18", "Решает система") + sub("135.64", "В масштабе компании")))
A('            </div>\n')
A('            </div>\n')
A(core("138.90", "Другой уровень управления", "ember"))
A('        </section>\n\n')

# ── СЦЕНА 14 · три уровня зрелости ──────────────────────────────────
A('        <!-- ══ СЦЕНА 14 · слайд 21 · AI-driven → AI-first → AI-native ══ -->\n')
A('        <section class="scene" id="s14" data-in="142.6" data-out="173.5">\n')
A('            <div class="steps">\n')
A('                <div class="link el" data-in="146.70">'
  '<svg viewBox="0 0 900 330" preserveAspectRatio="none">'
  '<polyline points="86,222 450,144 814,66"/></svg></div>\n')
A(core("143.10", "Три уровня зрелости", "solar", out="146.54"))
A('                <div class="st st1 el" data-in="146.70" data-cur="146.70 147.60 149.68 157.79">'
  '<div class="slot">%s</div><p class="label">AI-driven</p>%s</div>\n'
  % (circle("wrench", "solar", 96), sub("152.20", "ИИ как инструмент")))
A('                <div class="st st2 el" data-in="147.60" data-cur="147.60 148.50 158.08 167.57">'
  '<div class="slot">%s</div><p class="label">AI-first</p>%s</div>\n'
  % (circle("gear-six", "ember", 96), sub("160.95", "Встроен в модель")))
A('                <div class="st st3 el" data-in="148.50" data-cur="148.50 149.47 167.92 173.47">'
  '<div class="slot">%s</div><p class="label">AI-native</p>%s</div>\n'
  % (circle("rocket", "solar", 96), sub("171.66", "ИИ и есть продукт")))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 15 · финал ────────────────────────────────────────────────
A('        <!-- ══ СЦЕНА 15 · слайд 21 · от «использует ИИ» к «живёт им» ══ -->\n')
A('        <section class="scene" id="s15" data-in="173.6" data-out="180.4">\n')
A('            <div class="pair">\n')
A('                <div class="link el" data-in="176.98">'
  '<svg viewBox="0 0 820 112" preserveAspectRatio="none">'
  '<line x1="290" y1="56" x2="516" y2="56"/>'
  '<polygon points="540,56 514,44 514,68"/></svg></div>\n')
A('            <div class="row">\n')
A(item("175.12", "robot", "solar", 108, "Использует ИИ", cur="175.12 176.98"))
A(item("177.58", "sparkle", "ember", 108, "Существует<br>благодаря ИИ", cur="177.58 179.65",
       halo='<div class="halo el" data-in="177.58"><div class="glow glow-ember"></div></div>'))
A('            </div>\n')
A('            </div>\n')
A('        </section>\n\n')

html = html[:m_start] + "".join(L) + html[m_end:]

# ── длина ролика ─────────────────────────────────────────────────────
подмена("var DURATION = 169.0;                     // дорожка 167.1 c + хвост под шапку",
        "var DURATION = 181.0;                     // дорожка 179.7 c + хвост под шапку",
        "длина")

open(DST, "w", encoding="utf-8").write(html)
print("страница собрана:", DST, len(html), "байт")
