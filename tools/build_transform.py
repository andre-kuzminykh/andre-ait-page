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

/* Ток по связям: светлая точка бежит от начала линии к её концу.
   Владелец: «по ним идёт кружком типа ток». Точки живут в своём слое
   поверх линии — у самой линии opacity всегда 1 (она проявляется
   прочерчиванием), и точки в ней зажглись бы раньше времени. */
.flow{position:absolute;left:0;top:0;width:100%;pointer-events:none;z-index:0}
.flow .pulse{
    position:absolute;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;
    background:#fff;box-shadow:0 0 16px 5px rgba(196,181,253,.85);opacity:0;
}
.scene.on .flow.on .pulse{animation:runPulse 2.4s linear infinite}
@keyframes runPulse{
    0%{opacity:0;transform:translate(0,0) scale(.5)}
    10%{opacity:1}
    85%{opacity:1}
    100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.5)}
}

/* Вылетающие значки: из-под круга вверх идут цифры, мозги, роботы или
   молнии — «где данные, цифры вылетают, где intelligence — мозги».
   Значки те же, что в кругах (Phosphor), а не эмодзи: эмодзи рисуются
   системным шрифтом, которого на чужой машине может не быть вовсе. */
/* Значки вылетают ИЗ круга веером вверх: снизу под кругом стоит подпись,
   и пролетающая мимо цифра садилась прямо на буквы. */
.fly{
    position:absolute;left:50%;top:56px;width:0;height:0;
    pointer-events:none;z-index:0;
}
.fly i,.fly b{
    position:absolute;left:-25px;top:-25px;display:block;width:50px;height:50px;
    font:900 44px/1 'Montserrat',sans-serif;text-align:center;opacity:0;color:#fff;
    text-shadow:0 3px 14px rgba(10,4,24,.7);
}
.item .slot{position:relative;z-index:1}
.fly svg{width:100%;height:100%;fill:currentColor;
    filter:drop-shadow(0 3px 10px rgba(10,4,24,.55))}
/* Значок белый, а цвет ему даёт ореол: на оранжевом градиенте оранжевая
   цифра пропадала, на фиолетовом — фиолетовый мозг. */
.fly.solar i,.fly.solar b{filter:drop-shadow(0 0 10px rgba(136,84,243,.95)) drop-shadow(0 2px 6px rgba(10,4,24,.6))}
.fly.ember i,.fly.ember b{filter:drop-shadow(0 0 10px rgba(249,115,22,.95)) drop-shadow(0 2px 6px rgba(10,4,24,.6))}
.scene.on .fly.on i,.scene.on .fly.on b{animation:flyUp 3s ease-out infinite}
@keyframes flyUp{
    0%{opacity:0;transform:translate(0,8px) scale(.55) rotate(0deg)}
    22%{opacity:1}
    70%{opacity:.9}
    100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(1.15) rotate(var(--rot))}
}

