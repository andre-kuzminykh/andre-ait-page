# -*- coding: utf-8 -*-
"""Тесты графики поверх видео «ИИ-агенты» — слайды 4–8 лекции 1 (FR-SITE33).
Без зависимостей — запускается и как `python3 tests/test_agents_overlay.py`, и через pytest.

Третий ролик по тем же постоянным правилам, что лекция 1 (FR-SITE27) и
приветствие курса (FR-SITE30). Новое здесь — орбита вместо ряда и требование
владельца «более разнообразно»: у каждой сцены своя форма. Проверяем то, что
ломается молча: внешние зависимости, досочинённые слова, разъезд элементов с
речью, неравная орбита и разрыв связи «страница — субтитры.srt — собрать.sh».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR = os.path.join(_ROOT, "automation", "1", "overlay-agents")
_PAGE = os.path.join(_DIR, "index.html")
_DECK = os.path.join(_ROOT, "automation", "1", "index.html")
_SRT = os.path.join(_DIR, "субтитры.srt")
_DURATION = 168.5          # 02:48 — длина дорожки
_LAYER = 170.5             # слой длиннее: хвост держит шапку
_WORDS = 369               # столько слов в сценарии владельца
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
    for f in ("logo.png", "cover.png"):
        assert os.path.exists(os.path.join(_DIR, f)), "нет файла: %s" % f


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
    assert len(scenes) == 7, "сцен должно быть семь, а их %d" % len(scenes)
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


def test_orbit_keeps_every_property_at_one_distance():
    """Владелец: «надо, чтобы все кружки вокруг на одном расстоянии были».
    Орбита была эллипсом, и боковые спутники стояли дальше верхнего с нижним."""
    html = _html()
    pos = re.findall(r'<div class="sat [\w-]+" style="left:(\d+)px;top:(\d+)px">', html)
    assert len(pos) == 6, "на орбите должно быть шесть свойств, а их %d" % len(pos)
    m = re.search(r'#s\d \.core\{position:absolute;left:(\d+)px;top:(\d+)px', html)
    assert m, "не нашёл центр орбиты"
    cx, cy = float(m.group(1)), float(m.group(2))
    rr = [((float(x) - cx) ** 2 + (float(y) - cy) ** 2) ** 0.5 for x, y in pos]
    assert max(rr) - min(rr) <= 1.5, \
        "спутники на разном расстоянии от агента: %s" % [round(r) for r in rr]


def test_scenes_do_not_look_alike():
    """Владелец: «нужно более разнообразно… не просто кружки и текст».
    Приёмы: ряды, одиночный элемент с сиянием, поток со стрелками, орбита,
    финальная пара с двумя сияниями."""
    html = _html()
    assert 'class="orbit"' in html and 'class="sat ' in html, "орбита исчезла"
    assert 'class="arr el"' in html, "поток со стрелками исчез"
    assert html.count('class="glow') >= 3, "сияния за одиночными элементами исчезли"
    assert "glow-ember" in html and "glowPulse" in html, "оранжевое сияние не дышит"
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


def test_circles_are_one_size_in_a_row():
    """Владелец: «они все разного размера и высоты, должны быть одной».
    Разнокалиберные ряды и лесенка убраны: в рядовых сценах один диаметр и
    одна высота. Орбита — отдельная фигура, там центр крупнее спутников."""
    html = _html()
    assert "margin-top:68px" not in html, "вернулась лесенка — круги на разной высоте"
    layer = html[html.index('<div id="layer">'):html.index('<div id="cover">')]
    # диаметры в рядовых сценах: всё, что вне орбиты
    ряды = re.sub(r'<div class="orbit">.*?</div>\s*</section>', "", layer, flags=re.S)
    d = [int(x) for x in re.findall(r'class="circle [\w ]*ico" style="width:(\d+)px', ряды)]
    обычные = [x for x in d if x <= 100]
    assert обычные, "не нашёл кругов рядовых сцен"
    assert len(set(обычные)) == 1, "в рядах круги разного размера: %s" % sorted(set(обычные))


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
    # финал продиктован владельцем: «Цель → Агент сделал сам»
    "цель", "сделал", "сам",
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
    for heading in ("Кто такие", "Свойства", "Пример из жизни", "Базовая архитектура",
                    "Почему именно", "Сборы в командировку"):
        assert heading not in layer, "заголовок слайда попал в кадр: %r" % heading


def test_no_rectangular_blocks():
    """Правило 1: круг — единственная допустимая оправа."""
    html = _html()
    css = html[html.index("<style>"):html.index("</style>")]
    scene_css = css[css.index("/* ── Общее"):css.index("/* ── Обложка")]
    for radius in re.findall(r"border-radius:([^;}]+)", scene_css):
        assert "50%" in radius, "в сценах не круглая оправа: border-radius:%s" % radius


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
        assert 2 <= n <= 4, "в реплике %d слов (можно 2–4): %r" % (n, text)
        words += n
        prev_end = b
    assert words == _WORDS, "слов в субтитрах %d, а в сценарии %d" % (words, _WORDS)


def test_recognition_mistakes_are_fixed():
    """Распознавалка слышала своё: «AI cинструментов», «данными С
    корпоративных систем», теряла ё. Слова берутся из сценария владельца."""
    # склеиваем реплики в один поток слов: фраза может быть разорвана между строк
    поток = " ".join(t for _, _, t in _cues())
    assert "AI-инструментов" in поток, "не выправлено «AI cинструментов»"
    assert "данными из корпоративных систем" in поток, "осталось «данными С корпоративных систем»"
    assert "Четвёртое" in поток and "своё поведение" in поток, "потеряна ё"


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
    assert re.search(r"var DURATION = 170\.5", html), \
        "слой должен быть длиннее дорожки, чтобы в хвосте осталась одна шапка"
    последняя = max(float(t) for _, _, t, _ in [(a, b, c, d) for a, b, c, d in _scenes()])
    assert последняя <= _LAYER - 1.0, \
        "последняя сцена (%.1f) не оставляет в слое хвоста под шапку" % последняя
    assert "body.on-cover #chrome" in html, "шапка обязана прятаться только на обложке"


def test_cover_precedes_the_clip():
    html = _html()
    cover = float(re.search(r"var COVER = ([\d.]+);", html).group(1))
    assert cover == 0.2, "обложка должна идти 0.2 c, а стоит %s" % cover
    body = _script()
    assert '-t "$SEC" -i "$DIR/cover.png"' in body, "обложка не подаётся отдельным входом"
    assert "concat=n=2:v=1" in body, "обложка не приклеивается к ролику"
    assert body.index("subtitles=filename=") < body.index("concat=n=2:v=1"), \
        "субтитры вжигаются ПОСЛЕ приклейки обложки — все тайминги уедут"


def test_cover_does_not_break_frame_rate():
    """После concat частота кадров теряется, и без явного -r ffmpeg молча
    пишет 25 к/с, выбрасывая каждый шестой кадр 30-кадрового ролика."""
    body = _script()
    assert '-r "$FPS"' in body, "нет явного -r: после concat ffmpeg молча пишет 25 к/с"
    assert ",fps=$FPS[v]" not in body, "fps-фильтром после concat нельзя: съедает последний кадр"
    assert '-loop 1 -framerate "$FPS" -t "$SEC"' in body, \
        "без -framerate заставка на 30-кадровом ролике короче заказанного"


def test_fallback_layer_survives_spaces_in_the_folder_name():
    """$EXTRA подставляется в команду без кавычек, поэтому путь к запасному
    слою не должен содержать пробелов: папку ролика владелец переименовывает
    как угодно, и «Где ИИ создаёт ценность» рвало команду."""
    body = _script()
    assert 'EXTRA="-i $DIR/subs_c.mp4' not in body, \
        "путь к запасному слою с пробелами развалит команду"
    assert 'EXTRA="-i $TMP/sc.mp4 -i $TMP/sa.mp4"' in body, \
        "запасной слой не переложен в рабочую папку без пробелов"


def test_audio_is_copied_when_it_can_be():
    """Владелец: «звук шипит… в оригинале всё ок». Дорожка не пережимается."""
    body = _script()
    assert "-c:a copy" in body, "звук всегда пережимается — это и слышно"
    assert "-map 4:a:0" in body, "звук берётся не отдельным входом со сдвигом"
    assert "aresample=async" not in body, "звук растягивается под склейку — это и слышалось"


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
