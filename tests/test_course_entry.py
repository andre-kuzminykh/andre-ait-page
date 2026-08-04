# -*- coding: utf-8 -*-
"""Тесты входа в курс (/automation/) и правок лекции 1.

Закрепляют ровно то, что просил заказчик: один блок в фокусе, кнопка на
каждом блоке, портрет над кнопкой последнего блока, переключатель EN|RU как
на главной, отсутствие кикеров, фавиконы на всех страницах курса, заголовок
и описание модуля 1, запрет автоперехода при открытой панели текста.

Запускается и как `python3 tests/test_course_entry.py`, и через pytest.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENTRY = os.path.join(_ROOT, "automation/index.html")
_LECTURE1 = os.path.join(_ROOT, "automation/1/index.html")
_MAIN_SITE = os.path.join(_ROOT, "index.html")

_COURSE_PAGES = (
    "automation/index.html",
    "automation/main/index.html",
    "automation/roles/index.html",
    "automation/skills/index.html",
    "automation/1/practice/index.html",
) + tuple("automation/%d/index.html" % n for n in range(1, 9))


def _read(rel_or_abs):
    path = rel_or_abs if os.path.isabs(rel_or_abs) else os.path.join(_ROOT, rel_or_abs)
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Один блок в фокусе: страница не прокручивается, слои переключаются ──────

def test_page_does_not_scroll():
    html = _read(_ENTRY)
    assert re.search(r"html,body\{[^}]*overflow:hidden", html), \
        "страница должна переключать блоки, а не прокручиваться"


def test_four_blocks_switch_as_layers():
    html = _read(_ENTRY)
    ids = re.findall(r'<section class="panel[^"]*" id="([^"]+)"', html)
    assert ids == ["course", "roles", "skills", "start"], ids
    assert re.search(r"\.panel\{[^}]*position:absolute", html), "блоки — слои поверх фона"
    assert re.search(r"\.panel\{[^}]*visibility:hidden", html), "неактивный блок скрыт"
    assert re.search(r"\.panel\.on\{[^}]*visibility:visible", html), "активный блок показан"


def test_background_stays_put():
    """Фон и зерно живут вне дека, поэтому при смене блока не двигаются."""
    html = _read(_ENTRY)
    deck = html.index('<main class="deck"')
    assert html.index('<div class="grain">') < deck, "зерно должно лежать вне дека"
    assert re.search(r"body\{\s*\n?\s*background:var\(--bg\)", html), "фон задан body, не блоком"


def test_first_block_visible_without_script():
    html = _read(_ENTRY)
    assert '<section class="panel on" id="course"' in html, \
        "первый блок должен быть виден до выполнения скрипта"
    assert "<noscript>" in html, "без скрипта нужен фолбэк на обычную прокрутку"


# ── Кнопка «Начать обучение» на каждом блоке ───────────────────────────────

def test_cta_on_every_block():
    html = _read(_ENTRY)
    blocks = re.split(r'<section class="panel', html)[1:]
    assert len(blocks) == 4, len(blocks)
    for i, block in enumerate(blocks):
        assert "btn-start" in block, "на блоке %d нет кнопки «Начать обучение»" % i
        assert "https://andre.technology/automation/main" in block, \
            "кнопка блока %d должна вести на дорожную карту" % i


# ── Портрет над кнопкой последнего блока, по ширине кнопки ─────────────────

def test_portrait_only_on_last_block_above_the_button():
    html = _read(_ENTRY)
    blocks = re.split(r'<section class="panel', html)[1:]
    for i, block in enumerate(blocks[:-1]):
        assert "cta-photo" not in block, "портрет должен быть только на последнем блоке (найден в %d)" % i
    last = blocks[-1]
    assert last.index("cta-photo") < last.index("btn-start"), "портрет стоит НАД кнопкой"


def test_portrait_width_follows_the_button():
    html = _read(_ENTRY)
    assert "photo.style.width = w + 'px'" in html and "btn.offsetWidth" in html, \
        "ширина портрета берётся от кнопки"


def test_portrait_files_exist_and_markup_matches():
    from struct import unpack
    png = os.path.join(_ROOT, "automation/andre-cta.png")
    webp = os.path.join(_ROOT, "automation/andre-cta.webp")
    assert os.path.exists(png) and os.path.exists(webp), "нужны оба файла портрета"
    with open(png, "rb") as f:
        head = f.read(24)
    w, h = unpack(">II", head[16:24])
    html = _read(_ENTRY)
    m = re.search(r'class="cta-photo"[^>]*width="(\d+)" height="(\d+)"', html)
    assert m, "у портрета должны быть заявлены размеры"
    assert (int(m.group(1)), int(m.group(2))) == (w, h), \
        "размеры в разметке (%s) разошлись с файлом (%dx%d)" % (m.groups(), w, h)


# ── Кикеров 01/02 нет ──────────────────────────────────────────────────────

def test_no_kickers():
    html = _read(_ENTRY)
    for bad in ("kicker", "01 ·", "02 ·", "аудитория", "программа"):
        assert bad not in html, "кикер «%s» должен быть убран" % bad


# ── Переключатель языка — как на главной ───────────────────────────────────

def test_language_switch_matches_main_site():
    entry, site = _read(_ENTRY), _read(_MAIN_SITE)
    for marker in ('class="lang-switch"', 'class="lang-opt"', 'data-lang="en"', 'data-lang="ru"'):
        assert marker in entry and marker in site, "разметка переключателя должна повторять главную: " + marker
    assert "'ait_lang'" in entry and "'ait_lang'" in site, "ключ выбора языка общий с главной"
    assert re.search(r"\.lang-opt\.active\{", entry), "активный язык подсвечивается"


# ── Фавикон как на главной — на всех страницах курса ───────────────────────

def test_favicons_on_every_course_page():
    site = _read(_MAIN_SITE)
    icons = re.findall(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>', site)
    assert len(icons) >= 7, "на главной ожидается полный набор иконок"
    hrefs = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', site))
    for rel in _COURSE_PAGES:
        html = _read(rel)
        page_hrefs = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', html))
        assert hrefs <= page_hrefs, "%s: набор фавиконов должен совпадать с главной" % rel


# ── Модуль 1: заголовок вкладки и текст веб-превью ─────────────────────────

TITLE = "Автоматизация - Модуль 1 - Стратегия внедрения ИИ в бизнес-процессы"
DESC = ("Вы поймёте, как ИИ-агенты меняют операционную модель компании, сможете оценить "
        "уровень ИИ-зрелости бизнеса и определить, в какие процессы внедрение ИИ принесёт "
        "наибольший эффект.")


def test_lecture1_title():
    html = _read(_LECTURE1)
    assert "<title>%s</title>" % TITLE in html
    for prop in ('property="og:title"', 'name="twitter:title"'):
        assert re.search(r'<meta %s content="%s">' % (prop, re.escape(TITLE)), html), prop


def test_lecture1_preview_description():
    html = _read(_LECTURE1)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        assert re.search(r'<meta %s content="%s">' % (attr, re.escape(DESC)), html), attr


# ── Лекция: при открытом тексте автоперехода нет ───────────────────────────

def test_open_notes_panel_blocks_autoadvance():
    html = _read(_LECTURE1)
    m = re.search(r"p\.on\('ended', \(\) => \{(.*?)\}\);", html, re.S)
    assert m, "не найден обработчик окончания видео"
    body = m.group(1)
    gate = body.index("notes-open")
    advance = body.index("nextSlide()")
    assert gate < advance, "проверка открытой панели должна стоять ДО перехода к слайду"
    assert "return" in body[gate:advance], "при открытой панели обработчик должен выходить"


def test_notes_open_class_is_the_real_panel_state():
    html = _read(_LECTURE1)
    assert "classList.toggle('notes-open', open)" in html, \
        "класс notes-open должен ставиться самой панелью текста"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("\nВсе тесты входа в курс пройдены:", len(fns))
