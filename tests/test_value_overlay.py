# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «Где ИИ создаёт ценность» — слайды 13–16 (FR-SITE36).
Без зависимостей — запускается и как `python3 tests/test_ai_first_overlay.py`, и через pytest.

Пятый ролик по тем же постоянным правилам. Новое здесь — арка
RUN → CHANGE → DISRUPT, сеть с бегущими импульсами, сетка функций 3×2 и
финал, где метрики идут по очереди. Проверяем то, что ломается молча:
внешние зависимости, досочинённые слова, разъезд элементов с речью,
наслоение субтитров и разрыв связи «страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-value")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 167.1          # 02:47 — длина дорожки
_LAYER = 169.0             # слой длиннее: хвост держит шапку
_WORDS = 366               # столько слов в сценарии владельца
_POSTERS_TOP = 638         # верх рамок картин на стене


def _html(path=_PAGE):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _script():
    html = _html()
    return html[html.index("function joinScript()"):html.index("var joinBtn")]


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


def _labels():
    html = _html()
    body = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    out = []
    for raw in re.findall(r'<p class="label">(.*?)</p>', body, re.S):
        txt = re.sub(r"<br\s*/?>", " ", raw)
        out.append(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", txt)).strip())
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



# ── FR-SITE36: страница самодостаточна ───────────────────────────────────

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


# ── FR-SITE36: тайминги сведены с речью ──────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes()
    assert len(scenes) == 9, "сцен должно быть девять, а их %d" % len(scenes)
    prev = 0.0
    for sid, tin, tout, _ in scenes:
        assert tin < tout, "%s: окно вывернуто" % sid
        assert tin >= prev, "%s начинается раньше, чем кончилась предыдущая" % sid
        prev = tout
    assert prev <= _LAYER + 0.1, "последняя сцена выходит за длину слоя"


def test_every_element_lands_on_a_spoken_cue():
    """Владелец: «фразы появляются только когда голосом произносится».
    Значит время КАЖДОГО элемента обязано попадать внутрь реплики."""
    cues = _cues()
    html = _html()
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    секции = {m.group(1) for m in re.finditer(
        r'<section class="scene" id="\w+" data-in="([\d.]+)"', layer)}
    немой = []
    for m in re.finditer(r'data-in="([\d.]+)"', layer):
        t = m.group(1)
        if t in секции:
            continue            # начало сцены — не элемент, она проявляется заранее
        v = float(t)
        if not any(a - 0.001 <= v < b for a, b, _ in cues):
            немой.append(v)
    assert not немой, "элементы выходят в тишине между репликами: %s" % немой


def test_every_ring_lands_on_a_spoken_cue():
    """Владелец: «выделяй, когда говоришь про тот или иной объект»."""
    cues = _cues()
    html = _html()
    немой = []
    for m in re.finditer(r'data-cur="([^"]+)"', html):
        числа = [float(x) for x in m.group(1).split()]
        assert len(числа) % 2 == 0, "окна выделения заданы не парами"
        for i in range(0, len(числа), 2):
            assert числа[i] < числа[i + 1], "вывернутое окно выделения"
            if not any(a - 0.001 <= числа[i] < b for a, b, _ in cues):
                немой.append(числа[i])
    assert not немой, "кольцо загорается в тишине: %s" % немой


# ── FR-SITE36: приёмы сцен ───────────────────────────────────────────────

def test_arc_has_only_names_and_roles():
    """Владелец: «до вывода не надо ничего подписывать в RUN CHANGE DISRUPT,
    кроме их названий и процессы, продукты»."""
    html = _html()
    s1 = html[html.index('<section class="scene" id="s1"'):html.index("</section>")]
    роли = re.findall(r'<p class="role el"[^>]*>([^<]+)</p>', s1)
    assert роли == ["Процессы", "Проекты", "Продукты"], "роли зон не те: %s" % роли
    ядра = re.findall(r'<p class="core [\w ]*el" data-in="([\d.]+)"[^>]*>([^<]+)</p>', s1)
    assert [t for _, t in ядра] == ["Бизнес-прорывы", "Адаптация к среде",
                                    "Сохранение устойчивости"], \
        "по центру арки не те фразы: %s" % [t for _, t in ядра]
    assert all(float(t) >= 38.0 for t, _ in ядра), \
        "фраза выходит до вывода — там подписывать нечего"
    assert "@keyframes drawCurve" in html, "дуга не прочерчивается"


def test_arc_circles_are_one_size():
    """Владелец: «проверь, что кружки одного размера в RUN/CHANGE/DISRUPT»."""
    html = _html()
    s1 = html[html.index('<section class="scene" id="s1"'):html.index("</section>")]
    d = [int(x) for x in re.findall(r'class="circle [\w ]*ico" style="width:(\d+)px', s1)]
    assert len(d) == 3, "кругов в арке должно быть три, а их %d" % len(d)
    assert len(set(d)) == 1, "круги арки разного размера: %s" % d


def test_colours_alternate_in_the_arc_and_the_grid():
    html = _html()
    for sid, имя in (("s1", "арке"), ("s8", "сетке")):
        кусок = html[html.index('<section class="scene" id="%s"' % sid):]
        кусок = кусок[:кусок.index("</section>")]
        цвета = re.findall(r'class="circle (solar|ember) ico"', кусок)
        assert цвета == ["solar", "ember", "solar"] or \
               цвета == ["ember", "solar", "ember", "solar", "ember", "solar"], \
            "цвета в %s не чередуются: %s" % (имя, цвета)


def test_functions_are_a_grid_of_six():
    """Владелец: «финансы, HR, маркетинг, продажи, поддержка, аналитика —
    кружками в 6 сеток»."""
    html = _html()
    s8 = html[html.index('<section class="scene" id="s8"'):]
    s8 = s8[:s8.index("</section>")]
    подписи = re.findall(r'<p class="label">([^<]+)</p>', s8)
    assert подписи == ["Финансы", "HR", "Маркетинг", "Продажи", "Поддержка", "Аналитика"], \
        "в сетке не те функции: %s" % подписи
    assert "grid-template-columns:repeat(3,1fr)" in html, "функции не сеткой 3×2"
    времена = [float(x) for x in re.findall(r'<div class="item el" data-in="([\d.]+)"', s8)]
    assert времена == sorted(времена) and len(set(времена)) == 6, \
        "кружки сетки появляются не по одному: %s" % времена


def test_final_metrics_come_one_by_one():
    """Владелец: «не в ряд, оранжевое / фиолетовое сияние по очереди»."""
    html = _html()
    s9 = html[html.index('<section class="scene" id="s9"'):]
    s9 = s9[:s9.index("</section>")]
    метрики = re.findall(r'<p class="label">([^<]+)</p>', s9)
    assert метрики == ["Конкретные метрики", "Скорость", "Качество", "Прибыль"], \
        "финал не тот: %s" % метрики
    сияния = re.findall(r'<div class="glow ([\w-]*)"', s9)
    assert сияния == ["", "glow-ember", "", "glow-ember"], \
        "сияния не чередуются фиолетовое / оранжевое: %s" % сияния
    # четыре data-out: три у метрик (уступают место следующей) и один у секции
    assert s9.count("data-out=") == 4, "метрики не уступают место следующей"
    assert "@keyframes coinFall" in html, "у «Прибыли» не сыплются монетки"


def test_network_has_one_radius_and_pulses():
    html = _html()
    assert "@keyframes drawWire" in html, "связи сети не прочерчиваются"
    assert "@keyframes run{" in html, "по связям не бегут импульсы"
    assert "@keyframes breathe" in html, "ядро сети не дышит"
    линии = re.findall(r'<line x1="440" y1="180" x2="(\d+)" y2="(\d+)"/>', html)
    assert len(линии) == 8, "связей должно быть по четыре в двух сценах: %d" % len(линии)
    r = {round(((int(x) - 440) ** 2 + (int(y) - 180) ** 2) ** .5) for x, y in линии}
    assert len(r) == 1, "узлы не равноудалены от ядра: %s" % r


# ── FR-SITE36: постоянные правила подачи ─────────────────────────────────

def test_no_rectangular_blocks():
    html = _html()
    css = html[html.index("<style>"):html.index("</style>")]
    scene_css = css[css.index("/* ── Общее"):css.index("/* ── Обложка")]
    for правило in re.findall(r"([^{}]+)\{([^{}]*)\}", scene_css):
        for radius in re.findall(r"border-radius:([^;}]+)", правило[1]):
            assert "50%" in radius, \
                "в сценах не круглая оправа: %s{border-radius:%s}" % (правило[0].strip(), radius)


def test_no_small_print():
    html = _html()
    css = html[html.index("/* ── Общее"):html.index("/* ── Обложка")]
    sizes = [float(x) for x in re.findall(r"font-size:([\d.]+)px", css)]
    assert sizes, "не нашёл ни одного кегля"
    assert min(sizes) >= 24, "текст мельче 24px: %s" % sorted(sizes)[:3]


def test_no_hyphenation_and_no_headings():
    html = _html()
    assert "&shy;" not in html, "остался мягкий перенос"
    assert "hyphens:auto" not in html.replace(" ", ""), "автоперенос запрещён"
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    assert "<h1" not in layer and "<h2" not in layer and "<h3" not in layer, \
        "в кадр попал заголовок"


def test_zone_stays_above_the_posters():
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    height = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top + height <= _POSTERS_TOP, "графика доходит до картин на стене"


def test_brand_chrome_is_in_place():
    html = _html()
    assert "АКАДЕМИЯ ДАТАИСТА" in html, "нет фирменной шапки"
    assert 'id="chrome"' in html, "шапка не отдельным слоем — она нужна весь ролик"


def test_highlight_is_a_ring_not_a_fade():
    html = _html()
    assert "data-dim=" not in html, "вернулось затухание соседей — владелец его запретил"
    assert ".el.on.cur .circle{transform:scale(" in html, "выделение не увеличивает круг"


# ── FR-SITE36: субтитры ──────────────────────────────────────────────────

def test_subs_do_not_overlap():
    """Владелец: «чтобы субтитры друг на друга не наслаивались»."""
    cues = _cues()
    assert len(cues) >= 90, "реплик подозрительно мало: %d" % len(cues)
    for i, (a, b, t) in enumerate(cues):
        assert a < b, "вывернутая реплика: %r" % t
        if i + 1 < len(cues):
            assert b <= cues[i + 1][0] + 1e-6, \
                "реплики наслаиваются: %r кончается %.3f, а %r начинается %.3f" % (
                    t, b, cues[i + 1][2], cues[i + 1][0])


def test_subs_follow_the_script():
    cues = _cues()
    words = 0
    for a, b, text in cues:
        assert "TurboScribe" not in text, "водяной знак распознавалки в кадре"
        n = len(text.split())
        assert 2 <= n <= 4, "в реплике %d слов (можно 2–4): %r" % (n, text)
        words += n
        assert b <= _DURATION + 0.1, "реплика выходит за длину ролика: %r" % text
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_recognition_mistakes_are_fixed():
    поток = " ".join(t for _, _, t in _cues())
    assert "про изменения" in поток, "осталось «произменения» от распознавалки"
    assert "RUN — CHANGE" in поток, "«Run -Change-Disrupt» не собрано обратно"
    assert "даёт финансовый" in поток, "потеряна ё в «даёт»"


def test_subtitles_live_in_one_editable_file():
    assert os.path.exists(_SRT), "нет файла субтитров"
    html = _html()
    assert "субтитры.srt" in html, "страница не читает слова из файла"


# ── FR-SITE36: обложки частей и сборка ───────────────────────────────────

def test_four_part_covers_are_ready():
    """Владелец: «тут надо сделать часть 1 / 2 / 3 / 4 обложки».
    Обложка всего ролика — png (её ищет собрать.sh по точному имени),
    обложки частей — jpg: пятью png папка перевешивала лимит на отправку,
    а нарезать.sh расширение ищет сам."""
    p = os.path.join(_DIR, "cover.png")
    assert os.path.exists(p), "нет общей обложки cover.png"
    assert os.path.getsize(p) > 100000, "обложка cover.png подозрительно мала"
    for i in (1, 2, 3, 4):
        нашлась = [e for e in ("png", "jpg", "jpeg", "webp")
                   if os.path.exists(os.path.join(_DIR, "cover%d.%s" % (i, e)))]
        assert нашлась, "нет обложки части %d" % i
        путь = os.path.join(_DIR, "cover%d.%s" % (i, нашлась[0]))
        assert os.path.getsize(путь) > 50000, "обложка части %d подозрительно мала" % i


def test_cut_script_is_here():
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


def test_fallback_layer_survives_spaces_in_the_folder_name():
    """Папка ролика называется «Где ИИ создаёт ценность». $EXTRA подставляется
    в команду БЕЗ кавычек (иначе «-i файл» приедет одним аргументом), поэтому
    путь со пробелами рвал команду: ffmpeg искал файл «…/Desktop/Где»."""
    body = _script()
    assert 'EXTRA="-i $DIR/subs_c.mp4' not in body,         "путь к запасному слою с пробелами развалит команду"
    assert 'EXTRA="-i $TMP/sc.mp4 -i $TMP/sa.mp4"' in body,         "запасной слой не переложен в рабочую папку без пробелов"
    assert 'cp "$DIR/subs_c.mp4" "$TMP/sc.mp4"' in body, "слой не копируется в рабочую папку"

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
