# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «Эволюция ИИ и AI-First» — слайды 9–12 (FR-SITE34).
Без зависимостей — запускается и как `python3 tests/test_ai_first_overlay.py`, и через pytest.

Четвёртый ролик по тем же постоянным правилам. Новое здесь — таймлайн с
датами, диаграмма из пяти растущих столбиков и звёздный финал. Проверяем то,
что ломается молча: внешние зависимости, досочинённые слова, разъезд
элементов с речью и разрыв связи «страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-ai-first")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 165.0          # 02:45 — длина дорожки
_LAYER = 167.0             # слой длиннее: хвост держит шапку
_WORDS = 363               # столько слов в сценарии владельца
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


# ── FR-SITE33: страница самодостаточна ───────────────────────────────────

def test_page_is_self_contained():
    """В записи и офлайн страница обязана выглядеть так же, как на сайте."""
    html = _html()
    external = re.findall(r'(?:src|href)="(?:https?:)?//[^"]+"', html)
    assert not external, "страница тянет внешние ресурсы: %r" % external
    for f in re.findall(r"url\((fonts/[^)]+\.woff2)\)", html):
        assert os.path.exists(os.path.join(_DIR, f)), "нет файла шрифта: %s" % f
    assert os.path.exists(os.path.join(_DIR, "logo.png")), "нет файла logo.png"


def test_font_matches_the_deck():
    """Дек лекции набран Montserrat — графика поверх видео обязана совпадать."""
    assert "Montserrat" in _html(_DECK), "дек больше не на Montserrat — проверьте пару"
    assert "'Montserrat'" in _html(), "страница набрана не тем шрифтом, что дек"


def test_icons_come_from_the_deck():
    """Иконки берутся те же, что стоят на слайдах: кадр не должен расходиться
    с картинкой курса. Проверяем инлайновым SVG, а не именем класса."""
    html = _html()
    assert 'viewBox="0 0 256 256"' in html, "иконки не в системе координат Phosphor"
    assert html.count('viewBox="0 0 256 256"') >= 15, "иконок подозрительно мало"
    assert "ph-" not in html, "остался класс шрифтовых иконок — они тянут внешний CSS"


# ── FR-SITE33: тайминги сведены с речью ──────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes()
    assert len(scenes) == 8, "сцен должно быть восемь, а их %d" % len(scenes)
    prev = 0.0
    for sid, tin, tout, _ in scenes:
        assert tin < tout, "%s: окно вывернуто" % sid
        assert tin >= prev, "%s начинается раньше, чем кончилась предыдущая сцена" % sid
        prev = tout
    assert prev <= _DURATION + 0.5, "последняя сцена выходит за длину ролика"


def test_cues_are_within_scenes():
    for sid, tin, tout, cues in _scenes():
        for c in cues:
            assert tin <= c <= tout, "%s: элемент на %.1f вне окна сцены %.1f–%.1f" % (sid, c, tin, tout)


def test_every_element_lands_on_a_spoken_cue():
    """Главный инвариант подачи: элемент появляется ровно тогда, когда о нём
    говорят. Значит время КАЖДОГО элемента обязано попадать внутрь реплики —
    иначе графика идёт сама по себе, а речь сама по себе."""
    cues = _cues()
    for sid, tin, tout, times in _scenes():
        for t in times:
            assert any(a - 0.001 <= t < b for a, b, _ in cues), \
                "%s: элемент на %.2f c висит в тишине, между репликами" % (sid, t)


def test_bars_grow_and_keep_one_width():
    """Владелец: «там где эволюция сделаем столбиками и внутри столбиков на
    вершинах будут иконки». Ширина у столбиков одна — растёт только высота,
    и растёт по-настоящему: заливка поднимается снизу вверх."""
    html = _html()
    бары = re.findall(r'<div class="bar [\w ]*el"[^>]*style="left:(\d+)px;height:(\d+)px"', html)
    assert len(бары) == 5, "столбиков должно быть пять, а их %d" % len(бары)
    высоты = [int(h) for _, h in бары]
    assert высоты == sorted(высоты), "столбики не растут слева направо: %s" % высоты
    assert len(set(высоты)) == 5, "у столбиков совпадают высоты: %s" % высоты
    assert "#s3 .bar{position:absolute;bottom:0;width:120px}" in html, \
        "у столбиков разная ширина — расти должна только высота"
    assert "transform-origin:bottom;transform:scaleY(" in html, "заливка не вырастает снизу"
    assert "#s3 .bar.on .fill{transform:none}" in html, "заливка не доходит до полной высоты"


