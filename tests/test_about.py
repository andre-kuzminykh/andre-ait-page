# -*- coding: utf-8 -*-
"""FR-SITE40 — страница «Обо мне» (/about/ и /about/ru/).

Обе страницы собираются генератором tools/build_about.py из текстов
tools/about_copy.py, поэтому здесь проверяется и структура сборки, и то,
что RU с EN не разъехались.

Без зависимостей: `python3 tests/test_about.py` или через pytest.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _raw(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _read(rel):
    """Страница с обычными пробелами вместо неразрывных.

    Генератор клеит служебные слова со следующим неразрывным пробелом
    (FR-SITE42, tools/typo.py), а проверки ниже про текст, а не про перенос:
    без нормализации каждая такая проверка падала бы на \u00a0. Сам перенос
    проверяется отдельно — по сырому файлу через _raw()."""
    return _raw(rel).replace(u"\u00a0", " ").replace(u"\u2011", "-")


def _en():
    return _read("about/index.html")


def _ru():
    return _read("about/ru/index.html")


def _css():
    return _read("assets/about.css")


def _pages():
    return (("en", _en()), ("ru", _ru()))


def _screens(html):
    """Список экранов: (глава, внутренности) в порядке следования."""
    out = []
    for m in re.finditer(r'<section class="screen([^"]*)" data-i="(\d+)" data-chapter="([a-z]+)"[^>]*>(.*?)</section>',
                         html, re.S):
        out.append((m.group(3), m.group(4)))
    return out


def _mobile_blocks():
    css = _css()
    return [b for b in re.findall(r"@media \(max-width:1023px\) \{.*?\n  \}", css, re.S)]


# ── страницы собираются из одного шаблона ────────────────────────────────

def test_both_language_pages_exist():
    for rel in ("about/index.html", "about/ru/index.html", "assets/about.css",
                "tools/build_about.py", "tools/about_copy.py"):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel


def test_pages_are_generated_not_hand_written():
    """Биография живёт на двух языках: правим тексты, а не HTML, иначе
    страницы разъедутся."""
    for lang, html in _pages():
        assert "Собрано tools/build_about.py" in html.split("\n")[1], \
            lang + ": в шапке файла нет отметки о сборке"


def test_pages_share_one_stylesheet():
    for lang, html in _pages():
        assert '<link rel="stylesheet" href="/assets/about.css">' in html, \
            lang + ": вёрстка должна браться из общего assets/about.css"


def test_html_lang_matches_page():
    assert '<html lang="en">' in _en()
    assert '<html lang="ru">' in _ru()


def test_russian_and_english_pages_have_the_same_shape():
    """Тексты разные, а набор экранов и блоков — один в один."""
    en, ru = _screens(_en()), _screens(_ru())
    assert len(en) == len(ru), "разное число экранов: %d и %d" % (len(en), len(ru))
    for i, ((ch_en, body_en), (ch_ru, body_ru)) in enumerate(zip(en, ru)):
        assert ch_en == ch_ru, "экран %d: разные главы (%s / %s)" % (i, ch_en, ch_ru)
        kinds = lambda b: re.findall(r'<(h1|h2|p|div|ul) class="([a-z- ]+)"', b)
        assert kinds(body_en) == kinds(body_ru), "экран %d: разный состав блоков" % i


# ── FR-SITE40·2: EN|RU — ссылки друг на друга, язык запоминается ──────────

def test_language_switch_links_to_the_other_page():
    en, ru = _en(), _ru()
    assert '<a class="lang-opt" href="/about/ru/">RU</a>' in en, \
        "на английской странице RU — ссылка на /about/ru/"
    assert '<span class="lang-opt active">EN</span>' in en
    assert '<a class="lang-opt" href="/about/">EN</a>' in ru, \
        "на русской странице EN — ссылка на /about/"
    assert '<span class="lang-opt active">RU</span>' in ru


def test_page_stores_its_language_for_the_main_site():
    for lang, html in _pages():
        assert "localStorage.setItem(LANG_KEY, LANG)" in html, \
            lang + ": язык страницы должен запоминаться для главной"


def test_main_page_about_link_is_language_aware():
    html = _read("index.html")
    assert 'data-href-en="https://andre.technology/about/"' in html and \
           'data-href-ru="https://andre.technology/about/ru/"' in html, \
        "с главной ссылка ведёт на страницу того же языка"


def test_each_page_uses_its_own_video():
    assert 'src="/assets/Andre_AIT_video_compressed.mp4"' in _en()
    assert 'src="/assets/Andre_AIT_video_compressed_ru.mp4"' in _ru()
    for name in ("Andre_AIT_video_compressed.mp4", "Andre_AIT_video_compressed_ru.mp4"):
        assert os.path.exists(os.path.join(_ROOT, "assets", name)), "нет ролика " + name


# ── FR-SITE40·3: видео слева, текст справа; кружок на мобилке ─────────────

def test_desktop_keeps_the_same_proportions_as_the_main_site():
    """Правка владельца «сильно скрыл за чёрным»: пропорции ровно как на
    главной — ролик 67%, колонка текста 44%, кадр сдвинут влево."""
    css = _css()
    assert "--read-left: 56%" in css, "колонка текста занимает правые 44%"
    assert re.search(r"\.media \{ position: fixed;[^}]*width: 67%", css), \
        "колонка ролика шире колонки текста — её хвост уходит под чёрное"
    assert ".media video { transform: translateX(-6%); }" in css, \
        "кадр сдвинут влево так же, как #hero-video на главной"
    assert "@media (min-width:1024px) { .read { left: var(--read-left); } }" in css, \
        "экраны с текстом стоят ровно там, где кончается растушёвка"


def test_shade_starts_at_the_text_column_not_at_the_face():
    """Растушёвка отсчитывается от левого края КОЛОНКИ ТЕКСТА: замер по
    столбцам яркости на 36% ширины давал 60 против 124 у главной."""
    css = _css()
    shade = re.search(r"\.media-shadow \{[^}]*\}", css, re.S).group(0)
    assert shade.count("var(--read-left)") >= 7, "все стопы считаются от края колонки"
    assert "rgba(5,5,5,0)    calc(var(--read-left) * 0.746)" in shade, "лицо не затемняется"
    assert "#050505          calc(var(--read-left) * 1.493)" in shade, \
        "чёрное набирается уже под колонкой текста"


def test_mobile_turns_the_video_into_a_round_head():
    blocks = [b for b in _mobile_blocks() if ".media {" in b]
    assert blocks, "должен быть мобильный блок правил для ролика"
    block = blocks[0]
    assert "border-radius: 50%" in block, "на мобилке ролик — кружок"
    assert "blur(5px)" in block, "кадр размыт, пока голову не включили"
    assert ".media .media-shadow, .media .speaker { display: none; }" in block, \
        "бейдж спикера на мобилке скрыт — остаётся только кружок"


def test_video_circle_scales_with_the_window():
    """Правка владельца: «когда на компе сжимаю, голова не должна заходить за
    рамки — подтягивайся под размер экрана». Диаметр считается от МЕНЬШЕЙ
    стороны окна, поэтому на низком окне круг тоже уменьшается."""
    css = _css()
    assert "--vid-d: clamp(88px, min(34vw, 18vh), 168px);" in css, \
        "диаметр кружка тянется за меньшей стороной окна"
    assert "width: var(--vid-d); height: var(--vid-d)" in css, "кружок квадратный по --vid-d"


# ── FR-SITE40·4/5: меню и «домой» ────────────────────────────────────────

CHAPTERS = ["childhood", "education", "career", "startups", "ecosystem", "mission"]


def test_menu_lists_six_chapters_even_though_screens_are_many():
    """Экранов много, а пунктов меню по-прежнему шесть: экраны одной главы
    помечены одним data-chapter, и пункт ведёт на первый из них."""
    for lang, html in _pages():
        assert html.count('class="nav-tab') == len(CHAPTERS), lang + ": в меню шесть глав"
        screens = _screens(html)
        order = [ch for ch, _ in screens]
        # главы идут подряд и в том же порядке, что в меню
        seen = [k for i, k in enumerate(order) if i == 0 or order[i - 1] != k]
        assert seen == CHAPTERS, "%s: порядок глав сбился: %s" % (lang, seen)
        for key in CHAPTERS:
            assert order.count(key) >= 1, "%s: у главы %s нет экранов" % (lang, key)
        assert "for (var i = 0; i < screens.length; i++)" in html, \
            lang + ": пункт меню ищет ПЕРВЫЙ экран своей главы"


def test_first_screen_carries_the_tiger():
    """Тигр — на первом экране, там же, где про детство."""
    for lang, html in _pages():
        first = re.search(r'<section class="screen active[^"]*"[^>]*>(.*?)</section>', html, re.S).group(1)
        assert "ic-tiger" in first, lang + ": на первом экране должен быть тигр"


def test_screens_switch_by_wheel_swipe_and_keys():
    for lang, html in _pages():
        for hook in ("'wheel'", "'touchend'", "'keydown'", "function step(dir)"):
            assert hook in html, "%s: нет переключения экранов (%s)" % (lang, hook)
        assert "now - lastWheel < 900" in html, lang + ": один жест = один экран"


def test_home_icon_replaces_the_back_button():
    """Правка владельца: «вместо кнопки BACK иконку домой рядом с меню»."""
    css = _css()
    assert ".back" not in css, "овала «назад» больше нет"
    assert re.search(r"\.nav-home \{", css), "нет стиля иконки дома"
    for lang, html in _pages():
        assert html.count('class="nav-home" href="/"') == 1, lang + ": одна иконка дома"
        nav = html[html.index('<nav class="nav"'):html.index("</nav>")]
        assert nav.index('class="nav-home"') < nav.index('class="nav-tab'), \
            lang + ": иконка дома стоит ПЕРЕД пунктами меню"
        assert 'class="back"' not in html, lang + ": кнопок «назад» на экранах нет"


def test_logo_and_menu_are_present_on_both_pages():
    for lang, html in _pages():
        assert 'class="logo-btn" href="/"' in html, lang + ": лого ведёт на главную"
        assert 'class="brand-name"' not in html, lang + ": у лого не пишем название страницы"
        assert 'id="menu-btn"' in html, lang + ": нет кнопки меню"
        assert 'class="nav-brand-name"' in html, lang + ": нет бренд-шапки меню"
        assert "https://t.me/andre_dataist" in html, lang + ": нет соцсетей в подвале"


# ── FR-SITE40·6: акценты и финальная кнопка ──────────────────────────────

def test_cta_button_text_and_target():
    en, ru = _en(), _ru()
    assert re.search(r'<a class="btn-white" href="https://maturity\.andre\.technology/"[^>]*>Start AI Transformation', en), \
        "в конце английской страницы — кнопка Start AI Transformation на maturity"
    assert re.search(r'<a class="btn-white" href="https://maturity\.andre\.technology/"[^>]*>Начать ИИ-трансформацию', ru), \
        "в конце русской страницы — кнопка «Начать ИИ-трансформацию» на maturity"


def test_diagnostic_button_links_to_maturity():
    for lang, html in _pages():
        for m in re.finditer(r"<a class=\"btn-white cta\"[^>]*>", html):
            assert "https://maturity.andre.technology/" in m.group(0), \
                lang + ": кнопка диагностики ведёт на maturity (FR-SITE1)"


def test_quotes_and_accent_blocks_are_used():
    for lang, html in _pages():
        assert html.count('class="quote reveal"') >= 2, lang + ": ключевые цитаты — в рамках"
        assert html.count('class="stat reveal"') >= 3, lang + ": цифры — карточками"
        assert 'class="finale reveal"' in html, lang + ": нет финального блока"


def test_accent_frames_are_purple_orange():
    css = _css()
    quote = re.search(r"\.quote::before \{.*?\}", css, re.S).group(0)
    assert "#8854F3" in quote and "#F97316" in quote, \
        "рамка цитаты — фиолетово-оранжевый градиент бренда"


# ── FR-SITE40·7: фоновые знаки глав ──────────────────────────────────────

WM_ICONS = ["ic-tiger", "fa-graduation-cap", "fa-coins", "fa-rocket", "fa-microchip", "fa-star"]


def test_chapter_watermarks_sit_bottom_right():
    """Правка владельца: знаки глав — тигр, шапочка, ракета и прочие — у ВСЕХ
    глав стоят справа внизу."""
    css = _css()
    assert re.search(r"\.wm \{ position: absolute; right: 2\.5rem; bottom: 2\.6rem", css), \
        "знак главы прижат к правому нижнему углу"
    for lang, html in _pages():
        marks = re.findall(r'<div class="wm" style="--rot: [^"]+;" aria-hidden="true">(.*?)</div>', html, re.S)
        assert len(marks) == 13, "%s: знак есть у каждого экрана, найдено %d" % (lang, len(marks))
        bodies = " ".join(marks)
        for icon in WM_ICONS:
            assert icon in bodies, "%s: нет знака главы %s" % (lang, icon)


def test_watermarks_are_faint():
    """Знаки глав еле заметные. Прятать их на телефоне больше не нужно —
    владелец попросил вернуть («на мобилках нет больших иконок, а на вебе
    есть»), поэтому видимость проверяет test_chapter_marks_are_visible_on_phone."""
    css = _css()
    assert re.search(r"\.screen\.active \.wm \{ opacity: 0\.0\d+;", css), \
        "знаки глав — еле заметные"


# ── FR-SITE40·9: только по блокам, внутри экрана не листается ─────────────

def test_nothing_scrolls_inside_a_screen():
    """Правило владельца: «никакие эти страницы внутри себя не листаются —
    только по блокам»."""
    css = _css()
    screen = re.search(r"\.screen \{.*?\n    overflow: hidden;", css, re.S)
    assert screen, "экран не должен прокручиваться"
    # единственное исключение — полноэкранное МЕНЮ на маленьком телефоне
    for m in re.finditer(r"overflow-y: auto", css):
        head = css[max(0, m.start() - 400):m.start()]
        assert ".nav.open" in head, "внутри экрана не осталось прокручиваемых лент"
    for lang, html in _pages():
        assert "function innerScroll" not in html, \
            lang + ": скрипту больше не нужно искать внутреннюю прокрутку — её нет"


def test_long_chapters_are_split_into_short_screens():
    """Раз внутри не листается, длинная глава разрезана на несколько экранов,
    а не ужата кеглем: на экране заголовок и два-четыре блока."""
    for lang, html in _pages():
        screens = _screens(html)
        # FR-SITE82: владелец слил короткие экраны — их 13, самые плотные по 6 блоков
        assert len(screens) == 13, "%s: биография — 13 экранов (%d)" % (lang, len(screens))
        for i, (ch, body) in enumerate(screens):
            # верхние блоки экрана помечены .reveal / .hero-rise (плюс подвал);
            # вложенные карточки и пункты списков не в счёт
            blocks = re.findall(r'<(?:h1|h2|p|div|ul) class="[^"]*(?:reveal|hero-rise|foot)"', body)
            assert 2 <= len(blocks) <= 6, \
                "%s: экран %d (%s) — %d блоков, должно быть от 2 до 6" % (lang, i, ch, len(blocks))
            text = re.sub(r"<[^>]+>", " ", body).strip()
            assert len(text) > 40, "%s: экран %d почти пустой" % (lang, i)


def test_type_no_longer_shrinks_on_short_windows():
    """Прежние три «ступени плотности» ужимали кегль до 11px и всё равно не
    спасали. Теперь сжимается воздух: вертикальный ритм задан от высоты окна."""
    css = _css()
    assert "max-height:880px" not in css and "max-height:730px" not in css, \
        "ступени плотности убраны"
    assert ".screen.dense" not in css, "отдельного «плотного» экрана больше нет"
    for rule in ("clamp(0.4rem, 1.15vh, 0.72rem)",     # отступ абзаца
                 "clamp(5.9rem, 11vh, 7.4rem)"):        # верхнее поле экрана
        assert rule in css, "вертикальный ритм считается от высоты окна: " + rule


def test_desktop_and_mobile_share_one_large_scale():
    """Правило владельца: вёрстки две — веб и мобилка, но выглядят одинаково,
    просто в своём масштабе. Кегль телефона задан явно и крупно."""
    css = _css()
    mob = [b for b in _mobile_blocks() if "p { font-size" in b]
    assert mob, "нужен отдельный мобильный масштаб типографики"
    block = mob[0]
    # множитель --k равен 1, пока экран влезает в окно (FR-SITE82)
    for rule in ("p { font-size: calc(14px * var(--k, 1))",
                 # две строки героя при любой ширине телефона (FR-SITE82)
                 "h1 { font-size: calc(min(1.78rem, 5.58cqi) * var(--k, 1))",
                 "h2 { font-size: calc(clamp(1.15rem, 5.2vw, 1.55rem) * var(--k, 1))"):
        assert rule in block, "мобильный кегль: " + rule
    # и на вебе основной текст не мельче 13.5px
    assert "p { margin: 0 0 clamp(0.4rem, 1.15vh, 0.72rem); font-size: calc(clamp(13.5px" in css


def test_headline_breaks_where_the_owner_wants():
    """Правило владельца: «тайтлы могут в две строки, но с красивым
    переносом» — значит перенос размечен спанами, а не отдан ширине."""
    css = _css()
    assert "h1 .l { display: block; white-space: nowrap; }" in css, "строки заголовка — отдельными блоками"
    en, ru = _en(), _ru()
    assert '<span class="l">I build an <span class="hl-p"><span class="nb">AI-native</span> ecosystem</span></span>' in en
    assert '<span class="l">for <span class="hl-o">human good</span></span>' in en
    assert '<span class="l">Я строю <span class="hl-p nb">AI-Native экосистему</span></span>' in ru, \
        "«AI-Native экосистему» стоит одной строкой: на телефоне это вторая строка героя"
    for lang, html in _pages():
        assert "querySelectorAll('h1')" in html and "querySelectorAll('h2')" in html, \
            lang + ": кегль подгоняется, перенос не ломается"


def test_chapter_stands_in_the_middle_of_the_screen():
    """Правка владельца: глава стоит по центру экрана."""
    css = _css()
    assert "justify-content: center; justify-content: safe center;" in css, \
        "блок главы выключен по центру, но не обрезается сверху"
    assert ".finale { margin-top: auto; }" not in css, \
        "финальный экран короткий — финал стоит по центру, а не прижат к низу"


def test_footer_stands_at_the_bottom_of_the_last_screen():
    """Правка владельца: «2026 © Andre AI Technologies LTD — это должно быть
    внизу и иконки». Финал стоит по центру свободного места, подвал — у
    нижнего края; на телефоне нижнее поле поднимает подвал НАД кружком с
    роликом, иначе кружок накрывал левый край копирайта."""
    css = _css()
    assert ".screen.final { justify-content: flex-start; }" in css
    assert ".screen.final > h2 { margin-top: auto; }" in css and \
        ".screen.final .finale { margin-bottom: auto; }" in css, \
        "текст главы с прощанием — группой по центру, подвал уходит вниз (FR-SITE82)"
    assert ".screen.final { padding-bottom: calc(var(--vid-d) + 1.4rem" not in css, \
        "подвал стоит у самого низа: кружку разрешено его перекрывать"
    for lang, html in _pages():
        last = _screens(html)[-1][1]
        assert last.index('class="finale') < last.index('class="foot"'), lang


def test_layouts_are_only_web_and_mobile():
    """Правило владельца: «надо чтобы было только веб и мобила, а остальное
    всё адаптировалось». Значит вёрстку переключает ОДИН порог — 1024px (плюс
    1150px на меню, как на главной), а всё между ними просто масштабируется."""
    css = _css()
    # раскладка колонок меняется только на веб-пороге
    assert "@media (min-width:1024px) { .cards { grid-template-columns: 1fr 1fr; } }" in css, \
        "две карточки — признак веб-вёрстки"
    assert "min-width:640px" not in css, "промежуточной «планшетной» раскладки нет"
    assert "max-width:420px" not in css, "и отдельной раскладки для узких телефонов тоже"
    mob = [b for b in _mobile_blocks() if "max-width: 32rem" in b]
    assert mob, "на мобильной вёрстке колонка чтения не растягивается шире 32rem"
    # какие пороги вообще остались
    import re as _re
    widths = sorted(set(int(w) for w in _re.findall(r"(?:min|max)-width:\s*(\d+)px", css)))
    # 1023/1024 — сама вёрстка, 1149/1150 — меню (как на главной), 1319/1399/1439 —
    # плотность шапки, 380 — узкий телефон, 1600/1900/2300 — зум главной,
    # 600 — нижняя граница телефона В ГОРИЗОНТЕ (вместе с max-height:520px):
    # это не третья вёрстка, а та же мобильная в других пропорциях окна
    assert widths == [380, 600, 1023, 1024, 1149, 1150, 1319, 1399, 1439, 1600, 1900, 2300], \
        "лишний порог вёрстки: %s" % widths


def test_chapter_heading_wraps_as_a_whole():
    """Жалоба владельца по скриншоту окна ~498px: заголовок переносился, а
    иконка главы оставалась одна у левого края — h2 был флексом. Теперь
    иконка идёт строкой вместе с текстом, а строки делятся ровно."""
    css = _css()
    head = re.search(r"\n  h2 \{[^}]*\}", css, re.S).group(0)
    assert "display: block" in head and "text-wrap: balance" in head, \
        "заголовок — обычный блок с ровным переносом"
    assert "display: flex" not in head, "иконка больше не отдельный флекс-элемент"
    assert re.search(r"h2 i \{[^}]*margin-right: 0\.5em", css), "иконка стоит в строке"


def test_ai_native_never_splits_on_the_hyphen():
    """На 768px заголовок первого экрана рвался посреди слова: «AI- / native»."""
    assert ".nb { white-space: nowrap; }" in _css()
    assert '<span class="nb">AI-native</span>' in _en()
    # по-русски неразрывен уже весь оборот: правка владельца «„AI-Native
    # экосистему“ перенос» — термин уезжает на строку вместе с существительным
    assert '<span class="hl-p nb">AI-Native экосистему</span>' in _ru()


def test_ai_employee_areas_cover_ten_roles():
    """Правка владельца: «после менеджмента HR, после маркетинга SMM, потом
    после Sales — Support, Analytics, Design, Development и Engineering»."""
    import sys, os
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from about_copy import EN, RU
    assert [t for _i, t in EN["x4_facts"]] == [
        "Management", "HR", "Marketing", "SMM", "Sales",
        "Support", "Analytics", "Design", "Development", "Engineering"]
    assert [t for _i, t in RU["x4_facts"]] == [
        "Управление", "HR", "Маркетинг", "SMM", "Продажи",
        "Поддержка", "Аналитика", "Дизайн", "Разработка", "Инжиниринг"]
    assert len(set(i for i, _t in EN["x4_facts"])) == 10, "у каждой роли своя иконка"
    css = _css()
    assert ".facts.grid { display: grid; grid-template-columns: 1fr 1fr;" in css, \
        "десять ролей стоят в две колонки на любой ширине"


def test_no_gradient_strip_above_headings():
    """«Без градиентных полосок сверху»: ни линии над заголовком, ни полосы прогресса."""
    css = _css()
    assert "h2::before" not in css, "над заголовком главы полоски быть не должно"
    for lang, html in _pages():
        assert 'class="progress"' not in html, lang + ": верхняя полоса прогресса убрана"


def test_biography_is_a_deck_of_screens():
    css = _css()
    assert "overflow: hidden; width: 100vw" in css, "страница не прокручивается: это слайды"
    assert ".screen.active { display: flex; }" in css, "показан один экран"
    assert "@keyframes slideInScreen" in css, "экран приходит анимацией, как на главной"
    assert ".article.leaving .screen.active" in css, "уходящий экран анимируется"


def test_last_screen_is_the_finale_with_the_footer():
    for lang, html in _pages():
        last = _screens(html)[-1]
        assert last[0] == "mission", lang + ": последний экран — из главы «миссия»"
        assert 'class="finale' in last[1] and 'class="foot"' in last[1], \
            lang + ": финал и подвал с иконками — на последнем экране"


# ── FR-SITE40·8: текст не просвечивает сквозь шапку ──────────────────────

def test_top_fade_covers_text_under_the_header():
    css = _css()
    assert ".top-fade" in css and "z-index: 29" in css, "нужна растушёвка под шапкой"
    for lang, html in _pages():
        assert '<div class="top-fade" aria-hidden="true"></div>' in html, lang


def test_no_bottom_fade_over_the_chapter_mark():
    """FR-SITE82. Нижняя растушёвка гасила текст, проезжавший под кружком, —
    но внутри экрана ничего не прокручивается, а нижнее поле держит текст
    выше кружка. Осталась она только над знаком главы, который владелец
    хочет видеть в самом углу, — поэтому её нет."""
    css = _css()
    assert ".bottom-fade {" not in css, "растушёвки нет ни в одной вёрстке"
    for lang, html in _pages():
        assert 'class="bottom-fade"' not in html, lang + ": элемент растушёвки убран"


def test_frame_is_not_measured_in_vw():
    """Кадр и поля считаются от высоты и ширины окна, а не от ширины строки."""
    css = _css()
    assert "height: 100dvh" in css, "колонка ролика во всю высоту окна"


def test_quotes_are_not_clickable_or_zoomable():
    css = _css()
    assert re.search(r"\.quote, \.note, \.stat \{ pointer-events: none;", css), \
        "цитаты и врезки нельзя нажать или выделить"


def test_reveal_offsets_are_reset_after_the_block_appears():
    css = _css()
    assert ".quote.reveal.in, .note.reveal.in, .stat.reveal.in, .finale.reveal.in { transform: none; }" in css, \
        "сброс смещения обязан стоять ПОСЛЕ частных правил, иначе блоки налипают"


def test_data_engineer_is_bold():
    assert "<strong>Data Engineer</strong>" in _en()
    assert "<strong>инженера по данным</strong>" in _ru()


def test_phone_in_landscape_fits_without_scrolling():
    """Правка владельца: «в about чтобы всё тоже чётко было и при
    переворачивании в горизонталь тоже». Та же мобильная вёрстка в других
    пропорциях: кружок с роликом слева, текст правее него, кегль от высоты
    окна, блоки главы разворачиваются в ширину."""
    css = _read("assets/about.css")
    i = css.index("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)")
    block = css[i:]
    # поля симметричные: «пусть всё будет по середине по центру по горизонтали»
    assert ".screen { padding: 3.3rem calc(var(--vid-d) + 1.6rem); }" in block, \
        "текст стоит по центру между кружком и точками"
    assert "--vid-d: clamp(104px, 34vh, 150px);" in block, "кружок такой же, как в портрете"
    assert "h1 { font-size: calc(min(2.3rem, 8vh, 5.58cqi) * var(--k, 1))" in block, "кегль от высоты окна"
    assert ".facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in block, \
        "список ролей разворачивается в три колонки"


def test_chapter_text_is_left_aligned_everywhere():
    """Правка владельца: «ты по середине сделал оглавление, надо везде слева».
    Заголовок главы стоял по центру, а надзаголовок и абзацы — слева."""
    css = _read("assets/about.css")
    assert ".screen > .eyebrow, .screen > h1, .screen > h2 { text-align: left; }" in css, \
        "надзаголовок, заголовок главы и текст выключены по левому краю"
    assert ".screen > .eyebrow, .screen > h1, .screen > h2 { text-align: center; }" not in css

# ── девятнадцатый проход: переносы, подвал, палец, сироты ─────────────────

def test_function_words_are_bound_to_the_next_word():
    """FR-SITE42. Правило владельца: «ты видишь, по какому принципу я переношу
    предлоги?» — предлог, союз, частица и артикль не остаются в конце строки,
    они уезжают ВМЕСТЕ со своим словом. Технически это неразрывный пробел,
    который ставит генератор (tools/typo.py), а не правка руками."""
    nb = u"\u00a0"
    gen = _read("tools/build_about.py")
    assert "from typo import bind_copy" in gen, "переносы ставит общий модуль, а не копипаста"
    assert 'bind_copy(EN, "en")' in gen and 'bind_copy(RU, "ru")' in gen, \
        "прогоняются оба языка"
    # именно те места, которые владелец выписал по скриншотам
    for probe in (u"a" + nb + u"decade", u"that" + nb + u"still", u"but" + nb + u"discipline",
                  u"and" + nb + u"turn",
                  u"the" + nb + u"most", u"I" + nb + u"am" + nb + u"building"):
        assert probe in _raw("about/index.html"), "EN: не склеено «%s»" % probe.replace(nb, " ")
    for probe in (u"я" + nb + u"прошёл", u"не" + nb + u"могу",
                  u"в" + nb + u"систему", u"и" + nb + u"делать",
                  # притяжательные — из той же серии, нашлись замером
                  u"моё" + nb + u"представление"):
        assert probe in _raw("about/ru/index.html"), "RU: не склеено «%s»" % probe.replace(nb, " ")


def test_owner_named_line_breaks_that_are_not_prepositions():
    """Два места, где служебных слов нет, а строка всё равно разваливалась.
    «AI-Native экосистему» — термин едет на строку вместе с существительным;
    «Один вместо команды» — заголовок главы был на 27 знаков и всегда стоял
    в две строки (нужно 380px при колонке 355px)."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from about_copy import RU
    assert RU["s3_head"] == "Один вместо команды", "заголовок владельца, влезает от 320px"
    assert '<span class="hl-p nb">AI-Native экосистему</span>' in _ru()
    css = _css()
    # FR-SITE82: кегль героя считается от ширины колонки — строка с оборотом
    # целиком влезает при любой ширине телефона
    assert "h1 { font-size: calc(min(1.78rem, 5.58cqi) * var(--k, 1)); line-height: 1.14; }" in css, \
        "обе строки героя влезают при любой ширине"


