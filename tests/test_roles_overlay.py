# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «Новые роли в AI-first компании» — слайды
41–43 (FR-SITE44). Без зависимостей — запускается и как
`python3 tests/test_roles_overlay.py`, и через pytest.

Девятый ролик по тем же постоянным правилам. Шестнадцать сцен на дорожку
101.8 c: четыре новые роли крупным словом, между ними широкие пары над
картинами и ряды иконок.

Главный тест здесь тот же, что и в прошлом ролике —
test_elements_match_the_spoken_words: он сверяет САМИ СЛОВА элемента с
тем, что звучит в этот момент. Плюс новый, из правки владельца:
test_two_icons_always_stand_wide — два кружка в кадре обязаны стоять
широкой парой, иначе они съезжают на голову говорящего.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-roles")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 101.8          # 01:42 — длина дорожки (auto_9.srt)
_LAYER = 103.3             # слой длиннее: хвост держит шапку
_WORDS = 222               # столько слов в озвучке
_SCENES = 16
_BLOCKS = 4                # столько сцен со «словом + сиянием + значками»:
                           # четыре новые роли — опорные блоки ролика
_РЕЗЫ = (41.9,)               # «обрезка одна по 41 секунде, следовательно
                              # только 2 видео». Ровно 41 попадает внутрь
                              # слова «данных» (40.81…41.27), а 41.6 — внутрь
                              # его субтитра (кончается 41.62). 41.9 — это
                              # ровно смена сцены: пауза дорожки, ни одного
                              # субтитра в кадре, и вторая часть открывается
                              # появлением новой сцены
_KEGL = 50                 # кегль субтитров на кадре 1080×1920
_BAND = 940                # полоса под строку: #sub left:70px right:70px
_ПОЛОСА_ЧИПОВ = 900        # шире ряд подсказок в кадр не помещается
_FONT = os.path.join(_DIR, "fonts", "Montserrat-Black.ttf")
# Центры картин на стене: над ними встают парные элементы, между ними
# остаётся голова. Взяты из мок-фона страницы, он повторяет кадр съёмки.
_ART_L, _ART_R = 235, 820
# Размер сцены: 0,0 внутри неё — это (46, 238) по кадру.
_СЦЕНА_Ш, _СЦЕНА_В = 988, 392


def _шрифт():
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from ttf_width import Шрифт
    return Шрифт(_FONT)


def _html(path=_PAGE):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _script():
    html = _html()
    return html[html.index("function joinScript()"):html.index("var joinBtn")]


def _layer():
    html = _html()
    return html[html.index('<div id="layer">'):html.index('<div id="cover">')]


def _scenes():
    """[(id, in, out, [времена элементов])] по разметке сцен."""
    html, out = _html(), []
    for m in re.finditer(
            r'<section class="scene" id="(\w+)" data-in="([\d.]+)" data-out="([\d.]+)">',
            html):
        end = html.index("</section>", m.end())
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', html[m.end():end])]
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), cues))
    return out


def _cues():
    """[(начало, конец, текст)] из субтитры.srt."""
    with open(_SRT, encoding="utf-8") as f:
        text = f.read().replace("\r", "")
    out = []
    for block in re.split(r"\n\n+", text.strip()):
        m = re.search(r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s*-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)", block)
        if not m:
            continue
        body = " ".join(l for l in block.split("\n")
                        if "-->" not in l and not l.strip().isdigit()).strip()
        a = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000.0
        b = int(m.group(5)) * 3600 + int(m.group(6)) * 60 + int(m.group(7)) + int(m.group(8)) / 1000.0
        out.append((a, b, body))
    return out


def _головы():
    """Шапки блоков: заголовок вместе с сиянием и обоими веерами."""
    return re.findall(r'<div class="head el".*?</div>\n', _layer(), re.S)


def _кегль_заголовка():
    return int(re.search(r"\.block \.title\{\s*font-size:(\d+)px", _html()).group(1))


# ── FR-SITE42: страница самодостаточна ───────────────────────────────────

def test_page_is_self_contained():
    html = _html()
    external = re.findall(r'(?:src|href)="(?:https?:)?//[^"]+"', html)
    assert not external, "страница тянет внешние ресурсы: %r" % external
    for f in re.findall(r"url\((fonts/[^)]+\.woff2)\)", html):
        assert os.path.exists(os.path.join(_DIR, f)), "нет файла шрифта: %s" % f
    assert os.path.exists(os.path.join(_DIR, "logo.png")), "нет файла logo.png"


def test_font_and_icons_match_the_deck():
    assert "Montserrat" in _html(_DECK), "дек больше не на Montserrat"
    assert "'Montserrat'" in _html(), "страница набрана не тем шрифтом, что дек"
    html = _html()
    assert html.count('viewBox="0 0 256 256"') >= 20, "иконок Phosphor подозрительно мало"
    assert "ph-" not in html, "остался класс шрифтовых иконок — он тянет внешний CSS"


