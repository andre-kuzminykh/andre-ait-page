# -*- coding: utf-8 -*-
"""Тесты входа в курс (две языковые страницы) и правок лекции 1.

Закрепляют ровно то, что просил заказчик:
  · две страницы — английская `/automation/` и русская `/automation_ru/` —
    у каждой свой заголовок и своё веб-превью, переключатель EN|RU ходит
    между ними;
  · один блок в фокусе, кнопка «Начать обучение» на каждом блоке;
  · портрет над кнопкой последнего блока — по её ширине и вплотную к её
    верхней кромке, без просвета;
  · внутри блока листать нечего: прокрутки нет ни у страницы, ни у блока;
  · заголовок и описание модуля 1, запрет автоперехода при открытой панели.

Запускается и как `python3 tests/test_course_entry.py`, и через pytest.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from tools.build_course_entry import build, RU, EN, URL_EN, URL_RU, PATH_EN, PATH_RU  # noqa: E402

_EN_PAGE = "automation/index.html"
_RU_PAGE = "automation_ru/index.html"
_ENTRIES = (_EN_PAGE, _RU_PAGE)
_LECTURE1 = os.path.join(_ROOT, "automation/1/index.html")
_MAIN_SITE = os.path.join(_ROOT, "index.html")

_COURSE_PAGES = (
    _EN_PAGE,
    _RU_PAGE,
    "automation/main/index.html",
    "automation/roles/index.html",
    "automation/skills/index.html",
    "automation/1/practice/index.html",
) + tuple("automation/%d/index.html" % n for n in range(1, 9))


def _read(rel_or_abs):
    path = rel_or_abs if os.path.isabs(rel_or_abs) else os.path.join(_ROOT, rel_or_abs)
    with open(path, encoding="utf-8") as f:
        return f.read()


def _blocks(html):
    parts = re.split(r'<section class="panel', html)[1:]
    assert len(parts) == 3, len(parts)
    return parts


# ── Обе страницы собраны из одного шаблона ─────────────────────────────────

def test_pages_match_the_template():
    """Руками страницы не правят: они пересобираются из tools/build_course_entry.py."""
    for rel, expected in build().items():
        assert _read(rel) == expected, (
            "%s разошёлся с шаблоном — запустите python3 tools/build_course_entry.py" % rel
        )


def test_both_languages_have_their_own_page():
    assert _read(_EN_PAGE).startswith('<!DOCTYPE html>\n<html lang="en">')
    assert _read(_RU_PAGE).startswith('<!DOCTYPE html>\n<html lang="ru">')


def test_pages_are_structurally_identical():
    """Языки расходятся только текстами — вёрстка, стили и скрипт общие."""
    en, ru = _read(_EN_PAGE), _read(_RU_PAGE)
    for page in (en, ru):
        assert re.findall(r'<section class="panel[^"]*" id="([^"]+)"', page) == \
            ["course", "roles", "skills"]
    style = lambda h: h[h.index("<style>"):h.index("</style>")]          # noqa: E731
    assert style(en) == style(ru), "стили должны быть одинаковыми"
    body = lambda h: h[h.index("<script>\n    function storeGet"):h.index("</script>\n</body>")]  # noqa: E731
    # скрипт различается только кодом языка — его и обезличиваем
    blind = lambda s: s.replace("'en'", "'@'").replace("'ru'", "'@'")       # noqa: E731
    assert blind(body(en)) == blind(body(ru)), "поведение страниц должно быть одинаковым"


# ── Веб-превью: свой заголовок и своё описание на каждый язык ──────────────

RU_TITLE = "Курс по автоматизации бизнес-процессов с помощью ИИ-агентов"


def test_ru_preview_title_is_what_the_customer_asked_for():
    html = _read(_RU_PAGE)
    assert "<title>%s</title>" % RU_TITLE in html
    for attr in ('property="og:title"', 'name="twitter:title"'):
        assert '<meta %s content="%s">' % (attr, RU_TITLE) in html, attr


def test_ru_preview_description_says_who_it_is_for():
    html = _read(_RU_PAGE)
    desc = RU["desc"]
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        assert '<meta %s content="%s">' % (attr, desc) in html, attr
    for who in ("ИИ-консультант", "ИИ-инженер", "ИИ-основател"):
        assert who in desc, "описание должно называть, для кого курс: " + who


def test_en_page_has_its_own_preview():
    html = _read(_EN_PAGE)
    assert "<title>%s</title>" % EN["title"] in html
    assert '<meta name="description" content="%s">' % EN["desc"] in html
    assert EN["desc"] != RU["desc"] and EN["title"] != RU["title"], \
        "у страниц должны быть РАЗНЫЕ веб-превью"


def test_canonical_and_hreflang():
    for rel, url in ((_EN_PAGE, URL_EN), (_RU_PAGE, URL_RU)):
        html = _read(rel)
        assert '<link rel="canonical" href="%s">' % url in html, rel
        assert '<link rel="alternate" hreflang="en" href="%s">' % URL_EN in html, rel
        assert '<link rel="alternate" hreflang="ru" href="%s">' % URL_RU in html, rel
        assert '<link rel="alternate" hreflang="x-default" href="%s">' % URL_EN in html, rel
    assert '<meta property="og:locale" content="ru_RU">' in _read(_RU_PAGE)
    assert '<meta property="og:locale" content="en_US">' in _read(_EN_PAGE)


def test_og_url_points_at_its_own_page():
    assert '<meta property="og:url" content="%s">' % URL_EN in _read(_EN_PAGE)
    assert '<meta property="og:url" content="%s">' % URL_RU in _read(_RU_PAGE)


# ── Переключатель языка ходит между страницами ─────────────────────────────

def test_language_switch_navigates_between_pages():
    """Ссылки — от корня сайта: так они живые и на проде, и в локальном превью."""
    en, ru = _read(_EN_PAGE), _read(_RU_PAGE)
    assert '<a class="lang-opt active" data-lang="en" href="%s"' % PATH_EN in en
    assert '<a class="lang-opt" data-lang="ru" href="%s"' % PATH_RU in en
    assert '<a class="lang-opt active" data-lang="ru" href="%s"' % PATH_RU in ru
    assert '<a class="lang-opt" data-lang="en" href="%s"' % PATH_EN in ru


def test_language_switch_matches_main_site_markup():
    site = _read(_MAIN_SITE)
    for marker in ('class="lang-switch"', 'class="lang-opt"', 'data-lang="en"', 'data-lang="ru"'):
        for rel in _ENTRIES:
            assert marker in _read(rel), "разметка переключателя должна повторять главную: " + marker
        assert marker in site
    for rel in _ENTRIES:
        html = _read(rel)
        assert "'ait_lang'" in html, "ключ выбора языка общий с главной"
        assert re.search(r"\.lang-opt\.active\{", html), "активный язык подсвечивается"


def test_saved_language_takes_the_visitor_to_his_page():
    for rel, other in ((_EN_PAGE, PATH_RU), (_RU_PAGE, PATH_EN)):
        html = _read(rel)
        assert "location.replace('%s'" % other in html, rel
        assert "ait_lang_hop" in html, "авто-переход срабатывает один раз за вкладку"


def test_main_site_course_link_follows_the_language():
    site = _read(_MAIN_SITE)
    assert 'data-href-en="%s"' % URL_EN in site and 'data-href-ru="%s"' % URL_RU in site
    assert "querySelectorAll('[data-href-ru]')" in site, \
        "главная должна переключать ссылку на курс вместе с языком"


# ── Один блок в фокусе: ни страница, ни блок не прокручиваются ─────────────

def test_page_does_not_scroll():
    for rel in _ENTRIES:
        assert re.search(r"html,body\{[^}]*overflow:hidden", _read(rel)), rel


def test_block_does_not_scroll_inside_itself():
    """Заказчик: блоки листаются только целиком, внутри блока прокрутки нет."""
    for rel in _ENTRIES:
        html = _read(rel)
        assert re.search(r"\.panel\{[^}]*overflow:hidden", html), rel
        assert "overflow-y:auto" not in html, "внутренней прокрутки у блока в стилях быть не должно"
        assert "function fit(p)" in html, "блок, не влезший в экран, должен ужиматься, а не листаться"
        assert "scrollBy" not in html and "scrollTop" not in html, \
            "в скрипте не должно остаться прокрутки блока"


def test_four_blocks_switch_as_layers():
    for rel in _ENTRIES:
        html = _read(rel)
        assert re.search(r"\.panel\{[^}]*position:absolute", html), "блоки — слои поверх фона"
        assert re.search(r"\.panel\{[^}]*visibility:hidden", html), "неактивный блок скрыт"
        assert re.search(r"\.panel\.on\{[^}]*visibility:visible", html), "активный блок показан"


def test_background_stays_put():
    """Фон и зерно живут вне дека, поэтому при смене блока не двигаются."""
    for rel in _ENTRIES:
        html = _read(rel)
        deck = html.index('<main class="deck"')
        assert html.index('<div class="grain">') < deck, "зерно должно лежать вне дека"
        assert re.search(r"body\{\s*\n?\s*background:var\(--bg\)", html), "фон задан body"


def test_first_block_visible_without_script():
    for rel in _ENTRIES:
        html = _read(rel)
        assert '<section class="panel on" id="course"' in html, rel
        assert "<noscript>" in html, "без скрипта нужен фолбэк на обычную прокрутку"


def test_one_gesture_is_one_block():
    """Хвост инерции тачпада не листает лишнего, а новый толчок не глотается."""
    for rel in _ENTRIES:
        html = _read(rel)
        for name in ("var THRESH", "var QUIET", "var REARM", "var RISE_MIN", "var RISE_LEN"):
            assert name in html, "%s: нет %s" % (rel, name)
        assert "armed" in html, "жест взводит курок ровно один раз"
        assert "e.deltaMode === 1" in html, "дельту колеса надо нормализовать по deltaMode"
        # хвост инерции затухает не строго: на плато нестрогое сравнение взводило
        # курок само, и один взмах уводил дек через два блока на третий
        assert "a > prevAbs" in html and "a >= prevAbs" not in html, \
            "новый толчок опознаётся по СТРОГО растущей дельте"
        assert "(t - firedAt) > 700" not in html, \
            "взвода курка «по таймеру» быть не должно — хвост идёт кадрами по 16 мс"
        # снятие курка обнуляет накопитель, поэтому знак читается ДО него
        m = re.search(r"var dir = accum > 0(.*?)go\(dir\);", html, re.S)
        assert m and "disarmWheel();" in m.group(1), \
            "%s: направление должно читаться ДО disarmWheel() — он обнуляет accum" % rel
        assert "t - wheelAt < COOL" in html, \
            "%s: колесо не должно менять блок чаще, чем раз в COOL мс" % rel
        # …но потолок действует только ВНУТРИ потока. Щелчок мышиного колеса
        # приходит после паузы — это заведомо новое намерение, и глотать его
        # нельзя, иначе срабатывает лишь каждый второй щелчок.
        assert "!quietArm && t - wheelAt < COOL" in html, \
            "%s: потолок COOL не должен глотать изолированный щелчок мыши" % rel
        assert "armWheel(true)" in html and "armWheel(false)" in html, \
            "%s: взвод паузой и взвод ростом дельты различаются" % rel
        # смена блока чем угодно (точка, клавиша, кнопка) тоже снимает курок —
        # иначе хвост инерции доводил дек дальше уже после осознанного выбора
        assert re.search(r"firedAt = t;\n\s*disarmWheel\(\);", html), \
            "%s: jump() должен снимать курок колеса" % rel


# ── Кнопка «Начать обучение» на каждом блоке ───────────────────────────────

def test_cta_on_every_block():
    for rel in _ENTRIES:
        for i, block in enumerate(_blocks(_read(rel))):
            assert "btn-start" in block, "%s: на блоке %d нет кнопки" % (rel, i)
            assert "https://andre.technology/automation/main" in block, \
                "%s: кнопка блока %d должна вести на дорожную карту" % (rel, i)







# ── Кикеров 01/02 нет ──────────────────────────────────────────────────────

def test_no_kickers():
    for bad in ("kicker", "01 ·", "02 ·", "аудитория", "программа"):
        for rel in _ENTRIES:
            assert bad not in _read(rel), "кикер «%s» должен быть убран (%s)" % (bad, rel)


# ── Фавикон как на главной — на всех страницах курса ───────────────────────

def test_favicons_on_every_course_page():
    site = _read(_MAIN_SITE)
    icons = re.findall(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>', site)
    assert len(icons) >= 7, "на главной ожидается полный набор иконок"
    hrefs = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', site))
    for rel in _COURSE_PAGES:
        page_hrefs = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', _read(rel)))
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


# ── Практическое задание к лекции 1 ────────────────────────────────────────

_PRACTICE = "automation/1/practice/index.html"


def test_practice_page_is_self_sufficient():
    """Иконки задания вшиты в страницу и не зависят от внешнего CDN.

    На лекции иконки жили на unpkg, и при недоступности CDN страница
    оставалась вообще без иконок. У задания они — inline-SVG: рисуются
    всегда, в том числе офлайн и при печати.
    """
    html = _read(_PRACTICE)
    assert "unpkg.com" not in html and "cdnjs" not in html, \
        "иконки задания не должны грузиться со стороннего CDN"
    assert html.count("<symbol id=\"i-") >= 15, "нужен полный набор вшитых иконок"
    for name in ("i-scan", "i-target", "i-rocket-launch", "i-arrow-left"):
        assert 'id="%s"' % name in html and 'href="#%s"' % name in html, \
            "иконка %s должна быть и объявлена, и использована" % name


def test_practice_header_matches_the_course():
    """Шапка задания — той же геометрии, что шапка лекции и главной."""
    html = _read(_PRACTICE)
    assert "padding:1.1rem" in html and "@media (min-width:1024px){ header{ padding:2rem; } }" in html
    assert "clamp(2.85rem,12vw,3.7rem)" in html, "лого того же размера, что на главной"
    assert "clamp(2.5rem,11vw,3.3rem)" in html, "круглая кнопка бургерных размеров"
    assert "height:2.85rem; padding:0 1.4rem; font-size:11.5px; letter-spacing:.15em" in html, \
        "правая кнопка — метрики CTA главной"
    assert ">Буткемп " in html, "правая кнопка называется «Буткемп»"


def test_bootcamp_button_opens_bootcamp_page():
    """Кнопка «Буткемп» ведёт на страницу буткемпа, а не сразу в телеграм."""
    for rel in _ENTRIES:
        page = _read(rel)
        assert "location.href='/automation/bootcamp/'" in page, rel


def test_practice_is_linked_from_the_lecture():
    assert "/automation/1/practice/" in _read(_LECTURE1), \
        "кнопка «Задание» в лекции должна вести на страницу практики"


def test_practice_terms_do_not_break_on_hyphen():
    """«ИИ-агентов» не должно распадаться на две строки по дефису."""
    html = _read(_PRACTICE)
    body = html.split("<body>", 1)[1]
    plain = re.sub(r"<[^>]*>", " ", body)
    for bad in ("ИИ-агент", "ИИ-модел", "ИИ-трансформац"):
        assert bad not in plain, "%s: дефис в термине должен быть неразрывным (U+2011)" % bad


# ── Говорящая голова: обложка вместо дыры, локальные видео ─────────────────

_COVER = "/assets/1_video/auto_cover_1.jpg"


def test_lecture_videos_are_local_and_in_order():
    """42 ролика лежат в репозитории и идут по слайдам в порядке глав.

    Раньше они грузились с raw.githubusercontent.com по хешу коммита чужого
    репозитория — то есть жили на честном слове.
    """
    import os
    html = _read(_LECTURE1)
    assert "raw.githubusercontent.com" not in html, "видео должны браться из репозитория"
    urls = re.findall(r"'(/assets/1_video/auto_[^']+\.mp4)'", html)
    assert len(urls) == 42, "по одному ролику на слайд, а не %d" % len(urls)
    order = [tuple(map(int, re.search(r"auto_(\d+)-sq-(\d+)", u).groups())) for u in urls]
    assert order == sorted(order), "порядок роликов должен идти по главам и номерам"
    for u in urls + [_COVER, "/assets/1_video/auto_0_sq.mp4"]:
        assert os.path.isfile(os.path.join(_ROOT, u.lstrip("/"))), "нет файла " + u


def test_cover_shows_while_video_is_idle():
    """Пока ролик не играет, в кружке виден кадр-обложка, а не чёрная дыра."""
    html = _read(_LECTURE1)
    assert 'poster="%s"' % _COVER in html, "у видео лекции должен быть постер"
    assert _COVER in html.split('id="head-video"', 1)[1][:400], \
        "обложка должна стоять и фоном кружка — постер не виден после буферизации"


def test_entry_has_no_video_circle():
    """На входной странице кружка с головой НЕТ (просьба заказчика)."""
    for rel in _ENTRIES:
        page = _read(rel)
        assert 'id="head-video"' not in page, rel + ": кружок должен быть убран"
        assert 'class="head"' not in page, rel + ": разметка кружка должна быть убрана"
