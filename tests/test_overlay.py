# -*- coding: utf-8 -*-
"""Тесты анимированной графики поверх видео лекции 1 (FR-SITE27, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_overlay.py`, и через pytest.

Оверлей ложится на «говорящую голову» 1080×1920: слайды 1–3 лекции появляются
поэлементно под озвучку. Проверяем то, что ломается молча: внешние зависимости
(в записи их не будет), рассинхрон таймингов и расхождение текста с деком.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OVERLAY = os.path.join(_ROOT, "automation", "1", "overlay", "index.html")
_LECTURE = os.path.join(_ROOT, "automation", "1", "index.html")
_DURATION = 143.0          # 02:23 — длина ролика
_WORDS = 281               # столько слов в сценарии владельца
_COVER_MAX = 6.0           # заставка — секунды, а не полролика


def _html(path=_OVERLAY):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _scenes(html):
    """[(id, in, out, [(порядок в DOM, data-in элемента)])] по разметке сцен."""
    out = []
    for m in re.finditer(
            r'<section class="scene" id="(\w+)" data-in="([\d.]+)" data-out="([\d.]+)">',
            html):
        start = m.end()
        end = html.index("</section>", start)
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', html[start:end])]
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), cues))
    return out


# ── FR-SITE27: страница自足на, в записи и офлайн выглядит так же ──────────

def test_overlay_is_self_contained():
    html = _html()
    external = re.findall(r'(?:src|href)="(https?:)?//[^"]+"', html)
    assert not external, "оверлей тянет внешние ресурсы, в записи их не будет: %r" % external
    assert "cdn.tailwindcss.com" not in html, "оверлей не должен зависеть от Tailwind CDN"
    assert "fonts.googleapis.com" not in html, "шрифт должен лежать локально в overlay/fonts/"
    assert "unpkg.com" not in html, "иконки Phosphor должны быть вклеены инлайновым SVG"


def test_fonts_present():
    html = _html()
    files = re.findall(r"url\((fonts/[^)]+\.woff2)\)", html)
    assert len(set(files)) == 8, "ожидались 8 подмножеств Montserrat, найдено %d" % len(set(files))
    base = os.path.dirname(_OVERLAY)
    for rel in set(files):
        assert os.path.exists(os.path.join(base, rel)), "нет файла шрифта %s" % rel


# ── FR-SITE27: тайминги ──────────────────────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes(_html())
    assert len(scenes) == 3, "ожидались три сцены (слайды 1–3), найдено %d" % len(scenes)
    prev_out = 0.0
    for sid, t_in, t_out, _ in scenes:
        assert t_in < t_out, "%s: сцена начинается позже, чем кончается" % sid
        assert t_in >= prev_out, "%s: сцена наезжает на предыдущую (%s < %s)" % (sid, t_in, prev_out)
        assert t_out <= _DURATION, "%s: сцена выходит за 02:22 озвучки" % sid
        prev_out = t_out


def test_cues_are_within_scenes():
    for sid, t_in, t_out, cues in _scenes(_html()):
        assert cues, "%s: в сцене нет ни одного data-in" % sid
        for c in cues:
            assert t_in <= c < t_out, "%s: элемент на %.1fs вне окна сцены %.1f–%.1f" % (sid, c, t_in, t_out)


def test_list_items_appear_top_down():
    """Внутри списка порядок в DOM обязан совпадать с порядком озвучки: место
    под невидимый пункт зарезервировано, и пункт «не в очереди» оставил бы дыру.
    Между колонками порядок как раз перемешан — это нормально."""
    html = _html()
    for block in re.findall(r"<ul>(.*?)</ul>", html, re.S):
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', block)]
        assert cues == sorted(cues), "пункты списка появляются не сверху вниз: %r" % cues


def test_highlights_land_inside_their_scene():
    html = _html()
    for sid, t_in, t_out, _ in _scenes(html):
        start = html.index('id="%s"' % sid)
        end = html.index("</section>", start)
        for group in re.findall(r'data-hl="([\d.\s]+)"', html[start:end]):
            for t in (float(x) for x in group.split()):
                assert t_in <= t < t_out, "%s: подсветка на %.1fs вне окна сцены" % (sid, t)


# ── FR-SITE27: текст дословно из дека, своего не досочиняем ──────────────

def _labels():
    """Тексты всех подписей и пунктов оверлея."""
    html = _html()
    body = html[html.index('<div id="layer">'):html.index('<div id="guides">')]
    return [_plain(r) for r in re.findall(r"<(?:p|li)[^>]*>(.*?)</(?:p|li)>", body, re.S)]


def _plain(fragment):
    """Голый текст: <br> — это пробел, мягкий перенос не считается символом."""
    txt = re.sub(r"<br[^>]*>", " ", fragment)
    txt = re.sub(r"<[^>]+>", "", txt).replace("&shy;", "")
    return re.sub(r"\s+", " ", txt).strip()


# Владелец попросил именно эти слова вместо «Цифровая» и «Интеллектуальная»
# из дека — единственные два расхождения, все остальные тексты дословные.
_OWNER_WORDING = ("Цифровизация", "Интеллект")


def _lecture_words():
    """Все тексты дека — и из разметки, и из JS-данных.

    Дек лекции разросся и часть карточек теперь рисуется скриптом из массива,
    поэтому вырезать теги регуляркой нельзя: `<[^>]+>` съедает всё между `<` в
    JS-строке и ближайшим `>`, и текст карточек пропадает вместе с ним (так
    тест и падал после переезда дека). Берём файл целиком, снимая только то,
    что мешает сравнению: мягкие переносы, неразрывные пробелы, склейку строк.
    """
    raw = _html(_LECTURE).replace("&shy;", "").replace("&nbsp;", " ")
    raw = re.sub(r"<br[^>]*>", " ", raw)
    return re.sub(r"\s+", " ", raw)


def test_texts_match_lecture_slides():
    lecture = _lecture_words()
    for txt in _labels():
        if txt in _OWNER_WORDING:
            continue
        assert txt in lecture, "текста нет в деке лекции, значит он досочинён: %r" % txt
    assert len(_labels()) >= 14, "проверено подозрительно мало текстов (%d)" % len(_labels())


# ── FR-SITE27: переносы ──────────────────────────────────────────────────

def test_no_hyphenation_at_all():
    """Правило владельца: слова не переносятся. Значит и мягких переносов
    быть не должно — вместо них подбирается кегль, при котором слово влезает."""
    html = _html()
    assert "&shy;" not in html, "остался мягкий перенос — слова не должны переноситься"
    flat = html.replace(" ", "")
    assert "overflow-wrap:anywhere" not in flat, "anywhere рвёт слово посреди слога"
    assert "hyphens:auto" not in flat, "автоперенос запрещён"


# ── FR-SITE27: субтитры ──────────────────────────────────────────────────

def _subs():
    """[(начало, конец, текст)] из массива SUBS в скрипте страницы."""
    html = _html()
    block = html[html.index("var SUBS = ["):html.index("var DURATION")]
    return [(float(a), float(b), t) for a, b, t in
            re.findall(r"\[([\d.]+),([\d.]+),\"(.*?)\"\]", block)]


def test_subs_follow_the_transcript():
    """Реплики идут подряд, не наезжают друг на друга и укладываются в ролик.
    Ни одно слово сценария не потеряно при нарезке."""
    subs = _subs()
    assert len(subs) > 80, "субтитров подозрительно мало: %d" % len(subs)
    prev_end = -1.0
    for start, end, text in subs:
        assert start < end, "реплика %r начинается позже, чем кончается" % text
        assert start >= prev_end, "реплика %r наезжает на предыдущую" % text
        assert end <= _DURATION, "реплика %r выходит за длину ролика" % text
        prev_end = end
    assert sum(len(t.split()) for _, _, t in subs) == _WORDS, \
        "при нарезке потерялись или задвоились слова сценария"


# ── FR-SITE27: обложка, слой графики и сборка ────────────────────────────

def test_cover_precedes_the_clip():
    """Обложка идёт ПЕРЕД роликом, поэтому мастер-время сдвинуто на COVER,
    а графика и субтитры считаются от времени видео (time - COVER)."""
    html = _html()
    cover = float(re.search(r"var COVER = ([\d.]+);", html).group(1))
    assert 0 < cover <= _COVER_MAX, "странная длина заставки: %s" % cover
    assert os.path.exists(os.path.join(os.path.dirname(_OVERLAY), "cover.png")), \
        "нет файла обложки рядом со страницей"
    assert "var vt = time - COVER;" in html, "время видео не сдвинуто на заставку"
    assert "body.on-cover #layer,body.on-cover #sub,body.on-cover #scrim{display:none}" in html


def test_rendered_layer_is_present_and_split():
    """Слой графики отрендерен заранее и лежит ДВУМЯ файлами: прозрачности в
    mp4 нет, webm с альфой собирается не везде, а две дорожки в одном mp4 не
    переживают ремукс — это проверено, файл переставал декодироваться."""
    base = os.path.dirname(_OVERLAY)
    for name in ("overlay_c.mp4", "overlay_a.mp4"):
        path = os.path.join(base, name)
        assert os.path.exists(path), "нет файла слоя %s" % name
        assert os.path.getsize(path) > 200 << 10, "%s подозрительно маленький" % name


def test_page_can_be_rendered_frame_by_frame():
    """Слой рендерится покадрово, и время КАЖДОЙ анимации выставляется явно:
    иначе переходы играют по часам браузера, снимки идут медленнее реального
    времени, и все появления в слое размазываются."""
    html = _html()
    assert "window.__renderAt" in html, "нет точки входа покадрового рендера"
    assert "an.currentTime" in html, "время анимаций не выставляется явно"
    assert "document.documentElement.style.background = 'transparent'" in html, \
        "фон <html> не снят — снимок выйдет непрозрачным и слой нечем накладывать"


def test_script_burns_the_layer_into_the_frame():
    """Графику и субтитры нельзя доложить копированием дорожки — их надо
    нарисовать поверх каждого кадра. Значит одна пересборка, аппаратная где
    можно, с проверкой результата декодированием."""
    body = _html()
    body = body[body.index("function joinScript()"):body.index("var joinBtn")]
    assert "alphamerge" in body, "слой не сшивается из цвета и маски"
    assert "shortest=1" in body, \
        "без shortest длительность тянется по слою и короткий ролик раздувается"
    assert "overlay_c.mp4" in body and "overlay_a.mp4" in body, "слой не подключён"
    assert "videotoolbox" in body, "на маке пересборка должна идти аппаратно"
    assert "$ROT" in body, "поворот кадра не учитывается"
    assert "-f null" in body, "результат не проверяется декодированием"
    assert "command -v ffmpeg" in body, "скрипт должен сам сообщать о недостающих зависимостях"


def test_script_pins_clip_tracks_to_zero():
    """В MOV с телефона видеодорожка нередко начинается позже звука (edit list).
    Такой ролик, вклеенный как есть, даёт после обложки чёрный кадр: звук уже
    идёт, а картинки на шкале ещё нет. Дырка — не кадр, покадровые проверки её
    не видят, поэтому обе дорожки прижимаются к нулю явно."""
    body = _html()
    body = body[body.index("function joinScript()"):body.index("var joinBtn")]
    assert "[1:v]setpts=PTS-STARTPTS" in body, "видеодорожка ролика не прижата к нулю"
    assert "asetpts=PTS-STARTPTS" in body, "звук ролика не прижат к нулю"
    assert "aresample=async=1:first_pts=0" in body, \
        "звук не выравнивается по нулю — вернётся смещение относительно картинки"


def test_button_hands_over_the_script():
    """Сборка в браузере убрана намеренно: вжигание графики — это пересборка
    всего ролика, в wasm это десятки минут на вкладку."""
    html = _html()
    assert "joinScript()" in html and "'собрать.sh'" in html, "кнопка не отдаёт скрипт"
    base = os.path.dirname(_OVERLAY)
    assert not os.path.exists(os.path.join(base, "vendor")), \
        "остался неиспользуемый ffmpeg.wasm — 32 МБ мёртвого груза"
    assert not os.path.exists(os.path.join(base, "join.worker.js")), \
        "остался воркер сборки, которого больше нет в схеме"
    assert os.path.exists(os.path.join(base, "Запустить.command")), \
        "нет лаунчера локального сервера для офлайн-папки"


# ── FR-SITE27: служебный интерфейс не попадает в кадр ────────────────────

def test_hud_outside_stage():
    html = _html()
    stage_end = html.index('<div id="drop">')
    for panel in ('id="hud"', 'id="drop"'):
        assert html.index(panel) > stage_end, "%s лежит внутри #stage и попадёт в запись" % panel


def test_zone_stays_above_the_posters():
    """Графика не доходит до картин на стене (верх рамок — y638)."""
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    height = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top + height <= 638, "зона графики (%d..%d) доходит до картин" % (top, top + height)


# ── FR-SITE27: постоянные правила подачи ─────────────────────────────────

def _scene_css():
    """Кусок CSS, отвечающий за сцены: от правил элементов до направляющих.
    Дальше идёт служебный HUD, у него свои скругления и он в кадр не попадает."""
    style = _html()
    style = style[style.index("<style>"):style.index("</style>")]
    a = style.index("/* ── Элементы БЕЗ прямоугольных")
    b = style.index("/* ── Направляющие (?guides=1)")
    return style[a:b]


def _rules(css):
    """[(селектор, тело)] — грубого разбора хватает: вложенности здесь нет."""
    return [(m.group(1).strip(), m.group(2))
            for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


def test_no_rectangular_blocks():
    """Постоянное правило: элементы живут прямо на кадре — ни карточек, ни
    плашек, ни рамок. Единственная допустимая «оправа» — круг."""
    css = _scene_css()
    assert ".card" not in css, "вернулась карточка-подложка"
    for sel, body in _rules(css):
        # #cover — это САМ кадр (заставка на весь экран), а не элемент поверх
        # кадра: правило «без блоков» на него не распространяется.
        if "#cover" in sel:
            continue
        for radius in re.findall(r"border-radius:\s*([^;]+)", body):
            assert radius.strip() == "50%", "не круглая оправа у %s: %s" % (sel, radius)
        if re.search(r"(^|;)\s*background:", body):
            assert ".circle" in sel, "прямоугольная подложка у %s" % sel


def test_no_headings_and_no_small_print():
    """Наверху только элементы: без заголовков слайдов и без мелких пояснений.
    У элемента ровно одна подпись, и она крупная."""
    html = _html()
    body = html[html.index('<div id="layer">'):html.index('<div id="guides">')]
    for tag in ("<h1", "<h2", "<h3"):
        assert tag not in body, "вернулся заголовок %s — наверху должны быть только элементы" % tag
    for cls in ('class="hero"', 'class="sub"', 'class="note"'):
        assert cls not in body, "вернулся текстовый блок %s" % cls
    items = body.count('<div class="item')
    labels = body.count('<p class="label">')
    assert items == labels, "подписей (%d) не поровну с элементами (%d)" % (labels, items)
    assert items == 9, "ожидались 3 + 2 + 4 элемента, найдено %d" % items

    for sel, rule in _rules(_scene_css()):
        for size in re.findall(r"font-size:(\d+)px", rule):
            assert int(size) >= 24, "%s: кегль %spx — мелкий текст в кадре не нужен" % (sel, size)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Exception as e:  # AssertionError и любые сбои разбора
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    raise SystemExit(1 if failed else 0)