# ── FR-SITE42: тайминги сведены с речью ──────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes()
    assert len(scenes) == _SCENES, "сцен должно быть %d, а их %d" % (_SCENES, len(scenes))
    prev = 0.0
    for sid, tin, tout, _ in scenes:
        assert tin < tout, "%s: окно вывернуто" % sid
        assert tin >= prev, "%s начинается раньше, чем кончилась предыдущая" % sid
        prev = tout
    assert prev <= _LAYER + 0.1, "последняя сцена выходит за длину слоя"


def test_every_element_lands_on_a_spoken_cue():
    """Владелец: «элемент появляется, когда о нём говорят»."""
    cues, layer = _cues(), _layer()
    секции = {m.group(1) for m in re.finditer(
        r'<section class="scene" id="\w+" data-in="([\d.]+)"', layer)}
    немой = []
    for m in re.finditer(r'data-in="([\d.]+)"', layer):
        t = m.group(1)
        if t in секции:
            continue
        v = float(t)
        if not any(a - 0.35 <= v < b + 0.35 for a, b, _ in cues):
            немой.append(v)
    assert not немой, "элементы выходят в тишине между репликами: %s" % немой


def test_every_ring_lands_on_a_spoken_cue():
    cues, немой = _cues(), []
    for m in re.finditer(r'data-cur="([^"]+)"', _layer()):
        числа = [float(x) for x in m.group(1).split()]
        assert len(числа) % 2 == 0, "окна подсветки идут парами: %r" % m.group(1)
        for i in range(0, len(числа), 2):
            a, b = числа[i], числа[i + 1]
            assert a < b, "вывернутое окно подсветки %.2f–%.2f" % (a, b)
            if not any(x < b and y > a for x, y, _ in cues):
                немой.append((a, b))
    assert not немой, "подсветка горит в тишине: %s" % немой