def test_bar_labels_are_on_top_and_there_is_no_baseline():
    """Владелец: «подписи сверху, линии снизу нет»."""
    html = _html()
    подпись = html[html.index("#s3 .label{"):html.index("}", html.index("#s3 .label{"))]
    assert "bottom:100%" in подпись, "подписи столбиков не над ними"
    assert "#s3 .ladder::after" not in html, "вернулась линия-база под столбиками"


def test_timeline_has_dates_and_draws_itself():
    """Владелец: «там где история — там таймлайн сделать + с датами сверху»."""
    html = _html()
    даты = re.findall(r'<p class="date">([^<]+)</p>', html)
    assert len(даты) == 4, "дат на таймлайне должно быть четыре, а их %d" % len(даты)
    assert "#s1 .row::before" in html, "нет линии таймлайна"
    assert "@keyframes drawLine" in html, "линия таймлайна не прочерчивается"
    кегль = re.search(r"#s1 \.date\{[^}]*font-size:(\d+)px", html)
    assert кегль and int(кегль.group(1)) >= 24, "дата мельче 24px"


def test_scenes_do_not_look_alike():
    """Владелец: «нужно более разнообразно… не просто кружки и текст».
    Приёмы: ряды, одиночный элемент с сиянием, поток со стрелками, орбита,
    финальная пара с двумя сияниями."""
    html = _html()
    assert 'class="bar ' in html, "диаграмма столбиков исчезла"
    assert 'class="arr el"' in html, "пара со стрелкой исчезла"
    assert html.count('class="glow') >= 3, "сияния за одиночными элементами исчезли"
    assert "glow-ember" in html and "glowPulse" in html, "оранжевое сияние не дышит"
    assert "starTwinkle" in html and html.count('class="st"') >= 6, "звёздочки финала исчезли"
    assert "data-cur=" in html, "подсветка «о нём говорят сейчас» исчезла"


def test_highlight_is_a_ring_not_a_fade():
    """Владелец: «когда какой-то элемент выделяешь — да, круто его увеличить
    немного и во внешний круг взять и потом вернуть на место плавно по
    размеру, но остальные не надо прозрачность увеличивать — и так везде».
    Значит: выделение = кольцо + масштаб с переходом, и НИКАКОГО затухания
    соседей."""
    html = _html()
    assert "data-dim=" not in html, "вернулось затухание соседей — владелец его запретил"
    assert ".el.on.dim" not in html, "осталось правило затухания"
    assert ".el.on.cur .circle{transform:scale(" in html, "выделение не увеличивает круг"
    assert "border-color .5s var(--ease),transform .5s var(--ease)" in html, \
        "кольцо и размер возвращаются рывком, а не плавно"


def _section(html, sid):
    """Кусок разметки одной сцены."""
    начало = html.index('<section class="scene" id="%s"' % sid)
    return html[начало:html.index("</section>", начало)]


def test_circles_are_one_size_in_a_row():
    """Владелец: «они все разного размера и высоты, должны быть одной».
    Разнокалиберные ряды и лесенка убраны: в рядовых сценах один диаметр и
    одна высота. Диаграмма столбиков (s3) — отдельная фигура по прямой
    просьбе владельца («давай там где эволюция сделаем столбиками»): там
    иконка сидит в вершине столбика и мельче рядовой, но у всех пяти
    столбиков она ОДНА."""
    html = _html()
    assert "margin-top:68px" not in html, "вернулась лесенка — круги на разной высоте"
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    ряды = layer.replace(_section(html, "s3"), "")
    d = [int(x) for x in re.findall(r'class="circle [\w ]*ico" style="width:(\d+)px', ряды)]
    обычные = [x for x in d if x <= 100]
    assert обычные, "не нашёл кругов рядовых сцен"
    assert len(set(обычные)) == 1, "в рядах круги разного размера: %s" % sorted(set(обычные))
    # в самой диаграмме — тоже один диаметр на все столбики
    столбики = [int(x) for x in re.findall(
        r'class="circle [\w ]*ico" style="width:(\d+)px', _section(html, "s3"))]
    assert len(столбики) == 5, "иконок в столбиках должно быть пять, а их %d" % len(столбики)
    assert len(set(столбики)) == 1, \
        "иконки столбиков разного размера: %s" % sorted(set(столбики))


