# -*- coding: utf-8 -*-
"""FR-SITE40 — страница «Обо мне» (/about/ и /about/ru/).

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


# ── страницы и общая вёрстка существуют ───────────────────────────────────

def test_both_language_pages_exist():
    for rel in ("about/index.html", "about/ru/index.html", "assets/about.css"):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel


def test_pages_share_one_stylesheet():
    for lang, html in _pages():
        assert '<link rel="stylesheet" href="/assets/about.css">' in html, \
            lang + ": вёрстка должна браться из общего assets/about.css"


def test_html_lang_matches_page():
    assert '<html lang="en">' in _en()
    assert '<html lang="ru">' in _ru()


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
        assert "localStorage.setItem(LANG_KEY, LANG)" in html, lang
    assert "document.documentElement.lang === 'ru' ? 'ru' : 'en'" in _en()


def test_main_page_about_link_is_language_aware():
    html = _read("index.html")
    m = re.search(r'<a class="about-link"[^>]*>', html, re.S)
    assert m, "на главной должна быть ссылка «About me»"
    tag = m.group(0)
    assert 'data-href-en="https://andre.technology/about/"' in tag
    assert 'data-href-ru="https://andre.technology/about/ru/"' in tag


# ── FR-SITE40·1: у каждого языка свой ролик (FR-SITE28) ───────────────────

def test_each_page_uses_its_own_video():
    assert 'src="/assets/Andre_AIT_video_compressed.mp4"' in _en()
    assert 'src="/assets/Andre_AIT_video_compressed_ru.mp4"' in _ru()
    for name in ("Andre_AIT_video_compressed.mp4", "Andre_AIT_video_compressed_ru.mp4"):
        assert os.path.exists(os.path.join(_ROOT, "assets", name)), "нет ролика " + name


# ── FR-SITE40·3: видео слева + своя прокрутка текста; кружок на мобилке ───

def test_desktop_splits_video_and_reading_column():
    css = _css()
    assert re.search(r"\.media \{ position: fixed;[^}]*width: calc\(44% \+ 2px\)", css), \
        "на десктопе ролик — фиксированная колонка на 44% (плюс 2px, чтобы не было шва)"
    assert "@media (min-width:1024px) { .read { left: 44%; } }" in css, \
        "экраны с текстом занимают правую часть рядом с роликом"


def test_seam_between_video_and_text_has_no_bright_line():
    """Жалоба владельца: на стыке ролика и чёрного блестела полоска."""
    css = _css()
    assert "width: calc(44% + 2px)" in css, "ролик заходит под колонку текста"
    shade = re.search(r"\.media-shadow \{[^}]*\}", css, re.S).group(0)
    assert "#050505 93%" in shade, "чёрное в градиенте начинается до самого края"


def test_mobile_turns_the_video_into_a_round_head():
    css = _css()
    blocks = [b for b in re.findall(r"@media \(max-width:1023px\) \{.*?\n  \}", css, re.S)
              if ".media {" in b]
    assert blocks, "должен быть мобильный блок правил для ролика"
    block = blocks[0]
    assert "border-radius: 50%" in block, "на мобилке ролик — кружок"
    assert "blur(5px)" in block, "кадр размыт, пока голову не включили"
    assert ".media .speaker { display: none; }" in block or \
           ".media .media-shadow, .media .speaker { display: none; }" in block, \
        "бейдж спикера на мобилке скрыт — остаётся только кружок"


# ── FR-SITE40·4/5: меню и «назад» ────────────────────────────────────────

CHAPTERS = ["childhood", "education", "career", "startups", "ecosystem", "mission"]


def test_menu_lists_biography_chapters():
    """Сверху — главы биографии: детство, образование и так далее."""
    for lang, html in _pages():
        for key in CHAPTERS:
            assert 'data-chapter="%s"' % key in html, "%s: в меню нет главы %s" % (lang, key)
        assert html.count('class="nav-tab') == len(CHAPTERS), lang + ": в меню шесть глав"
        screens = re.findall(r'<section class="screen[^"]*" data-i="(\d+)" data-chapter="([a-z]+)"', html)
        assert len(screens) >= 6, lang + ": биография разложена по экранам"
        assert screens[0][1] == "childhood", lang + ": первый экран — про детство"


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


def test_main_page_opens_the_screen_from_the_hash():
    html = _read("index.html")
    assert "var start = (location.hash || '').replace('#', '');" in html, \
        "главная должна открывать экран из хеша"
    assert "window.addEventListener('hashchange'" in html, \
        "возврат «назад» меняет только хеш — нужен hashchange"


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
        assert 'class="home-link"' not in html, lang + ": «Back to home» внизу убран"


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
    assert re.search(r'<a class="btn-white" href="https://maturity\.andre\.technology/"[^>]*>\s*Start AI Transformation', en), \
        "в конце английской страницы — кнопка Start AI Transformation на maturity"
    assert re.search(r'<a class="btn-white" href="https://maturity\.andre\.technology/"[^>]*>\s*Начать ИИ-трансформацию', ru), \
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

WM_ICONS = ["ic-tiger", "fa-graduation-cap", "fa-coins", "fa-rocket", "fa-microchip"]


def test_chapter_watermarks_alternate_sides():
    for lang, html in _pages():
        marks = re.findall(r'<div class="wm ([lr])"[^>]*>(.*?)</div>', html, re.S)
        assert len(marks) >= 5, "%s: у экранов должны быть фоновые знаки, найдено %d" % (lang, len(marks))
        sides = [side for side, _ in marks]
        assert sides == ["l" if i % 2 == 0 else "r" for i in range(len(sides))], \
            "%s: знаки идут по очереди слева и справа, получилось %s" % (lang, sides)
        bodies = " ".join(b for _, b in marks)
        for icon in WM_ICONS:
            assert icon in bodies, "%s: нет знака главы %s" % (lang, icon)


def test_chapters_are_dense_slides():
    """Правка владельца: детство целиком на первом слайде, образование на
    втором и так далее — один слайд на главу, без пустых нарезок."""
    for lang, html in _pages():
        screens = re.findall(r'<section class="screen[^"]*" data-i="\d+" data-chapter="([a-z]+)"', html)
        assert screens[:5] == ["childhood", "education", "career", "startups", "ecosystem"], \
            "%s: порядок глав сбился: %s" % (lang, screens[:5])
        first = re.search(r'<section class="screen active".*?</section>', html, re.S).group(0)
        keep = "Intelligence creates possibilities" if lang == "en" else "Интеллект открывает возможности"
        drop = "Sometimes the strongest motivation" if lang == "en" else "Иногда самая сильная мотивация"
        assert keep in first, "%s: цитата должна быть на первом слайде" % lang
        assert drop not in html, "%s: вторую цитату владелец просил убрать" % lang
        tail = "That period shaped" if lang == "en" else "Этот период сформировал"
        assert tail not in html, "%s: хвост главы про детство убран" % lang
        last = re.findall(r'<section class="screen"[^>]*>.*?</section>', html, re.S)[-1]
        assert 'class="finale' in last and 'class="foot"' in last, \
            "%s: финал и подвал с иконками — на последнем слайде" % lang


def test_no_gradient_strip_above_headings():
    """«Без градиентных полосок сверху»: ни линии над заголовком, ни полосы прогресса."""
    css = _css()
    assert "h2::before" not in css, "над заголовком главы полоски быть не должно"
    for lang, html in _pages():
        assert 'class="progress"' not in html, lang + ": верхняя полоса прогресса убрана"


def test_biography_is_a_deck_of_screens():
    """Правило владельца: не простыня, а экраны, которые СМЕНЯЮТ друг друга —
    как разделы на главной."""
    css = _css()
    assert "overflow: hidden; width: 100vw" in css, "страница не прокручивается: это слайды"
    assert ".screen.active { display: flex; }" in css, "показан один экран"
    assert "@keyframes slideInScreen" in css, "экран приходит анимацией, как на главной"
    assert ".article.leaving .screen.active" in css, "уходящий экран анимируется"
    for lang, html in _pages():
        screens = re.findall(r'<section class="screen"[^>]*>(.*?)</section>', html, re.S)
        total = len(re.findall(r'<section class="screen[^"]*" data-i=', html))
        assert total == 6, "%s: шесть экранов, по главе (%d)" % (lang, total)
        for i, body in enumerate(screens):
            text = re.sub(r"<[^>]+>", " ", body).strip()
            assert len(text) > 40, "%s: экран %d почти пустой" % (lang, i + 1)


def test_watermarks_are_faint_and_hidden_on_mobile():
    css = _css()
    assert re.search(r"\.screen\.active \.wm \{ opacity: 0\.0\d+;", css), \
        "знаки глав — еле заметные"
    assert "@media (max-width:1023px) { .wm { display: none; } }" in css, \
        "на мобилке фоновых знаков нет: только текст и кружок"


# ── FR-SITE40·8: текст не просвечивает сквозь шапку ──────────────────────

def test_top_fade_covers_text_under_the_header():
    css = _css()
    assert ".top-fade" in css and "z-index: 29" in css, "нужна растушёвка под шапкой"
    for lang, html in _pages():
        assert '<div class="top-fade" aria-hidden="true"></div>' in html, lang


def test_density_steps_survive_the_main_site_zoom():
    """body{zoom} главной умножает вёрстку, а медиазапрос видит окно: без
    поправки на масштаб плотные главы уезжали в прокрутку на 1600 и 1920."""
    css = _read("assets/about.css")
    for w, k in (("1600px", 1.15), ("1900px", 1.3), ("2300px", 1.5)):
        assert "(min-width:%s) and (max-height:" % w in css, \
            "нет ступени плотности с поправкой на масштаб " + w
    # ступени должны стоять ПОСЛЕ акцентов, иначе базовые отступы .quote/.note
    # перебивают их по порядку следования
    assert css.index("===== Акценты") < css.index("На невысоких окнах"), \
        "ступени плотности обязаны идти после акцентов"


def test_third_density_step_covers_very_short_windows():
    """Окно высотой ~635px (владелец смотрит именно в таком): самые длинные
    главы переливались на 60–105px и уезжали в прокрутку. Третья ступень
    ужимает их целиком, включая сведённую главу «экосистема»."""
    css = _read("assets/about.css")
    for w, h in (("1024px", "730px"), ("1600px", "840px"), ("1900px", "949px"), ("2300px", "1095px")):
        assert "(min-width:%s) and (max-height:%s)" % (w, h) in css, \
            "нет третьей ступени плотности для %s/%s" % (w, h)
    third = css[css.index("третья ступень"):]
    third = third[:third.index("Очень плотный экран")]
    assert ".screen.dense p {" in third, "сведённая глава ужимается на этой ступени тоже"
    assert "padding-top: 5.1rem" in third, "шапка экрана прижата плотнее"


def test_frame_is_not_measured_in_vw():
    """vw умножается на body{zoom} — рамку страницы меряем процентами."""
    for rel in ("assets/about.css",):
        css = _read(rel)
        for m in re.finditer(r"(width|left|right): calc\([^)]*?\d+vw", css):
            raise AssertionError(rel + ": рамка в vw — " + m.group(0))


def test_quotes_are_not_clickable_or_zoomable():
    """Правка владельца: цитаты просто стоят на своих местах."""
    css = _css()
    lock = re.search(r"\.quote, \.note, \.stat \{(.*?)\}", css, re.S)
    assert lock, "нет правила, запрещающего нажатие на цитаты"
    body = lock.group(1)
    for rule in ("pointer-events: none", "user-select: none", "touch-action: manipulation"):
        assert rule in body, "у цитат нет «%s»" % rule


def test_reveal_offsets_are_reset_after_the_block_appears():
    """Корень «налипания»: у .quote/.note/.stat своя transform той же
    специфичности, и без сброса ПОСЛЕ них блок навсегда оставался смещённым."""
    css = _css()
    reset = ".quote.reveal.in, .note.reveal.in, .stat.reveal.in { transform: none; }"
    assert reset in css, "нет сброса смещения после появления"
    assert css.index(".stat.reveal {") < css.index(reset), \
        "сброс обязан идти ПОСЛЕ частных правил, иначе он ничего не значит"


def test_headline_fits_one_line_on_desktop():
    """Правка владельца: заголовок должен влезать в одну строку по шрифту."""
    for lang, html in _pages():
        assert "function fitHeadings" in html, lang + ": нет подбора кегля заголовка"
        assert "whiteSpace = 'nowrap'" in html, lang + ": заголовок набирается в одну строку"
        assert "fitHeadings(screens[cur])" in html, \
            lang + ": подбор должен работать и на показанном экране, а не только при загрузке"
        assert "!root.querySelectorAll" in html, \
            lang + ": resize передаёт событие — его нельзя принимать за узел"


def test_ecosystem_chapters_are_merged_into_one_screen():
    """Правка владельца: «Моя цель…» и «Сейчас я строю…» переехали на слайд
    про экосистему, и все три части живут на одном экране."""
    for lang, html in _pages():
        dense = re.search(r'<section class="screen dense"[^>]*>(.*?)</section>', html, re.S)
        assert dense, lang + ": нет объединённого экрана экосистемы"
        body = dense.group(1)
        marks = (("My goal became", "Now I am building", "$20M+", "Large companies")
                 if lang == "en" else
                 ("Моей целью стало", "Сейчас я создаю", "$20M+", "Крупные компании"))
        for mark in marks:
            assert mark in body, "%s: на объединённом экране нет «%s»" % (lang, mark)
    css = _css()
    assert "columns: 2" not in css, \
        "экран экосистемы должен выглядеть как остальные — в одну колонку"


def test_data_engineer_is_bold():
    assert "<strong>Data Engineer</strong>" in _en()
    assert "<strong>инженера по данным</strong>" in _ru()


def test_last_two_paragraphs_moved_to_the_mission():
    """Правка владельца: «But technology alone is not enough…» и абзац про
    университеты переехали в главу «миссия»."""
    for lang, html in _pages():
        mission = re.search(r'<section class="screen"[^>]*data-chapter="mission"[^>]*>(.*?)</section>',
                            html, re.S)
        assert mission, lang + ": нет экрана миссии"
        body = mission.group(1)
        marks = (("But technology alone is not enough", "I began collaborating with")
                 if lang == "en" else
                 ("Но одной технологии недостаточно", "начал сотрудничать"))
        for mark in marks:
            assert mark in body, "%s: в миссии нет «%s»" % (lang, mark)
        dense = re.search(r'<section class="screen dense"[^>]*>(.*?)</section>', html, re.S).group(1)
        for mark in marks:
            assert mark not in dense, "%s: «%s» осталось на экране экосистемы" % (lang, mark)


def test_chapter_heading_never_jumps_between_slides():
    """Правка владельца «чтобы ничего не скакало»: экран прижат к постоянному
    верху, поэтому заголовок главы стоит на одной высоте на всех слайдах."""
    css = _css()
    screen = re.search(r"\n  \.screen \{(.*?)\}", css, re.S)
    assert screen, "не найдено правило .screen"
    body = screen.group(1)
    assert "justify-content: flex-start" in body, "экран прижат к верху"
    assert "safe center" not in body, \
        "вертикального центрирования быть не должно — оно двигало заголовок"


def test_dense_screen_is_typeset_like_the_others():
    """Правка владельца: слайд «экосистема» не должен выглядеть мельче остальных."""
    css = _css()
    dense = re.findall(r"\.screen\.dense[^{]*\{([^}]*)\}", css)
    assert dense, "нет правил плотного экрана"
    for body in dense:
        assert "font-size" not in body, \
            "у плотного экрана не должно быть своего кегля: " + body.strip()[:70]


def test_mobile_text_fades_out_behind_the_video_circle():
    """На мобилке глава длиннее экрана и текст проезжает под кружком видео."""
    css = _css()
    assert ".bottom-fade" in css, "нет затемнения внизу колонки"
    for lang, html in _pages():
        assert 'class="bottom-fade"' in html, lang + ": нет элемента затемнения"


if __name__ == "__main__":
    import sys
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   " + name)
            except AssertionError as e:
                fails += 1
                print("FAIL " + name + ": " + str(e))
    print(("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not fails else "ПРОВАЛЕНО: %d" % fails))
    sys.exit(1 if fails else 0)
