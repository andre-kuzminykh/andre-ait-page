# -*- coding: utf-8 -*-
"""Тесты лекций-презентаций /automation/1..8 (FR-SITE13, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_lectures.py`, и через pytest.

Лекции — отдельные слайд-страницы (Tailwind, Montserrat), их стиль НЕ приводится
к главной. Проверяем инварианты «портального» стиля: палитра, портальные блоки,
навигация, видео-кружок.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ALL_LECTURES = tuple("automation/%d/index.html" % n for n in range(1, 9))
# Открыт только модуль 1: лекции 2-8 закрыты и НЕ опубликованы — их файлов нет
# в репозитории, поэтому по адресу /automation/2/ отдаётся 404 и контент
# недоступен даже прямой ссылкой (это стережёт test_locked_modules_closed).
# Проверки идут по фактически опубликованным лекциям, так что вернувшийся
# модуль автоматически попадает под весь набор тестов — без правки списка.
_LECTURES = tuple(r for r in _ALL_LECTURES if os.path.exists(os.path.join(_ROOT, r)))
_VIMEO = ("automation/3/index.html", "automation/4/index.html", "automation/5/index.html")
_NATIVE_CDN = {
    "automation/6/index.html": "corp/6/videos",
    "automation/7/index.html": "corp/7/videos",
    "automation/8/index.html": "corp/8/videos",
}


def _pages(only=None):
    for rel in (only or _LECTURES):
        path = os.path.join(_ROOT, rel)
        if not os.path.exists(path):
            continue  # закрытый модуль — проверять нечего
        with open(path, encoding="utf-8") as f:
            yield rel, f.read()


# ── FR-SITE13: палитра портала, мяты старого стиля не осталось ────────────

def test_portal_palette():
    for rel, html in _pages():
        assert "solar: '#8B5CF6'" in html, rel + ": solar должен быть фиолетовым #8B5CF6"
        for mint in ("#35F0C7", "rgba(53,240,199", "rgba(53, 240, 199"):
            assert mint not in html, "%s: остался мятный цвет старого стиля (%s)" % (rel, mint)


# ── FR-SITE13: портальные блоки стиля и скриптов на месте ─────────────────

def test_portal_blocks_present():
    for rel, html in _pages():
        for block in ('id="portal-deck"', 'id="portal-dark"', 'id="lecture-chrome"',
                      'id="portal-theme"', 'id="portal-autostart"', 'id="portal-fit"',
                      'id="lecture-header"'):
            assert block in html, "%s: нет портального блока %s" % (rel, block)


# ── FR-SITE13: слайдер управляем извне (portal-fit, стрелки, свайп) ───────

def test_slider_api_and_swipe():
    for rel, html in _pages():
        for api in ("window.updateSlides", "window.nextSlide", "window.prevSlide"):
            assert api in html, "%s: %s должен выставляться на window" % (rel, api)
        # эталонный блок («Свайп-навигация») или родной свайп компактного шаблона (swipeStartX)
        assert "Свайп-навигация" in html or "swipeStartX" in html, \
            rel + ": нет свайп-навигации по слайдам"


# ── FR-SITE13: видео-кружок — источники видео корректны ───────────────────

def test_video_sources():
    for rel, html in _pages(_VIMEO):
        assert "player.vimeo.com/api/player.js" in html, rel + ": лекции 3-5 играют головы с Vimeo"
    for rel, html in _pages(tuple(_NATIVE_CDN)):
        path = _NATIVE_CDN[rel]
        assert "raw.githubusercontent.com/andre-kuzminykh/automation/" in html and path in html, \
            "%s: лекции 6-8 играют головы с CDN (%s)" % (rel, path)
    for rel, html in _pages():
        assert "{{VIDEO_SHA}}" not in html, rel + ": не подставлен SHA коммита с видео"


# ── FR-SITE13: число слайдов сходится с totalSlides ───────────────────────

def test_total_slides_consistent():
    for rel, html in _pages():
        real = html.count('class="slide-container')
        m = re.search(r"const totalSlides = (\d+);", html)
        if m:  # у лекций 7-8 totalSlides вычисляется динамически
            assert int(m.group(1)) == real, \
                "%s: totalSlides=%s, а слайдов в разметке %d" % (rel, m.group(1), real)
        else:
            assert "document.querySelectorAll('.slide-container').length" in html, \
                rel + ": totalSlides не задан ни константой, ни подсчётом DOM"
        assert real >= 30, "%s: подозрительно мало слайдов (%d)" % (rel, real)




# ── FR-SITE14: панель «Текст к слайду» ────────────────────────────────────

def test_notes_panel_present():
    for rel, html in _pages():
        for part in ('id="notes-panel-style"', 'id="notes-panel"', 'id="notes-panel-script"',
                     'id="notes-toggle"', 'id="notes-close"', 'id="slide-notes"'):
            assert part in html, "%s: нет части панели текста (%s)" % (rel, part)
        # кнопка живёт в шапке лекции, слева от переключателя темы
        assert re.search(r'<button id="notes-toggle".*?<button id="lec-theme"', html, re.S), \
            rel + ": кнопка текста должна стоять в шапке перед переключателем темы"


def test_notes_data_valid():
    import json
    for rel, html in _pages():
        m = re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>', html, re.S)
        assert m, rel + ": нет данных slide-notes"
        data = json.loads(m.group(1))
        total = html.count('class="slide-container')
        for key, note in data.items():
            assert key.isdigit() and int(key) < total, \
                "%s: ключ %r вне диапазона слайдов (0..%d)" % (rel, key, total - 1)
            for b in note.get("blocks", []):
                assert b.get("t") in ("p", "h", "ul", "ol", "note", "cards"), \
                    "%s: слайд %s — неизвестный тип блока %r" % (rel, key, b.get("t"))
                assert b.get("v"), "%s: слайд %s — пустой блок" % (rel, key)
                if b["t"] != "cards":
                    continue
                # FR-SITE14: карточка без иконки/названия рисуется пустотой
                for c in b["v"]:
                    assert re.match(r'^ph-[a-z0-9-]+$', c.get("i", "")), \
                        "%s: слайд %s — плохое имя иконки %r" % (rel, key, c.get("i"))
                    assert c.get("h") and c.get("p"), \
                        "%s: слайд %s — карточка без названия или пояснения" % (rel, key)


def test_notes_coverage():
    import json
    for rel, html in _pages():
        data = json.loads(re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>', html, re.S).group(1))
        total = html.count('class="slide-container')
        # допускаем один непокрытый слайд (финальный экран с кнопкой теста)
        assert len(data) >= total - 1, \
            "%s: текст есть только к %d слайдам из %d" % (rel, len(data), total)


def test_no_shadows():
    """FR-SITE14: теней нет нигде — правило-глушитель есть на каждой странице."""
    for rel, html in _pages():
        assert "box-shadow:none !important" in html, rel + ": нет правила, снимающего тени"
        assert "text-shadow:none !important" in html, rel + ": нет правила, снимающего text-shadow"
        assert '[class*="drop-shadow"]{ filter:none !important; }' in html, \
            rel + ": drop-shadow-утилиты Tailwind не сняты"


def test_notes_lists_are_cards():
    """FR-SITE14: пункты перечислений — карточки, маркер на уровне первой строки."""
    for rel, html in _pages():
        assert 'class="n-li"' in html, rel + ": содержимое пункта не обёрнуто (жирный ломает флекс)"
        assert re.search(r'\.notes-body ul\.n-ul li[^{]*\{[^}]*display:flex', html), \
            rel + ": пункты списка должны быть флекс-карточками"


def test_shared_blocks_identical():
    """FR-SITE15: общие блоки во всех лекциях побайтово одинаковы.

    Лекции правятся по отдельности, и блок легко разъезжается: часть правил
    попадает в одни файлы и не попадает в другие. Тест ловит это сразу.
    """
    import hashlib
    for block, tag in (("slide-polish", "style"), ("notes-panel-style", "style"),
                       ("notes-panel-script", "script"), ("radial-fig", "style"),
                       ("portal-fit", "script")):
        seen = {}
        for rel, html in _pages():
            m = re.search(r'<%s id="%s">(.*?)</%s>' % (tag, block, tag), html, re.S)
            assert m, "%s: нет блока %s" % (rel, block)
            seen.setdefault(hashlib.md5(m.group(1).encode()).hexdigest(), []).append(rel)
        assert len(seen) == 1, \
            "блок %s разъехался между лекциями: %s" % (block, list(seen.values()))


# ── FR-SITE16: термины панели и книги — по-русски, как на слайдах ─────────

_BOOK = "automation/AI_Automation Engineer_Book.txt"

# Англицизмы, у которых есть принятый русский эквивалент (см. FR-SITE16).
_ANGLICISMS = (
    "baseline", "payback", "hard savings", "cost avoidance", "capacity value",
    "unit economics", "governance", "guardrail", "human-in-the-loop", "human review",
    "adoption", "fine-tuning", "revenue uplift", "fully loaded", "utilization factor",
    "gross margin", "scalability ratio", "workflow", "reasoning", "retrieval",
    "backend", "webhook", "backlog", "circuit breaker", "refinement loop",
    "task grooming", "throughput", "headcount", "forecast", "follow-up", "upsell",
    "change management", "change request", "break-even", "infrastructure cost",
    "code generation", "fallback", "summarization", "polling", "Bearer Token",
    "Data Stewards", "Data lineage", "продакшен", "чекпоинт", "снапшот",
    "scoring-модул", "Quick wins", "Mid-term", "Long-term",
)

# Имена продуктов, нод и расшифровки аббревиатур латиницей остаются, плюс
# сознательно оставленные пояснения в скобках.
_TERM_KEEP = (
    "Retrieval-Augmented Generation", "Custom n8n Workflow Tool",
    "MCP Server Trigger", "MCP Client Tool",
    "идеальный путь (happy path)", "(touch time)", "(lead time)",
)

# «AI» остаётся только там, где это часть имени.
_AI_KEEP = (
    "AI-First", "AI-first", "AI-Native", "AI-native", "AI-Driven", "AI-driven",
    "AI-powered", "AI Maturity", "Chief AI Officer", "AI Product",
    "AI Automation Engineer", "AI Agent",
)


def _strip_keep(text, extra=()):
    # В вёрстке дефис в терминах вроде «AI-First» неразрывный (U+2011), иначе
    # строка рвалась ровно по нему и на второй оставался огрызок. Для сверки
    # словаря оба дефиса — одно и то же.
    text = text.replace("\u2011", "-")
    for keep in sorted(_TERM_KEEP + tuple(extra), key=len, reverse=True):
        text = text.replace(keep, " ")
    return text


def _notes_text(html):
    import json
    data = json.loads(re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>',
                                html, re.S).group(1))
    return json.dumps(data, ensure_ascii=False)


def test_notes_terms_are_russian():
    """Термин в панели должен читаться так же, как на слайде."""
    for rel, html in _pages():
        blob = _strip_keep(_notes_text(html))
        for word in _ANGLICISMS:
            assert not re.search(re.escape(word), blob, re.I), \
                "%s: в тексте панели остался англицизм %r" % (rel, word)
        blob = _strip_keep(blob, _AI_KEEP)
        assert not re.search(r"\bAI\b", blob), rel + ": в тексте панели остался «AI» вместо «ИИ»"


def test_book_terms_are_russian():
    """Книга — первоисточник панели, правится синхронно с ней."""
    with open(os.path.join(_ROOT, _BOOK), encoding="utf-8-sig") as f:
        blob = _strip_keep(f.read())
    for word in _ANGLICISMS:
        assert not re.search(re.escape(word), blob, re.I), \
            "книга: остался англицизм %r — панель и книга разъедутся" % word
    blob = _strip_keep(blob, _AI_KEEP)
    assert not re.search(r"\bAI\b", blob), "книга: остался «AI» вместо «ИИ»"



# ── Канон «ничего не листается» и «никакого мигания» ───────────────────────

def test_no_scrolling_anywhere():
    """Лекция — экран, а не документ: ни страница, ни слайд не прокручиваются.

    Раньше у .slide-container стоял overflow-y:auto, и любой промах подгонки
    превращался в скрытую прокрутку: заголовок уезжал под шапку, низ слайда
    терялся. Теперь не влезло = дефект подгонки, а не повод листать.
    """
    for rel, html in _pages():
        assert re.search(r"html \{[^}]*overflow: clip;", html, re.S), \
            rel + ": у html должен стоять overflow:clip (страница не едет вовсе)"
        slide = re.search(r"\.slide-container \{[^}]*\}", html, re.S)
        assert slide and "overflow-y: auto" not in slide.group(0), \
            rel + ": слайд не должен прокручиваться"
        assert "padding-block: 10px !important" not in html, \
            rel + ": вертикальные отступы content-z задаёт только portal-fit"


def test_tailwind_is_prebuilt_not_cdn():
    """Tailwind собран заранее — иначе первый кадр рисуется без стилей.

    cdn.tailwindcss.com компилирует классы в браузере уже ПОСЛЕ первой
    отрисовки: кнопки секунду выглядят «квадратными», потом становятся
    нормальными. Обычный <link> блокирует отрисовку — промежуточного кадра
    не существует.
    """
    for rel, html in _pages():
        assert "<script src=\"https://cdn.tailwindcss.com\">" not in html, \
            rel + ": Play-CDN Tailwind даёт мигание (упоминание в комментарии допустимо)"
        assert re.search(r'<link rel="stylesheet" href="/assets/lecture-[\w-]+\.css">', html), \
            rel + ": нужен статический собранный Tailwind из /assets"
        assert "window.tailwind = window.tailwind || {}" in html, \
            rel + ": рантайм-конфиг должен быть защищён от отсутствия CDN"


def test_fit_does_not_compensate_min_height():
    """min-height внутри zoom компенсировать НЕЛЬЗЯ (см. portal-fit).

    Проценты внутри zoom считаются от высоты родителя, уже переведённой в
    масштаб элемента; деление на z накладывалось второй раз и давало высоту
    600/z² — слайд становился прокручиваемым.
    """
    for rel, html in _pages():
        assert "minHeight = (100 / z)" not in html, rel + ": вернулась двойная компенсация min-height"


def test_video_circle_shows_play_icon():
    """На кружке сразу виден значок play; пауза — при наведении во время игры."""
    for rel, html in _pages(("automation/1/index.html",)):
        assert 'id="video-icon" class="ph-fill ph-play-circle' in html, \
            rel + ": по умолчанию на кружке значок play"
        assert "#video-bubble.is-playing #video-overlay{ opacity:0; }" in html, \
            rel + ": во время воспроизведения значок скрыт"
        assert "@media (hover:hover){ #video-bubble.is-playing:hover #video-overlay{ opacity:1; } }" in html, \
            rel + ": при наведении во время игры показываем паузу"


def test_head_and_arrows_do_not_cover_content_on_phones():
    """Телефон: ряд управления внизу — и подгонка резервирует под него полосу.

    Голова со стрелками стояла стопкой в правом углу (полоса ~190px) и лежала
    ПОВЕРХ текста: аудит наложений ловил её на 24 слайдах из 42 («Человек в
    центре», «Пройти тест», нижние примечания). На компьютере угол пустой и
    резерв не нужен, на телефоне — обязателен.
    """
    for rel, html in _pages(("automation/1/index.html",)):
        assert re.search(r"@media \(max-width:767px\)\{\s*\n\s*:root\{ --bub:", html), \
            rel + ": на телефоне у угла свои размеры"
        # Правка заказчика: голова крупнее и стоит НАД кнопками листания в
        # правом углу; она лежит поверх слайда и перетаскивается пальцем.
        # Канон уточнён: голова ЦЕЛИКОМ на экране (12px от правого края —
        # раньше центрировалась над стрелками и вылезала на 12px за экран),
        # а пара стрелок центрируется под головой и потому стоит левее.
        # Обвязка масштабируется --chrome-scale: он равен прежней общей формуле
        # min(по ширине, по высоте), а холст слайда в мобильной форме
        # увеличивается отдельно (FR-SITE27) — кнопки от этого не растут.
        assert "right:calc(12px * var(--chrome-scale,1)) !important;" in html, \
            rel + ": голова у правого края целиком на экране"
        assert "right:calc(12px * var(--chrome-scale,1) + var(--bub)/2 - var(--arw-pair)/2) !important;" in html, \
            rel + ": стрелки по центру под головой"
        assert "bottom:calc(24px * var(--chrome-scale,1) + var(--arw)) !important;" in html, \
            rel + ": голова стоит НАД кнопками, а не в их ряду"
        assert "mob: { w:376,  h:844, top:88,  bottom:124" in html, \
            rel + ": мобильная форма резервирует полосу под ряд управления"


def test_radial_figures_declare_their_density():
    """У каждой радиальной схемы в разметке проставлено число спутников.

    Правила `[data-sats="7"]`/`[data-sats="8"]` в таблице стилей были мёртвыми:
    атрибута в разметке не существовало, и подписи тесных схем («Инфра-
    структура», «Исследования») наезжали на соседние кружки на телефоне.
    """
    for rel, html in _pages(("automation/1/index.html",)):
        figs = re.findall(r'<div class="radial-fig[^"]*"([^>]*)>', html)
        assert figs, rel + ": не нашёл радиальных схем"
        for attrs in figs:
            assert re.search(r'data-sats="\d+"', attrs), \
                rel + ": у схемы нет data-sats — правила плотности не сработают"


def test_satellite_labels_are_single_line_everywhere():
    """Подписи радиальных схем — В ОДНУ СТРОКУ на обеих формах.

    Правка заказчика: на телефоне подписи рвались («Мультимодал/ьность»,
    «Постоянное улучшение» в 4 строки) — переносы отменены, пилюля лежит
    поверх кольца одной строкой. Стережём от возврата поздних правил с
    white-space:normal, которые перебивали базовый nowrap.
    """
    for rel, html in _pages(("automation/1/index.html",)):
        assert "white-space:normal !important" not in html.split('<style id="radial-fig">')[1].split("</style>")[0], \
            rel + ": в radial-fig не должно быть правил переноса подписей"
        assert "hyphens:none !important; max-width:none !important" in html, \
            rel + ": мобильные подписи схемы — одной строкой"


def test_two_frozen_forms_scale_only():
    """Ровно ДВЕ железные формы: веб 1440x900 и мобилка 390x844.

    Канон заказчика: раскладка внутри формы не зависит от окна — текст
    никогда не переносится иначе, элементы не едут. Реальное окно получает
    готовый холст формы, умноженный на один общий масштаб --view-scale, той
    же механикой transform:scale, какой слайд ужимается при открытой панели
    «Текст». Ресайз ничего не пересобирает — кроме пересечения границы форм.
    """
    for rel, html in _pages():
        assert "var REF = { pc:  { w:1380, h:864" in html and "mob: { w:376,  h:844" in html, \
            rel + ": две формы с фиксированными холстами"
        assert "scale(calc(var(--fit-shrink,1) * var(--view-scale,1)))" in html, \
            rel + ": окно применяется одним transform-масштабом"
        assert "var availH = g.h, availW = g.w;" in html, \
            rel + ": подгонка считает в координатах формы, не окна"
        assert "if (form() === lastForm) return;" in html, \
            rel + ": ресайз внутри формы ничего не пересобирает"
        assert "freeW / 1280" not in html, \
            rel + ": никакого расширения раскладки под ширину окна"
        assert "--bub:calc(224px * var(--chrome-scale,1))" in html, \
            rel + ": кружок с головой масштабируется коэффициентом обвязки"
        assert "function chromeScale(){" in html and \
            "return Math.min(window.innerWidth / g.w, window.innerHeight / g.h);" in html, \
            rel + ": обвязка живёт по прежней формуле min(ширина, высота)"


def test_mobile_slides_scale_up_without_stretching():
    """Мобилка в окне браузера: НЕ растягивать, а увеличивать (FR-SITE27).

    Было: холст 376×844 вписывался как min(по ширине, по высоте) — в широком
    невысоком окне (744×825) побеждала высота, слайд висел полосой на 47%
    экрана и читался мелко. Растягивать холст нельзя (заказчик: «вот так как
    справа растягивать не надо») — карточки превращаются в ленты.
    Поэтому холст остаётся КАНОНИЧЕСКИМ, а масштаб каждый слайд получает свой:
    насколько он сам может вырасти по ширине окна и по свободной высоте между
    шапкой и кружком. Обвязка масштабируется отдельным --chrome-scale и не
    раздувается.
    """
    for rel, html in _pages():
        assert "function refGeom(){ return REF[form()]; }" in html, \
            rel + ": холст канонический, без растягивания"
        assert "function slideScale(inkPainted){" in html, \
            rel + ": у каждого слайда свой масштаб холста"
        assert "var sTop = (mid - g.top * cs) / (half + off);" in html and \
            "var sBot = (mid - g.bottom * cs) / Math.max(half - off, 1);" in html, \
            rel + ": масштаб считается по фактическим краям чернил"
        assert "return Math.max(cs, Math.min(sW, sTop, sBot));" in html, \
            rel + ": мельче прежнего слайд не становится никогда"
        assert "'--chrome-scale', String(chromeScale())" in html, \
            rel + ": обвязка получает свой коэффициент"
        assert "var lift = form() === 'mob' ? 0" in html, \
            rel + ": в мобильной форме подтяжки вверх нет — иначе верх уйдёт под шапку"


def test_mobile_stacked_cards_fold_into_rows():
    """Телефон: карточка «иконка сверху» в стопке складывается в строку.

    Стопка вертикальных карточек была «простынёй» — каждая тянула высоту,
    подгонка ужимала весь слайд и текст мельчал. Строкой (иконка слева,
    текст справа — как принятый заказчиком список на входной странице)
    карточка втрое ниже.
    """
    for rel, html in _pages():
        assert "grid-template-columns:auto minmax(0,1fr);" in html, \
            rel + ": мобильная карточка — сетка «иконка | текст»"
        # Карточки размечает JS ОДИН раз на загрузке (классы js-*): цепочки
        # :has(...) пересчитывались браузером при каждой смене классов body
        # и давали задачу на ~1-1.8с при показе страницы.
        assert "function annotate()" in html, \
            rel + ": разметка карточек — один раз в JS, не в :has-селекторах"
        assert ".js-card > .js-ico{" in html and ".js-card > .js-badge{" in html, \
            rel + ": CSS матчится по готовым классам js-*"
        assert "sc.indexOf('absolute') !== -1){ if(!badge) badge = sub[m]; }" in html, \
            rel + ": абсолютный бейдж-пилюля не должен приниматься за иконку"
        assert "annotate(); syncShrink(); markActive();" in html, \
            rel + ": разметка выполняется до первой подгонки"


def test_visible_slide_never_relaid_after_reveal():
    """После появления страницы видимый слайд НЕ перекладывается.

    Заказчик дважды ловил «сначала одно положение, потом другое»: второй
    проход «общий кегль заголовков» доезжал фоном через секунду и
    пересобирал уже видимый слайд. Канон: показ — только когда шрифты
    загружены, все 42 слайда подогнаны и общий кегль применён; после показа
    проход общего кегля видимый слайд пропускает, а клик по стартовому окну
    дожимает очередь синхронно.
    """
    for rel, html in _pages():
        assert "fitAll(reveal);" in html, \
            rel + ": показ страницы ждёт завершения ВСЕЙ очереди подгонки"
        assert "function drainFits(){ chunkStep(fitEpoch, true); }" in html, \
            rel + ": очередь дорабатывается синхронно перед показом"
        assert "if(nodes[j] === live && revealed){" in html and "removeAttribute('data-fit')" in html, \
            rel + ": после показа общий кегль не трогает видимый слайд"
        # Дожим — только по НАСТОЯЩЕМУ клику: автостарт кликает по скрытому
        # оверлею программно, и синхронный дожим по нему замораживал главный
        # поток на ~1-2с (вся подгонка одной задачей).
        assert "if (e.isTrusted) reveal();" in html, \
            rel + ": живой клик по стартовому окну дожимает подгонку, автоклик — нет"
        assert "setTimeout(reveal, 1200)" not in html, \
            rel + ": страховка в 1.2с показывала страницу раньше шрифтов"


def test_fitting_is_budgeted_not_frozen():
    """Подгонка 42 слайдов не замораживает страницу.

    42 синхронных fitOne × 4 вызова на загрузке давали ~2.2с блокировки
    главного потока (замерено PerformanceObserver longtask). Теперь синхронно
    подгоняется только видимый слайд, скрытые — пачками по бюджету 8мс/кадр;
    слайд, до которого пачка не дошла, дожимает markActive при показе.
    """
    for rel, html in _pages():
        assert "performance.now() - t0 >= budget" in html, rel + ": пачки по бюджету времени"
        assert "if(revealed && active && !fitFresh(nodes[i])){ fitOne(nodes[i]); fitMark(nodes[i]); }" in html, \
            rel + ": слайд без свежей подгонки дожимается при показе"
        assert 'preload="auto"' not in html, \
            rel + ": видео не тянет мегабайты на загрузке страницы"
        if "<video " in html:  # именно тег, а не упоминание в комментарии
            assert 'preload="metadata"' in html, rel + ": у видео метаданные вместо auto"


def test_owner_canon_batch8():
    """Страж правок владельца (батч 8): тексты, однострочные подписи, широкие
    карточки, размеры кружка, центр вариантов теста. Если это сломается —
    значит кто-то откатил канон, чинить надо здесь, а не переспрашивать."""
    with open(os.path.join(_ROOT, "automation/1/index.html"), encoding="utf-8") as f:
        html = f.read()
    # RUN/CHANGE/DISRUPT: подписи зон
    for t in ('leading-none">Процессы</p>', 'leading-none">Проекты</p>', 'leading-none">Продукты</p>'):
        assert t in html, "зоны ценности подписаны Процессы/Проекты/Продукты"
    assert "Ста&shy;бильные процессы" not in html and 'leading-none">Опти&shy;мизация' not in html
    # Пять уровней — одной строкой, без переносов
    for t in ("Разговорные", "Рассуждающие", "Автономные", "Креативные", "Мультиагентные"):
        assert '<span class="whitespace-nowrap">%s</span>' % t in html, t + ": одной строкой"
    # Архитектура агента: иконка+слово неразрывны
    for t in ("Внешний мир", "Внешние API"):
        assert '<span class="whitespace-nowrap">%s</span>' % t in html, t + ": неразрывно"
    # Широкие карточные слайды (комп): маркер wide-cards
    assert html.count("content-z") >= 42
    assert html.count("wide-cards") >= 15, "широкие карточки на слайдах владельца (>=15 вхождений)"
    assert ".content-z.wide-cards{ max-width:1280px; }" in html
    # SWOT: квадраты
    assert html.count("swot-q") >= 5 and ".swot-q{ aspect-ratio:1/1; }" in html
    # Где строить своё: бейджи и тайтлы одной строкой
    for t in ("РАЗРАБАТЫВАТЬ СВОЁ", "ГОТОВЫЕ ПЛАТФОРМЫ", "Поддерживающие", "Управленческие"):
        assert '<span class="whitespace-nowrap">%s</span>' % t in html, t + ": одной строкой"
    # Разработка: тексты карточек
    assert "Сценарии поведения.<br>Где нужен код" in html
    assert "с системами и данными<br>Принятие решений" in html
    assert "Может давать первые результаты</p>" in html and "Рабочий MVP" not in html
    # Новые роли
    assert "Новые роли:<br><span" in html
    assert '<span class="whitespace-nowrap">Создание ИИ-агентов</span>' in html
    # Кружок: комп 224, мобила 170 (батчи 11-12 укрупнили со 132); на мобиле
    # он целиком на экране у правого края, стрелки по центру под ним
    # Обвязка масштабируется --chrome-scale (FR-SITE27): холст слайда в
    # мобильной форме увеличивается сам по себе, кнопки за ним не растут.
    assert "--bub:calc(224px * var(--chrome-scale,1))" in html
    assert "--bub:calc(170px * var(--chrome-scale,1))" in html
    assert "var(--bub)/2 - var(--arw-pair)/2" in html, "стрелки по центру под кружком на мобиле"
    # Финальный тест (канон уточнён батчем 10): буква и текст ВАРИАНТА слева,
    # по вертикали текст в центре кнопки; «Далее» по центру, автопрокрутка
    assert "quiz-option text-left" in html and "quiz-option text-center" not in html
    assert "flex items-center justify-start gap-3 md:gap-4" in html
    assert "tracking-widest self-center" in html
    assert "quizNextBtn.scrollIntoView" in html, "после ответа кнопка «Далее» подъезжает сама"
    # Радиалки: ядра «Цикл обучения»/«Постоянное улучшение» умерены
    assert html.count("font-size:calc(var(--lbl,14px)*.86)") == 2


def test_owner_canon_batch9():
    """Страж правок владельца (батч 9): иконки пунктов не отрываются от текста,
    «Мышление» в две строки, радиалки/уровни мельче, SWOT-квадраты на мобиле,
    подтайтл ИИ-инженера, крупная подпись на слайде обучения."""
    with open(os.path.join(_ROOT, "automation/1/index.html"), encoding="utf-8") as f:
        html = f.read()
    # Пункты «Почему ИИ-агенты»: иконка ЖИВЁТ ВНУТРИ nowrap-спана — li рендерится
    # блоком, и спан без иконки переносился, оставляя стрелку/галочку сиротой
    for t in ("Ускорение отдельных задач", "Процесс остается на человеке",
              "Самостоятельные участники", "Выполняют целые функции",
              "Иная архитектура компании", "Единая гибридная команда"):
        m = re.search(r'<span class="whitespace-nowrap"><i class="ph-bold [^"]*"></i> %s</span>' % t, html)
        assert m, t + ": иконка должна быть внутри неразрывного спана"
    assert html.count("lg:px-5 rounded-[20px]") == 3, "карточкам слайда дан запас ширины"
    # «Мышление»: две строки, хвост неразрывен
    assert '<span class="whitespace-nowrap">разбивает на шаги и планирует</span>' in html
    # Радиалки: подписи мельче (0.145), налегание на круги ушло
    assert "s1.offsetWidth * 0.145" in html and "s1.offsetWidth * 0.165" not in html
    # Пять уровней: названия на компе на шаг мельче
    assert html.count("lg:text-sm mt-1 md:mt-2 leading-none") == 4
    assert html.count("lg:text-base mt-1 md:mt-2 leading-none") == 1
    assert "lg:text-lg mt-1 md:mt-2 leading-none" not in html
    # SWOT: квадраты действуют и на мобиле — правило ВНЕ @media
    assert html.index(".swot-q{ aspect-ratio:1/1; }") < html.index(".content-z.wide-cards{ max-width:1280px; }")
    # …а на компе сетке дана ширина с перебиванием анти-overflow min-width:0
    assert '"swot-grid grid grid-cols-2' in html
    assert ".slide-container .grid.swot-grid{ min-width:24rem !important; }" in html
    assert ".swot-q{ min-height:0; }" in html
    # Слайд 13: без AI-Native в подписи зоны
    assert "Новые бизнес-модели, создание продуктов" in html
    assert "создание AI‑Native продуктов" not in html
    # ИИ-инженер: «(по автоматизации)» — видимый второй подтайтл
    assert '<span class="whitespace-nowrap">Создание ИИ-агентов</span><br><span class="whitespace-nowrap">(по автоматизации)</span>' in html
    assert '<span class="hidden">(по автоматизации)</span>' not in html
    # Обучение: «От универсального инструмента…» крупная и жирная
    # (батч 10 укрупнил ещё раз: md:text-lg → md:text-xl)
    assert '<p class="text-sm md:text-xl font-bold leading-snug"><i class="ph-fill ph-buildings' in html
    # Слайд 1: «От инструмента к агенту» — одной строкой (вопрос владельца)
    assert '<span class="whitespace-nowrap">От инструмента к агенту</span>' in html
    # Панель «Текст»: резерв под лого растёт с var(--chrome-scale) — шапка
    # зумится этим же множителем, иначе «СЛАЙД 1/42» налезает на лого (мак)
    assert "* var(--chrome-scale,1)) clamp(1rem,2.6vw,1.6rem) .85rem;" in html


def test_owner_canon_batch10():
    """Страж правок владельца (батч 10): «Дорожная карта» на SWOT-слайде шире
    и с подписью в две строки, бейдж «Эксперимент» сидит верхом на границе
    карточки, подчёркивание «С» без смещения вниз (как у «БЕЗ»)."""
    with open(os.path.join(_ROOT, "automation/1/index.html"), encoding="utf-8") as f:
        html = f.read()
    # SWOT: «Дорожная карта» шире — карте отдан весь остаток ряда (узкий
    # lg:gap-3 и стрелка text-4xl высвобождают ширину; жёсткий min-width
    # наезжал бы на стрелку — бюджет фиттера не резиновый), подпись ровно
    # в 2 строки закреплена <br>-ом
    assert '"swot-road w-full max-w-sm' in html
    assert "План от быстрых побед<br>к масштабированию" in html
    assert ".slide-container .grid.swot-grid{ flex: 0 0 24rem !important; }" in html
    assert ".slide-container .swot-road.w-full{ width: 26rem !important; flex: 0 1 auto !important; max-width: 26rem !important; }" in html
    swot_slide = html[html.index('id="slide-30"'):html.index('id="slide-31"')]
    assert "gap-4 lg:gap-3" in swot_slide, "узкий lg-зазор ряда SWOT — ширина уходит карте"
    assert "ph-arrow-right text-4xl" in swot_slide, "стрелка ужата до text-4xl ради ширины карты"
    # A/B-слайд: бейдж на границе карточки (translate -50% по вертикали),
    # на компе справа с внутренним отступом, не вылетая за правый край
    assert '"vs-exp-badge bg-solar' in html
    assert "transform: translate(-50%, -50%);" in html
    assert ".vs-exp-badge{ left: auto; right: 1.5rem; transform: translateY(-50%); }" in html
    assert 'md:absolute md:top-4 md:right-4' not in html, "старая посадка бейджа внутри карточки должна уйти"
    # Черточка под «С» — ровно как у «БЕЗ», без pb-1 (он ронял линию вниз)
    assert '<span class="border-b-2 border-solar">С</span>' in html
    assert 'border-solar pb-1">С<' not in html


def test_lecture1_web_preview_image():
    """Веб-превью лекции 1 — картинка владельца 1_lecture.jpg: она лежит в
    репозитории, на неё указывают og:image и twitter:image, а размеры в тегах
    совпадают с фактическими (соцсети верят тегам, а не качают файл)."""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:        # без PIL проверяем только разметку (как в тесте портрета)
        return
    from PIL import Image
    path = os.path.join(_ROOT, "automation/1/1_lecture.jpg")
    assert os.path.isfile(path), "нет файла automation/1/1_lecture.jpg"
    w, h = Image.open(path).size
    with open(os.path.join(_ROOT, "automation/1/index.html"), encoding="utf-8") as f:
        html = f.read()
    url = "https://andre.technology/automation/1/1_lecture.jpg"
    for tag in ('<meta property="og:image" content="%s">' % url,
                '<meta property="og:image:secure_url" content="%s">' % url,
                '<meta name="twitter:image" content="%s">' % url,
                '<meta property="og:image:width" content="%d">' % w,
                '<meta property="og:image:height" content="%d">' % h,
                '<meta name="twitter:card" content="summary_large_image">'):
        assert tag in html, "нет тега: " + tag
    assert "assets/1_long.jpg" not in html, "старая картинка превью должна уйти"


# ── Доступ к модулям 2-8 закрыт (правка владельца) ────────────────────────

def _published_pages():
    """Все страницы/скрипты сайта, которые реально отдаются с Pages."""
    skip = {".git", "tests", "tools", ".github", ".pytest_cache"}
    for base, dirs, files in os.walk(_ROOT):
        dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".")]
        for name in files:
            if name.endswith((".html", ".js", ".json", ".xml", ".txt", ".webmanifest")):
                path = os.path.join(base, name)
                with open(path, encoding="utf-8", errors="ignore") as f:
                    yield os.path.relpath(path, _ROOT), f.read()


def test_process_practice_page():
    """Практика «разбор бизнес-процесса» (FR-SITE28): шаги, примеры, окно, CTA."""
    rel = "automation/practice/process/index.html"
    path = os.path.join(_ROOT, rel)
    assert os.path.exists(path), "страница практики должна лежать в " + rel
    with open(path, encoding="utf-8") as f:
        html = f.read()

    # четыре шага задания
    for n in range(1, 5):
        assert "Шаг %d" % n in html, rel + ": нет шага %d" % n
    for title in ("бизнес-цель, метрику и границы", "AS-IS", "BPMN",
                  "узкие места и точки автоматизации", "TO-BE"):
        assert title in html, rel + ": потерян блок «%s»" % title
    for mode in ("Простое правило", "ИИ-агент", "Человек", "Гибрид"):
        assert ">%s<" % mode in html, rel + ": нет варианта «%s»" % mode
    assert "Human-in-the-Loop" in html

    # какой процесс взять — не список готовых процессов, а критерии выбора
    # «низковисящего фрукта» из лекции: те же пять, что и в первом задании
    for crit in ("заметно влияет на бизнес-результат",
                 "не требует большого количества интеграций",
                 "зависит от минимального числа сотрудников",
                 "использует доступные и структурированные данные",
                 "может быть реализован с помощью готовых ИИ-моделей"):
        assert crit in html, rel + ": нет критерия «%s»" % crit
    assert "«низковисящий фрукт»" in html, rel + ": не назван сам фреймворк"
    assert "picks" not in html, rel + ": трёх процессов-кандидатов здесь больше нет"
    # хиро перечисляет и граф навыков агента
    assert "графа навыков агента" in html, rel + ": в результат не входит граф навыков агента"
    assert "не список идей" not in html, rel + ": лишний абзац про «на выходе» убран"

    # шесть отраслей + «свой процесс» — одним окном
    keys = re.findall(r'<button class="v-tab[^"]*" role="tab" data-key="([a-z]+)"', html)
    assert keys == ["consult", "hr", "marketing", "callcenter", "design", "software"], keys
    assert "v-own" not in html, rel + ": отдельной вкладки «свой процесс» быть не должно"
    for k in keys:
        assert '<pre class="mmd-src" id="src-%s">' % k in html, rel + ": нет исходника схемы " + k
        assert '<div class="case-info" id="info-%s"' % k in html, rel + ": нет описания " + k
    # схемы — классические sequenceDiagram: участники в блоках box, фазы в
    # rect, ветвления alt/opt/loop, нумерация шагов (FR-SITE28)
    sources = html[html.index('<div id="mmd-sources"'):html.index('<div class="viewer"')]
    per = re.findall(r'<pre class="mmd-src" id="src-(\w+)">(.*?)</pre>', sources, re.S)
    assert len(per) == 6, rel + ": исходников должно быть шесть"
    for key, code in per:
        assert code.lstrip().startswith("sequenceDiagram"), rel + ": %s — не sequenceDiagram" % key
        assert "\nautonumber" in code, rel + ": %s — нет автонумерации шагов" % key
        assert code.count("\nbox rgba(") == 2, rel + ": %s — нужны блоки внешних и внутренних" % key
        assert code.count("\nrect rgba(") >= 4, rel + ": %s — фазы процесса не выделены" % key
        assert "rgb(" not in code.replace("rgba(", ""), \
            rel + (": %s — непрозрачный цвет; на тёмной теме это белый прямоугольник" % key)
        # узкие места отмечены прямо в схеме и подписаны одинаково
        assert len(re.findall(r"note over [^:]+: Узкое место:", code)) >= 3, \
            rel + ": %s — в схеме меньше трёх узких мест" % key
        assert re.search(r"\n(alt|opt|loop) ", code), rel + ": %s — нет ветвлений" % key
    assert "flowchart" not in sources, rel + ": примеры процессов — sequenceDiagram, не flowchart"

    # главный CTA — инструмент ИИ-стратегии
    cta = "https://strategy.andre.technology/ai-strategy"
    assert html.count(cta) >= 3, rel + ": CTA в шапке, после шагов и после примеров"
    assert "if (history.length > 1) history.back(); else location.href = FALLBACK;" in html
    assert "family=Montserrat" in html and "unpkg.com" not in html
    for color in ("#8B5CF6", "#F97316", "#4C1D95"):
        assert color in html, rel + ": цвет " + color
    assert re.search(r"\*, \*::before, \*::after\{ box-shadow:none !important", html), \
        rel + ": теней быть не должно"
    assert "localStorage.getItem('welcome-theme')" in html


def test_process_practice_viewer():
    """Одно окно: масштаб, перетаскивание, своя схема, ошибки, сохранение."""
    rel = "automation/practice/process/index.html"
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        html = f.read()

    # путь «интервью → схема» и готовый промт
    for step in ("Проведите интервью", "Запишите и расшифруйте", "Отправьте промт AS-IS",
                 "Вставьте код в окно выше", "Отправьте промт TO-BE", "Отрисуйте TO-BE и сравните"):
        assert step in html, rel + ": нет шага «%s»" % step
    assert "Свой процесс" not in html, rel + ": вкладки «Свой процесс» нет — ссылаться на неё нельзя"
    prompt = html[html.index('id="prompt-src"'):html.index("</pre>", html.index('id="prompt-src"'))]
    for must in ("sequenceDiagram", "autonumber", "box rgba(", "rect", "alt/else",
                 "Узкое место:", "СЮДА ВСТАВЬТЕ ТЕКСТ ИНТЕРВЬЮ", "ТОЛЬКО код mermaid"):
        assert must in prompt, rel + ": в промте AS-IS нет «%s»" % must
    # второй промт: схема AS-IS → точки автоматизации, роль человека, TO-BE
    tobe = html[html.index('id="prompt-tobe"'):html.index("</pre>", html.index('id="prompt-tobe"'))]
    for must in ("Точки автоматизации", "Новая роль человека", "Навыки будущего агента",
                 "TO-BE", "СЮДА ВСТАВЬТЕ КОД СХЕМЫ ИЗ ОКНА ВЫШЕ"):
        assert must in tobe, rel + ": во втором промте нет «%s»" % must
    # кнопка в окне подставляет в этот промт схему, которая сейчас открыта
    assert 'id="v-tobe"' in html and "СЮДА ВСТАВЬТЕ КОД СХЕМЫ ИЗ ОКНА ВЫШЕ', (input.value" in html, \
        rel + ": «промт TO-BE» должен подставлять код открытой схемы"

    # окно: масштаб кнопками и колесом, перетаскивание, «по размеру»
    for el in ('id="v-stage"', 'id="v-layer"', 'id="v-level"', 'data-zoom="in"',
               'data-zoom="out"', 'data-zoom="fit"'):
        assert el in html, rel + ": в окне нет " + el
    # листается обычной прокруткой по обеим осям: колесо, тачпад, палец,
    # полоса, клавиши. Вертикальную прокрутку не перехватываем — она нужна
    # чаще всего (FR-SITE28)
    assert re.search(r"\.v-stage\{[^}]*overflow:auto", html), rel + ": схема прокручивается сама"
    assert "stage.addEventListener('wheel'" in html, rel + ": колесо обслуживается"
    assert "const canY = stage.scrollHeight > stage.clientHeight + 2;" in html \
        and "if(canY) return;" in html, \
        rel + ": пока есть куда листать вниз, колесо листает вниз, а не вбок"
    assert "if(e.ctrlKey || e.metaKey){" in html, rel + ": Ctrl+колесо — масштаб, как в браузере"
    assert "if(e.target.closest('.v-btn, .v-tools, .v-save')) return;" in html, \
        rel + ": перетаскивание не должно начинаться на кнопках"
    assert "stage.scrollTop  = grab.top  - (e.clientY - grab.y);" in html, \
        rel + ": перетаскивание работает и по вертикали"
    # схема подгоняется по ширине окна, но не мельче 75%: ниже подписи не
    # прочесть, и тогда остаётся прокрутка вбок
    assert "function startView(){" in html and "sizeTo(Math.min(Math.max(kW, 0.75), 1.15));" in html, \
        rel + ": стартовый масштаб — по ширине окна в границах 75-115%"
    # окно шире текстовой колонки: sequenceDiagram в 864px не читается
    assert "@media (min-width:1180px){ .viewer{ width:1100px;" in html \
        and "@media (min-width:1420px){ .viewer{ width:1340px;" in html, \
        rel + ": на больших экранах окно со схемой выходит за колонку"
    # 100vw включает полосу прокрутки: окно во всю ширину экрана дало бы
    # горизонтальный перелив страницы. В комментариях слово допустимо.
    assert "100vw" not in re.sub(r"/\*.*?\*/", "", html, flags=re.S), \
        rel + ": ширина окна считается от колонки, а не в vw"
    assert "el.style.width  = Math.round(natW * k) + 'px';" in html, \
        rel + ": масштаб — реальный размер SVG, текст остаётся резким"
    # центрирование: safe — иначе верх переполнившей схемы уходит туда,
    # докуда прокрутка не достаёт, и первый шаг оказывается срезан
    assert "align-content:center;   align-content:safe center;" in html, \
        rel + ": мелкая схема по центру, крупная — от начала, без срезанного верха"
    assert "margin:auto" not in html[html.index(".v-layer{"):html.index(".v-layer{") + 200], \
        rel + ": центрирование margin:auto прячет верх схемы — только safe center"
    # узлы на краю растворяются, а не срезаются ножом — по всем четырём кромкам
    assert ".v-fade-l{ left:0; background:linear-gradient(to right,var(--diagram-bg),transparent); }" in html
    for cls in ("has-left", "has-right", "has-up", "has-down"):
        assert "shell.classList.toggle('%s'" % cls in html, \
            rel + ": нет растушёвки для " + cls
    # рисуется ровно то, что в поле: направление схемы больше не подменяем
    assert "forView" not in html, rel + ": код рисуется как есть, без подмены направления"
    assert "await mermaid.render('v-svg-' + Date.now(), code);" in html, \
        rel + ": рисуется ровно тот код, что показан в поле"
    # «целиком» показывает всю схему; за край её не увести — прокрутка сама
    # держится в границах ленты
    assert "function fitAll(){" in html and 'data-zoom="fit"' in html, \
        rel + ": кнопка «целиком» показывает схему полностью"
    assert "clampView" not in html, \
        rel + ": ручной панорамы с упорами больше нет — листает обычная прокрутка"
    # sequenceDiagram: без своих переменных темы подписи остаются тёмными на
    # тёмном, а перенос строк держит ширину схемы в разумных пределах
    for v in ("signalTextColor:", "actorTextColor:", "labelTextColor:", "loopTextColor:",
              "noteBkgColor:", "noteTextColor:"):
        assert v in html, rel + ": в теме нет переменной " + v
    assert "sequence: { wrap: true" in html, rel + ": без переноса одна подпись растягивает всю схему"
    # узкие места видно сразу: заметка «Узкое место…» перекрашивается в оранжевый
    assert "function markBottlenecks(){" in html and "const BN = /^\\s*узкое место/i;" in html, \
        rel + ": узкие места должны выделяться в отрисованной схеме"
    assert "rect.style.setProperty('fill', bg, 'important');" in html, \
        rel + ": у mermaid своё правило для .note — атрибут покраски не переживёт"
    # подсказка висит над схемой, поэтому она в плашке с фоном
    assert re.search(r"\.v-hint\{[^}]*background:var\(--card\)", html), \
        rel + ": подсказка на фоне, иначе наезжает на узлы"

    # поле кода одно и всегда редактируемое, кнопки «показать схему» нет
    for el in ('id="v-input"', 'id="v-copy"'):
        assert el in html, rel + ": в панели кода нет " + el
    for gone in ('id="v-draw"', 'id="v-example"', 'id="v-src"'):
        assert gone not in html, rel + ": лишний элемент " + gone + " — код рисуется сам"
    assert "input.addEventListener('input'" in html and "window.renderDiagrams(true); }, 500);" in html, \
        rel + ": правка кода перерисовывает схему сама, без кнопки"
    assert "const SAVE_KEY = 'ait-mermaid-draft';" in html, rel + ": черновик переживает перезагрузку"
    assert "await mermaid.parse(code);" in html, rel + ": код проверяется до отрисовки"

    # ошибка показывается и превращается в промт на исправление
    assert 'id="v-err-text"' in html and 'id="v-fixprompt"' in html
    assert "Исправь только сломанное место" in html
    assert "Библиотека mermaid не загрузилась" in html

    # сохранение картинки
    assert "canvas.toBlob" in html and "image/svg+xml" in html, rel + ": сохранение SVG и PNG"
    assert "rect.setAttribute('fill', dark ? '#0A0A0A' : '#FFFFFF');" in html, \
        rel + ": в файл подкладывается фон, иначе схема в документе невидима"

    # окно рисует не только flowchart — об этом сказано рядом с полем кода
    for kind in ("sequenceDiagram", "stateDiagram-v2", "classDiagram", "erDiagram",
                 "gantt", "mindmap", "timeline", "pie"):
        assert kind in html, rel + ": в списке поддерживаемых типов нет " + kind


def test_locked_modules_closed():
    """Открыт только модуль 1. Лекций 2-8 нет в репозитории — значит их нет и в
    артефакте Pages: по адресу /automation/2/ отдаётся 404, контент недоступен
    даже прямой ссылкой (не редирект и не спрятанный CSS-ом слой, из которого
    исходник всё равно вычитывается). Архив контента — тег lectures-2-8-archive.
    """
    assert os.path.exists(os.path.join(_ROOT, "automation/1/index.html")), \
        "модуль 1 открыт и должен быть опубликован"
    for n in range(2, 9):
        assert not os.path.exists(os.path.join(_ROOT, "automation/%d" % n)), \
            "модуль %d закрыт: каталога automation/%d не должно быть в репозитории" % (n, n)


def test_no_links_to_locked_modules():
    """Ни одна опубликованная страница не ведёт на закрытый модуль — на сайте
    нет ссылок, которые упирались бы в 404."""
    link = re.compile(r"automation/[2-8](?=[/\"'#?)\s]|$)")
    for rel, text in _published_pages():
        hits = link.findall(text)
        assert not hits, "%s: ссылка на закрытый модуль (%s)" % (rel, hits[:3])


def test_locked_module_cards_have_no_href():
    """Карточки модулей 2-8 на /automation/main/ — под замком и без href."""
    with open(os.path.join(_ROOT, "automation/main/index.html"), encoding="utf-8") as f:
        html = f.read()
    cards = re.findall(r'<a class="module( locked)?"([^>]*)>', html)
    assert len(cards) == 8, "на главной курса восемь карточек модулей"
    opened = [c for c in cards if not c[0]]
    assert len(opened) == 1 and "href=" in opened[0][1], "открыт ровно один модуль — первый"
    for locked, attrs in [c for c in cards if c[0]]:
        assert "href=" not in attrs, "закрытая карточка не должна иметь href: " + attrs
        assert 'aria-disabled="true"' in attrs, "закрытая карточка помечена aria-disabled"


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
