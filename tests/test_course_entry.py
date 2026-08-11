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
# Открыт только модуль 1: лекции 2-8 закрыты и не опубликованы (см.
# tests/test_lectures.py::test_locked_modules_closed). Проверяем то, что
# реально лежит на сайте, — вернувшийся модуль подхватится сам.
_COURSE_PAGES = tuple(
    p for p in _COURSE_PAGES if os.path.exists(os.path.join(_ROOT, p)))


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


def test_direct_link_wins_over_saved_language():
    """Адрес — источник истины: прямой заход на языковую страницу НЕ уводится
    авто-редиректом по сохранённому ait_lang (жалоба владельца: ссылка на
    /automation_ru/ с мобилки открывала английскую версию). Страница сама
    запоминает свой язык — его читает переключатель EN|RU."""
    for rel, lang in ((_EN_PAGE, "en"), (_RU_PAGE, "ru")):
        html = _read(rel)
        assert "ait_lang_hop" not in html, rel + ": авто-переход должен быть выпилен"
        assert "location.replace('/automation" not in html, rel + ": никаких языковых редиректов"
        assert "localStorage.setItem('ait_lang', '%s')" % lang in html, rel


def test_main_site_course_link_follows_the_language():
    site = _read(_MAIN_SITE)
    assert 'data-href-en="%s"' % URL_EN in site and 'data-href-ru="%s"' % URL_RU in site
    assert "querySelectorAll('[data-href-ru]')" in site, \
        "главная должна переключать ссылку на курс вместе с языком"


# ── Один блок в фокусе: ни страница, ни блок не прокручиваются ─────────────




def test_background_stays_put():
    """Фон и зерно живут вне дека, поэтому при смене блока не двигаются."""
    for rel in _ENTRIES:
        html = _read(rel)
        deck = html.index('<main class="deck"')
        assert html.index('<div class="grain">') < deck, "зерно должно лежать вне дека"
        assert re.search(r"body\{\s*\n?\s*background:var\(--bg\)", html), "фон задан body"




def test_single_cta_at_the_bottom():
    """Призыв к действию на странице ОДИН — внизу, после «чему научитесь».

    Раньше кнопка «Начать обучение» стояла в каждом из трёх блоков. Заказчик
    оставил одну: три одинаковые кнопки на коротком лендинге читаются как
    навязчивость, а воздух под каждой из них раздувал страницу.
    """
    for rel in _ENTRIES:
        blocks = _blocks(_read(rel))
        assert len(blocks) == 3, "%s: блоков должно быть три" % rel
        for i, block in enumerate(blocks[:-1]):
            assert "btn-start" not in block, \
                "%s: в блоке %d кнопки быть не должно" % (rel, i)
        assert "btn-start" in blocks[-1], rel + ": в последнем блоке кнопка обязана быть"
        assert "https://andre.technology/automation/main" in blocks[-1], \
            rel + ": кнопка ведёт на дорожную карту курса"


def test_header_button_is_the_same_call_to_action():
    """Кнопка шапки — тот же вход в курс, тем же текстом.

    Была «Буткемп» и уводила на отдельную страницу — посетитель попадал не в
    курс, а в другое предложение. Буткемп остаётся доступен из шапки лекции и
    страницы задания.
    """
    for rel in _ENTRIES:
        html = _read(rel)
        label = "Начать обучение" if "_ru" in rel else "Start learning"
        assert "location.href='https://andre.technology/automation/main'" in html, \
            rel + ": кнопка шапки ведёт в курс"
        assert html.count(label) >= 3, \
            rel + ": подпись «%s» — и в шапке (текст + aria), и на кнопке внизу" % label
        for gone in ("Буткемп", "Bootcamp", "/automation/bootcamp/"):
            assert gone not in html, rel + ": буткемпа на входной странице больше нет (%s)" % gone


def test_role_caption_breaks_into_two_lines():
    """Подпись роли — ровно две строки, уточнение уходит на вторую.

    «Автоматизирует бизнес с ИИ-агентами» одной строкой ломалось по-разному
    на каждой ширине; заказчик зафиксировал перенос перед предлогом.
    """
    heads = {
        "automation_ru/index.html": ("Находит процессы<br>для", "Автоматизирует бизнес<br>с",
                                     "Строит бизнес<br>с помощью"),
        "automation/index.html": ("Finds processes<br>ready for", "Automates business<br>with",
                                  "Builds a business<br>powered by"),
    }
    for rel in _ENTRIES:
        html = _read(rel)
        for part in heads[rel]:
            assert part in html, "%s: нет переноса «%s»" % (rel, part)







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