def test_each_element_is_highlighted_once():
    """Одно окно на элемент, и в кадре одновременно горит один."""
    layer = _layer()
    for m in re.finditer(r'<section class="scene" id="(\w+)"', layer):
        кусок = layer[m.end():layer.index("</section>", m.end())]
        окна = []
        for c in re.findall(r'data-cur="([^"]+)"', кусок):
            числа = [float(x) for x in c.split()]
            assert len(числа) == 2, \
                "в сцене %s элемент подсвечен %d раза: %s" % (m.group(1), len(числа) // 2, c)
            окна.append((числа[0], числа[1]))
        окна.sort()
        for i in range(len(окна) - 1):
            a, b = окна[i], окна[i + 1]
            if a == b:
                continue
            assert a[1] <= b[0] + 1e-6, \
                "в сцене %s одновременно горят две подсветки: %s и %s" % (m.group(1), a, b)


def test_nothing_runs_past_the_track():
    for sid, tin, tout, cues in _scenes():
        assert tout <= _LAYER + 0.1, "%s кончается позже слоя" % sid
        for t in cues:
            assert t <= _DURATION + 0.1, "%s: элемент в %.2f — уже после речи" % (sid, t)


def test_elements_match_the_spoken_words():
    """Элемент показывает то, о чём говорят ПРЯМО СЕЙЧАС.

    Проверка «попал внутрь реплики» слабее, чем кажется: с дорожкой от
    другого дубля все элементы аккуратно лежали внутри речи, просто не
    своей. Берём слова самого элемента (корни в пять букв) и ищем их в
    речи вокруг появления.
    """
    ОКНО_ДО, ОКНО_ПОСЛЕ, КОРЕНЬ = 1.0, 2.2, 5
    СИНОНИМЫ = {"ии": "ai", "ии-процессы": "ai-процессы",
                "a/b-тестирование": "a-b", "четыре": "4"}
    КОРОТКИЕ = {"hr", "ai", "api"}
    СТОП = set("""и в на с а не но или для к по от до за из о об у же то это
как что чем чему все всё их его её ещё уже там тут""".split())
    # Кольцо — КАРТА шести этапов, которые названы дальше по ролику
    # («Первый этап — бизнес-анализ» звучит на 33-й секунде). Во
    # вступлении те же шаги названы своими словами («сначала цели»,
    # «создаётся агент», «интегрируется в процессы», «дообучение»), и
    # кружок выходит ровно на своей фразе — но не на своём слове.
    ИТОГ = {"Бизнес-анализ", "Разработка", "Внедрение", "Обучение"}

    def корни(текст):
        из = []
        # дефис РАЗБИВАЕМ: «A/B-тестирование» в кадре и «A-B тестирование»
        # в речи — одно слово, а единым токеном они не совпадали.
        for с in re.findall(r"\w+", текст.lower().replace("/", "-"), re.U):
            с = СИНОНИМЫ.get(с, с)
            if с in СТОП or (len(с) < 3 and с not in КОРОТКИЕ):
                continue
            из.append(с[:КОРЕНЬ])
        return из

    cues, layer = _cues(), _layer()

    def речь(t):
        return " ".join(c[2] for c in cues if c[1] > t - ОКНО_ДО and c[0] < t + ОКНО_ПОСЛЕ)

    пары = []
    for m in re.finditer(
            r'<div class="(?:item|head) el"[^>]*data-in="([\d.]+)"[^>]*>(.*?)'
            r'(?=<div class="(?:item|head) el"|</section>|<div class="chips">)',
            layer, re.S):
        подпись = re.search(r'<p class="(?:label|title)">(.*?)</p>', m.group(2))
        if подпись:
            пары.append((float(m.group(1)), подпись.group(1)))
        доп = re.search(r'<p class="sub el" data-in="([\d.]+)">(.*?)</p>', m.group(2))
        if доп:
            пары.append((float(доп.group(1)), доп.group(2)))
    for вид in ("chip", "core"):
        for m in re.finditer(r'<p class="%s [^"]*"[^>]*data-in="([\d.]+)"[^>]*>(.*?)</p>' % вид, layer):
            пары.append((float(m.group(1)), m.group(2)))

    assert len(пары) >= 45, "элементов подозрительно мало: %d" % len(пары)
    мимо = []
    for t, текст in пары:
        if текст in ИТОГ:
            continue
        сказано = корни(речь(t))
        if not any(к in сказано for к in корни(текст)):
            мимо.append((t, текст, речь(t)[:60]))
    assert not мимо, "элемент выходит не на своих словах:\n" + "\n".join(
        "  %.2f  %s  ← в кадре речь: %s" % x for x in мимо)


def test_scene_changes_are_a_crossfade_in_the_rendered_layer():
    """Владелец: «новая оргструктура, люди-ИИ — там вообще резко убирается
    и появляется „ИИ-агенты“ резко».

    Ломались не тайминги, а покадровый рендер: __renderAt перематывал
    каждый переход на (time − start), а start всегда брался из data-in.
    Для УХОДА это в разы больше длины перехода, и он прыгал в конец —
    графика пропадала за один кадр (замер: альфа 114.8 → 104.3 за 1/30 c).
    На превью не видно: там переходы играют по часам браузера.

    Тест смотрит ГОТОВЫЙ слой, а не страницу, и ищет ОБРЫВ: кадр, который
    изменился рывком, а соседние стоят на месте. У настоящего фейда
    соседние кадры тоже меняются — он размазан по десятку кадров.
    """
    import subprocess
    маска = os.path.join(_DIR, "overlay_a.mp4")
    assert os.path.exists(маска), "нет слоя overlay_a.mp4"
    сырое = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", маска, "-vf",
         "crop=1080:392:0:238,scale=108:39,format=gray", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    кадр = 108 * 39
    n = len(сырое) // кадр
    assert n > 3000, "слой прочитался не целиком: кадров %d" % n
    ряд = [0.0]
    пред = сырое[:кадр]
    for i in range(1, n):
        текущий = сырое[i * кадр:(i + 1) * кадр]
        ряд.append(sum(abs(a - b) for a, b in zip(текущий, пред)) / float(кадр))
        пред = текущий
    обрывы = [(i / 30.0, ряд[i]) for i in range(1, n - 1)
              if ряд[i] > 4 and ряд[i - 1] < 1.5 and ряд[i + 1] < 1.5]
    assert not обрывы, "графика меняется обрывом, а не фейдом: %s" % \
        ", ".join("t=%.2f (на %.1f)" % x for x in обрывы[:6])
    # и сам фейд обязан быть длиной в кадры, а не в один кадр
    подряд, самый = 0, 0
    for d in ряд:
        подряд = подряд + 1 if d > 0.5 else 0
        самый = max(самый, подряд)
    assert самый >= 8, "самый длинный переход всего %d кадров — это рывок" % самый


def test_graphics_never_leave_an_empty_frame():
    """Владелец: «ты просто бросаешь инфографику — надо чтобы она
    оставалась, пока не появляется новая».

    Сцена гаснет за 0.55 c, поэтому зазор даже в полсекунды виден: кадр
    успевает опустеть до одной шапки. В этом ролике таких дыр набиралось
    5.1 c. Конец сцены обязан совпадать с началом следующей."""
    scenes = _scenes()
    for a, b in zip(scenes, scenes[1:]):
        assert b[1] <= a[2] + 0.01, \
            "между %s (кончается %.2f) и %s (начинается %.2f) пустой кадр %.2f c" \
            % (a[0], a[2], b[0], b[1], b[1] - a[2])
    # последняя доживает до конца речи, дальше в слое остаётся одна шапка
    assert abs(scenes[-1][2] - _DURATION) < 0.1, \
        "последняя сцена кончается на %.2f, а дорожка на %.2f" % (scenes[-1][2], _DURATION)


def test_cuts_land_in_a_pause_right_before_a_new_scene():
    """Раньше рез проверялся «на стык сцен» — то есть в дыру между ними.
    Дыр больше нет: графика держится до следующей сцены, и любая секунда
    ролика лежит внутри какой-нибудь сцены. Поэтому требования к резу
    стали прямыми:

      1. рез в ПАУЗЕ дорожки — часть не обрывается на полуслове;
      2. рядом с резом ничего не появляется — иначе элемент разрежется
         пополам между частями;
      3. сразу за резом начинается новая сцена — вторая часть открывается
         сменой кадра, а не серединой чужой мысли.
    """
    scenes, cues = _scenes(), _cues()
    layer = _layer()
    # только ЭЛЕМЕНТЫ: у сцены свой data-in, и он равен резу по замыслу —
    # именно сменой сцены и открывается вторая часть
    появления = sorted(float(x) for x in re.findall(
        r'class="[^"]*\bel\b[^"]*"[^>]*data-in="([\d.]+)"', layer))
    assert появления, "в слое не нашлось элементов с временем появления"
    for рез in _РЕЗЫ:
        в_речи = [c for c in cues if c[0] <= рез <= c[1]]
        assert not в_речи, "рез %.2f попал внутрь реплики %r" % (рез, в_речи[0][2])

        # элемент, вышедший НЕПОСРЕДСТВЕННО перед резом, разрежется пополам:
        # его появление длится полсекунды. Появление сразу ПОСЛЕ реза —
        # наоборот, хорошо: этим открывается вторая часть.
        перед = [t for t in появления if 0 <= рез - t < 0.6]
        assert not перед, "перед резом %.2f появляется элемент (%r) — он разрежется" % (рез, перед)

        следующая = [s for s in scenes if s[1] >= рез]
        assert следующая and следующая[0][1] - рез <= 1.0, \
            "за резом %.2f новая сцена начинается не сразу" % рез


def test_only_the_four_roles_are_big_words():
    """Крупным словом с сиянием и разлётом значков идут только опорные
    блоки ролика — четыре новые роли. Всё остальное кружками с иконками
    (правило восьмого ролика: «остальные будут иконками»)."""
    layer = _layer()
    слова = re.findall(r'<p class="title">(.*?)</p>', layer)
    assert слова == ["Chief AI Officer", "AI Product Engineer",
                     "ИИ-инженеры", "Операторы ИИ-агентов"], \
        "крупным словом идут не четыре роли, а %r" % слова
    # перечисления — кружками с иконками, а не словами
    for sid in ("s11", "s12"):
        начало = layer.index('id="%s"' % sid)
        кусок = layer[начало:layer.index("</section>", начало)]
        assert 'class="cards"' in кусок, "%s перестала быть рядом иконок" % sid
        assert 'class="chip ' not in кусок, "%s снова набрана словами, а не иконками" % sid
        assert кусок.count('class="circle') >= 3, "%s: в ряду меньше трёх иконок" % sid


def test_icon_rows_are_measured_by_their_labels():
    """Ширина колонки ряда — по подписям: иначе они сходятся буква к букве."""
    html, ш = _html(), _шрифт()
    кегль = int(re.search(r"\.cards \.label\{font-size:(\d+)px", html).group(1))
    зазор = int(re.search(r"\.cards \.row\{gap:(\d+)px", html).group(1))
    layer = _layer()
    for m in re.finditer(r"#(s\d+) \.cards \.item\{flex:0 0 (\d+)px\}", html):
        sid, ширина = m.group(1), int(m.group(2))
        начало = layer.index('id="%s"' % sid)
        кусок = layer[начало:layer.index("</section>", начало)]
        подписи = re.findall(r'<p class="label">(.*?)</p>', кусок)
        шаг = ширина + зазор
        for a, b in zip(подписи, подписи[1:]):
            зазор_букв = шаг - (ш.ширина(a, кегль) + ш.ширина(b, кегль)) / 2.0
            assert зазор_букв >= 20, \
                "%s: «%s» и «%s» сходятся (зазор %.0f)" % (sid, a, b, зазор_букв)
        поле = 540 - шаг * (len(подписи) - 1) / 2.0 - max(
            ш.ширина(п, кегль) for п in (подписи[0], подписи[-1])) / 2.0
        assert поле >= 55, "%s: ряд подходит к краю кадра (поле %.0f)" % (sid, поле)


def test_blocks_are_a_word_with_a_glow_and_flying_icons():
    """Владелец: «только заголовки, без иконок, а оранжевым / фиолетовым
    сзади свечением и эмодзи слева справа»."""
    layer, html = _layer(), _html()
    блоки = re.findall(r'<div class="block">(.*?)</div>\s*</section>', layer, re.S)
    assert len(блоки) == _BLOCKS, "блоков должно быть %d, а их %d" % (_BLOCKS, len(блоки))
    for б in блоки:
        голова = б[:б.index('class="chips"')]
        assert 'class="title"' in б, "у блока нет заголовка-слова"
        assert 'class="circle' not in голова, "у заголовка снова круг с иконкой"
        assert 'class="glow' in голова, "за заголовком нет сияния"
        assert голова.count('class="fly') == 2, "значки вылетают не с обеих сторон"
        assert 'class="circle' not in б, "у подсказок появились кружки"
    assert "flyOut" in html, "нет анимации разлёта значков"
    assert ".block .chip.on.cur{transform:scale(" in html, \
        "подсказка не подрастает, когда о ней говорят"
    assert "opacity:.4" not in html and "data-dim=" not in html, \
        "вернулось затухание соседей — владелец его запретил"


def test_every_fan_has_four_icons():
    """Владелец про уровни внедрения: «эмодзи добавь вылетающие».
    Веер стал по четыре значка на сторону вместо трёх."""
    веера = re.findall(r'<span class="fly [^"]+"[^>]*>(.*?)</span>', _layer(), re.S)
    assert веера, "веера значков пропали"
    for в in веера:
        assert в.count("<i ") == 4, "в веере %d значков вместо четырёх" % в.count("<i ")


def test_title_fits_the_frame():
    """Кегль заголовка проверяем метриками шрифта, а не на глаз."""
    ш, кегль = _шрифт(), _кегль_заголовка()
    for заголовок in re.findall(r'<p class="title">(.*?)</p>', _layer()):
        w = ш.ширина(заголовок.replace("&amp;", "&"), кегль)
        assert w <= 940, "заголовок %r занимает %.0fpx — не влезает" % (заголовок, w)


def test_flying_icons_stay_in_frame():
    """У широкого заголовка сбоку места нет, и значки улетали за кадр:
    отступ вбок не больше свободного места, сколько бы его ни было."""
    ш, кегль = _шрифт(), _кегль_заголовка()
    for блок in _головы():
        заголовок = re.search(r'<p class="title">(.*?)</p>', блок).group(1)
        запас = (1080 - ш.ширина(заголовок.replace("&amp;", "&"), кегль)) / 2.0 - 56
        for dx in [abs(int(x)) for x in re.findall(r"--dx:(-?\d+)px", блок)]:
            assert dx <= max(запас, 0) + 1, \
                "значок у %r улетает на %dpx при запасе %.0f" % (заголовок, dx, запас)


def test_upward_fan_stays_under_the_header():
    """Веер вверх не должен залезать под шапку: у блока без подсказок
    заголовок стоит выше, и подъём 144 уводил значок в зону шапки."""
    for блок in _головы():
        for dy in [int(x) for x in re.findall(r"--dy:(-?\d+)px", блок)]:
            assert dy >= -122, "значок поднимается на %d — залезет под шапку" % dy


def test_chip_rows_fit_the_band():
    """Ряды подсказок набираются по ШИРИНЕ строки, а не по счёту слов:
    три длинных слова в кадр не влезают, четыре коротких — влезают."""
    ш = _шрифт()
    кегль = int(re.search(r"\.block \.chip\{\s*font-size:(\d+)px", _html()).group(1))
    зазор = int(re.search(r"\.block \.line\{[^}]*gap:(\d+)px", _html()).group(1))
    for блок in re.findall(r'<div class="chips">(.*?)\n                </div>', _layer(), re.S):
        ряды = re.findall(r'<div class="line">(.*?)</div>', блок, re.S)
        assert len(ряды) <= 2, "подсказки разложены в %d ряда" % len(ряды)
        for р in ряды:
            слова = re.findall(r'<p class="chip [^"]+"[^>]*>(.*?)</p>', р)
            ширина = sum(ш.ширина(с, кегль) for с in слова) + зазор * (len(слова) - 1)
            assert ширина <= _ПОЛОСА_ЧИПОВ + 1, \
                "ряд подсказок %r занимает %.0fpx при полосе %d" % (слова, ширина, _ПОЛОСА_ЧИПОВ)


def test_flying_icons_last_a_few_seconds():
    """Владелец: «все эмодзи вылетающие сделай 3-4 секунды». Один проход
    анимации, а не бесконечный цикл."""
    html = _html()
    m = re.search(r"\.scene\.on \.fly\.on i\{animation:flyOut ([\d.]+)s [^}]*\}", html)
    assert m, "не нашёл анимацию разлёта значков"
    assert "infinite" not in m.group(0), "значки летят весь блок, а не 3–4 секунды"
    длительность = float(m.group(1))
    задержки = sorted(float(x) for x in re.findall(r"animation-delay:([\d.]+)s", _layer()))
    assert длительность + задержки[-1] <= 4.2, \
        "разлёт тянется %.1f c" % (длительность + задержки[-1])


def test_glow_is_sized_to_the_word():
    """Владелец: «слишком большое свечение относительно текста».
    Ширина облака считается по ширине заголовка."""
    ш, кегль = _шрифт(), _кегль_заголовка()
    for блок in _головы():
        сияние = re.search(r'class="glow[^"]*" style="width:(\d+)px"', блок)
        assert сияние, "у заголовка нет облака заданной ширины"
        заголовок = re.search(r'<p class="title">(.*?)</p>', блок).group(1)
        w = ш.ширина(заголовок.replace("&amp;", "&"), кегль)
        assert abs(int(сияние.group(1)) - max(520, min(900, w + 280))) <= 1, \
            "облако у %r не по размеру слова" % заголовок


# ── FR-SITE42: сетки, пары и трио ────────────────────────────────────────

def test_no_ring_left_from_the_previous_lecture():
    """Кольцо цикла было главным кадром восьмого ролика. Здесь его нет —
    и не должно остаться ни разметкой, ни мёртвым CSS в странице."""
    layer = _layer()
    assert 'class="cycle"' not in layer, "в разметке осталось кольцо прошлой лекции"


def test_pairs_have_the_arrows_the_owner_asked_for():
    """Правило восьмого ролика: середина пары — стрелка или «VS».
    Здесь стрелка ведёт от потока данных к интеллекту, а «VS»
    противопоставляет инструмент изменению и пользователя — тому, кто
    встроил ИИ в ядро."""
    layer = _layer()
    со_стрелкой = {"s9": "vs", "s10": "arrow", "s13": "vs"}
    for sid, вид in со_стрелкой.items():
        начало = layer.index('id="%s"' % sid)
        кусок = layer[начало:layer.index("</section>", начало)]
        assert 'class="%s el"' % вид in кусок, "в %s пропала середина пары (%s)" % (sid, вид)
        # середина стоит МЕЖДУ элементами, а не сбоку
        левый = кусок.index('class="item el"')
        правый = кусок.rindex('class="item el"')
        середина = кусок.index('class="%s el"' % вид)
        assert левый < середина < правый, "%s: середина пары стоит не между кружками" % sid
    assert layer.count('class="vs el"') == 2, "«VS» должно быть два"


def test_paired_scenes_stand_over_the_paintings():
    """Два элемента в кадре разведены над картинами, между ними голова."""
    html = _html()
    assert ".scene .row.duo{justify-content:space-between" in html, \
        "пара перестала расходиться по краям"
    ш = _шрифт()
    # Кегль подписи в паре бывает свой у сцены: пары, собранные рядом из
    # двух, берут его от ряда иконок, и длинным подписям он задан по
    # замеру. Берём переопределение сцены, иначе общий.
    общий = int(re.search(r"^\.duo \.label\{font-size:(\d+)px", html, re.M).group(1))
    свои = {sid: int(k) for sid, k in
            re.findall(r"#(s\d+) \.duo \.label\{font-size:(\d+)px", html)}
    layer = _layer()
    # Кусок берём ОТ ТЕГА СЦЕНЫ: id нужен, чтобы понять, разрешён ли в
    # этой паре перенос подписи (иначе id остаётся выше среза).
    пары = [layer[layer.rindex('<section class="scene"', 0, m.start()):
                  layer.index("</section>", m.start())]
            for m in re.finditer(r'<div class="row duo">', layer)]
    assert пары, "парных сцен не осталось"
    # Владелец разрешил перенос в паре «Универсальный инструмент →
    # Инструмент под компанию»: там подпись меряется по самому длинному
    # СЛОВУ, а не по всей строке — строка честно идёт в две.
    переносят = set(re.findall(r"#(s\d+) \.duo \.label\{white-space:normal", html))
    for кусок in пары:
        sid = re.search(r'id="(s\d+)"', кусок)
        кегль = свои.get(sid.group(1) if sid else "", общий)
        подписи = re.findall(r'<p class="label">(.*?)</p>', кусок)
        assert len(подписи) == 2, "в паре не два элемента: %r" % подписи
        for центр, текст in zip((_ART_L + 11, _ART_R + 14), подписи):
            куски = текст.split() if (sid and sid.group(1) in переносят) else [текст]
            ширина = max(ш.ширина(к, кегль) for к in куски)
            поле = центр - ширина / 2.0
            assert поле >= 60, "подпись %r подходит к краю кадра (поле %.0f)" % (текст, поле)


def test_graphics_stay_off_the_posters():
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    high = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top >= 238, "зона графики залезает под шапку (top %d)" % top
    assert top + high <= 638, "зона графики доходит до картин (низ %d)" % (top + high)


def test_only_the_names_keep_latin_ai():
    """Правило владельца: в кадре «ИИ», а не «AI». Латиницей остаются
    только имена собственные — уровень зрелости «AI-first» и названия
    должностей, которые так и звучат в речи."""
    layer = _layer()
    тексты = re.findall(r"<p class=\"(?:title|label|core|chip|sub)[^\"]*\"[^>]*>(.*?)</p>",
                        layer, re.S)
    ИМЕНА = {"AI-first модель", "AI-first компания",
             "Chief AI Officer", "AI Product Engineer"}
    осталось = [т for т in тексты if re.search(r"\bAI\b|AI-", т) and т not in ИМЕНА]
    assert not осталось, "в кадре осталось латинское AI: %r" % осталось


def test_no_dead_css_from_previous_lectures():
    """Страница собрана из прошлой: чужие правила не должны прилипать к
    сценам с теми же номерами."""
    html = _html()
    assert "#s8 .steps" not in html, "остался CSS дорожной карты шестого ролика"
    assert ".grid4" not in html, "осталась сетка 2×2 седьмого ролика"
    assert "#s18 .item" not in html, "осталась колонка трио седьмого ролика"
    assert ".trio " not in html, "остался CSS рядов-трио"


# ── FR-SITE37: субтитры ──────────────────────────────────────────────────

def test_subs_do_not_overlap():
    cues = _cues()
    assert len(cues) >= 70, "реплик подозрительно мало: %d" % len(cues)
    for i, (a, b, t) in enumerate(cues):
        assert a < b, "вывернутая реплика: %r" % t
        if i + 1 < len(cues):
            assert b <= cues[i + 1][0] + 1e-6, \
                "реплики наслаиваются: %r кончается %.3f, а %r начинается %.3f" % (
                    t, b, cues[i + 1][2], cues[i + 1][0])


def test_no_cue_wraps_to_a_second_line():
    ш = _шрифт()
    for _, _, text in _cues():
        w = ш.ширина(text, _KEGL)
        assert w <= _BAND, "реплика %.0fpx при полосе %dpx — уедет на вторую строку: %r" % (
            w, _BAND, text)


def test_subs_follow_the_script():
    cues, words = _cues(), 0
    for a, b, text in cues:
        assert "TurboScribe" not in text, "водяной знак распознавалки в кадре"
        n = len(text.split())
        assert 1 <= n <= 4, "в реплике %d слов (можно 1–4): %r" % (n, text)
        words += n
        assert b <= _DURATION + 0.1, "реплика выходит за длину ролика: %r" % text
        assert b - a >= 0.28, "реплика мелькает %.2f c: %r" % (b - a, text)
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_recognition_mistakes_are_fixed():
    """Распознавалка рвёт слова по дефису, теряет ё и путает
    согласование. Времена у неё честные, слова берём по сценарию."""
    поток = " ".join(t for _, _, t in _cues())
    assert "TurboScribe" not in поток, "водяной знак распознавалки остался"
    # слово, разорванное по дефису на две реплики
    for склейка in ("AI-first", "AI-инженеры", "AI-агентов", "бизнес-процессы"):
        assert склейка in поток, "«%s» не склеено" % склейка
    # потерянная ё
    assert "берёт" in поток, "потеряна ё в «берёт»"
    assert "задаёт" in поток, "потеряна ё в «задаёт»"
    # проглоченная приставка и согласование — слова из сценария
    # фраза разорвана между репликами — правим тот кусок, где слово лежит
    assert "встроить AI в" in поток, "«строить AI в» не поправлено"
    assert "компаниями, которые" in поток, "«компаниями, которая» не поправлено"
    assert "научатся видеть" in поток, "«научится видеть» не поправлено"
    assert "усиленным интеллектом" in поток, "«усиленный интеллектом» не поправлено"


def test_subtitles_live_in_one_editable_file():
    assert os.path.exists(_SRT), "нет файла субтитров"
    assert "субтитры.srt" in _html(), "страница не читает слова из файла"
    assert "субтитры.srt" in _script(), "сборка вжигает не тот файл, который правит владелец"


def test_fallback_subs_layer_matches_the_srt():
    import hashlib
    sha = os.path.join(_DIR, "субтитры.sha")
    assert os.path.exists(sha), "нет хэша текста субтитров"
    want = open(sha, encoding="utf-8").read().strip()
    got = hashlib.sha256(open(_SRT, "rb").read()).hexdigest()
    assert got == want, \
        "субтитры.srt правился, а слой subs_c/subs_a не перерендерен — сборка без libass соберёт старые слова"
    assert "only-subs" in _html(), "нет режима ?only=subs — слой субтитров нечем рендерить"


def test_burned_subtitles_are_the_same_size_as_the_preview():
    поправка = 1.0 / _шрифт().коэффициент_libass()
    assert abs(поправка - 1.562) < 0.01, "поправка шрифта изменилась: %.3f" % поправка
    body = _script()
    assert "h*0.026" in body, "кегль субтитров больше не считается от высоты кадра как на странице"
    assert "k*1.562" in body, "кегль не умножается на поправку libass"
    assert "h*0.028" not in body, "остался прежний кегль: в кадре он даёт 34px вместо 50"


# ── FR-SITE42: слои и сборка ─────────────────────────────────────────────

def test_layers_are_here_and_long_enough():
    for f in ("overlay_c.mp4", "overlay_a.mp4", "subs_c.mp4", "subs_a.mp4"):
        p = os.path.join(_DIR, f)
        assert os.path.exists(p), "нет слоя %s" % f
        assert os.path.getsize(p) > 100000, "слой %s подозрительно мал" % f
    assert "var DURATION = %s" % _LAYER in _html(), \
        "длина ролика на странице разошлась со слоем"
    # и сами файлы слоя должны быть ровно этой длины
    import subprocess
    for f in ("overlay_c.mp4", "subs_c.mp4"):
        сек = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "format=duration", "-of", "csv=p=0",
                              os.path.join(_DIR, f)],
                             capture_output=True, text=True).stdout.strip()
        assert сек and abs(float(сек) - _LAYER) < 0.1, \
            "%s длится %s c, а слой должен быть %s" % (f, сек, _LAYER)