def test_binder_never_touches_tags_and_metadata():
    """Неразрывный пробел нужен только в видимом тексте. Внутри тегов он ломал
    бы классы иконок и ссылки, в title — заголовок вкладки."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from typo import bind_short_words, bind_copy
    nb = u"\u00a0"
    assert bind_short_words('<i class="fa-solid fa-user"></i> a dog', "en") == \
        '<i class="fa-solid fa-user"></i> a' + nb + 'dog'
    # служебное слово на стыке с тегом — именно там рвалось «an / AI-native»
    assert bind_short_words('I build an <span>AI-native</span> world', "en") == \
        'I' + nb + 'build an' + nb + '<span>AI-native</span> world'
    src = {"title": "AI and me", "meta_desc": "a page", "lead": "a page"}
    out = bind_copy(src, "en")
    assert out["title"] == "AI and me" and out["meta_desc"] == "a page", "метаданные не трогаем"
    assert out["lead"] == "a" + nb + "page", "видимый текст склеен"


def test_finale_sits_in_the_middle_and_the_footer_at_the_bottom():
    """FR-SITE43. Правка владельца: «иконки и Andre AI Technologies должно быть
    внизу, прям перед точками, а „добро пожаловать в новую экономику“ по
    середине» — и само прощание крупнее."""
    css = _css()
    assert ".screen.final { justify-content: flex-start; }" in css
    assert ".screen.final > h2 { margin-top: auto; }" in css and \
        ".screen.final .finale { margin-bottom: auto; }" in css, \
        "группа главы с прощанием по центру свободного места, подвал внизу (FR-SITE82)"
    # Подвал у самого низа, кружку разрешено его перекрывать (FR-SITE55):
    # «кружок можно перемещать, поэтому пофигу что он там закрывает».
    assert ".screen.final { padding-bottom: calc(2.4rem + env(safe-area-inset-bottom, 0px)); }" in css, \
        "на телефоне нижний запас под кружок финалу не нужен — подвал прижат к точкам"
    # Крупнее — ровно там, где колонка это позволяет. Кегли подобраны замером
    # предела, за которым появляется лишняя строка (см. FR-SITE43):
    assert ".finale p { font-size: calc(17px * var(--k, 1)); }" in css, "телефон, английский: 14.5px → 17px (предел 20px)"
    assert 'html[lang="ru"] .finale p { font-size: calc(16px * var(--k, 1)); }' in css, \
        "телефон, русский: 14.5px → 16px (предел 16.25px на 390px)"
    assert ".finale p, html[lang=\"ru\"] .finale p { font-size: calc(clamp(13px, 3.8vh, 17px) * var(--k, 1)); }" in css, \
        "горизонт: 12.6–14.4px → 13.7–15.7px; русский селектор повторён, иначе портретное правило перебивает"
    assert ".finale p { margin: 0 0 1rem; font-size: calc(clamp(14px, min(1.15vw, 2.6vh), 18px) * var(--k, 1));" in css, \
        "в вебе кегль прежний: на 1280 по-русски предел равен старому размеру"


def test_circle_follows_a_finger():
    """FR-SITE44. «КРУЖОЧКИ НИХУЯ НЕ ДВИГАЮТСЯ». Мышью двигались, пальцем нет:
    жест забирал браузер, а путь считался по movementX, который у тача 0."""
    css = _css()
    assert ".media { touch-action: none;" in css, \
        "с manipulation браузер съедает жест и pointermove не приходит"
    js = _read("about/index.html")
    assert "e.movementX" not in js, "у тач-событий movementX всегда 0"
    assert "drag.sx" in js and "drag.sy" in js, "путь считается от точки касания"


def test_landscape_grids_have_no_orphan_row():
    """FR-SITE45. «Чтобы не торчал отдельно четвёртый пункт — значит надо два
    сверху и два снизу»: число колонок подбирается под число пунктов."""
    css = _css()
    i = css.index("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)")
    block = css[i:]
    assert ".facts:has(li:nth-child(4):last-child) { grid-template-columns: repeat(2, minmax(0, 1fr)); }" in block, \
        "четыре пункта — два ряда по два"
    assert ".facts:has(li:nth-child(7):last-child) { grid-template-columns: repeat(4, minmax(0, 1fr)); }" in block
    assert ".facts:has(li:nth-child(10):last-child) { grid-template-columns: repeat(5, minmax(0, 1fr)); }" in block


def test_runner_stands_at_the_end_of_the_file():
    """Блок запуска исполняется В МОМЕНТ, когда до него дошёл разбор файла,
    поэтому тесты, дописанные ПОСЛЕ него, молча не выполнялись — так мимо
    прогона прошли пять проверок сразу. Он должен быть последним в файле."""
    src = _raw("tests/test_about.py")
    tail = src[src.rindex('\nif __name__ == "__main__":'):]
    assert "\ndef test_" not in tail, "тесты после блока запуска не запускаются"


def test_no_coloured_glow_around_text():
    """Правка владельца: «убери это странное свечение везде». Цвет слова
    остаётся, цветной ореол вокруг букв снят."""
    css = _css()
    assert ".hl-p { color: #a071ff; }" in css and ".hl-o { color: #ff8a33; }" in css, \
        "у выделенных слов больше нет text-shadow"
    for rel in ("assets/about.css", "index.html"):
        src = _raw(rel)
        assert "text-shadow: 0 0 22px rgba(136,84,243" not in src, rel + ": остался фиолетовый ореол"
        assert "text-shadow: 0 0 22px rgba(249,115,22" not in src, rel + ": остался оранжевый ореол"


def test_chapter_marks_are_visible_on_phone():
    """Правка владельца: «на мобилках снизу внизу нет больших иконок, а на
    вебе есть». Знак главы виден и на телефоне — крупный, но еле заметный."""
    css = _css()
    assert "@media (max-width:1023px) { .wm { display: none; } }" not in css, \
        "знаки глав больше не прячутся на телефоне"
    # FR-SITE82: «на мобилах иконки большие должны быть справа внизу прям» —
    # знак в самом углу, нижней растушёвки, которая его закрашивала, больше нет
    assert ".wm { right: 1rem; bottom: calc(1.2rem + env(safe-area-inset-bottom, 0px)); font-size: min(44vw, 30vh); }" in css, \
        "в портрете знак стоит в правом нижнем углу"
    assert ".screen.active .wm { opacity: 0.075; }" in css
    land = css[css.rindex("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)"):]
    assert ".wm { bottom: 1.2rem; }" in land, "в горизонте знак стоит у нижнего края"


def test_circle_in_landscape_is_as_big_as_in_portrait():
    """Жалоба владельца «кружок на горизонталке схуяли такой маленький».
    Причина: --vid-d объявлен у `html, body`, а переопределялся только у
    `:root` — body оставался со старым значением, кружок наследовал 88px."""
    assert ":root, body { --vid-d: clamp(104px, 34vh, 150px); }" in _css()


def test_landscape_text_is_centred_and_breathes():
    """Правки владельца: «на горизонталке весь текст по середине по центру»
    и «всё налипает друг на друга»."""
    css = _css()
    block = css[css.index("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)"):]
    assert "text-align: center; padding-left: 0; }" in block, "в горизонте текст по центру"
    # FR-SITE61: правило покрывает не только прямых потомков экрана —
    # врезки, цитаты, подписи к числам и карточки тоже выключены по центру
    assert ".note p, .quote p, .stat p, .card h3, .card p {" in block, \
        "текст внутри врезок, цитат и карточек тоже по центру"
    # надзаголовок — inline-flex, text-align на него не действует
    # .eyebrow и .card h3 — оба display:flex, и text-align на них НЕ действует:
    # содержимое флекса пакуется к flex-start. Замер: «Обо мне» стояло на 227px
    # левее центра, заголовки карточек — вплотную к левому краю (зазор 0.0px,
    # смещение до −90.6px на 915×412), хотя text-align им уже был задан.
    assert ".screen > .eyebrow, .card h3 { justify-content: center; }" in block, \
        "надзаголовок и заголовок карточки центрируются свойством флекса"
    # в горизонте заголовок главы по центру, поэтому значок возвращается в строку
    assert "h2 i { position: static; width: auto; margin-right: 0.5em; font-size: 1em; }" in block
    assert ".top-fade { height: 3.4rem; }" in block, \
        "верхняя растушёвка ужата под шапку горизонта, иначе она гасит заголовок главы"
    # зазор между колонками ужат с 1.1rem: колонки были слишком узкие для
    # длинных слов, см. test_list_items_do_not_glue_prepositions
    assert "gap: 0.42rem 0.55rem;" in block, "ряды списка не слипаются (было 0.04rem)"
    assert ".facts li { line-height: 1.38; gap: 0.3rem; }" in block
    assert ".facts li { overflow-wrap: break-word; }" in block, \
        "страховка: слово длиннее колонки переломится, а не заедет на соседа"


def test_icon_sits_on_the_first_line_of_its_item():
    """«Выровни текст под иконки»: значок пункта стоит строкой той же высоты,
    что и текст, а не опускается на 0.4rem вниз."""
    css = _css()
    assert ".facts i { color: #8854F3; font-size: 1em; line-height: inherit;" in css
    assert "margin-top: 0.4rem" not in css.split(".facts i")[1][:200]


def test_one_left_edge_on_the_phone():
    """«Выровни текст под иконки»: в вертикали заголовок, абзацы и пункты
    начинаются от одной линии, значки висят слева от неё."""
    assert ".screen > p, .screen > .lead { padding-left: 1.85rem; }" in _css()


def test_startup_studio_chapter_is_renamed():
    """Правка владельца: не «Уход из корпоративного мира», а «Стартап-студия»."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from about_copy import EN, RU
    assert RU["s1_head"] == "Стартап-студия"
    assert EN["s1_head"] == "Startup Studio"
    assert "Уход из корпоративного мира" not in _ru()


