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
    assert "localStorage.setItem(LANG_KEY, 'en')" in _en()
    assert "localStorage.setItem(LANG_KEY, 'ru')" in _ru()


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
    assert re.search(r"\.media\s*\{[^}]*position:\s*fixed[^}]*width:\s*44%", css), \
        "на десктопе ролик — фиксированная колонка на 44%"
    assert re.search(r"\.read\s*\{[^}]*margin-left:\s*44%[^}]*overflow-y:\s*auto", css, re.S), \
        "текст листается своей колонкой рядом с роликом"


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

NAV = ["strategy", "neuronium", "landao", "antropolis", "academy", "dataist", "contact"]


def test_menu_links_point_to_main_page_screens():
    for lang, html in _pages():
        for screen in NAV:
            assert 'href="/#%s"' % screen in html, \
                "%s: в меню нет пункта на экран %s" % (lang, screen)


def test_main_page_opens_the_screen_from_the_hash():
    html = _read("index.html")
    assert "var start = (location.hash || '').replace('#', '');" in html, \
        "главная должна открывать экран из хеша"
    assert "window.addEventListener('hashchange'" in html, \
        "возврат «назад» меняет только хеш — нужен hashchange"


def test_back_button_falls_back_to_home():
    for lang, html in _pages():
        assert 'id="back-btn"' in html, lang + ": нет кнопки «Назад»"
        assert "location.href = '/'" in html, \
            lang + ": при прямом заходе «Назад» ведёт на главную"


def test_logo_and_menu_are_present_on_both_pages():
    for lang, html in _pages():
        assert 'class="logo-btn" href="/"' in html, lang + ": лого ведёт на главную"
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
        assert html.count('class="quote reveal"') >= 3, lang + ": ключевые цитаты — в рамках"
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
        assert len(marks) >= 12, "%s: у экранов должны быть фоновые знаки, найдено %d" % (lang, len(marks))
        sides = [side for side, _ in marks]
        assert sides == ["l" if i % 2 == 0 else "r" for i in range(len(sides))], \
            "%s: знаки идут по очереди слева и справа, получилось %s" % (lang, sides)
        bodies = " ".join(b for _, b in marks)
        for icon in WM_ICONS:
            assert icon in bodies, "%s: нет знака главы %s" % (lang, icon)


def test_biography_is_split_into_screens():
    """Правило владельца: не простыня, а экраны — на каждом свой текст."""
    css = _css()
    assert ".screen {" in css and "min-height: 100dvh" in css, "экран занимает высоту окна"
    assert "scroll-snap-align: center" in css, "прокрутка прилипает к экрану"
    assert "scroll-snap-type: y proximity" in css, "у колонки чтения включено прилипание"
    for lang, html in _pages():
        screens = re.findall(r'<section class="screen"[^>]*>(.*?)</section>', html, re.S)
        assert len(screens) >= 12, "%s: биография должна быть разложена по экранам (%d)" % (lang, len(screens))
        for i, body in enumerate(screens):
            text = re.sub(r"<[^>]+>", " ", body).strip()
            assert len(text) > 40, "%s: экран %d почти пустой" % (lang, i + 1)


def test_watermarks_are_faint_and_hidden_on_mobile():
    css = _css()
    assert re.search(r"\.screen\.in \.wm \{ opacity: 0\.0\d+;", css), \
        "знаки глав — еле заметные"
    assert "@media (max-width:1023px) { .wm { display: none; } }" in css, \
        "на мобилке фоновых знаков нет: только текст и кружок"


# ── FR-SITE40·8: текст не просвечивает сквозь шапку ──────────────────────

def test_top_fade_covers_text_under_the_header():
    css = _css()
    assert ".top-fade" in css and "z-index: 29" in css, "нужна растушёвка под шапкой"
    for lang, html in _pages():
        assert '<div class="top-fade" aria-hidden="true"></div>' in html, lang


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
