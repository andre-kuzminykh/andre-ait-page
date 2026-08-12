# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «ИИ-индекс зрелости» — слайды 22–30
(FR-SITE40). Без зависимостей — запускается и как
`python3 tests/test_index_overlay.py`, и через pytest.

Седьмой ролик по тем же постоянным правилам. Новое здесь — блок без
круга с иконкой: в кадре одно слово, за ним сияние, из-за краёв слова
разлетаются значки, а подсказки под ним — просто слова. Проверяем то,
что ломается молча: внешние зависимости, досочинённые слова, разъезд
элементов с речью, перенос субтитров на две строки и разрыв связи
«страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-index")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 174.2          # 02:54 — длина дорожки
_LAYER = 176.0             # слой длиннее: хвост держит шапку
_WORDS = 395               # столько слов в озвучке
_SCENES = 13
_KEGL = 50                 # кегль субтитров на кадре 1080×1920
_BAND = 940                # полоса под строку: #sub left:70px right:70px
_FONT = os.path.join(_DIR, "fonts", "Montserrat-Black.ttf")
# Центры картин на стене: над ними встают парные элементы, между ними
# остаётся голова. Взяты из мок-фона страницы, он повторяет кадр съёмки.
_ART_L, _ART_R = 235, 820


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


# ── FR-SITE40: страница самодостаточна ───────────────────────────────────

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


# ── FR-SITE40: тайминги сведены с речью ──────────────────────────────────

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


# ── FR-SITE40: блок без иконки ───────────────────────────────────────────

def test_blocks_are_a_word_with_a_glow_and_flying_icons():
    """Владелец: «только заголовки — Данные / Модели и т.д., без иконок, а
    оранжевым / фиолетовым сзади свечением и эмодзи слева справа»."""
    layer, html = _layer(), _html()
    блоки = re.findall(r'<div class="block">(.*?)</div>\s*</section>', layer, re.S)
    assert len(блоки) == 7, "измерений индекса должно быть семь, а их %d" % len(блоки)
    for б in блоки:
        # шапка блока — всё до ряда подсказок: правый разлёт значков
        # стоит ПОСЛЕ заголовка, и обрезка по первому </p> его теряла
        голова = б[:б.index('class="chips"')]
        assert 'class="title"' in б, "у блока нет заголовка-слова"
        assert 'class="circle' not in голова, "у заголовка снова круг с иконкой"
        assert 'class="glow' in голова, "за заголовком нет сияния"
        assert 'class="fly' in голова and голова.count('class="fly') == 2, \
            "значки вылетают не с обеих сторон"
        assert 'class="chip' in б, "под заголовком нет подсказок"
        assert 'class="circle' not in б, "у подсказок остались кружки"
    assert "flyOut" in html, "нет анимации разлёта значков"
    assert ".block .chip.on.cur{transform:scale(" in html, \
        "подсказка не подрастает, когда о ней говорят"
    assert "opacity:.4" not in html and "data-dim=" not in html, \
        "вернулось затухание соседей — владелец его запретил"


def test_title_fits_the_frame():
    """Кегль 54 выбран замером: «Исследования и разработки» на 64 занимают
    1029px при кадре 988. Меряем каждый заголовок по метрикам шрифта."""
    ш = _шрифт()
    кегль = int(re.search(r"\.block \.title\{\s*font-size:(\d+)px", _html()).group(1))
    for заголовок in re.findall(r'<p class="title">(.*?)</p>', _layer()):
        w = ш.ширина(заголовок.replace("&amp;", "&"), кегль)
        assert w <= 940, "заголовок %r занимает %.0fpx — не влезает" % (заголовок, w)


def test_flying_icons_stay_in_frame():
    """У широкого заголовка сбоку места нет, и значки улетали за кадр:
    сборщик обязан развернуть их вверх, а не вбок."""
    ш = _шрифт()
    кегль = int(re.search(r"\.block \.title\{\s*font-size:(\d+)px", _html()).group(1))
    layer = _layer()
    for блок in re.findall(r'<div class="head el".*?</div>\n', layer, re.S):
        заголовок = re.search(r'<p class="title">(.*?)</p>', блок).group(1)
        запас = (1080 - ш.ширина(заголовок.replace("&amp;", "&"), кегль)) / 2.0 - 56
        for dx in [abs(int(x)) for x in re.findall(r"--dx:(-?\d+)px", блок)]:
            assert dx <= max(запас, 80) + 1, \
                "значок у %r улетает на %dpx при запасе %.0f" % (заголовок, dx, запас)


def test_seven_blocks_are_a_grid():
    """Семь подписей в один ряд не влезают — 4 сверху и 3 снизу."""
    html, layer = _html(), _layer()
    assert 'class="grid7"' in layer, "обзор семи блоков перестал быть сеткой"
    assert layer.count('class="grid7"') == 2, "сетка должна быть и в обзоре, и в профиле"
    for сетка in re.findall(r'<div class="grid7">(.*?)\n            </div>', layer, re.S):
        верх, низ = сетка.split('<div class="row bottom">')
        assert верх.count('class="item el"') == 4, "в верхнем ряду не четыре блока"
        assert низ.count('class="item el"') == 3, "в нижнем ряду не три блока"


def test_pilots_are_the_only_dim_frame():
    html = _html()
    assert "#s2 .item .circle{filter:saturate(" in html, "пилоты перестали быть приглушёнными"
    assert html.count("filter:saturate(") == 1, "приглушён не один кадр ролика"


def test_graphics_stay_off_the_posters():
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    high = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top >= 238, "зона графики залезает под шапку (top %d)" % top
    assert top + high <= 638, "зона графики доходит до картин (низ %d)" % (top + high)


def test_only_the_ai_first_keeps_latin_ai():
    """Владелец: «вместо AI должно быть ИИ»."""
    остатки = [t.strip() for t in re.findall(r">([^<>]*\bAI\b[^<>]*)<", _layer())]
    лишние = [t for t in остатки if t not in ("AI-first",)]
    assert not лишние, "в кадре осталось латинское AI: %r" % лишние


def test_roadmap_has_three_steps_and_an_arrow():
    layer = _layer()
    начало = layer.index('id="s13"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert кусок.count('class="item el"') == 3, "в дорожной карте не три шага"
    assert "<polygon" in кусок, "у дорожной карты пропала стрелка"


# ── FR-SITE37: субтитры ──────────────────────────────────────────────────

def test_subs_do_not_overlap():
    cues = _cues()
    assert len(cues) >= 120, "реплик подозрительно мало: %d" % len(cues)
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
    поток = " ".join(t for _, _, t in _cues())
    assert "AI-индекс" in поток, "слово, разорванное по дефису, не склеено"
    assert "бизнес-результатами" in поток, "«бизнес» и «-результатами» не склеены"
    assert "AI-агентов" in поток, "«AI» и «-агентов» не склеены"
    assert "вовлечённость" in поток, "потеряна ё в «вовлечённость»"
    assert "Четвёртый" in поток, "потеряна ё в «Четвёртый»"
    assert "остаётся" in поток, "потеряна ё в «остаётся»"


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


# ── FR-SITE40: слои и сборка ─────────────────────────────────────────────

def test_layers_are_here_and_long_enough():
    for f in ("overlay_c.mp4", "overlay_a.mp4", "subs_c.mp4", "subs_a.mp4"):
        p = os.path.join(_DIR, f)
        assert os.path.exists(p), "нет слоя %s" % f
        assert os.path.getsize(p) > 100000, "слой %s подозрительно мал" % f
    assert "var DURATION = 176.0" in _html(), "длина ролика на странице разошлась со слоем"


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