def test_compound_words_never_break_at_the_hyphen():
    """Правка владельца: «топ-менеджменту» рвалось по дефису. В составных
    словах стоит неразрывный дефис U+2011 — в JetBrains Mono он той же
    ширины, что обычный, поэтому строки не сдвигаются."""
    nb = u"\u2011"
    for rel in ("about/index.html", "about/ru/index.html",
                "ai-strategy/index.html", "ai-strategy/ru/index.html"):
        assert nb in _raw(rel), rel + ": неразрывных дефисов нет"



def test_landscape_finale_has_symmetric_padding():
    """FR-SITE55: в ГОРИЗОНТЕ у финала поля сверху и снизу одинаковые.

    Портретное правило (`.screen.final`, вес 0,2,0) перебивает ландшафтное
    `.screen` (0,1,0), поэтому запас снизу приходится задавать явно — иначе
    глава стоит на 14px ниже середины окна."""
    css = _css()
    land = css[css.rindex("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)"):]
    assert ".screen.final { padding-bottom: 3.3rem; }" in land, \
        "в горизонте запас снизу равен верхнему (3.3rem)"


def test_ten_roles_fit_five_columns_in_landscape():
    """FR-SITE54.5: пять колонок по 83px — «Разработка» и «Engineering» не
    влезали и наезжали на значок соседа (замер: 6px)."""
    css = _css()
    land = css[css.rindex("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)"):]
    assert ".facts:has(li:nth-child(10):last-child) { gap: 0.3rem 0.5rem; }" in land
    assert ".facts:has(li:nth-child(10):last-child) li { font-size: calc(clamp(9px, 2.4vh, 11.5px) * var(--k, 1)); gap: 0.28rem; }" in land
    assert ".facts:has(li:nth-child(10):last-child) i { width: 0.9rem; }" in land



