# -*- coding: utf-8 -*-
"""Тесты главной andre.technology (index.html) — лендинг-слайды (FR-SITE95..97).

Без зависимостей — запускается и как `python3 tests/test_site.py`, и через pytest.

Прежняя главная (FR-SITE1..12, 17..26, 89..94 в части index.html) заменена
целиком; её тесты остались в истории git и возвращаются вместе с откатом
(точка отката — в AGENTS.md, чекпоинт pr93).

FR-SITE95 — главная: одиннадцать слайдов, холст фиксированной ширины, ИИ-мозг
            из графа, переходы видео ↔ кружок ↔ полоса ↔ «Andre AI».
FR-SITE96 — политика конфиденциальности и условия использования: свои страницы
            на двух языках (tools/build_legal.py), подвал ведёт на них.
FR-SITE97 — соцсети в подвале: у русской и английской версии свои аккаунты.
FR-SITE98 — телефон: заголовки и анимации по центру и по середине экрана.
FR-SITE99 — подвал: иконки почти под меню, «ANDRE AI» с формой — по центру.
FR-SITE100 — составные слова с «ИИ-» — обычный дефис и запрет переноса, без
            неразрывного дефиса U+2011 (его нет в JetBrains Mono).
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _html():
    return _read("index.html")


def _tag(html, pattern):
    """Первый открывающий тег <a …>, внутри которого есть pattern."""
    for m in re.finditer(r"<a\s[^>]*>", html):
        if pattern in m.group(0):
            return m.group(0)
    return None


def _attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % re.escape(name), tag)
    return m and m.group(1)


# ── FR-SITE95: устройство главной ──────────────────────────────────────────

SLIDES = ["hero", "change", "maturity", "strategy", "neuronium", "training",
          "cases", "pricing", "faq", "start", "footer"]


def test_slides_in_order():
    ids = re.findall(r'<section class="slide[^"]*" id="([a-z]+)"', _html())
    assert ids == SLIDES, ids


def test_no_dead_links():
    """Владелец: «ты всё заполни» — на проде ни одной ссылки в никуда."""
    html = _html()
    assert 'href="#"' not in html, "осталась ссылка-заглушка href=\"#\""
    assert not re.search(r"<a\s[^>]*\bdata-todo\b", html), "осталась ссылка с пометкой data-todo"
    assert "заглушк" not in html.lower(), "в разметке остались пометки про заглушки"


def test_diagnostic_buttons_lead_to_maturity_in_the_visitor_language():
    """Первый шаг воронки — бесплатная ИИ-диагностика; русская версия ведёт в
    продукт на русском (FR-SITE85/86)."""
    html = _html()
    tags = [m.group(0) for m in re.finditer(r"<a\s[^>]*maturity\.andre\.technology[^>]*>", html)]
    assert len(tags) >= 4, "кнопки диагностики: шапка, первый слайд, зрелость, финал"
    for t in tags:
        assert _attr(t, "data-href-en") == "https://maturity.andre.technology/", t
        assert _attr(t, "data-href-ru") == "https://maturity.andre.technology/?lang=ru", t


def test_strategy_and_landing_links_follow_the_language():
    html = _html()
    st = _tag(html, 'data-href-en="https://strategy.andre.technology/"')
    assert st and _attr(st, "data-href-ru") == "https://strategy.andre.technology/?lang=ru"
    land = _tag(html, 'data-href-en="https://andre.technology/ai-strategy/"')
    assert land and _attr(land, "data-href-ru") == "https://andre.technology/ai-strategy/ru/"
    about = _tag(html, 'data-href-en="https://andre.technology/about/"')
    assert about and _attr(about, "data-href-ru") == "https://andre.technology/about/ru/"
    assert "querySelectorAll('[data-href-ru]')" in html or "$$('[data-href-ru]')" in html, \
        "ссылки переставляются вместе с языком"


def test_ai_brain_link_goes_to_neuronium():
    """Владелец: «где переход в ИИ-брейн — там neuronium.ai»."""
    html = _html()
    m = re.search(r'<a class="link" href="([^"]+)"><span data-i18n="s5\.link">', html)
    assert m and m.group(1) == "https://neuronium.ai/", m and m.group(1)
    assert "'s5.link': 'Discover AI Brain'" in html


def test_language_switch_and_shared_key():
    html = _html()
    assert 'data-lang="en"' in html and 'data-lang="ru"' in html
    assert "localStorage.getItem('ait_lang')" in html, "язык общий с биографией и курсом — ключ ait_lang"
    assert "[?&]lang=(ru|en)" in html, "адрес ?lang= выбирает язык"


def test_head_metadata_is_complete():
    """Набор иконок, превью для соцсетей и разметка организации — как на
    прежней главной (курс сверяет свои фавиконы с главной)."""
    html = _html()
    head = html.split("</head>")[0]
    assert '<link rel="canonical" href="https://andre.technology/">' in head
    icons = re.findall(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>', head)
    assert len(icons) >= 7, icons
    for rel in re.findall(r'href="/((?:favicon|apple-touch|site\.web)[^"]*)"', head):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel
    for prop in ("og:title", "og:description", "og:image", "og:image:width", "og:image:height", "og:url"):
        assert 'property="%s"' % prop in head, prop
    for name in ("twitter:card", "twitter:title", "twitter:image"):
        assert 'name="%s"' % name in head, name
    assert os.path.exists(os.path.join(_ROOT, "assets/og/andre-ai-technologies.png"))
    assert '"@type": "Organization"' in head and '"legalName": "Andre AI Technologies LTD"' in head
    for alt in ('hreflang="ru"', 'hreflang="en"', 'hreflang="x-default"'):
        assert alt in head, alt


def test_video_and_poster_are_served_from_the_site():
    """Ролик и постер — с корня сайта: живые и на проде, и в локальном превью."""
    html = _html()
    for rel in ("assets/Andre_AIT_video_compressed.mp4", "assets/Andre_AIT_video_compressed_ru.mp4", "andre_ai.jpg"):
        assert "'/%s'" % rel in html or '"/%s"' % rel in html, rel
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel
    assert "https://andre.technology/assets/Andre_AIT" not in html


def test_fixed_canvas_and_single_column_for_small_square_windows():
    """Холст: телефон — 390, компьютер — 1180…1280; небольшое почти квадратное
    окно (браузер на пол-экрана) получает одну колонку, а не ужатый до ~0,6
    компьютерный холст («всё сильно мелко»)."""
    html = _html()
    assert "m = w / h < 0.9 || (w / h <= 1 && w < 900)" in html
    assert "Math.max(1180, Math.min(1280," in html


def test_typewriter_caret_takes_no_room():
    """«Когда текст допечатался, его подбивает вправо»: каретка не занимает
    места в строке и не даёт переноса посреди слова."""
    html = _html()
    rule = re.search(r"\.tw-car \{[^}]*\}", html).group(0)
    assert "display: inline;" in rule and "padding-left: 0.1em;" in rule and "margin-right: -0.1em;" in rule, rule
    assert "inline-block" not in rule


def test_brain_route_runs_strictly_along_graph_edges():
    """Владелец: «двигалось именно по выстроенным связям». Каждая нога пути —
    цепочка СОСЕДНИХ точек графа; после ТЗ две ветки идут параллельно и
    сходятся в «Коде»."""
    html = _html()
    nums = lambda s: [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s)]
    verts = re.search(r"var BRV = \[(.*?)\],\n", html, re.S).group(1)
    edges = nums(re.search(r"BRE = \[([^\]]*)\]", html).group(1))
    n_v = len(re.findall(r"\[[^\[\]]+\]", verts))
    assert 30 <= n_v <= 60, "мозг из небольшого числа точек: %d" % n_v
    E = set()
    for i in range(0, len(edges), 2):
        a, b = int(edges[i]), int(edges[i + 1])
        E.add((a, b)); E.add((b, a))
    legs = re.findall(r"\[(\d+), (\d+), \[([\d, ]+)\]\]", re.search(r"var BRL = \[(.*?)\];", html, re.S).group(1))
    assert len(legs) == 7, legs
    nodes = [int(v) for v in re.findall(r"\[(\d+), \d\]", re.search(r"var BRN = \[(.*?)\];", html).group(1))]
    into = {}
    for fr, to, path in legs:
        pts = [int(x) for x in path.split(",")]
        assert pts[0] == nodes[int(fr)] and pts[-1] == nodes[int(to)], (fr, to, pts)
        for a, b in zip(pts, pts[1:]):
            assert (a, b) in E, "нога %s→%s идёт не по связи %d-%d" % (fr, to, a, b)
        into[int(to)] = into.get(int(to), 0) + 1
    outs = {}
    for fr, _to, _p in legs:
        outs[int(fr)] = outs.get(int(fr), 0) + 1
    assert max(outs.values()) == 2 and max(into.values()) == 2, "одна развилка и одно слияние"


def test_brain_icons_names_and_loop():
    html = _html()
    assert html.count("'os.n") >= 7 and "data-i18n=\"os.n' + ai + '\"" in html, "имена артефактов"
    assert "BRI = ['\\uf0e0', '\\uf0ae', '\\uf1c0', '\\uf15c', '\\uf5ae', '\\uf121', '\\uf135']" in html, "значки артефактов"
    assert "c = c % B.CL" in html, "сценарий мозга зациклен"
    assert "os.ro1" not in html, "имён ролей в мозге больше нет"


def test_final_strip_slides_to_the_wordmark():
    """Финал: видео → полоса → полоса едет к середине и раскрывается в «Andre AI»
    (без растяжки на всю ширину); обратно — наоборот."""
    html = _html()
    assert "x0 = lerp(S.x, wline.x, kb), x1 = lerp(S.x + S.w, wline.x + wline.w, kb);" in html
    assert "SW(), kb)" not in html, "полоса больше не растягивается на всю ширину экрана"


def test_case_cards_are_the_same_size_and_two_lines_at_most():
    html = _html()
    assert ".mc { width: clamp(18.5rem, 23.5cqw, 20rem); height:" in html
    assert "-webkit-line-clamp: 2;" in html
    ru = re.findall(r'<span data-i18n="c\d">([^<]+)</span>', html)
    assert len(ru) == 9 and all(t.startswith("ИИ-агент ") for t in ru), ru
    en = re.findall(r"'c\d': '([^']+)'", html)
    assert len(en) == 9 and all(t.startswith("AI agent ") for t in en), en


def test_custom_price_does_not_grow_the_cards():
    """«Почему когда Custom выбираю, увеличиваются блоки»: колонки не растут от
    содержимого, а у «Индивидуально / Custom» строка той же высоты, что у цифры."""
    html = _html()
    assert ".tiers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in html
    assert "#pricing .t-pr .num { font-size: 54px; } #pricing .t-pr .num.txt { font-size: 32px; line-height: 54px; }" in html
    assert ".t-pr .num.txt { font-size: 26px; line-height: 40px; }" in html


def test_footer_antropolis_mark_is_centred_over_the_socials():
    html = _html()
    assert ".foot .f-hg { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);" in html
    assert ".foot .f-hg .antro { justify-self: start; white-space: nowrap; gap: 0.55rem; margin: 0 0 0 -0.675rem; }" in html


def test_no_cookie_banner():
    """FR-SITE88: сайт не ставит cookie — баннера нет; язык живёт в localStorage."""
    html = _html()
    assert "document.cookie" not in html and "cookie-banner" not in html



def test_phone_titles_and_animations_are_centred():
    """FR-SITE98. Владелец: «по середине пусть тайтлы и анимации будут всё же на
    мобиле … по центру, по середине». На телефоне заголовки — по центру ширины;
    пара «заголовок + анимация» — ровно по середине экрана под шапкой
    («тут не по середине, а к верху» — потолок по кружку снят)."""
    html = _html()
    css = re.search(r"@container stage \(max-width:767px\) \{\n    \.split > :first-child, \.pr-h > div:first-child, \.faq > \.st \{ text-align: center; \}(.*?)\n  \}", html, re.S)
    assert css, "правило центровки заголовков на телефоне"
    assert ".split .kicker, .split .actions, .pr-h .kicker, .faq .kicker { justify-content: center; }" in css.group(1)
    assert "bub = $('#bubble-probe'), bt = (bub ? rr(bub).top : lim) - 12" in html
    assert "sh = Math.floor((lim - t0 - bh) / 2)" in html, "ровно по середине экрана под шапкой"
    assert "bt - t0 - bh" not in html, "потолок «не ниже кружка» прижимал высокие рисунки к верху"
    assert "if (sh > 0) { sp.style.marginTop = sh + 'px';" in html
    assert "sp.style.marginTop = ''" in html, "сдвиг сбрасывается при каждом пересчёте"


def test_phone_cases_title_is_centred_too():
    """FR-SITE98 ред. 2: «следующий блок тоже — тайтл влево уехал». У «Кейсов»
    обёртка заголовка — flex: её блок ужимался по тексту и стоял слева."""
    assert ".cases-h { justify-content: center; } .cases-h > div { width: 100%; }" in _html()


def test_footer_icons_under_menu_and_wordmark_with_form_centred():
    """FR-SITE99. Владелец: «в последнем блоке иконки ещё выше поднять — почти
    под меню, но с отступом; по центру — Andre AI, строку подписки чуть выше».
    Верх подвала — сразу под шапкой; по середине экрана — пара «ANDRE AI + форма»."""
    html = _html()
    assert ".foot .f-top { justify-content: flex-start !important; padding-top: clamp(0.45rem, 1.4cqh, 0.95rem); }" in html
    assert ".foot { --fgap: clamp(0.55rem, 1.5cqh, 0.95rem); --fx: calc((2.5rem + var(--fgap)) / 2); }" in html
    assert ".foot .f-mid, .foot .f-bot .news { position: relative; top: calc((var(--hdr) + clamp(0.4rem, 2cqh, 1.4rem) - 2rem) / -2 - var(--fx)); }" in html
    assert ".foot .f-bot .news { margin-top: var(--fgap) !important;" in html

# ── FR-SITE96: политика и условия ──────────────────────────────────────────

LEGAL = {"privacy": ("/privacy/", "/privacy/ru/"), "terms": ("/terms/", "/terms/ru/")}


def test_footer_links_to_legal_pages_in_the_visitor_language():
    html = _html()
    for key, (en, ru) in LEGAL.items():
        t = _tag(html, 'data-href-en="%s"' % en)
        assert t and _attr(t, "data-href-ru") == ru and _attr(t, "href") == ru, (key, t)
        assert os.path.exists(os.path.join(_ROOT, en.strip("/"), "index.html"))
        assert os.path.exists(os.path.join(_ROOT, ru.strip("/"), "index.html"))


def test_legal_pages_are_built_from_the_generator():
    """Страницы собирает tools/build_legal.py; сборка воспроизводит файлы в git
    байт в байт — правка текста только через генератор."""
    from tools import build_legal
    before = {}
    for en, ru in LEGAL.values():
        for p in (en, ru):
            rel = p.strip("/") + "/index.html"
            before[rel] = _read(rel)
    build_legal.build()
    for rel, txt in before.items():
        assert _read(rel) == txt, rel + ": файл в git расходится с генератором"


def test_legal_pages_content():
    for kind, (en, ru) in LEGAL.items():
        for path, lang in ((en, "en"), (ru, "ru")):
            html = _read(path.strip("/") + "/index.html")
            assert '<html lang="%s">' % lang in html
            assert '<link rel="canonical" href="https://andre.technology%s">' % path in html
            assert "admin@andre.technology" in html and "Andre AI Technologies LTD" in html
            assert "localStorage.setItem('ait_lang', '%s')" % lang in html
            assert 'href="#"' not in html
    assert "no cookies" in _read("privacy/index.html") and "не ставит cookie" in _read("privacy/ru/index.html"), \
        "политика совпадает с FR-SITE88: cookie нет"


# ── FR-SITE97: соцсети по языку ─────────────────────────────────────────────

SOCIAL = {
    "YouTube": ("https://www.youtube.com/@andre_dataist", "https://www.youtube.com/@andre.dataist"),
    "Instagram": ("https://www.instagram.com/andre_dataist", "https://www.instagram.com/andre.dataist"),
    "TikTok": ("https://www.tiktok.com/@andre_dataist", "https://www.tiktok.com/@andre.dataist"),
}


def test_socials_follow_the_language():
    html = _html()
    for label, (ru, en) in SOCIAL.items():
        t = _tag(html, 'aria-label="%s"' % label)
        assert t, label
        assert _attr(t, "data-href-ru") == ru and _attr(t, "data-href-en") == en and _attr(t, "href") == ru, t
    x = _tag(html, 'aria-label="X"')
    assert _attr(x, "href") == "https://x.com/andre_dataist" and 'data-only="en"' in x
    tg = _tag(html, 'aria-label="Telegram"')
    assert _attr(tg, "href") == "https://t.me/andre_dataist" and 'data-only="ru"' in tg
    assert '<i class="fa-solid fa-paper-plane"></i></a>' in html[html.index('aria-label="Telegram"'):][:200], \
        "Telegram в подвале — простой самолётик"
    assert _attr(_tag(html, 'aria-label="LinkedIn"'), "href") == "https://www.linkedin.com/in/andre-kuzminykh/"



def test_compound_words_use_a_glyph_the_font_has():
    """FR-SITE100: «ИИ_Старатегия» вместо «ИИ-стратегия» (владелец 2026-11-02).
    Заголовки набраны JetBrains Mono, а в нём нет неразрывного дефиса U+2011
    (`&#8209;`) — браузер дорисовывал знак из чужого шрифта, и на части
    устройств он выглядел подчёркиванием. Теперь дефис обычный, а от
    переноса слово держит класс `.nw` (white-space: nowrap)."""
    html = _read("index.html")
    assert "&#8209;" not in html and "\u2011" not in html
    assert ".nw { white-space: nowrap; }" in html
    for word in ("ИИ-экономику", "ИИ-диагностики", "ИИ-компании", "ИИ-операционная",
                 "ИИ-стратегии", "ИИ-трансформации", "ИИ-трансформацию"):
        assert re.search(r'class="[^"]*\bnw\b[^"]*">' + word, html), word


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok  ", name)
            n += 1
    print("\nВсе тесты сайта пройдены:", n)