def test_three_part_covers_are_ready():
    """Обложка на весь ролик и по одной на каждую часть, с подписью
    «Часть N» — скрипт нарезки видит их и вторую подпись не рисует."""
    assert os.path.exists(os.path.join(_DIR, "cover.png")), "нет общей обложки"
    # обложки частей — jpg: три png весили 5.4 МБ, а ZIP владельцу должен
    # оставаться лёгким. Скрипт нарезки берёт и png, и jpg.
    for n in range(1, len(_РЕЗЫ) + 2):
        assert os.path.exists(os.path.join(_DIR, "cover%d.jpg" % n)), \
            "нет обложки части %d" % n
    лишняя = os.path.join(_DIR, "cover%d.jpg" % (len(_РЕЗЫ) + 2))
    assert not os.path.exists(лишняя), "обложек частей больше, чем частей"


def test_header_is_in_the_layer_from_the_first_frame():
    """Владелец: «лого слева и академия датаиста должно быть с первой доли
    секунды видео после обложки»."""
    html = _html()
    assert "body.on-cover #chrome" in html.replace("\n", ""), "шапка не привязана к обложке"
    assert re.search(r"#chrome\{[^}]*position:absolute", html), "шапки нет в кадре"
    assert "opacity:0" not in re.search(r"#chrome\{[^}]*\}", html).group(0), \
        "шапка появляется не сразу"