def test_list_items_do_not_glue_prepositions():
    """FR-SITE42 намеренно НЕ действует внутри пунктов списков (*_facts).

    Пункт списка — не проза, а ячейка узкой сетки: в горизонте телефона на
    него приходится 121px. Склейка предлога со следующим словом давала там
    неразрывный кусок шире ячейки целиком — «по\u00a0бизнес\u2011информатике»
    занимало 139px, и текст заезжал в соседнюю колонку на 18–28px (замер на
    740×360). Неразрывный дефис (FR-SITE52) при этом остаётся."""
    nb = u"\u00a0"
    ru = _raw("about/ru/index.html")
    en = _raw("about/index.html")
    assert u"Бакалавр по бизнес\u2011информатике" in ru, \
        "в пункте списка предлог отделён обычным пробелом, а дефис остался неразрывным"
    # привязываемся к самому пункту: «по бизнес-информатике» встречается и в
    # прозе (олимпиада), и там склейка как раз нужна — проверяем именно ячейку
    assert u"Бакалавр по" + nb not in ru, "предлог в пункте списка не склеен"
    assert u"after moving to Moscow" in en, "EN: пункт списка без склейки"
    assert u"moving" + nb + u"to" not in en, "EN: предлог в пункте списка не склеен"
    # а в прозе — склеен, как и просил владелец
    assert u"я" + nb + u"прошёл" in ru, "в прозе склейка предлогов осталась"