def test_colours_alternate():
    """Владелец: «фиолетовый и оранжевый надо чередовать». Белых кругов в
    раскладке больше нет — каждый круг либо solar, либо ember."""
    html = _html()
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    круги = re.findall(r'<div class="circle ([\w ]*?) ?ico"', layer)
    assert круги, "не нашёл ни одного круга"
    без_цвета = [c for c in круги if "solar" not in c and "ember" not in c]
    assert not без_цвета, "остались круги без фирменного цвета: %d" % len(без_цвета)
    assert sum("solar" in c for c in круги) >= 5, "фиолетовых кругов подозрительно мало"
    assert sum("ember" in c for c in круги) >= 5, "оранжевых кругов подозрительно мало"


# ── FR-SITE33: постоянные правила подачи ─────────────────────────────────

_OWNER_WORDING = {
    # Прямые формулировки владельца и слова из его сценария: в деке они есть
    # не всегда дословно, но досочинёнными не являются.
    "локальная", "цифровые", "сотрудники", "единая", "гибридная", "команда",
    "зонт", "отель",
    # финал и связки продиктованы владельцем
    "работают", "вместе", "новый", "способ", "строить",
}


def test_labels_come_from_the_deck():
    """Каждое значимое слово подписи — из слайдов 4–8 или из прямой
    формулировки владельца. Всё остальное — досочинённое обещание."""
    deck = _html(_DECK).replace("&nbsp;", "").replace("&shy;", "")
    # дек пишет «ИИ‑модель» неразрывным дефисом (U+2011) — для сверки слов
    # это тот же дефис, что и обычный
    deck = re.sub(r"[\u2010-\u2015\u2212]", "-", re.sub(r"\s+", " ", deck)).lower()
    skip = {"и", "в", "по", "как", "с", "не"}
    for label in _labels():
        for word in re.findall(r"[\w-]+", re.sub(r"[\u2010-\u2015\u2212]", "-", label)):
            low = word.lower()
            if low in skip or len(word) < 3 or low in _OWNER_WORDING:
                continue
            stem = (word[:-2] if len(word) > 6 else word).lower()
            assert stem in deck, "слова нет в деке, значит подпись досочинена: %r (из %r)" % (word, label)
    assert len(_labels()) >= 16, "проверено подозрительно мало подписей (%d)" % len(_labels())


def test_no_headings_in_frame():
    html = _html()
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    layer = re.sub(r"<!--.*?-->", " ", layer, flags=re.S)
    assert "<h1" not in layer and "<h2" not in layer and "<h3" not in layer, "в кадре заголовок"
    for heading in ("Исторический контекст", "Пять уровней", "Почему агенты",
                    "Что такое", "Мы здесь"):
        assert heading not in layer, "заголовок слайда попал в кадр: %r" % heading


def test_no_rectangular_blocks():
    """Правило 1: круг — единственная допустимая оправа.

    Единственное исключение — заливка столбика диаграммы (`#s3 .fill`):
    столбики попросил сам владелец («давай там где эволюция сделаем
    столбиками»). И даже там прямоугольника нет: вершина скруглена по
    половине ширины, получается столбик с куполом, а низ уходит в
    прозрачность."""
    html = _html()
    css = html[html.index("<style>"):html.index("</style>")]
    scene_css = css[css.index("/* ── Общее"):css.index("/* ── Обложка")]
    исключение = "#s3 .fill"
    for правило in re.findall(r"([^{}]+)\{([^{}]*)\}", scene_css):
        селектор, тело = правило[0].strip(), правило[1]
        for radius in re.findall(r"border-radius:([^;}]+)", тело):
            if исключение in селектор:
                assert radius.strip().endswith("0 0"), \
                    "столбик стал плашкой: border-radius:%s" % radius
                continue
            assert "50%" in radius, \
                "в сценах не круглая оправа: %s{border-radius:%s}" % (селектор, radius)
    assert scene_css.count(исключение + "{") == 1, \
        "исключение для столбика расползлось по CSS"