def test_page_scrolls_normally():
    """От «листания по блокам» отказались: страница обычная, прокручиваемая.

    Никакого перехвата колеса и свайпа — именно это ломало поведение на части
    устройств и раздражало заказчика. Блоки просто идут друг за другом.
    """
    for rel in _ENTRIES:
        page = _read(rel)
        assert "overflow:hidden" not in page.split("<body")[0].split("html,body")[-1][:200], \
            rel + ": страница не должна запрещать прокрутку"
        assert "addEventListener('wheel'" not in page, rel + ": колесо не перехватываем"
        assert "addEventListener('touchmove'" not in page, rel + ": свайп не перехватываем"
        assert re.search(r"\.deck\{position:relative", page), rel + ": дек стал обычным потоком"
        assert re.search(r"\.panel\{[^}]*position:relative", page), rel + ": блоки в обычном потоке"
        assert "scroll-behavior:smooth" in page, rel + ": прокрутка плавная"


def test_blocks_visible_immediately():
    """Контент виден сразу, без анимаций появления (правка владельца:
    на мобилке блоки «доезжали» каскадом и страница выглядела пустой)."""
    for rel in _ENTRIES:
        page = _read(rel)
        assert ".panel .wrap > *{opacity:1;transform:none}" in page, rel + ": контент виден сразу"
        assert ".panel.in .wrap > *{animation:riseIn" not in page, rel + ": каскада появления больше нет"
        assert ".panel .wrap > *{opacity:0" not in page, rel + ": контент не прячется"
        assert "scrollIntoView({ behavior:" in page, rel + ": переход к блоку плавный"


def test_blocks_go_one_after_another_without_empty_screens():
    """Блок занимает столько, сколько нужно содержимому, а не целый экран.

    `min-height:100svh` раздувал каждый блок до высоты окна: между текстом
    соседних блоков зияло 300-450px пустоты, и страница читалась как набор
    полупустых экранов. Ритм задаём отступами, как на странице буткемпа.
    """
    for rel in _ENTRIES:
        panel = re.search(r"\n  \.panel\{(.*?)\}", _read(rel), re.S)
        assert panel, rel + ": не нашёл правило .panel"
        assert "min-height" not in panel.group(1), \
            rel + ": блок не растягиваем на весь экран — это и давало провалы"
        assert re.search(r"padding:clamp\([^)]*\) 1rem", panel.group(1)), \
            rel + ": вертикальный ритм задаём отступом блока"


def test_no_scroll_hint():
    """Подсказки «SCROLL DOWN» нет: обычная страница в ней не нуждается."""
    for rel in _ENTRIES:
        page = _read(rel)
        for mark in ("scroll-hint", "SCROLL DOWN", "Листайте вниз"):
            assert mark not in page, rel + ": подсказка прокрутки убрана (" + mark + ")"


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
    """Кнопка «Буткемп» ведёт на страницу буткемпа, а не сразу в телеграм.

    На входных страницах курса её больше нет (там единственный призыв —
    «Начать обучение»), поэтому проверяем шапку страницы задания.
    """
    for rel in (_PRACTICE, "automation/1/index.html"):
        assert 'href="/automation/bootcamp/"' in _read(rel), rel


def test_diagnostic_button_opens_maturity():
    """«Бесплатно пройти диагностику» ведёт на maturity.andre.technology.

    Диагностика живёт на maturity-поддомене (правка заказчика); strategy —
    это кабинет, и отправлять туда человека без пройденного теста нельзя.
    """
    html = open(os.path.join(_ROOT, "automation/1/practice/index.html"), encoding="utf-8").read()
    i = html.find("Бесплатно пройти диагностику")
    assert i != -1, "кнопка диагностики пропала со страницы практики"
    a = html.rfind("<a ", 0, i)
    tag = html[a:i]
    assert 'href="https://maturity.andre.technology/"' in tag, \
        "диагностика должна открываться на maturity.andre.technology: " + tag[:120]


def test_methodology_button_opens_the_book():
    """«Изучить методику» открывает книгу «AI Maturity Index», а не лекцию.

    Три вещи, которые здесь легко сломать:
      · файл должен лежать в репозитории — иначе кнопка ведёт в 404;
      · пробелы в имени обязаны быть закодированы (%20): с «живым» пробелом
        ссылка рвётся на части серверов и в мессенджерах;
      · target=_blank — 3.8МБ PDF не должен затирать страницу задания.
    """
    book = "books/AI MATURITY INDEX.pdf"
    path = os.path.join(_ROOT, book)
    assert os.path.exists(path), "книга должна лежать в репозитории: " + book
    with open(path, "rb") as f:
        assert f.read(5) == b"%PDF-", book + ": это должен быть настоящий PDF"

    html = _read(_PRACTICE)
    link = re.search(r'<a class="btn btn-ghost"[^>]*>(?:(?!</a>).)*Изучить методику', html, re.S)
    assert link, "не нашёл кнопку «Изучить методику»"
    tag = link.group(0)
    assert 'href="/books/AI%20MATURITY%20INDEX.pdf"' in tag, \
        "кнопка ведёт на книгу, путь — с кодированными пробелами"
    assert 'target="_blank"' in tag and 'rel="noopener"' in tag, \
        "книга открывается в новой вкладке, страница задания остаётся"


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