def test_build_and_cut_scripts_are_here():
    for f in ["собрать.sh", "нарезать.sh", "Нарезать на части.command", "Запустить.command"]:
        assert os.path.exists(os.path.join(_DIR, f)), "нет файла %s" % f


def test_script_burns_the_layer_and_the_subtitles():
    body = _script()
    assert "alphamerge" in body, "слой не сшивается из цвета и маски"
    assert "eof_action=pass" in body, "слой обрежет ролик, который длиннее его"
    assert "tpad=stop=-1:stop_mode=clone" in body, "шапка пропадёт на длинном дубле"
    assert "subtitles=filename=" in body, "субтитры не вжигаются явным ключом"
    assert '-r "$FPS"' in body, "нет явного -r: после concat ffmpeg молча пишет 25 к/с"
    assert "-c:a copy" in body, "звук пережимается"


def test_second_build_is_refused():
    body = _script()
    assert "*-готовый.mp4" in body, "нет защиты от повторной сборки"
    assert "Возьмите ИСХОДНЫЙ дубль" in body, "скрипт не объясняет, что делать"


def test_folder_script_matches_the_page():
    файл = open(os.path.join(_DIR, "собрать.sh"), encoding="utf-8").read()
    body = _script()
    for строка in ("KEGL=$(awk", "alphamerge", "*-готовый.mp4", "субтитры.sha"):
        assert строка in файл, "в собрать.sh нет куска %r" % строка
        assert строка in body, "в скрипте со страницы нет куска %r" % строка


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Exception as e:
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    raise SystemExit(1 if failed else 0)