def test_no_small_print():
    """Правило 3: минимум 24px при ширине кадра 1080."""
    html = _html()
    css = html[html.index("/* ── Общее"):html.index("/* ── Обложка")]
    sizes = [float(x) for x in re.findall(r"\.label\{font-size:([\d.]+)px", css)]
    sizes += [float(x) for x in re.findall(r"label\{[^}]*?font-size:([\d.]+)px", css)]
    assert sizes, "не нашёл ни одного кегля подписей"
    assert min(sizes) >= 24, "подпись мельче 24px: %s" % sorted(sizes)[:3]


def test_no_hyphenation_at_all():
    html = _html()
    assert "&shy;" not in html, "остался мягкий перенос"
    flat = html.replace(" ", "")
    assert "overflow-wrap:anywhere" not in flat, "anywhere рвёт слово посреди слога"
    assert "hyphens:auto" not in flat, "автоперенос запрещён"


def test_zone_stays_above_the_posters():
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    height = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top + height <= _POSTERS_TOP, \
        "зона графики (%d..%d) заходит на картины (y%d)" % (top, top + height, _POSTERS_TOP)


def test_brand_chrome_is_in_place():
    html = _html()
    assert 'id="chrome"' in html and "АКАДЕМИЯ ДАТАИСТА" in html, "нет фирменной шапки"
    assert "body.on-cover #chrome" in html, "на обложке шапка обязана прятаться"
    zone_top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    assert zone_top >= 244, "зона графики залезает под шапку (top %d)" % zone_top


# ── FR-SITE33: субтитры правятся без перерендера ─────────────────────────

def test_subtitles_live_in_one_editable_file():
    assert os.path.exists(_SRT), "нет файла субтитров"
    html = _html()
    assert "var SUBS = [];" in html, "в странице осталась своя копия слов — она разойдётся с файлом"
    assert "parseSRT" in html and "loadSubs" in html, "страница не читает файл субтитров"
    assert "субтитры.srt" in _script(), "сборка вжигает не тот файл, который правит владелец"


def test_subs_follow_the_transcript():
    cues = _cues()
    assert len(cues) >= 90, "реплик подозрительно мало: %d" % len(cues)
    prev_end, words = 0.0, 0
    for a, b, text in cues:
        assert a < b, "вывернутая реплика: %r" % text
        assert a >= prev_end - 0.001, "реплики наезжают друг на друга: %r" % text
        assert b <= _DURATION + 0.1, "реплика выходит за длину ролика: %r" % text
        assert "TurboScribe" not in text, "водяной знак распознавалки в кадре"
        n = len(text.split())
        # Хвост дорожки — единственная реплика в пять слов: иначе «ими.»
        # мигало бы отдельной строкой на четверть секунды.
        предел = 5 if (a, b, text) == cues[-1] else 4
        assert 2 <= n <= предел, "в реплике %d слов (можно 2–4): %r" % (n, text)
        words += n
        prev_end = b
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_recognition_mistakes_are_fixed():
    """Распознавалка слышала своё и теряла ё. Слова берутся из сценария."""
    поток = " ".join(t for _, _, t in _cues())
    assert "жёстким правилам" in поток, "потеряна ё в «жёстким»"
    assert "Четвёртый" in поток, "нет «Четвёртый»"
    assert "сформировался спрос" in поток, "осталось «сформулировался» от распознавалки"


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


# ── FR-SITE33: слой и сборка ─────────────────────────────────────────────

def test_page_can_be_rendered_frame_by_frame():
    html = _html()
    assert "window.__renderAt" in html, "нет покадрового рендера — слой нечем собрать"
    assert "an.currentTime" in html, "время анимаций не выставляется явно — появления размажутся"
    assert "documentElement.style.background = 'transparent'" in html, \
        "фон <html> не снят: снимки выйдут непрозрачными"


def test_script_burns_the_layer_and_the_subtitles():
    body = _script()
    assert "alphamerge" in body, "слой не сшивается из цвета и маски"
    assert "eof_action=pass" in body, "слой обрежет ролик, который длиннее его"
    assert "subtitles=filename=" in body, "субтитры не вжигаются явным ключом"
    assert "Montserrat Black" in body, "в стиле не полное имя шрифта — субтитры выйдут системным"
    assert os.path.exists(os.path.join(_DIR, "fonts", "Montserrat-Black.ttf")), \
        "нет ttf для вжигания: woff2 libass не понимает"
    assert "$ROT" in body, "поворот кадра не учитывается"
    assert "-f null" in body, "результат не проверяется декодированием"