def test_chapter_title_sits_on_the_common_left_edge():
    """FR-SITE66. Правка владельца «выровни текст под иконки»: в ВЕРТИКАЛИ
    заголовок главы, абзац и пункты начинаются от одной линии.

    Значок главы инлайновый, и ширина его глифа гуляет: Font Awesome квантует
    её по 0.125em, что при кегле 20.3px даёт шаг ровно 2.53px. Текст заголовка
    плясал в пределах 43…53px, тогда как абзацы и пункты стоят намертво на
    47.2px. Замер после правки: разброс 0px на трёх размерах вертикали и обоих
    языках."""
    css = _css()
    mob = css[css.index("@media (max-width:1023px) {"):]
    assert "h2 { padding-left: 1.85rem; position: relative; }" in mob, \
        "у заголовка та же колонка значка, что у пунктов списка"
    # FR-SITE82: значок 0.82 кегля по центру первой строки — самый широкий
    # глиф не доходит до текста ближе 10px
    assert "h2 i { position: absolute; left: 0; top: calc(0.1rem + 0.2439em); width: 1.15rem;" in mob, \
        "значок вынесен в фиксированную колонку, и ширина глифа больше ни на что не влияет"




def test_owner_copy_checklist_2026_09_23():
    """FR-SITE67. Чеклист владельца по биографии: глава «Путь не был прямым»
    убрана, тексты заменены, строки разбиты там, где он сказал."""
    ru, en = _raw("about/ru/index.html"), _raw("about/index.html")
    for dead in (u"Путь не был прямым", u"компьютерного журнала", u"Not a Straight Line", u"computer magazine",
                 u"способом двигаться вперёд", u"картой движения", u"Могли двигаться невероятно быстро",
                 u"Could move incredibly fast"):
        assert dead not in ru and dead not in en, u"старый текст убран: " + dead
    for want in (u"Образование помогало мне расти.", u"дорожной картой",
                 u"Двигались очень быстро, но ресурсов хватало не на все идеи."):
        assert want in ru.replace(u"\u00a0", u" ").replace(u"\u2011", u"-"), want
    assert u"Move fast, but limited resources constrain execution." in en.replace(u"\u00a0", u" ")
    # разбивка строк — блочными .l: каждая начинается с новой строки
    assert u'<span class="l">— Дальневосточный' in ru and u'<span class="l">— Far Eastern' in en
    assert u'<span class="l">и\u00a0анализа данных' in ru or u'<span class="l">и анализа данных' in ru
    css = _css()
    assert ".screen p .l, .screen li .l { display: block; }" in css
    assert ru.count('class="screen') == en.count('class="screen') == 13, "экранов стало 13 (FR-SITE82)"



