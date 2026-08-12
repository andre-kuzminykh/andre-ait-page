# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «Три трансформации бизнеса» — слайды 17–21
(FR-SITE39). Без зависимостей — запускается и как
`python3 tests/test_transform_overlay.py`, и через pytest.

Шестой ролик по тем же постоянным правилам. Новое здесь — пирамида
«решения наверху, задачи вниз», матрица кросс-функциональных команд с
током по связям, переходы со стрелкой и три уровня зрелости в один ряд.
Проверяем то, что ломается молча: внешние зависимости, досочинённые
слова, разъезд элементов с речью, перенос субтитров на две строки и
разрыв связи «страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-transform")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 179.7          # 02:59 — длина дорожки
_LAYER = 181.0             # слой длиннее: хвост держит шапку
_WORDS = 373               # столько слов в озвучке
_SCENES = 15
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


# ── FR-SITE39: страница самодостаточна ───────────────────────────────────

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


# ── FR-SITE39: тайминги сведены с речью ──────────────────────────────────

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
            continue            # начало сцены — не элемент, она проявляется заранее
        v = float(t)
        if not any(a - 0.35 <= v < b + 0.35 for a, b, _ in cues):
            немой.append(v)
    assert not немой, "элементы выходят в тишине между репликами: %s" % немой


def test_every_ring_lands_on_a_spoken_cue():
    """Владелец: «выделяй, когда говоришь про тот или иной объект»."""
    cues, немой = _cues(), []
    for m in re.finditer(r'data-cur="([^"]+)"', _layer()):
        числа = [float(x) for x in m.group(1).split()]
        assert len(числа) % 2 == 0, "окна подсветки идут парами: %r" % m.group(1)
        for i in range(0, len(числа), 2):
            a, b = числа[i], числа[i + 1]
            assert a < b, "вывернутое окно подсветки %.2f–%.2f" % (a, b)
            if not any(x < b and y > a for x, y, _ in cues):
                немой.append((a, b))
    assert not немой, "кольцо горит в тишине: %s" % немой


def test_nothing_runs_past_the_track():
    for sid, tin, tout, cues in _scenes():
        assert tout <= _LAYER + 0.1, "%s кончается позже слоя" % sid
        for t in cues:
            assert t <= _DURATION + 0.1, "%s: элемент в %.2f — уже после речи" % (sid, t)


# ── FR-SITE39: правила подачи ────────────────────────────────────────────

def test_no_rectangles_and_no_headings():
    html = _html()
    layer = _layer()
    assert "border-radius:50%" in html, "круги перестали быть кругами"
    assert "<h1" not in layer and "<h2" not in layer, "в кадр попал заголовок"
    assert "&shy;" not in html, "остался мягкий перенос"


def test_circles_in_a_scene_are_the_same_size():
    """Иерархию несёт выделение, а не диаметр (правило владельца)."""
    for m in re.finditer(r'<section class="scene" id="(\w+)"', _html()):
        html = _html()
        end = html.index("</section>", m.end())
        кусок = html[m.end():end]
        размеры = set(re.findall(r"width:(\d+)px;height:\1px", кусок))
        assert len(размеры) <= 1, \
            "в сцене %s круги разного размера: %s" % (m.group(1), sorted(размеры))


def test_neighbours_never_dim():
    html = _html()
    assert "data-dim=" not in html, "вернулось затухание соседей — владелец его запретил"
    assert ".el.on.cur .circle{transform:scale(" in html, "выделение не увеличивает круг"


def test_graphics_stay_off_the_posters():
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    high = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top >= 238, "зона графики залезает под шапку (top %d)" % top
    assert top + high <= 638, "зона графики доходит до картин (низ %d)" % (top + high)


def test_only_the_maturity_levels_keep_latin_ai():
    """Владелец: «вместо AI должно быть ИИ». Латиницей остались только
    названия уровней — он сам их так назвал, и на слайде они такие же."""
    остатки = [t.strip() for t in re.findall(r">([^<>]*\bAI\b[^<>]*)<", _layer())]
    лишние = [t for t in остатки if t not in ("AI-Driven", "AI-First", "AI-Native")]
    assert not лишние, "в кадре осталось латинское AI: %r" % лишние


