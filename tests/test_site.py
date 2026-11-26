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
FR-SITE101 — цены: ползунок «сколько сотрудников», три пакета (ред. 26.11 — по
            FR-SITE113…118).
FR-SITE113…119, NFR-SITE103…105 — цены 26.11: только доллары; «Месяц | Год −17%» над
            ползунком, в «Год» зачёркнутая прежняя цена; группы 1–10 / 11–100 / 101–249 /
            250+ и пакеты ценовой политики; цена меняется на ходу, «≈ $X на сотрудника»;
            без «Начать бесплатно — 1 процесс», под каждым пакетом «Первый процесс —
            бесплатно»; 250+ — «По запросу» и заявка. В браузере (RU и EN, компьютер и
            телефон, ползунок через границы групп, ошибки консоли, высота кнопок) это
            проверяет tools/pricing_check.py.
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
    содержимого. NFR-SITE103 (ред. 26.11): у 250+ «По запросу», в «Год» над ценой
    зачёркнутая прежняя — строка цены не переносится и держит высоту крупного
    числа (--nf), строки зачёркнутой цены, продления и «на сотрудника» держат место
    и пустыми; длинную цену ужимает скрипт по ширине карточки."""
    html = _html()
    assert ".tiers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in html
    assert "grid-template-rows: subgrid; grid-template-columns: minmax(0, 1fr);" in html, \
        "колонка карточки не шире самой карточки"
    assert (".t-pr .pr-row { display: flex; align-items: flex-start; flex-wrap: nowrap; white-space: nowrap; "
            "min-height: var(--nf); }") in html
    assert ".t-pr .num { font-size: var(--nf);" in html
    assert ".t-pr .t-was { margin: 0 0 0.35rem; min-height: 1.4em;" in html
    assert ".t-pr .t-add { margin: 0.7rem 0 0; min-height: 1.4em;" in html
    assert ".t-inc { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr);" in html
    assert "function fitPrices()" in html and "shrink(r, $('.num', r), 0.55);" in html
    assert "$$('#pkgs .t-add, #pkgs .t-was').forEach(function (a) { shrink(a, a, 0.7); });" in html
    assert "num.txt" not in html, "строки «Индивидуально / Custom» больше нет"


# ── FR-SITE113…119 (владелец 26.11): только доллары, «Месяц | Год −17%», пакеты по размеру ──

# ценовая политика §2–§3: группа, сотрудников до (включительно), A — стратегия разово, N — Нейроний в месяц, $
POLICY_BANDS = [("1–10", 10, 100, 100), ("11–100", 100, 500, 500), ("101–249", 249, 1000, 1000), ("250+", None, None, None)]
# публичные цены «от» (R = 0, ставка $50/ч), центы: стратегия, платформа за 1-й месяц, трансформация за 3 месяца
POLICY_FROM = {"1–10": (10000, 20000, 125714), "11–100": (50000, 100000, 285714), "101–249": (100000, 200000, 485714)}


def _pricing():
    html = _html()
    return html[html.index('<section class="slide" id="pricing"'):html.index('<section class="slide" id="faq"')]


def _calc_js():
    """Код калькулятора: данные (EMP … PRICE_TXT) и отрисовка (renderCalc … заявка)."""
    html = _html()
    a = html[html.index("/* Калькулятор цен (FR-SITE113"):html.index("var DIMS = {")]
    b = html[html.index("/* ---------- калькулятор (FR-SITE113…118) ---------- */"):html.index("/* ---------- заявки и рассылка")]
    return a + b


def _home_bands():
    rows = re.findall(r"\{ id: '([^']+)', hi: (\d+|null), a: (\d+|null), n: (\d+|null) \}", _html())
    conv = lambda v: None if v == "null" else int(v)  # noqa: E731
    return [(i, conv(hi), conv(a), conv(n)) for i, hi, a, n in rows]


def test_pricing_is_dollars_only():
    """FR-SITE113. Владелец 26.11: «прайсинг на сайте убери рубли и выбор валют».
    Ни знака ₽, ни переключателя «$ / ₽», ни рублёвой валюты по умолчанию у
    русской версии; деньги — «$1 257,14» по-русски и «$1,257.14» по-английски."""
    html, sec, js = _html(), _pricing(), _calc_js()
    assert "₽" not in html, "на главной нет рублей — ни в ценах, ни в ответах FAQ"
    for gone in ('data-cur', 'id="cur"', "#cur", "curOf", "'rub'", "rub:", "state.cur", "Валюта", "Currency"):
        assert gone not in html, gone
    assert sec.count('<span class="cur">$</span>') == 3, "у каждого пакета — доллар"
    assert ("function money(c, L) { var d = Math.floor(c / 100), r = c % 100;\n"
            "    return '$' + String(d).replace(/\\B(?=(\\d{3})+(?!\\d))/g, L === 'en' ? ',' : '\\u00a0') + "
            "(r ? (L === 'en' ? '.' : ',') + (r < 10 ? '0' : '') + r : ''); }") in js, \
        "разряды: по-русски неразрывный пробел, по-английски запятая; центы — через запятую / точку, целые без центов"


def test_bands_and_packages_follow_the_pricing_policy():
    """FR-SITE114: группы размеров 1–10 / 11–100 / 101–249 / 250+ и пакеты ценовой
    политики: стратегия = A, платформа = A + N за первый месяц, трансформация =
    A + 3N + B за три месяца; B — буткемп 12 ч × $50 ÷ 0,70; названий тарифов
    (Соло … Крупный) больше нет."""
    from tools import build_strategy as B
    html, js = _html(), _calc_js()
    assert _home_bands() == POLICY_BANDS, _home_bands()
    assert "var YEAR_PAID = 10, BOOT = Math.round(12 * 50 * 100 / 0.7);" in js
    assert B.BOOTCAMP_CENTS == 85714, "буткемп $857,14"
    assert "if (key === 'strategy') return { now: A, was: null, next: null };" in js
    assert ("return { now: A + (y ? YEAR_PAID : key === 'platform' ? 1 : 3) * N + B, was: y ? A + 12 * N + B : null, "
            "next: y ? YEAR_PAID * N : N };") in js
    assert "B = key === 'transformation' ? BOOT : 0;" in js
    # цены «от» из политики — по тем же формулам (генератор лендинга считает так же, его сверяет test_strategy)
    for band in B.BANDS[:3]:
        got = tuple(B.package_price(k, band, "month")["now"] for k in B.PACKAGES)
        assert got == POLICY_FROM[band[0]], (band[0], got)
    for gone in ("Соло", "Микро", "Малый", "Средний", "Крупный", "'Solo'", "Micro", "'Small'", "'Medium'", "'Large'",
                 "Тариф «", " plan · ", "TARIFF", "MENTOR", "2900", "$2 900", "$2,900"):
        assert gone not in html, gone
    # период рядом с ценой и чек: стратегия разово, платформа за месяц или год, обучение (буткемп) разово
    assert "per: { strategy: 'разово', platform: 'за 1-й месяц', transformation: 'за 3 месяца', year: 'за 1-й год' }" in js
    assert "per: { strategy: 'one-time', platform: 'first month', transformation: 'first 3 months', year: 'first year' }" in js
    assert ("var CC = { a: P.free, s: p ? money(b.a * 100, L) : P.ask2, p: p ? money((y ? YEAR_PAID : 1) * b.n * 100, L) + "
            "(y ? P.yr : P.mo) : P.ask2,") in js and "t: p ? money(BOOT, L) : P.ask2 };" in js


def test_band_bounds_are_inclusive():
    """FR-SITE114/116: границы групп включены (10 — первая, 11 — вторая, 100 —
    вторая, 101 — третья, 249 — третья, 250 — «по запросу»), и каждая граница —
    деление ползунка: цена меняется ровно на ней."""
    from tools import build_strategy as B
    js = _calc_js()
    assert ("function bandOf(n) { for (var i = 0; i < BANDS.length; i++) if (BANDS[i].hi == null || n <= BANDS[i].hi) "
            "return i; return BANDS.length - 1; }") in js
    emp = [int(x) for x in re.search(r"var EMP = \[([^\]]+)\];", js).group(1).split(",")]
    for n in (10, 11, 100, 101, 249, 250):
        assert n in emp, "граница группы — деление ползунка: %d" % n
    want = {10: "1–10", 11: "11–100", 100: "11–100", 101: "101–249", 249: "101–249", 250: "250+", 1000: "250+", 1: "1–10"}
    bands = _home_bands()
    for n, band in want.items():
        got = next(b[0] for b in bands if b[1] is None or n <= b[1])   # то же правило, что bandOf
        assert got == band and B.band_of(n)[0] == band, (n, got, band)
    assert emp[0] == 1 and emp[-1] == 1000 and emp == sorted(emp) and emp[4] == 5
    assert '<input class="rng" id="emp-n" type="range" min="0" max="%d" step="1" value="4">' % (len(emp) - 1) in _pricing()


def test_period_switch_is_above_the_team_size_with_savings_badge():
    """FR-SITE115. Владелец 26.11: «month и year поставь у года процент экономии …
    год/месяц — выше, а размер команды ниже». Год = 12 месяцев по цене 10 → −17%."""
    from tools import build_strategy as B
    html, sec = _html(), _pricing()
    ctl = sec[sec.index('<div class="pr-ctl">'):sec.index('<div class="tiers')]
    assert ctl.index('id="period"') < ctl.index('<div class="emp">') < ctl.index('<ol class="bands"'), \
        "сверху «Месяц | Год», под ним ползунок, под ползунком — группы размеров"
    assert ('<button type="button" data-period="month" aria-pressed="true" data-i18n="s8.month">Месяц</button>'
            '<button type="button" data-period="year" aria-pressed="false" data-i18n="s8.year">Год <em>−17%</em></button>') in ctl
    assert "'s8.month': 'Month', 's8.year': 'Year <em>−17%</em>'" in html
    assert B.YEAR_SAVE == 17 == round(100.0 * (12 - B.YEAR_PAID) / 12)
    for gone in ("2 месяца в подарок", "2 months free", 'class="pr-sw"'):
        assert gone not in html, gone
    assert "#period em { display: inline-block;" in html and "color: var(--o2); background: rgba(249,115,22,0.14); }" in html
    assert ".pr-h .pr-ctl > #period { align-self: center; }" in html, "на телефоне переключатель по центру над ползунком"


def test_year_shows_new_price_and_struck_monthly_price():
    """FR-SITE115, NFR-SITE104: в «Год» у пакетов с Нейронием — новая цена (A + 10N
    [+ B]) и над ней зачёркнутая прежняя (A + 12N [+ B]) с текстом «было $X» для
    экранного диктора; у стратегии и в «Месяц» зачёркнутой цены нет; продление —
    «далее $10N / год»."""
    from tools import build_strategy as B
    js = _calc_js()
    assert ("roll($('.t-was', c), p && p.was ? '<s><span class=\"sr\">' + P.was + ' </span>' + thin(money(p.was, L)) + "
            "'</s>' : '', quiet);") in js
    assert "was: 'было'," in js and "was: 'was'," in js
    assert ".sr { position: absolute; width: 1px; height: 1px;" in _html()
    assert "next: function (m, y) { return 'далее ' + m + (y ? ' / год' : ' / мес'); }" in js
    assert "next: function (m, y) { return 'then ' + m + (y ? ' / yr' : ' / mo'); }" in js
    assert "roll($('.t-next', c), p && p.next ? thin(P.next(money(p.next, L), y)) : '', quiet);" in js
    for band in B.BANDS[:3]:
        A, N = band[3] * 100, band[4] * 100
        assert B.package_price("strategy", band, "year") == {"now": A, "was": None, "next": None}
        assert B.package_price("platform", band, "year") == {"now": A + 10 * N, "was": A + 12 * N, "next": 10 * N}
        assert B.package_price("transformation", band, "year") == {"now": A + 10 * N + 85714, "was": A + 12 * N + 85714, "next": 10 * N}
        for k in B.PACKAGES:
            assert B.package_price(k, band, "month")["was"] is None, "в «Месяц» зачёркнутых цен нет"


def test_price_updates_live_on_input_with_a_short_roll():
    """FR-SITE116, NFR-SITE104. Владелец 26.11: «мне надо чтобы при увеличении
    размера команды можно было бы динамически меняться цена» — пересчёт на
    `input` (во время перетаскивания), смена числа — короткая «прокрутка» (≤ 300
    мс), при prefers-reduced-motion — сразу."""
    html, js = _html(), _calc_js()
    assert "$('#emp-n').addEventListener('input', function (e) { state.emp = +e.target.value; renderCalc(); });" in js
    assert "$('#emp-n').addEventListener('change'" not in html, "не по отпусканию ползунка"
    dur = int(re.search(r"\{ duration: (\d+), easing: 'cubic-bezier\(0\.22, 1, 0\.36, 1\)' \}", js).group(1))
    assert dur <= 300, dur
    assert "window.matchMedia('(prefers-reduced-motion: reduce)').matches)) return;" in js
    assert "roll($('.num', row), p ? big(p.now) : P.ask, quiet);" in js
    assert "@media (prefers-reduced-motion: reduce) {\n    *, *::before, *::after { animation-duration: 0.001s !important;" in html


def test_per_employee_line_and_active_band():
    """FR-SITE116: «≈ $X на сотрудника в месяц» (Нейроний за месяц, за год — 10N /
    12, ÷ сотрудников, до доллара) меняется на каждом шаге; под ползунком группы
    размеров, активная — белая, жирная и с полосой (не только цветом)."""
    from tools import build_strategy as B
    html, sec, js = _html(), _pricing(), _calc_js()
    assert ("function perEmp(bi, period, n) { var b = BANDS[bi]; return b.n == null ? null : "
            "Math.round((period === 'year' ? YEAR_PAID * b.n / 12 : b.n) / n); }") in js
    assert "perEmp: function (m) { return '≈ ' + m + ' на сотрудника в месяц'; }" in js
    assert "perEmp: function (m) { return '≈ ' + m + ' per employee / mo'; }" in js
    assert "roll($('.t-emp', c), p && p.next ? thin(P.perEmp(money(pe * 100, L))) : '', quiet);" in js
    # те же числа, что у генератора лендинга: 5 → $20 / $17, 50 → $10 / $8, 150 → $7 / $6
    for n, month, year in ((5, 20, 17), (50, 10, 8), (150, 7, 6), (10, 10, 8), (11, 45, 38), (249, 4, 3)):
        band = B.band_of(n)
        assert (B.per_employee(band, "month", n), B.per_employee(band, "year", n)) == (month, year), n
    assert B.per_employee(B.band_of(300), "month", 300) is None
    assert ('<ol class="bands" id="bands" aria-hidden="true"><li class="on">1–10</li><li>11–100</li><li>101–249</li>'
            '<li>250+</li></ol>') in sec
    assert "$$('#bands li').forEach(function (li, k) { li.classList.toggle('on', k === bi); });" in js
    assert ".bands li.on { color: #fff; font-weight: 700; }" in html
    assert ".bands li.on::before { background: linear-gradient(90deg, #8854F3, #F97316); }" in html
    assert "rg.setAttribute('aria-valuetext', P.emp(n, more) + ' (' + b.id + ')');" in js


def test_no_start_free_button_and_first_process_free_under_each_card():
    """FR-SITE117. Владелец 26.11: «"One process pool for the whole company — the
    admin decides who gets how many" — убери», «"Start free — 1 process" — эту
    кнопку убери, просто должно быть снизу под каждой написано First process free»."""
    html, sec = _html(), _pricing()
    for gone in ("Начать бесплатно — 1 процесс", "Start free — 1 process", "pr-go", "pr-free", "pr-lim", "s8.lim", "s8.free",
                 "Запас процессов", "One process pool", "admin decides"):
        assert gone not in html, gone
    foot = '<p class="t-foot" data-i18n="s8.first">Первый процесс — бесплатно</p></div>'
    assert sec.count(foot) == 3 and sec.count('<article class="tier') == 3, "под кнопкой каждого из трёх пакетов"
    assert "'s8.first': 'First process free'" in html
    assert ".t-foot { margin: 0; text-align: center; font-size: 11.5px; color: var(--tx3); white-space: nowrap; }" in html


def test_large_company_is_on_request_and_opens_the_lead_form():
    """FR-SITE118: с 250 сотрудников — «По запросу» / “On request”, кнопки пакетов —
    «Связаться», та же заявка FormSubmit; источник заявки — размер, группа, период
    и пакет без валюты: «Pricing: 5 (1–10) / month / platform»."""
    html, js = _html(), _calc_js()
    assert "ask: 'По запросу', ask2: 'по запросу', contact: 'Связаться'," in js
    assert "ask: 'On request', ask2: 'on request', contact: 'Contact us'," in js
    assert "if (b.a == null) return null;" in js and "row.classList.toggle('ask', !p);" in js
    assert "go.innerHTML = p ? t(go.getAttribute('data-i18n')) : P.contact;" in js
    assert ("openLead('Pricing: ' + n + (n >= EMP[EMP.length - 1] ? '+' : '') + ' (' + BANDS[bandOf(n)].id + ') / ' + "
            "state.period + ' / ' + state.pkg, 'quote');") in js
    assert re.findall(r'data-pick="(\w+)"', html) == ["strategy", "platform", "transformation"]
    assert ".t-pr .ask .cur, .t-pr .ask .per { display: none; }" in html
    assert "var LEAD_ENDPOINT = 'https://formsubmit.co/ajax/admin@andre.technology';" in html


def test_packages_stay_as_they_were():
    """FR-SITE101/114: те же три карточки, состав, «Рекомендуем» и кнопки-заявки;
    пакеты — стратегия, платформа, трансформация."""
    sec = _pricing()
    assert re.findall(r'<article class="tier( hot)?" data-pkg="(\w+)"', sec) == \
        [("", "strategy"), ("", "platform"), (" hot", "transformation")]
    assert '<em class="t-badge" data-i18n="rec">Рекомендуем</em>' in sec
    for key, name in (("p1", "ИИ-стратегия"), ("p2", "ИИ-платформа"), ("p3", "ИИ-трансформация")):
        assert '<p class="t-name" data-i18n="%s">%s</p>' % (key, name) in sec
    assert [sec.count('data-c="%s"' % c) for c in "aspt"] == [3, 3, 2, 1], "состав пакетов прежний"
    assert sec.count('<span data-i18n="s8.c.') == 3
    assert sec.count('<div class="t-pr"><p class="t-was"></p><div class="pr-row"><span class="cur">$</span><span class="num"></span>'
                     '<span class="per"></span></div><p class="t-add t-next"></p><p class="t-add t-emp"></p></div>') == 3


def test_pricing_slide_never_scrolls_inside():
    """FR-SITE95, NFR-SITE103: внутри слайдов прокрутки нет — на коротком окне
    содержимое ужимается целиком; на телефоне переключатель, ползунок и кнопки —
    не ниже 44 px."""
    html = _html()
    assert "function fitPricing()" in html
    assert "inn.style.zoom = (z * room / now * 0.995).toFixed(4);" in html
    assert "buildRoad(); fitPricing(); });" in html, "после загрузки шрифта"
    assert "placeLang(); fitPricing(); if (ORDER[state.i] === 'pricing')" in html, "при смене размера окна"
    assert "#period button { min-height: 44px; }" in html
    assert ".tier .t-go { min-height: 44px; }" in html
    assert ".rng { flex: 1 1 auto; min-width: 0; height: 44px;" in html


def test_faq_prices_follow_the_new_grid():
    """FR-SITE114: ответы FAQ о цене не спорят с калькулятором — стратегия разово
    $100 / $500 / $1 000 по размеру, 250+ по запросу; платформа от $100 в месяц, год —
    как 10 месяцев; обучение — три месяца, 12 занятий по часу, от $857 при $50/ч."""
    html = _html()
    for gone in ("$29", "2 900", "2,900", "$2,500", "249 000", "Подписка по тарифу", "subscription by plan", "50–249"):
        assert gone not in html, gone
    assert ('<p data-i18n="fa.s5">Разово, по размеру компании: $100 — до 10 сотрудников, $500 — 11–100, $1 000 — 101–249, '
            'для 250+ — по запросу.') in html
    assert "'fa.s5': 'A one-time payment by company size: $100 for up to 10 employees, $500 for 11–100, $1,000 for 101–249, on request for 250+." in html
    assert '<p data-i18n="fa.o6">Подписка от $100 в месяц в зависимости от размера компании' in html
    assert "'fa.o6': 'A subscription from $100/month depending on company size" in html
    assert '<p data-i18n="fa.t4">Обучение — три месяца, 12 занятий по часу с консультантом: от $857 при ставке $50 в час.' in html
    assert "'fa.t4': 'Training is three months, 12 one-hour sessions with a consultant: from $857 at $50/hour." in html


def test_home_and_ai_strategy_page_share_the_grid():
    """FR-SITE119, NFR-SITE105: главная и лендинг ИИ-стратегии считают по одной
    сетке — группы, деления ползунка, буткемп и «год = 10 месяцев»."""
    from tools import build_strategy as B
    js = _calc_js()
    assert [(b[0], b[2], b[3], b[4]) for b in B.BANDS] == _home_bands()
    emp = [int(x) for x in re.search(r"var EMP = \[([^\]]+)\];", js).group(1).split(",")]
    assert emp == B.EMP_STOPS
    assert round(12 * 50 * 100 / 0.7) == B.BOOTCAMP_CENTS and B.YEAR_PAID == 10


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
