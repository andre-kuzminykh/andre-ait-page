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


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


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
        first = re.search(r'<section class="screen active"[^>]*>(.*?)</section>', html, re.S).group(1)
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
        assert len(marks) >= 15, "%s: знак есть у каждого экрана, найдено %d" % (lang, len(marks))
        bodies = " ".join(marks)
        for icon in WM_ICONS:
            assert icon in bodies, "%s: нет знака главы %s" % (lang, icon)


def test_watermarks_are_faint_and_hidden_on_mobile():
    css = _css()
    assert re.search(r"\.screen\.active \.wm \{ opacity: 0\.0\d+;", css), \
        "знаки глав — еле заметные"
    assert "@media (max-width:1023px) { .wm { display: none; } }" in css, \
        "на мобилке фоновых знаков нет: только текст и кружок"


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
        assert len(screens) >= 15, "%s: биография разложена на много коротких экранов (%d)" % (lang, len(screens))
        for i, (ch, body) in enumerate(screens):
            # верхние блоки экрана помечены .reveal / .hero-rise (плюс подвал);
            # вложенные карточки и пункты списков не в счёт
            blocks = re.findall(r'<(?:h1|h2|p|div|ul) class="[^"]*(?:reveal|hero-rise|foot)"', body)
            assert 2 <= len(blocks) <= 5, \
                "%s: экран %d (%s) — %d блоков, должно быть от 2 до 5" % (lang, i, ch, len(blocks))
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
    for rule in ("p { font-size: 14px",
                 "h1 { font-size: clamp(1.75rem, 7.6vw, 2.4rem)",
                 "h2 { font-size: clamp(1.15rem, 5.2vw, 1.55rem)"):
        assert rule in block, "мобильный кегль: " + rule
    # и на вебе основной текст не мельче 13.5px
    assert "p { margin: 0 0 clamp(0.4rem, 1.15vh, 0.72rem); font-size: clamp(13.5px" in css


def test_headline_breaks_where_the_owner_wants():
    """Правило владельца: «тайтлы могут в две строки, но с красивым
    переносом» — значит перенос размечен спанами, а не отдан ширине."""
    css = _css()
    assert "h1 .l { display: block; }" in css, "строки заголовка — отдельными блоками"
    en, ru = _en(), _ru()
    assert '<span class="l">I build an <span class="hl-p">AI-native ecosystem</span></span>' in en
    assert '<span class="l">for <span class="hl-o">human good</span></span>' in en
    assert '<span class="l">Я строю <span class="hl-p">AI-Native экосистему</span></span>' in ru
    for lang, html in _pages():
        assert "querySelectorAll('h1 .l, h2')" in html, \
            lang + ": кегль подгоняется построчно, перенос не ломается"


def test_chapter_stands_in_the_middle_of_the_screen():
    """Правка владельца: глава стоит по центру экрана."""
    css = _css()
    assert "justify-content: center; justify-content: safe center;" in css, \
        "блок главы выключен по центру, но не обрезается сверху"
    assert ".finale { margin-top: auto; }" not in css, \
        "финальный экран короткий — финал стоит по центру, а не прижат к низу"


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


def test_mobile_text_fades_out_behind_the_video_circle():
    css = _css()
    assert re.search(r"\.bottom-fade \{[^}]*var\(--vid-d\)", css, re.S), \
        "низ колонки уходит в затемнение ровно под кружком"
    assert "@media (min-width:1024px) { .bottom-fade { display: none; } }" in css, \
        "на вебе затемнения снизу нет"


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
    assert ".quote.reveal.in, .note.reveal.in, .stat.reveal.in { transform: none; }" in css, \
        "сброс смещения обязан стоять ПОСЛЕ частных правил, иначе блоки налипают"


def test_data_engineer_is_bold():
    assert "<strong>Data Engineer</strong>" in _en()
    assert "<strong>инженера по данным</strong>" in _ru()


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