def test_script_picks_a_capable_ffmpeg():
    body = _script()
    assert "/opt/homebrew/bin/ffmpeg" in body, "brew-путь не пробуется мимо PATH"
    assert 'grep -q " subtitles "' in body, "кандидат не проверяется на фильтр subtitles"
    assert "субтитры.sha" in body, "сборка не сверяет хэш текста со слоем"


def test_chrome_survives_a_longer_clip():
    """Владелец: «в конце исчезает лого и АКАДЕМИЯ ДАТАИСТА — это никогда не
    исчезает, кроме обложки». Слой конечен, а дубль может оказаться длиннее:
    после конца слоя шли голые кадры без шапки. tpad держит ПОСЛЕДНИЙ кадр
    слоя (на нём только шапка) до конца ролика."""
    body = _script()
    assert "tpad=stop=-1:stop_mode=clone" in body, \
        "слой не удерживает последний кадр — на длинном дубле шапка пропадёт"
    html = _html()
    assert re.search(r"var DURATION = 167\.0", html), \
        "слой должен быть длиннее дорожки, чтобы в хвосте осталась одна шапка"
    последняя = max(float(t) for _, _, t, _ in [(a, b, c, d) for a, b, c, d in _scenes()])
    assert последняя <= _LAYER - 1.0, \
        "последняя сцена (%.1f) не оставляет в слое хвоста под шапку" % последняя
    assert "body.on-cover #chrome" in html, "шапка обязана прятаться только на обложке"


def test_cover_precedes_the_clip():
    """Обложка идёт 0.2 c перед роликом. Своей у этого ролика пока нет, и
    сборка из-за этого не встаёт: нет cover.png — берётся первый кадр
    ролика, он и так становится превью в ленте."""
    html = _html()
    cover = float(re.search(r"var COVER = ([\d.]+);", html).group(1))
    assert cover == 0.2, "обложка должна идти 0.2 c, а стоит %s" % cover
    body = _script()
    assert '-t "$SEC" -i "$COVERPIC"' in body, "обложка не подаётся отдельным входом"
    assert "concat=n=2:v=1" in body, "обложка не приклеивается к ролику"
    assert body.index("subtitles=filename=") < body.index("concat=n=2:v=1"), \
        "субтитры вжигаются ПОСЛЕ приклейки обложки — все тайминги уедут"
    assert "-frames:v 1" in body and "COVERPIC=" in body, \
        "без своей обложки сборка встанет вместо того, чтобы взять первый кадр"


def test_cover_does_not_break_frame_rate():
    """После concat частота кадров теряется, и без явного -r ffmpeg молча
    пишет 25 к/с, выбрасывая каждый шестой кадр 30-кадрового ролика."""
    body = _script()
    assert '-r "$FPS"' in body, "нет явного -r: после concat ffmpeg молча пишет 25 к/с"
    assert ",fps=$FPS[v]" not in body, "fps-фильтром после concat нельзя: съедает последний кадр"
    assert '-loop 1 -framerate "$FPS" -t "$SEC"' in body, \
        "без -framerate заставка на 30-кадровом ролике короче заказанного"


def test_audio_is_copied_when_it_can_be():
    """Владелец: «звук шипит… в оригинале всё ок». Дорожка не пережимается."""
    body = _script()
    assert "-c:a copy" in body, "звук всегда пережимается — это и слышно"
    assert "-map 4:a:0" in body, "звук берётся не отдельным входом со сдвигом"
    assert "aresample=async" not in body, "звук растягивается под склейку — это и слышалось"


# ── FR-SITE35: нарезка готового ролика на части с обложками ──────────────

_CUT = os.path.join(_DIR, "нарезать.sh")


def _cut():
    with open(_CUT, encoding="utf-8") as f:
        return f.read()