def test_owner_merged_screens_2026_09_27():
    """FR-SITE82. Правка владельца: главы слиты — «Наука и преподавание» в
    «Наука и образование», «ИИ во всём банке» в «От данных к ИИ-трансформации»,
    «Что я строил» в «Стартап-студию», «Система вместо стартапа» в «Один вместо
    команды», прощание с подвалом — в «Части одной экосистемы». Шахматы
    переименованы в «Интеллект и дисциплину». Ни один текст не потерян."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from about_copy import EN, RU
    assert RU["c2_head"] == u"Интеллект и дисциплина" and EN["c2_head"] == "Intelligence and Discipline"
    assert RU["e1_head"] == u"Наука и образование" and EN["e1_head"] == "Science and Education"
    for key in ("e2_head", "k2_head", "s2_head", "s4_head"):
        assert key not in RU and key not in EN, u"заголовок убран: " + key
    ru, en = _ru(), _en()
    for dead in (u"Наука и преподавание", u"ИИ во всём банке", u"Что я строил", u"Система вместо стартапа",
                 u"Шахматы и дисциплина", "Research and Teaching", "AI Across the Bank", "What I Built",
                 "A System, Not a Startup", "Chess and Discipline"):
        assert dead not in ru.replace(u"\u00a0", " ") and dead not in en.replace(u"\u00a0", " "), dead
    for lang, html in _pages():
        screens = _screens(html)
        assert len(screens) == 13, lang
        bodies = [b for _, b in screens]
        def screen_with(text):
            hits = [b for b in bodies if text in b]
            assert len(hits) == 1, "%s: «%s» ровно на одном экране" % (lang, text)
            return hits[0]
        c = RU if lang == "ru" else EN
        pairs = [("e1_head", ("e2_note",)), ("k1_head", ("k2_stat",)), ("s1_head", ("s2_stat",)),
                 ("s3_head", ("s4_p1",)), ("m2_head", ("finale_btn",))]
        for head, keys in pairs:
            body = screen_with(c[head].replace(" ", u"\u00a0") if c[head].replace(" ", u"\u00a0") in html else c[head])
            for k in keys:
                v = c[k][0] if isinstance(c[k], tuple) else c[k]
                probe = re.sub(r"<[^>]+>", "", v)[:6]
                assert probe in re.sub(r"<[^>]+>", "", body), "%s: %s на экране %s" % (lang, k, head)
        last = bodies[-1]
        assert 'class="finale' in last and 'class="foot"' in last, lang + ": прощание и подвал на последнем экране"
        assert c["m2_head"] in last.replace(u"\u00a0", " ") or c["m2_head"].replace(" ", u"\u00a0") in last


def test_hero_title_is_two_lines_of_one_size():
    """FR-SITE82. «„Я строю…“ в любом случае в две строчки и одинакового шрифта
    и на рус и на англ — выровни по тексту и где „Обо мне“». Шрифт
    моноширинный: самая длинная строка — английская, 30 знаков = 17.7em;
    кегль = ширина колонки / 17.9 одинаков в обеих версиях, строки не
    переносятся, а на телефоне первый экран стоит от одного края."""
    css = _css()
    assert "container-type: inline-size;" in css, "кегль героя считается от ширины колонки"
    assert "h1 { margin: 0 0 clamp(0.42rem, 1.2vh, 0.75rem); font-size: calc(min(2.7rem, 8vh, 5.58cqi) * var(--k, 1));" in css
    assert "h1 .l { display: block; white-space: nowrap; }" in css, "строка героя не переносится"
    assert ".screen.hero > p, .screen.hero > .lead { padding-left: 0; }" in css, \
        "«Обо мне», заголовок и текст первого экрана — от одного края"
    for lang, html in _pages():
        assert re.search(r'<section class="screen active hero"', html), lang
        assert "querySelectorAll('h1')" in html and "el.querySelectorAll('.l')" in html, \
            lang + ": страховка ужимает весь заголовок разом, а не одну строку"


def test_chapter_icon_is_centred_and_spaced():
    """FR-SITE82. «Иконки херово болтаются — к тексту прижимаются и сверху».
    Веб: зазор полкегля вместо 0.6rem; телефон: значок 0.82 кегля в колонке,
    по центру первой строки. Замер по пикселям: центр значка совпадает с
    центром заглавных ±1px, зазор 9.5–18.5px."""
    css = _css()
    assert "h2 i { font-size: 1em; line-height: 1; color: var(--ic, #8854F3); margin-right: 0.5em;" in css
    mob = css[css.index("@media (max-width:1023px) {"):]
    assert "font-size: 0.82em; margin-right: 0; text-align: center; }" in mob


def test_dense_screen_shrinks_instead_of_overflowing():
    """FR-SITE82. После слияния глав плотный экран на коротком телефоне или в
    горизонте выше окна. Он не обрезается и не листается: скрипт подбирает
    общий множитель кегля --k (двоичным поиском), отступы и левый край
    остаются на месте."""
    css = _css()
    assert css.count("* var(--k, 1))") >= 30, "кегль текста экрана умножается на --k"
    for lang, html in _pages():
        assert "function fitScreen(s)" in html and "s.style.setProperty('--k'" in html, lang
        assert "getComputedStyle(el).position !== 'absolute'" in html, \
            lang + ": знак главы и подвал в горизонте в высоту не считаются"
    land = css[css.rindex("@media (max-width:1023px) and (min-width:600px) and (max-height:520px)"):]
    assert ".screen.final .foot { position: absolute; left: 0; right: 0; bottom: 0.55rem;" in land, \
        "в горизонте подвал — строкой в нижнем поле"


if __name__ == "__main__":
    import sys
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except AssertionError as err:
                fails += 1
                print("FAIL", name + ":", err)
    print("ПРОВАЛЕНО:", fails) if fails else print("ВСЕ ТЕСТЫ БИОГРАФИИ ПРОЙДЕНЫ")
    sys.exit(1 if fails else 0)