# ── Говорящая голова: обложка вместо дыры, видео с ветки media ─────────────
# Канон хостинга (правка заказчика): деплой GitHub Pages падал по таймауту
# из-за тяжёлого артефакта, поэтому все mp4 живут в ветке `media` и отдаются
# через raw.githubusercontent.com; в main остаются только лёгкие ассеты.

_COVER = "/assets/video_sq/poster_auto_0.jpg"
_MEDIA = "https://raw.githubusercontent.com/andre-kuzminykh/andre-ait-page/refs/heads/media"
# структура глав лекции 1 — ролики «кв» из assets/video_sq (в ветке media)
_CHAPTERS = {1: 3, 2: 5, 3: 4, 4: 4, 5: 5, 6: 9, 7: 3, 8: 7, 9: 2}


def test_lecture_videos_are_on_media_branch_and_in_order():
    """42 ролика идут по слайдам в порядке глав и берутся с ветки media
    (raw.githubusercontent.com), а не из артефакта Pages."""
    import os, urllib.parse
    html = _read(_LECTURE1)
    assert "/assets/1_video/" not in html, "ссылок на удалённую папку быть не должно"
    urls = re.findall(r"'(%s/assets/video_sq/[^']*%%D0%%BA%%D0%%B2[^']*\.mp4)'" % re.escape(_MEDIA), html)
    assert len(urls) == 42, "по одному ролику на слайд, а не %d" % len(urls)
    order = [tuple(map(int, re.search(r"auto_(\d+)-%D0%BA%D0%B2-(\d+)", u).groups())) for u in urls]
    assert order == sorted(order), "порядок роликов должен идти по главам и номерам"
    counts = {}
    for ch, _ in order:
        counts[ch] = counts.get(ch, 0) + 1
    assert counts == _CHAPTERS, "структура глав разъехалась: %r" % counts
    # обложка — лёгкий jpg, живёт в main как раньше
    rel = urllib.parse.unquote(_COVER.lstrip("/"))
    assert os.path.isfile(os.path.join(_ROOT, rel)), "нет файла " + rel


def test_no_mp4_in_main_tree_or_local_links():
    """Сторож канона: в main нет ни одного mp4 (артефакт Pages лёгкий, деплой
    не упирается в таймаут очереди), а страницы не ссылаются на локальные mp4 —
    только на https (ветка media или внешние репозитории)."""
    import subprocess
    tracked = subprocess.check_output(
        ["git", "ls-files", "*.mp4"], cwd=_ROOT, text=True).strip()
    assert tracked == "", "mp4 в main запрещены (видео — в ветку media): %s" % tracked
    pages = subprocess.check_output(
        ["git", "ls-files", "*.html"], cwd=_ROOT, text=True).split()
    for page in pages:
        html = _read(os.path.join(_ROOT, page))
        for m in re.finditer(r"""["'(]([^"'()\s]+\.mp4)""", html):
            src = m.group(1)
            assert src.startswith("https://"), \
                "%s: локальная ссылка на видео %s (нужен https с ветки media)" % (page, src)


def test_cover_shows_while_video_is_idle():
    """Пока ролик не играет: виден его собственный ПЕРВЫЙ КАДР — размытый,
    под кнопкой play (правка заказчика). Обложка остаётся только фоном на
    время загрузки данных, постера-картинки больше нет."""
    html = _read(_LECTURE1)
    tag = html.split('id="head-video"', 1)[1][:400]
    assert 'poster=' not in tag, "постер — первый кадр самого ролика, не картинка"
    assert _COVER in tag, "обложка должна остаться фоном на время загрузки"
    assert 'preload="metadata"' in tag, "видео не тянет мегабайты на загрузке страницы"
    assert "#video-bubble:not(.is-playing) #head-video{ filter:blur(" in html, \
        "неиграющий кадр должен стоять размытым"
    assert ".currentTime = 0.01" in html, \
        "первый кадр отрисовывается сдвигом таймкода после загрузки метаданных"


def test_entry_has_no_video_circle():
    """На входной странице кружка с головой НЕТ (просьба заказчика)."""
    for rel in _ENTRIES:
        page = _read(rel)
        assert 'id="head-video"' not in page, rel + ": кружок должен быть убран"
        assert 'class="head"' not in page, rel + ": разметка кружка должна быть убрана"