def test_tasks_are_numbered_and_come_one_by_one():
    """Владелец: «где задачи там Задача 1 / Задача 2, по очереди появляются»."""
    layer = _layer()
    начало = layer.index('id="s2"')
    кусок = layer[начало:layer.index("</section>", начало)]
    времена = []
    for блок in кусок.split('<div class="item el"')[1:]:
        m = re.search(r'Задача (\d)', блок)
        if not m:
            continue
        времена.append((int(m.group(1)), float(re.search(r'data-in="([\d.]+)"', блок).group(1))))
    assert [n for n, _ in времена] == [1, 2, 3], "задачи подписаны не по порядку: %s" % времена
    времена = [t for _, t in времена]
    assert времена == sorted(времена) and len(set(времена)) == 3, \
        "задачи выходят не по очереди: %s" % времена


def test_links_carry_current():
    """Владелец: «по ним идёт кружком типа ток» — и в матрице, и в пирамиде."""
    html, layer = _html(), _layer()
    assert "runPulse" in html, "нет анимации тока по связям"
    for сцена in ("s2", "s3"):
        начало = layer.index('id="%s"' % сцена)
        кусок = layer[начало:layer.index("</section>", начало)]
        assert 'class="pulse"' in кусок, "в сцене %s по связям не бежит ток" % сцена


def test_matrix_is_linked_diagonally():
    """Владелец: «они ещё по диагонали соединяются»."""
    layer = _layer()
    начало = layer.index('id="s3"')
    кусок = layer[начало:layer.index("</section>", начало)]
    линии = re.findall(r'<line x1="(\d+)" y1="(\d+)" x2="(\d+)" y2="(\d+)"', кусок)
    диагонали = [l for l in линии if l[0] != l[2] and l[1] != l[3]]
    assert len(диагонали) >= 4, "диагоналей в матрице всего %d" % len(диагонали)


def test_each_element_is_highlighted_once():
    """Владелец: «зачем ты по нескольку раз выделяешь кружками + где-то ты
    выделил кружками и цифру, и ИИ». Значит у элемента ровно одно окно
    подсветки, и в один момент горит один круг — кроме случая, когда
    группа загорается целиком (тогда окна совпадают в точности)."""
    for m in re.finditer(r'<section class="scene" id="(\w+)"', _layer()):
        layer = _layer()
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
                continue        # группа загорается разом — так и задумано
            assert a[1] <= b[0] + 1e-6, \
                "в сцене %s одновременно горят два кольца: %s и %s" % (m.group(1), a, b)


def test_tasks_have_no_rings():
    """Владелец: «задачи не выделяй кружками отдельно»."""
    layer = _layer()
    начало = layer.index('id="s2"')
    кусок = layer[начало:layer.index("</section>", начало)]
    задачи = [б for б in кусок.split('<div class="item el"')[1:] if "Задача" in б]
    assert len(задачи) == 3, "задач должно быть три"
    for б in задачи:
        assert "data-cur" not in б.split("</div>")[0], "у задачи осталось кольцо"