/* Перечёркивание: владелец просил «интуицию перечеркни анимацией». */
.strike{
    position:absolute;left:50%;top:56px;width:170px;height:170px;
    transform:translate(-50%,-50%);pointer-events:none;z-index:3;overflow:visible;
}
.strike.el,.strike.el.on{opacity:1;transform:translate(-50%,-50%)}
.strike line{
    stroke:#fff;stroke-width:9;stroke-linecap:round;
    stroke-dasharray:240;stroke-dashoffset:240;
    filter:drop-shadow(0 2px 7px rgba(10,4,24,.85));
}
.strike.el.on line{animation:drawStrike .5s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes drawStrike{to{stroke-dashoffset:0}}

/* Два элемента в кадре стоят ШИРОКО: владелец просил развести их так,
   чтобы каждый оказался над своей картиной, а середина осталась пустой
   (там его голова). Центры картин в кадре — 235 и 820 по горизонтали. */
.scene .row.duo{justify-content:space-between;gap:0}
.scene .row.duo>.item{flex:0 0 400px}
.duo .link{height:112px}

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
/* Сияние за фразой: у абзаца высота одной строки, и стандартное
   top:38% уводило облако вверх, к кругам. Прижимаем к самой строке. */
.core .glow{width:780px;height:210px;top:50%}
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
/* Владелец: «где задачи — там Задача 1 / Задача 2, по очереди». */
#s2 .down .label{font-size:26px;margin-top:10px}
#s2 .core{font-size:34px;margin-top:8px}

/* ── СЦЕНА 3 · стало: матрица ───────────────────────────────────────
   Шесть кружков в два ряда, столбец = команда: в каждой разные функции.
   Линии внутри столбца, поперёк рядов И ПО ДИАГОНАЛЯМ (владелец:
   «они ещё по диагонали соединяются») — это и есть матрица; по связям
   бежит ток. */
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
.pair{position:relative;width:100%}
.pair .link{height:112px}
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
#s8 .label{font-size:34px;margin-top:16px;white-space:nowrap}

/* ── СЦЕНА 9 · интуиция против фактов ───────────────────────────────
   Единственный приглушённый круг ролика — это прошлое, а не схема.
   Соседи при этом НЕ гаснут: приглушена только сама интуиция. */
#s9 .label{font-size:34px;margin-top:16px;white-space:nowrap}
#s9 .dim .circle{filter:saturate(.3);opacity:.8}
#s9 .dim .label{color:rgba(255,255,255,.72)}
#s9 .core{margin-top:38px}

/* ── СЦЕНА 10 · человек в центре решений ────────────────────────────── */
#s10 .label{font-size:34px;margin-top:16px;white-space:nowrap}

/* ── СЦЕНА 11 · что дала цифра и где встала ─────────────────────────── */
#s11 .label{font-size:30px;margin-top:14px;white-space:nowrap}


/* ── СЦЕНА 12 · предел цифровой модели ──────────────────────────────── */
#s12 .label{font-size:32px;margin-top:16px;white-space:nowrap}
#s12 .core{margin-top:40px}

/* ── СЦЕНА 14 · три уровня зрелости ─────────────────────────────────
   Владелец: «AI Driven / AI First и AI Native на одной линии без
   полоски». Ступеньки и соединяющая линия убраны: три круга в ряд,
   уровень читается по подписи и по кольцу выделения. */
#s14 .label{font-size:34px;margin-top:14px;white-space:nowrap}
#s14 .sub{font-size:24px;margin-top:8px}
#s14 .cores{height:52px;margin-bottom:6px}

/* ── СЦЕНА 15 · финал ───────────────────────────────────────────────── */
#s15 .label{font-size:32px;margin-top:16px;line-height:1.16}

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


def core(in_, текст, цвет, out=None, halo=False, ещё=""):
    # ВНУТРИ <p> только строчные теги: <div> браузер закрывает абзац
    # раньше времени, и фраза вываливалась из .core — «Предел цифровой
    # модели» вышел системным кеглем 16px вместо 38.
    гало = ('<span class="halo"><span class="glow %s %s"></span></span>'
            % ("glow-ember" if цвет == "ember" else "", ещё)) if halo else ""
    return ('            <p class="core %s el"%s>%s%s</p>\n'
            % (цвет, атрибуты(in_, out), гало, текст))


def cores(mt, *строки):
    return ('            <div class="cores" style="margin-top:%dpx">\n%s            </div>\n'
            % (mt, "".join(строки)))


def sub(in_, текст):
    return '<p class="sub el" data-in="%s">%s</p>' % (in_, текст)


def halo(цвет, in_, ещё=""):
    return ('<div class="halo el" data-in="%s"><div class="glow %s %s"></div></div>'
            % (in_, "glow-ember" if цвет == "ember" else "", ещё))


# Разлёт значков: слева направо, каждый со своим сдвигом, поворотом и
# задержкой — иначе они летят строем и выглядят как одна деталь.
# Куда летит каждый значок: сдвиг по x, по y, поворот и задержка. Веер
# вверх из центра круга — вниз нельзя, там подпись.
# Выше -105 не поднимаем: круг стоит на y≈330, а зона графики кончается
# на 238 — значок улетал бы под самую шапку.
РАЗЛЁТ = [(-138, -52, -18, 0.00), (-78, -88, 12, 0.55), (0, -104, -8, 1.10),
          (78, -84, 16, 1.65), (138, -48, -14, 2.20)]


def fly(in_, цвет, значок=None, цифры=None):
    куски = []
    for (dx, dy, rot, задержка), знак in zip(РАЗЛЁТ, (цифры or [None] * 5)):
        тег = "b" if цифры else "i"
        нутро = знак if цифры else ico(значок)
        куски.append('<%s style="--dx:%dpx;--dy:%dpx;--rot:%ddeg;animation-delay:%.2fs">%s</%s>'
                     % (тег, dx, dy, rot, задержка, нутро, тег))
    return ('<div class="fly %s el" data-in="%s">%s</div>' % (цвет, in_, "".join(куски)))


def strike(in_):
    """Перечёркивание круга: линия чертится по диагонали."""
    return ('<div class="strike el" data-in="%s">'
            '<svg viewBox="0 0 170 170"><line x1="20" y1="150" x2="150" y2="20"/></svg>'
            '</div>' % in_)


# ── СЦЕНА 1 · три трансформации ─────────────────────────────────────
A('        <!-- ══ СЦЕНА 1 · слайд 17 · Agile → Цифровая → AI ══ -->\n')
A('        <section class="scene" id="s1" data-in="0.9" data-out="40.25">\n')
A('            <div class="stage">\n')
A('                <div class="link el" data-in="3.85">'
  '<svg viewBox="0 0 940 112" preserveAspectRatio="none">'
  '<line x1="148" y1="56" x2="792" y2="56"/></svg></div>\n')
A('            <div class="row">\n')
A(item("3.85", "users-three", "solar", 104, "Agile",
       cur="6.86 17.39",
       extra='<p class="role el" data-in="10.08">Команды</p>', cls="item i1"))
A(item("4.62", "database", "ember", 104, "Цифровая",
       cur="17.88 26.74",
       extra='<p class="role el" data-in="18.92">Данные</p>', cls="item i2"))
A(item("5.30", "brain", "solar", 104, "ИИ",
       cur="26.74 32.73",
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
A('                <div class="flow el" data-in="42.60">'
  '<span class="pulse" style="left:360px;top:96px;--dx:-220px;--dy:90px"></span>'
  '<span class="pulse" style="left:360px;top:96px;--dx:0px;--dy:90px;animation-delay:.5s"></span>'
  '<span class="pulse" style="left:360px;top:96px;--dx:220px;--dy:90px;animation-delay:1s"></span>'
  '</div>\n')
A('                <div class="top item el" data-in="40.66" data-cur="40.66 42.10">'
  '<div class="slot">%s</div><p class="label">Решения</p></div>\n'
  % circle("user-gear", "solar", 96))
A('                <div class="down">\n')
# Владелец: задачи подписаны по отдельности и выходят по очереди.
for t, подпись in [("42.60", "Задача 1"), ("43.20", "Задача 2"), ("43.80", "Задача 3")]:
    A(item(t, "list-checks", "ember", 96, подпись))
A('                </div>\n')
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
  '<line x1="66" y1="168" x2="594" y2="168"/>'
  '<line x1="66" y1="44" x2="330" y2="168"/>'
  '<line x1="330" y1="44" x2="66" y2="168"/>'
  '<line x1="330" y1="44" x2="594" y2="168"/>'
  '<line x1="594" y1="44" x2="330" y2="168"/></svg></div>\n')
A('                <div class="flow el" data-in="49.40">'
  '<span class="pulse" style="left:66px;top:44px;--dx:264px;--dy:124px"></span>'
  '<span class="pulse" style="left:594px;top:44px;--dx:-264px;--dy:124px;animation-delay:.6s"></span>'
  '<span class="pulse" style="left:66px;top:44px;--dx:528px;--dy:0px;animation-delay:1.2s"></span>'
  '<span class="pulse" style="left:330px;top:44px;--dx:0px;--dy:124px;animation-delay:1.8s"></span>'
  '</div>\n')
A('                <div class="grid">\n')
матрица = [("47.90", "chart-line-up", "solar"), ("48.20", "code", "ember"),
           ("48.50", "megaphone", "solar"), ("48.80", "users", "ember"),
           ("49.10", "wrench", "solar"), ("49.40", "headset", "ember")]
for in_, icon, colour in матрица:
    A(item(in_, icon, colour, 76, ""))
A('                </div>\n')
A('                <p class="foot el" data-in="51.91">'
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
  '<svg viewBox="0 0 988 112" preserveAspectRatio="none">'
  '<line x1="272" y1="56" x2="676" y2="56"/>'
  '<polygon points="704,56 674,42 674,70"/></svg></div>\n')
A('            <div class="row duo">\n')
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
A('            <div class="row duo">\n')
A(item("86.54", "graph", "solar", 108, "Цифровой след", cur="86.54 88.08"))
A(item("88.30", "currency-dollar", "ember", 108, "Новая нефть", cur="88.30 90.85",
       halo='<div class="halo el" data-in="88.30"><div class="glow glow-ember"></div></div>'))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 9 · интуиция → факты → data-driven ────────────────────────
A('        <!-- ══ СЦЕНА 9 · слайд 19 · решения по фактам, а не по интуиции ══ -->\n')
A('        <section class="scene" id="s9" data-in="91.1" data-out="98.7">\n')
A('            <div class="row duo">\n')
A(item("93.08", "lightbulb", "solar", 104, "Интуиция", cur="93.08 94.66",
       cls="item dim", extra=strike("94.30")))
A(item("94.66", "check-circle", "ember", 104, "Факты", cur="94.66 95.49"))
A('            </div>\n')
A(core("96.34", "Data-driven управление", "solar"))
A('        </section>\n\n')

# ── СЦЕНА 10 · человек в центре ─────────────────────────────────────
A('        <!-- ══ СЦЕНА 10 · слайд 19 · человек остаётся центром решений ══ -->\n')
A('        <section class="scene" id="s10" data-in="98.8" data-out="106.9">\n')
A('            <div class="row duo">\n')
A(item("99.00", "user-gear", "solar", 112, "Человек", cur="98.84 102.14",
       extra=sub("99.74", "Центр решений"), halo=halo("solar", "99.00")))
A(item("102.14", "warning", "ember", 112, "Ограничение", cur="102.14 106.81",
       extra=sub("105.12", "Дальше — ИИ"),
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
A('            <div class="row duo">\n')
A(item("121.60", "clock", "ember", 104, "Скорость мышления", cur="121.60 123.36"))
A(item("123.36", "eye", "solar", 104, "Масштаб внимания", cur="123.36 124.75"))
A('            </div>\n')
A(core("125.50", "Предел цифровой модели", "ember"))
A('        </section>\n\n')

# ── СЦЕНА 13 · data-driven → intelligence-driven ────────────────────
A('        <!-- ══ СЦЕНА 13 · слайд 20 · переход к intelligence-driven ══ -->\n')
A('        <section class="scene" id="s13" data-in="127.5" data-out="141.95">\n')
A('            <div class="pair">\n')
A('                <div class="link el" data-in="130.20">'
  '<svg viewBox="0 0 988 112" preserveAspectRatio="none">'
  '<line x1="272" y1="56" x2="676" y2="56"/>'
  '<polygon points="704,56 674,42 674,70"/></svg></div>\n')
A('            <div class="row duo">\n')
A(item("129.39", "chart-line-up", "ember", 104, "Data-driven", cur="129.39 130.92",
       halo=halo("ember", "129.39") + fly("129.39", "ember", цифры=["1", "0", "1", "0", "1"])))
A(item("130.92", "brain", "solar", 104, "Intelligence-driven", cur="130.92 133.13",
       halo=halo("solar", "130.92") + fly("130.92", "solar", значок="brain")))
A('            </div>\n')
A('            </div>\n')
A(core("138.90", "Другой уровень управления", "ember"))
A('        </section>\n\n')

# ── СЦЕНА 14 · три уровня зрелости ──────────────────────────────────
A('        <!-- ══ СЦЕНА 14 · слайд 21 · AI-driven → AI-first → AI-native ══ -->\n')
A('        <section class="scene" id="s14" data-in="142.6" data-out="173.5">\n')
A(cores(0, core("143.10", "Три уровня зрелости", "solar", out="146.54")))
A('            <div class="row">\n')
A(item("146.70", "wrench", "solar", 96, "AI-Driven", cur="149.68 157.79",
       extra=sub("152.20", "ИИ как инструмент")))
A(item("147.60", "gear-six", "ember", 96, "AI-First", cur="158.08 167.57",
       extra=sub("160.95", "Встроен в модель")))
A(item("148.50", "rocket", "solar", 96, "AI-Native", cur="167.92 173.47",
       extra=sub("171.66", "ИИ и есть продукт")))
A('            </div>\n')
A('        </section>\n\n')

# ── СЦЕНА 15 · финал ────────────────────────────────────────────────
A('        <!-- ══ СЦЕНА 15 · слайд 21 · от «использует ИИ» к «живёт им» ══ -->\n')
A('        <section class="scene" id="s15" data-in="173.6" data-out="180.4">\n')
A('            <div class="pair">\n')
A('                <div class="link el" data-in="176.98">'
  '<svg viewBox="0 0 988 112" preserveAspectRatio="none">'
  '<line x1="272" y1="56" x2="676" y2="56"/>'
  '<polygon points="704,56 674,42 674,70"/></svg></div>\n')
A('            <div class="row duo">\n')
A(item("175.12", "robot", "solar", 108, "Использует ИИ", cur="175.12 176.98",
       halo=halo("solar", "175.12") + fly("175.12", "solar", значок="robot")))
A(item("177.58", "sparkle", "ember", 108, "Существует<br>благодаря ИИ", cur="177.58 179.65",
       halo=halo("ember", "177.58") + fly("177.58", "ember", значок="lightning")))
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