def test_cut_script_is_next_to_the_covers():
    """Скрипт лежит в папке ролика: обложки он берёт из своей же папки."""
    assert os.path.exists(_CUT), "нет скрипта нарезки"
    assert _cut().startswith("#!/bin/sh"), "скрипт не на sh — на маке запускают им"
    assert 'DIR=$(cd "$(dirname "$0")" && pwd)' in _cut(), \
        "обложки ищутся не рядом со скриптом — из другой папки нарезка их не найдёт"


def test_cut_has_no_cyrillic_names():
    """dash (это /bin/sh на маке через `sh файл`) кириллические имена функций
    не принимает: «Bad function name». Один раз уже наступали."""
    for имя in re.findall(r"^([^\s(]+)\(\)\s*\{", _cut(), re.M):
        assert имя.isascii(), "имя функции %r не латиницей — dash не примет" % имя
    for имя in re.findall(r"^([A-Za-zА-Яа-яЁё_][\w]*)=", _cut(), re.M):
        assert имя.isascii(), "имя переменной %r не латиницей" % имя


def test_cut_makes_any_number_of_parts():
    """Владелец: «я могу ещё нарезать на 4 части также с обложками».
    Сколько чисел — столько резов, частей на одну больше."""
    body = _cut()
    assert 'STARTS="$OLD $PTS"' in body, "части считаются не от списка чисел"
    assert 'ENDS="$PTS"' in body, "у последней части должен быть открытый конец"
    assert "sort -n" in body, "числа не сортируются: «128 62» дало бы кусок отрицательной длины"
    assert "sec() {" in body, "мм:сс не разбирается — «2:08» ушло бы в ffmpeg как есть"
    assert "$(echo $PTS | wc -w) + 1" in body, "число частей не считается по числу резов"


def test_cut_labels_every_part():
    """Владелец: «под тайтлом чуть ниже пиши Часть 1 / Часть 2 / … шрифт
    поменьше сделай»."""
    body = _cut()
    assert 'CAPWORD="Часть"' in body, "подпись частей исчезла"
    assert "$CAPWORD $1" in body, "в подписи нет номера части"
    assert "Montserrat-Black.ttf" in body, "подпись не тем шрифтом, что весь текст роликов"
    # кегль подписи — заметно меньше тайтла обложки (тот в кадре 1080 около 110px)
    m = re.search(r'CAPSIZE:=\$\(awk -v h="\$DH" .BEGIN\{ printf "%d", h\*([\d.]+) \}', body)
    assert m, "не нашёл кегль подписи"
    assert 24 <= float(m.group(1)) * 1920 <= 80, \
        "кегль подписи %dpx — не «поменьше»" % (float(m.group(1)) * 1920)
    assert "низ=" in body and "кегль=" in body, "подпись нельзя подвинуть и уменьшить"
    assert "нет|no|off" in body, "подпись нельзя выключить"


def test_cut_draws_the_label_with_whatever_ffmpeg_can():
    """drawtext есть не в каждой сборке (нужен libfreetype), subtitles — не в
    каждой другой (нужен libass). Умеем обоими, иначе подпись молча пропала бы."""
    body = _cut()
    assert "DRAWOK=1" in body and "ASSOK=1" in body, "нет второго способа нарисовать подпись"
    assert "for m in draw ass" in body, "способы не перебираются по очереди"
    assert "drawtext=fontfile=" in body, "drawtext без явного файла шрифта уйдёт в системный"
    assert "Style: Cap,Montserrat Black," in body, \
        "в ASS не полное имя шрифта — libass молча возьмёт системный"
    assert ",8,40,40,$CAPY,1" in body, "выравнивание не по верху: MarginV поедет от низа кадра"
    assert "ни drawtext, ни subtitles в этой сборке" in body, \
        "сборка без обоих фильтров не предупреждает"


def test_cut_can_show_the_covers_as_pictures():
    """Обложка идёт 0.2 с — в плеере её не поймать. Режим «превью» кладёт
    рядом картинки обложек, чтобы подпись можно было увидеть глазами."""
    body = _cut()
    assert "превью|превью=*|preview" in body, "нет режима превью"
    assert '"$BASE-обложка$i.png"' in body, "превью не сохраняется картинкой"
    assert "Ролики НЕ резались" in body, "превью молча притворяется нарезкой"