def test_intuition_is_crossed_out():
    """Владелец: «интуицию перечеркни анимацией красиво»."""
    html, layer = _html(), _layer()
    начало = layer.index('id="s9"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert 'class="strike el"' in кусок, "интуиция не перечёркнута"
    assert "drawStrike" in html, "перечёркивание не анимировано"
    полоса = кусок[кусок.index('class="strike el"'):]
    assert "<line" in полоса, "перечёркивание нарисовано не линией"


def test_human_glows_like_the_limit():
    """Владелец: «человек — выдели фиолетовым, как ограничение оранжевым»."""
    layer = _layer()
    начало = layer.index('id="s10"')
    кусок = layer[начало:layer.index("</section>", начало)]
    куски = кусок.split('<div class="item el"')
    человек = [б for б in куски if "Человек" in б][0]
    предел = [б for б in куски if "Ограничение" in б][0]
    assert 'class="glow ' in человек and "glow-ember" not in человек.split("</div>")[0], \
        "у «Человека» нет фиолетового сияния"
    assert "glow-ember" in предел, "у «Ограничения» пропало оранжевое сияние"


def test_limit_has_no_glow_at_all():
    """Владелец: «предел цифровой модели — там оранжевое свечение улетает
    вверх, убери его вообще». Ни облака, ни анимации всплытия."""
    html, layer = _html(), _layer()
    начало = layer.index('id="s12"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert 'class="glow' not in кусок, "у «предела цифровой модели» осталось свечение"
    assert "glowRise" not in html, "осталась мёртвая анимация всплывающего свечения"


def test_matrix_circles_have_no_rings():
    """Владелец: «где кросс-функциональные команды — не выделяй кружками
    отдельно». Матрица работает связями и током, а не подсветкой."""
    layer = _layer()
    начало = layer.index('id="s3"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert "data-cur" not in кусок, "в матрице остались кольца подсветки"


def test_driven_pair_has_gradients_and_flying_icons():
    """Владелец: «снизу ничего не подписывай, просто оранж и фиолетовое
    сзади сделай градиенты + эмодзи вылетающие»."""
    layer = _layer()
    начало = layer.index('id="s13"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert 'class="sub' not in кусок, "под data/intelligence остались подписи"
    assert кусок.count('class="glow ') == 2, "нет градиентов за обоими кругами"
    assert 'class="fly ember el"' in кусок and 'class="fly solar el"' in кусок, \
        "не вылетают значки"
    цифры = re.findall(r'<b style="[^"]*">(\d)</b>', кусок)
    assert len(цифры) >= 5, "у data-driven не вылетают цифры"


def test_finale_has_robots_and_lightning():
    """Владелец: «использует ИИ — снизу вылетают роботы и фиолетовое
    свечение; существует благодаря ИИ — оранж сзади и вылетают молнии»."""
    layer = _layer()
    начало = layer.index('id="s15"')
    кусок = layer[начало:layer.index("</section>", начало)]
    куски = кусок.split('<div class="item el"')
    использует = [б for б in куски if "Использует" in б][0]
    существует = [б for б in куски if "Существует" in б][0]
    assert 'class="fly solar el"' in использует, "роботы не вылетают"
    assert 'class="fly ember el"' in существует, "молнии не вылетают"
    assert "glow-ember" in существует, "нет оранжевого сзади"


def test_maturity_levels_are_in_one_row_without_a_line():
    """Владелец: «AI Driven / AI First и AI Native на одной линии без полоски»."""
    layer = _layer()
    начало = layer.index('id="s14"')
    кусок = layer[начало:layer.index("</section>", начало)]
    assert "polyline" not in кусок, "вернулась соединяющая полоска у уровней зрелости"
    assert 'class="steps"' not in кусок, "уровни снова стоят ступенями"
    assert кусок.count('class="item el"') == 3, "уровней зрелости должно быть три"


def test_pairs_stand_over_the_posters():
    """Владелец: «где два элемента — чуть подальше друг от друга, чтобы по
    середине над картинами были». Ширина колонки задана явно, чтобы центры
    кругов встали над картинами, а середина осталась пустой."""
    html = _html()
    assert ".scene .row.duo{justify-content:space-between" in html, \
        "парные сцены больше не разводятся по краям"
    m = re.search(r"\.scene \.row\.duo>\.item\{flex:0 0 (\d+)px\}", html)
    assert m, "у парных сцен не задана ширина колонки"
    колонка = int(m.group(1))
    пад = int(re.search(r"--zone-pad:(\d+)px", html).group(1))
    центр_л = пад + колонка / 2.0
    центр_п = 1080 - пад - колонка / 2.0
    assert abs(центр_л - _ART_L) <= 30, "левый круг не над картиной (%.0f)" % центр_л
    assert abs(центр_п - _ART_R) <= 30, "правый круг не над картиной (%.0f)" % центр_п
    duo = len(re.findall(r'class="row duo"', _layer()))
    assert duo >= 6, "парных сцен с широкой расстановкой всего %d" % duo


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
    """Владелец: «чтобы субтитры друг на друга не наслаивались». На две
    строки уходит одна длинная реплика — меряем по метрикам шрифта."""
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
        assert b - a >= 0.3, "реплика мелькает %.2f c: %r" % (b - a, text)
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_recognition_mistakes_are_fixed():
    поток = " ".join(t for _, _, t in _cues())
    assert "жёсткой иерархии" in поток, "потеряна ё в «жёсткой»"
    assert "Agile перевёл" in поток, "потеряна ё в «перевёл»"
    assert "всё ещё оставался" in поток, "осталось «все еще»"
    assert "Эта гибкость стала" in поток, "не собрана фраза про гибкость"
    assert "AI-трансформацию." in поток, "слово, разорванное по дефису, не склеено"


def test_subtitles_live_in_one_editable_file():
    assert os.path.exists(_SRT), "нет файла субтитров"
    assert "субтитры.srt" in _html(), "страница не читает слова из файла"
    assert "субтитры.srt" in _script(), "сборка вжигает не тот файл, который правит владелец"


def test_fallback_subs_layer_matches_the_srt():
    """Запасной путь для ffmpeg без libass: субтитры лежат готовым слоем, а
    хэш текста рядом. Правка srt без перерендера слоя должна ловиться."""
    import hashlib
    sha = os.path.join(_DIR, "субтитры.sha")
    assert os.path.exists(sha), "нет хэша текста субтитров"
    want = open(sha, encoding="utf-8").read().strip()
    got = hashlib.sha256(open(_SRT, "rb").read()).hexdigest()
    assert got == want, \
        "субтитры.srt правился, а слой subs_c/subs_a не перерендерен — сборка без libass соберёт старые слова"
    assert "only-subs" in _html(), "нет режима ?only=subs — слой субтитров нечем рендерить"


def test_burned_subtitles_are_the_same_size_as_the_preview():
    """libass считает Fontsize по метрикам OS/2, а не по em: без поправки
    вжжённые субтитры выходят в полтора раза мельче превью."""
    поправка = 1.0 / _шрифт().коэффициент_libass()
    assert abs(поправка - 1.562) < 0.01, "поправка шрифта изменилась: %.3f" % поправка
    body = _script()
    assert "h*0.026" in body, "кегль субтитров больше не считается от высоты кадра как на странице"
    assert "k*1.562" in body, "кегль не умножается на поправку libass"
    assert "h*0.028" not in body, "остался прежний кегль: в кадре он даёт 34px вместо 50"


# ── FR-SITE39: слои, обложки и сборка ────────────────────────────────────

def test_layers_are_here_and_long_enough():
    for f in ("overlay_c.mp4", "overlay_a.mp4", "subs_c.mp4", "subs_a.mp4"):
        p = os.path.join(_DIR, f)
        assert os.path.exists(p), "нет слоя %s" % f
        assert os.path.getsize(p) > 100000, "слой %s подозрительно мал" % f
    assert "var DURATION = 181.0" in _html(), "длина ролика на странице разошлась со слоем"


def test_five_part_covers_are_ready():
    """Владелец дал одну картинку и четыре реза — частей пять."""
    p = os.path.join(_DIR, "cover.png")
    assert os.path.exists(p), "нет общей обложки cover.png"
    assert os.path.getsize(p) > 100000, "обложка cover.png подозрительно мала"
    for i in range(1, 6):
        нашлась = [e for e in ("png", "jpg", "jpeg", "webp")
                   if os.path.exists(os.path.join(_DIR, "cover%d.%s" % (i, e)))]
        assert нашлась, "нет обложки части %d" % i
        путь = os.path.join(_DIR, "cover%d.%s" % (i, нашлась[0]))
        assert os.path.getsize(путь) > 50000, "обложка части %d подозрительно мала" % i


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
    """Дважды собранный дубль — это две строки субтитров друг на друге."""
    body = _script()
    assert "*-готовый.mp4" in body, "нет защиты от повторной сборки"
    assert 'Возьмите ИСХОДНЫЙ дубль' in body, "скрипт не объясняет, что делать"


def test_folder_script_matches_the_page():
    """Кнопка «Скрипт сборки» и файл в папке — один и тот же скрипт."""
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