def test_cut_finds_a_font_even_without_the_folder():
    """Скрипт часто кладут ОДИН, рядом с видео. Без запасного шрифта подпись
    в этом случае молча не появлялась бы."""
    body = _cut()
    assert "$HOME/Library/Fonts/Montserrat-Black.ttf" in body, "не ищет шрифт в системных папках мака"
    assert "/System/Library/Fonts/Supplemental/Arial Bold.ttf" in body, "нет системного запасного шрифта"
    assert "ПОДПИСИ «$CAPWORD N» НЕ БУДЕТ" in body, "молчит, когда шрифта нет вовсе"
    assert 'cp "$f" "$TMP/fonts/f.ttf"' in body, \
        "шрифт не копируется под простое имя — путь с пробелом сломает фильтр"


def test_cut_verifies_the_label_actually_landed():
    """Владелец: «запустил скрипт, нарезалось всё, а подпись "Часть _" не
    вставилось». Фильтр может отработать вхолостую и не сказать ни слова,
    поэтому подпись проверяется на пробном кадре ДО нарезки."""
    body = _cut()
    assert "captest()" in body, "нет самопроверки подписи"
    assert 'color=c=black:s=${DW}x${DH}' in body, "проверка не на пробном кадре"
    assert "-f md5 -" in body, "результат проверки не сверяется побайтово"
    assert "подпись не нарисовал — пробую другой" in body, \
        "при осечке не пробуется второй способ"
    assert "ПОДПИСИ «$CAPWORD N» НЕ БУДЕТ" in body, "молчит, когда не нарисовали оба способа"
    assert "проверено на пробном кадре" in body, "в логе не видно, что подпись реально легла"


def test_cut_builds_the_label_in_one_place():
    """Один и тот же кусок фильтра идёт и в самопроверку, и в нарезку —
    иначе проверили бы одно, а нарисовали другое."""
    body = _cut()
    assert body.count("capfilter() {") == 1, "функция подписи не одна"
    assert 'capfilter 1 "$1"' in body, "самопроверка рисует не тем же фильтром"
    assert 'DRAW=$(capfilter "$i" "$CAPMODE")' in body, "нарезка рисует не тем же фильтром"


def test_cut_takes_covers_from_the_folder():
    """Владелец: «вставишь в начале те же обложки, что будут в cover стоять
    в папке». Своя на часть, общая на все, иначе первый кадр части."""
    body = _cut()
    assert '"$DIR/cover$1.$e"' in body, "нет отдельной обложки на каждую часть"
    assert '"$DIR/cover.$e"' in body, "нет общей обложки на все части"
    assert "png jpg jpeg webp" in body, "обложка ищется только одним расширением"
    assert '-ss "$2" -i "$VIDEO" -frames:v 1' in body, \
        "нет запасного варианта: без обложки в папке часть осталась бы без заставки"


def test_cut_replaces_the_old_intro_instead_of_stacking():
    """Ролик из собрать.sh уже начинается с заставки 0.2 с. Если приклеить
    вторую, зритель увидит стоп-кадр вдвое дольше."""
    body = _cut()
    assert "freezedetect=n=0.001:d=0.08" in body, "стоп-кадр в начале не ищется"
    assert "заставка=*|intro=*" in body, "нет ручного переопределения длины старой заставки"
    assert '-i "$VIDEO" -frames:v 1 -f md5' not in body, \
        "хэши кадров ролика не годятся: одна картинка кодируется с потерями и декодируется по-разному"


def test_cut_keeps_the_frame_rate_and_the_audio():
    """Те же два правила, что в собрать.sh: явный -r после concat и звук копией."""
    body = _cut()
    assert '-r "$FPS"' in body, "нет явного -r: после concat ffmpeg молча пишет 25 к/с"
    assert '-loop 1 -framerate "$FPS" -t "$SEC"' in body, \
        "без -framerate обложка на 30-кадровом ролике короче заказанной"
    assert "-c:a copy" in body, "звук пережимается — владелец на это уже жаловался"
    assert '-itsoffset "$SEC"' in body, "звук не сдвинут на длину обложки — уедет на её длину"
    assert "aresample=async" not in body, "звук растягивается под склейку — это и слышалось"


def test_cut_checks_every_part():
    body = _cut()
    assert '-f null - 2>&1 || true' in body, "результат не проверяется декодированием"
    assert "будет чернота" in body, "не проверяется, что видеодорожка не короче куска"


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
