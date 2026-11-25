# -*- coding: utf-8 -*-
"""Тесты главной andre.technology (index.html) — лендинг-слайды (FR-SITE95..97).

Без зависимостей — запускается и как `python3 tests/test_site.py`, и через pytest.

Прежняя главная (FR-SITE1..12, 17..26, 89..94 в части index.html) заменена
целиком; её тесты остались в истории git и возвращаются вместе с откатом
(точка отката — в AGENTS.md, чекпоинт pr93).

FR-SITE95 — главная: слайды (с FR-SITE103 — двенадцать), холст фиксированной
            ширины, ИИ-мозг из графа, переходы видео ↔ кружок ↔ полоса ↔ «Andre AI».
FR-SITE96 — политика конфиденциальности и условия использования: свои страницы
            на двух языках (tools/build_legal.py), подвал ведёт на них.
FR-SITE97 — соцсети в подвале: у русской и английской версии свои аккаунты.
FR-SITE98 — телефон: заголовки и анимации по центру и по середине экрана.
FR-SITE99 — подвал: иконки почти под меню, «ANDRE AI» с формой — по центру.
FR-SITE100 — составные слова с «ИИ-» — обычный дефис и запрет переноса, без
            неразрывного дефиса U+2011 (его нет в JetBrains Mono).
FR-SITE101 — цены: ползунок «сколько сотрудников» сам выбирает тариф, месяц / год,
            $ / ₽, бесплатный процесс — главная кнопка, у 250+ «от …» и «Связаться»;
            пакеты прежние. В браузере (1440×900 и 390×844, RU и EN, переключатели,
            прокрутка, ошибки консоли, высота кнопок) это проверяет tools/pricing_check.py.
FR-SITE103 — «Как закрываем ИИ-трансформацию»: семь измерений ИИ-зрелости → пять
            решений (Andre AI, обучение, Нейроний, консультант, R&D под задачу),
            пакет подсвечивает свою часть и показывает цену по ползунку «Цен», путь
            продукта. В браузере (12 размеров, RU и EN) — tools/cover_check.py.
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

SLIDES = ["hero", "change", "maturity", "cover", "strategy", "neuronium", "training",
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
    содержимого. С FR-SITE101 «Индивидуально / Custom» нет — у 250+ цена «от …»,
    а самая длинная строка — рубли за год: строка цены не переносится, цифры
    ужимает скрипт по ширине карточки, высота строки остаётся прежней."""
    html = _html()
    assert ".tiers { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));" in html
    assert "grid-template-rows: subgrid; grid-template-columns: minmax(0, 1fr);" in html, \
        "колонка карточки не шире самой карточки"
    assert ".t-pr .pr-row { display: flex; align-items: flex-start; flex-wrap: nowrap; white-space: nowrap; }" in html
    assert ".t-inc { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr);" in html
    assert "function fitPrices()" in html and "r.style.minHeight = getComputedStyle(n).fontSize; shrink(r, n, 0.55);" in html
    assert "num.txt" not in html, "строки «Индивидуально / Custom» больше нет"


# ── FR-SITE101: цены — ползунок «сколько сотрудников», месяц / год, $ / ₽ ──

# сетка владельца 24.11: $ в месяц, $ за год, ₽ в месяц, ₽ за год; год = 10 месяцев
OWNER_GRID = {"solo": (29, 290, 2900, 29000), "micro": (100, 1000, 9900, 99000),
              "small": (500, 5000, 49900, 499000), "medium": (1000, 10000, 99900, 999000),
              "large": (2500, 25000, 249000, 2490000)}


def _pricing():
    html = _html()
    return html[html.index('<section class="slide" id="pricing"'):html.index('<section class="slide" id="faq"')]


def test_pricing_slider_picks_the_plan_by_headcount():
    """FR-SITE101. Владелец 24.11: «не карточки тарифов, а ползунок „сколько
    сотрудников“ (1 … 1000+): по выбранному числу сам определяется тариф (1 — Соло,
    2–9 — Микро, 10–49 — Малый, 50–249 — Средний, 250+ — Крупный)». Деления —
    те же, что на лендинге ИИ-стратегии (tools/build_strategy.py, FR-SITE102)."""
    from tools import build_strategy as B
    html, sec = _html(), _pricing()
    assert '<input class="rng" id="emp-n" type="range" min="0" max="38" step="1" value="4">' in sec
    assert 'data-size=' not in html and "1–10</button>" not in html and "10–100" not in html, \
        "прежних размеров 1–10 / 10–100 / 100–250 нет"
    emp = [int(x) for x in re.search(r"var EMP = \[([^\]]+)\];", html).group(1).split(",")]
    assert emp == B.EMP_STOPS and emp[0] == 1 and emp[-1] == 1000 and len(emp) == 39
    assert emp[4] == 5, "ползунок стоит на 5 сотрудниках — «Микро»"
    for lo in (1, 2, 10, 50, 250):
        assert lo in emp, "нижняя граница тарифа — деление ползунка: %d" % lo
    assert ("function tariffOf(n) { return n <= 1 ? 'solo' : n <= 9 ? 'micro' : n <= 49 ? 'small' : "
            "n <= 249 ? 'medium' : 'large'; }") in html
    assert "$('#emp-n').addEventListener('input', function (e) { state.emp = +e.target.value; renderCalc(); });" in html
    # рядом с ползунком — число и тариф, экранному диктору — словами
    assert "$('#emp-v').innerHTML = '<b>' + n + (n >= 1000 ? '+' : '') + '</b> · ' + P.name[k];" in html
    assert "rg.setAttribute('aria-valuetext', P.emp(n, n >= 1000) + ', ' + tl);" in html
    for word in ("name: { solo: 'Соло', micro: 'Микро', small: 'Малый', medium: 'Средний', large: 'Крупный' }",
                 "name: { solo: 'Solo', micro: 'Micro', small: 'Small', medium: 'Medium', large: 'Large' }"):
        assert word in html, word


def test_pricing_grid_is_the_owners_and_matches_the_ai_strategy_page():
    """FR-SITE101/102: цены — сетка владельца 24.11 (год = 10 месяцев, 2 в подарок);
    главная и лендинг ИИ-стратегии считают по одной сетке."""
    from tools import build_strategy as B
    html = _html()
    grid = dict((k, tuple(int(x) for x in v)) for k, *v in re.findall(
        r"(\w+): \{ usd: \[(\d+), (\d+)\], rub: \[(\d+), (\d+)\] \}", html))
    assert grid == OWNER_GRID, grid
    assert dict((r[0], r[2:]) for r in B.TARIFFS) == OWNER_GRID, "лендинг ИИ-стратегии — та же сетка"
    for k, (um, uy, rm, ry) in OWNER_GRID.items():
        assert uy == 10 * um and ry == 10 * rm, k + ": год = 10 месяцев"


def test_pricing_switches_month_year_and_currency():
    """FR-SITE101: рядом с ползунком — «Месяц / Год — 2 месяца в подарок» и валюта
    $ / ₽; переключение меняет все цены; русская версия по умолчанию в рублях,
    английская — в долларах."""
    html, sec = _html(), _pricing()
    assert ('<button type="button" data-period="month" aria-pressed="true" data-i18n="s8.month">Месяц</button>'
            '<button type="button" data-period="year" aria-pressed="false" data-i18n="s8.year">Год <em>— 2 месяца в подарок</em></button>') in sec
    assert "'s8.month': 'Month', 's8.year': 'Year <em>— 2 months free</em>'" in html
    assert ('<button type="button" data-cur="usd" aria-pressed="false">$</button>'
            '<button type="button" data-cur="rub" aria-pressed="true">₽</button>') in sec
    assert "function curOf() { return state.cur || (state.lang === 'en' ? 'usd' : 'rub'); }" in html
    assert "emp: 4, period: 'month', cur: null," in html, "по умолчанию — месяц, валюта по языку"
    assert "T = TARIFF[k][cur][y], M = MENTOR[cur]" in html, "цена — по тарифу, периоду и валюте"
    assert "$('#period').addEventListener('click'" in html and "$('#cur').addEventListener('click'" in html
    assert "function money(n, cur) { return cur === 'rub' ? digits(n) + '\\u00a0₽' : '$' + digits(n); }" in html, \
        "рубль — после числа, доллар — перед"
    assert "period: 'Оплата: помесячно или за год', cur: 'Валюта'" in html
    assert "period: 'Billing: monthly or yearly', cur: 'Currency'" in html


def test_free_process_is_the_main_button():
    """FR-SITE101: «бесплатный процесс — главная кнопка»: белая кнопка `.btn` в
    продукт (тот же адрес, что у «Построить ИИ-стратегию», русская — с ?lang=ru).
    На компьютере она под пакетами, на телефоне — сразу под заголовком: кружок
    с роликом внизу справа её не закрывает."""
    html, sec = _html(), _pricing()
    links = re.findall(r'<a class="btn pr-go( pr-go-m)?" href="([^"]+)" data-href-en="([^"]+)" data-href-ru="([^"]+)">'
                       r'<span data-i18n="s8.free">Начать бесплатно — 1 процесс</span>', sec)
    assert len(links) == 2 and {l[0] for l in links} == {"", " pr-go-m"}, links
    for _m, href, en, ru in links:
        assert (href, en, ru) == ("https://strategy.andre.technology/?lang=ru", "https://strategy.andre.technology/",
                                  "https://strategy.andre.technology/?lang=ru")
    assert "'s8.free': 'Start free — 1 process'" in html
    assert ".pr-go-m { display: none; }" in html
    assert ".pr-go-m { display: flex; width: 100%; min-height: 48px; margin-top: 0.9rem; }" in html
    assert ".pr-free .pr-go { display: none; }" in html


def test_large_plan_shows_from_and_contact():
    """FR-SITE101: у 250+ цена «от …», а кнопки пакетов — «Связаться» (та же заявка,
    что и раньше у пакетов, — канал сайта FormSubmit на admin@andre.technology)."""
    html = _html()
    assert "from: 'от', contact: 'Связаться'" in html and "from: 'from', contact: 'Contact us'" in html
    assert "(big ? '<span class=\"from\">' + P.from + '</span>' : '')" in html
    assert "go.innerHTML = big ? P.contact : t(go.getAttribute('data-i18n'));" in html
    assert "openLead('Pricing: ' + n + (n >= 1000 ? '+' : '') + ' (' + tariffOf(n) + ') / ' + state.period + ' / ' + curOf() + ' / ' + state.pkg, 'quote');" in html


def test_process_pool_note_replaces_per_employee_limits():
    """FR-SITE101, владелец 24.11: «убери тексты „при оплате помесячно запас
    открывается частями“ и „10 процессов на сотрудника сразу + 1 каждый месяц“ —
    запас процессов общий на компанию, кому сколько раздаёт админ»."""
    html, sec = _html(), _pricing()
    assert ('<p class="pr-lim" data-i18n="s8.lim">Первый процесс — бесплатно. Запас процессов — общий на компанию, '
            'админ раздаёт кому сколько</p>') in sec
    assert ("'s8.lim': 'First process free. One process pool for the whole company — the admin decides who gets how many'"
            in html)
    for gone in ("на сотрудника", "на подключённого", "открывается частями", "копятся до", "per employee",
                 "opens in parts", "carry over"):
        assert gone not in html, gone


def test_packages_stay_as_they_were():
    """FR-SITE101: пакеты «стратегия / инструменты / ментор» не трогаем — те же три
    карточки, состав, «Рекомендуем» и обучение $2 900 в месяц; от тарифа берётся
    только цена: стратегия — по тарифу, Нейроний — подписка на ту же сумму."""
    html, sec = _html(), _pricing()
    assert re.findall(r'<article class="tier( hot)?" data-pkg="(\w+)"', sec) == [("", "strategy"), ("", "tools"), (" hot", "mentor")]
    assert '<em class="t-badge" data-i18n="rec">Рекомендуем</em>' in sec
    for key, name in (("p1", "ИИ-стратегия"), ("p2", "ИИ-платформа"), ("p3", "ИИ-трансформация")):
        assert '<p class="t-name" data-i18n="%s">%s</p>' % (key, name) in sec
    assert [sec.count('data-c="%s"' % c) for c in "aspt"] == [3, 3, 2, 1], "состав пакетов прежний"
    assert sec.count('<span data-i18n="s8.c.') == 3
    assert "var MENTOR = { usd: 2900, rub: 289000 };" in html
    assert "if (key === 'strategy') v = row(T, per)" in html and "else if (key === 'tools') v = row(2 * T, per)" in html
    assert "else v = row(M + 2 * T, per)" in html


def test_pricing_slide_never_scrolls_inside():
    """FR-SITE95: внутри слайдов прокрутки нет. Новые строки цен выше прежних —
    на коротком окне (телефон 375×667, планшет, очень широкое окно) содержимое
    ужимается целиком, как экраны лендинга ИИ-стратегии (fitScreen)."""
    html = _html()
    assert "function fitPricing()" in html
    assert "inn.style.zoom = (z * room / now * 0.995).toFixed(4);" in html
    assert "buildRoad(); fitPricing(); });" in html, "после загрузки шрифта"
    assert "placeLang(); fitPricing(); if (ORDER[state.i] === 'pricing')" in html, "при смене размера окна"
    # телефон: переключатели и кнопки под палец
    assert ".pr-sw .sizes button { min-height: 44px; } #cur button { min-width: 44px; }" in html
    assert ".tier .t-go { min-height: 44px; }" in html
    assert ".rng { flex: 1 1 auto; min-width: 0; height: 44px;" in html


def test_faq_prices_follow_the_plans():
    """FR-SITE101: ответы FAQ о цене — по новой сетке, без разовой стратегии и
    прежних размеров «10–100» / «250+ — индивидуально»."""
    html = _html()
    for gone in ("Разово:", "разовая стратегия", "one-time", "$3 400", "$3,400", "10–100", "индивидуально", "custom for 250+"):
        assert gone not in html, gone
    assert "от 2 900 ₽ в месяц за одного до 99 900 ₽ за 50–249 человек, для 250+ — от 249 000 ₽" in html
    assert "from $29/month for one person to $1,000 for 50–249 people, from $2,500 for 250+" in html
    assert '<p data-i18n="fa.o6">Подписка от 2 900 ₽ в месяц' in html and "'fa.o6': 'A subscription from $29/month" in html


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


# ── FR-SITE103: как закрываем ИИ-трансформацию ─────────────────────────────

def _cover():
    html = _html()
    return html[html.index('<section class="slide" id="cover"'):html.index('<section class="slide" id="strategy"')]


def _en(key):
    """Английская строка словаря EN по ключу (русская — в самой разметке)."""
    m = re.search(r"'%s': '((?:[^'\\]|\\.)*)'" % re.escape(key), _html())
    return m and m.group(1)


# что закрывает каждая группа схемы: измерения ИИ-зрелости → слайд решения (или заявка) и его имя
COVER_GROUPS = [
    ("s", ["Стратегия"], 'data-go="strategy"', "Andre AI"),
    ("t", ["Люди"], 'data-go="training"', "Обучение"),
    ("p", ["Инфраструктура", "Данные", "Модели"], 'data-go="neuronium"', "Нейроний"),
    ("c", ["Внедрение"], 'data-go="training"', "Консультант"),
    (None, ["R&amp;D"], 'data-lead="R&amp;D"', "Под вашу задачу"),
]


def _groups():
    return _cover().split('<div class="cvr-g" role="listitem"')[1:]


def test_cover_slide_follows_the_maturity_index():
    """FR-SITE103. Владелец 24.11: «чтобы было понятно, что закроет каждую часть». Слайд «Как закрываем
    ИИ-трансформацию» стоит сразу за «Индексом ИИ-зрелости»: там семь измерений диагностики, здесь — что
    закрывает каждое."""
    assert SLIDES.index("cover") == SLIDES.index("maturity") + 1
    sec = _cover()
    assert '<section class="slide" id="cover" data-head="bubble">' in sec
    assert '<span data-i18n="cv.k">Как закрываем <span class="nw">ИИ-трансформацию</span></span>' in sec
    assert _en("cv.k") == "How we cover AI transformation"
    assert _en("cv.h") == '<span class="l">A <span class="pv">solution</span></span><span class="l">for every <span class="go">part</span></span>'
    assert ('<h2 class="h2 st" data-i18n="cv.h"><span class="l">Своё <span class="pv">решение</span></span>'
            '<span class="l">для каждой <span class="go">части</span></span></h2>') in sec
    assert "cover: { label: { ru: 'Решения', en: 'Solutions' } }" in _html()


def test_cover_maps_the_seven_dimensions_to_five_solutions():
    """FR-SITE103: стратегия — Andre AI (ИИ-стратегия: что делать); люди — обучение; инфраструктура, данные и
    модели — Нейроний; внедрение — консультант по стратегии; R&D — под вашу задачу. Измерения те же и в том же
    порядке, что на радаре диагностики (DIMS), по-русски и по-английски; каждое решение ведёт на свой слайд,
    R&D — в заявку."""
    html, groups = _html(), _groups()
    assert len(groups) == len(COVER_GROUPS) == 5
    dims = []
    for (key, want, target, title), g in zip(COVER_GROUPS, groups):
        assert (' data-cv="%s"' % key in g.split(">")[0]) if key else "data-cv" not in g.split(">")[0], (key, g[:80])
        got = re.findall(r'<span class="cvr-d" style="--row:\d"><span[^>]*>([^<]+)</span>', g)
        assert got == want, (key, got)
        dims += got
        btn = re.search(r'<button class="cvr-s[^"]*" type="button" ([^>]+)><b[^>]*>([^<]+)', g)
        assert btn and btn.group(1).startswith(target) and btn.group(2) == title, (key, btn and btn.groups())
    radar = re.search(r"var DIMS = \{ ru: \[([^\]]+)\], en: \[([^\]]+)\] \};", html)
    assert [d.replace("&amp;", "&") for d in dims] == [x.strip(" '") for x in radar.group(1).split(",")]
    assert [_en("cv.d%d" % i) for i in range(1, 7)] + ["R&D"] == [x.strip(" '") for x in radar.group(2).split(",")]
    # три измерения сходятся скобкой в одно решение — Нейроний на три строки
    assert '<i class="cvr-l cvr-l3" style="--row:3;--n:3" aria-hidden="true"></i>' in groups[2]
    assert '<button class="cvr-s cvr-s3" type="button" data-go="neuronium" style="--row:3;--n:3">' in groups[2]
    for k, en in (("cv.s1", "Andre AI"), ("cv.s2", "Training"), ("cv.s3", "Neuronium"), ("cv.s4", "Consultant"),
                  ("cv.s5", "Built for your task")):
        assert _en(k).startswith(en), (k, _en(k))
    assert "'R&amp;D'" not in html and 'data-lead="R&amp;D"' in _cover(), "источник заявки — «R&D»"


def test_cover_packages_are_the_pricing_packages():
    """FR-SITE103: «свяжи с существующими пакетами». Переключатель над схемой — те же три пакета, что в «Ценах»;
    пакет подсвечивает то, что в нём есть, — по составу чека его карточки (data-c): стратегия — Andre AI,
    платформа — ещё Нейроний, трансформация — ещё обучение с консультантом (люди и внедрение). R&D — под задачу,
    ни в один пакет не входит и не гаснет. По умолчанию — рекомендованная «ИИ-трансформация»."""
    html, sec, price = _html(), _cover(), _pricing()
    assert "var COVER = { strategy: ['s'], tools: ['s', 'p'], mentor: ['s', 'p', 't', 'c'] };" in html
    cover = {"strategy": ["s"], "tools": ["s", "p"], "mentor": ["s", "p", "t", "c"]}
    line = {"s": "s", "p": "p", "t": "t", "c": "t"}  # обучение и внедрение — одна строка чека «ИИ-обучение»
    for pkg, parts in cover.items():
        card = price[price.index('data-pkg="%s"' % pkg):]
        card = card[:card.index("</article>")]
        assert set(re.findall(r'data-c="(\w)"', card)) - {"a"} == {line[p] for p in parts}, pkg
    assert re.findall(r'data-cvr-pkg="(\w+)" aria-pressed="(\w+)"', sec) == [("strategy", "false"), ("tools", "false"), ("mentor", "true")]
    assert "pkg: 'mentor', cov: 'mentor'," in html
    for k, ru, en in (("cv.b1", "ИИ-стратегия", "AI Strategy"), ("cv.b2", "ИИ-платформа", "AI Platform"),
                      ("cv.b3", "ИИ-трансформация", "AI Transformation")):
        assert '<span class="tl" data-i18n="%s">%s</span>' % (k, ru) in sec and _en(k) == en, k
    assert "g.classList.toggle('off', has.indexOf(g.getAttribute('data-cv')) < 0)" in html
    assert ".cvr-g.off > * { opacity: 0.3; }" in html


def test_cover_price_is_the_package_price_from_the_pricing_slider():
    """FR-SITE103: «…и ценами ползунком (не ломай их)». Цена выбранного пакета — тот же расчёт, что в его
    карточке, по тому же ползунку, периоду и валюте; пересчитывается при каждом их изменении (renderCalc);
    цена — кнопка на «Цены». Разметка по умолчанию — «ИИ-трансформация» на 5 сотрудников за месяц в рублях."""
    html, sec = _html(), _cover()
    assert "    renderCover();\n    fitPricing();\n  }" in html, "renderCalc пересчитывает и этот слайд"
    assert "T = TARIFF[k][cur][y], M = MENTOR[cur], pk = state.cov, has = COVER[pk];" in html
    # стратегия — тариф; платформа — вдвое; трансформация — ещё обучение помесячно, за год — отдельной строкой (как в карточке)
    assert "var v = pk === 'strategy' ? T : (pk === 'tools' || y) ? 2 * T : M + 2 * T" in html
    assert "(pk === 'mentor' && y ? th(P.train(money(M, cur))) : P.emp(n, n >= 1000) + ' · ' + P.name[k])" in html
    assert "th((big ? P.from + ' ' : '') + money(v, cur))" in html, "у 250+ — «от …»"
    assert '<button class="cvr-pr" type="button" id="cvr-pr" data-go="pricing" aria-live="polite">' in sec
    rub = OWNER_GRID["micro"][2]
    default = 289000 + 2 * rub
    assert default == 308800
    assert '<b>308<span class="th"></span>800<span class="th"></span>₽</b> / мес' in sec
    assert '<span class="cvr-p2">5 сотрудников · Микро</span>' in sec
    assert "$$('#cover [data-go=\"pricing\"]').forEach(" in html, "на телефоне лента «Цен» открывается на выбранном пакете"


def test_cover_tells_the_product_path():
    """FR-SITE103: путь продукта — ИИ-диагностика → интервью и схемы «как есть / как будет» → план → «Разработать
    в Нейроний» (без второго входа: те же процессы с агентами, граф артефактов, переключение на операции) →
    внедрение с консультантом."""
    sec = _cover()
    path = re.findall(r'<span data-i18n="cv\.w(\d)">([^<]+)</span>', sec)
    assert [w for _, w in path] == ["ИИ-диагностика", "интервью и схемы", "план", "Нейроний", "внедрение"]
    assert [_en("cv.w%s" % i) for i, _ in path] == ["AI assessment", "interview &amp; maps", "plan", "Neuronium", "rollout"]
    assert sec.count('<i aria-hidden="true">→</i>') == 4 + 1, "стрелки пути + стрелка у цены"
    assert ' <i aria-hidden="true">→</i> ' in sec, "между шагами — пробелы: строка пути переносится"
    t3 = re.search(r'data-i18n="cv\.t3">([^<]+)<', sec).group(1)
    for part in ("«Разработать в Нейроний»", "без второго входа", "те же процессы, но с агентами", "граф артефактов",
                 "документы, системы и данные связаны", "переключение на операции"):
        assert part in t3, part
    for part in ("Build in Neuronium", "no second sign-in", "the same processes, now with agents", "artifact graph",
                 "documents, systems and data", "operations view"):
        assert part in _en("cv.t3"), part
    assert 'data-i18n="cv.t1">что делать: схемы «как есть → как будет» и план<' in sec and _en("cv.t1").startswith("what to do")
    assert "внедряет ваш план" in sec and _en("cv.t4") == "rolls out your AI transformation plan"
    assert "по запросу" in sec and _en("cv.t5").endswith("on request")


def test_cover_fits_without_scrolling_and_keeps_buttons_out_from_under_the_bubble():
    """FR-SITE95/103: слайд не листается внутри. Он плотнее остальных — как «Цены»: на телефоне прижат к верху
    (внизу справа кружок с роликом), выше рамки — ужимается целиком; на телефоне схема ещё и кончается выше
    кружка (не мельче 0,8). Кнопки на телефоне — не ниже 44px. В браузере — tools/cover_check.py."""
    html = _html()
    assert '<div class="inner split cvr-split" data-top data-fit=".cvr-map">' in html
    assert "function fitDense(inn)" in html and "lim = rr(bub).top - 10" in html and "Math.max(0.8, z2 * (lim - top) / (bot - top))" in html
    assert "var dense = sp.hasAttribute('data-fit'); if (dense) sp.style.zoom = '';" in html, "ужатие сбрасывается перед замером"
    assert "if (!phone) { if (dense) fitDense(sp);" in html
    assert "if (sp.hasAttribute('data-top')) { if (dense) fitDense(sp); return; }" in html
    assert "sp.style.left = Math.round(dx / (parseFloat(sp.style.zoom) || 1)) + 'px'" in html, "сдвиг ужатого слайда — в его масштабе"
    # компьютер: пара «текст + схема» левее кружка и на холсте 1180
    assert ".cvr-split > .vis { width: min(100%, 37.5rem, calc(100cqw - 680px)); }" in html
    # телефон: кнопки под палец, путь — левее кружка, решения — именем
    for rule in (".cvr-pk .sizes button { min-height: 44px;", "justify-content: center; min-height: 44px; margin: 0.3rem auto 0.5rem;",
                 "grid-template-rows: repeat(7, minmax(44px, 1fr));", ".cvr-path { max-width: calc(100% - var(--bs) - var(--bm));",
                 ".cvr-s .cvr-x, .cvr-s:not(.cvr-s3) .cvr-t { display: none; }", "#cover .actions { display: none; }"):
        assert rule in html, rule
    assert os.path.exists(os.path.join(_ROOT, "tools", "cover_check.py"))


def test_cover_is_in_the_phone_menu_and_footer_but_not_the_header():
    """FR-SITE103: в шапке девятый пункт не помещается — на холсте 1180 (окно 1024×768, 1280×1024) он налезает
    на EN|RU и кнопку диагностики; слайд стоит в потоке между «Диагностикой» и «Стратегией», а в меню телефона
    и в ссылках подвала у него свой пункт."""
    html = _html()
    hdr = html[html.index('<nav class="nav"'):html.index("</nav>", html.index('<nav class="nav"'))]
    assert 'data-go="cover"' not in hdr
    assert ('<a href="#cover" data-go="cover" style="--ic:#c06bc9"><i class="fa-solid fa-puzzle-piece"></i>'
            '<span data-i18n="nav.cover">Решения</span><i class="fa-solid fa-arrow-right"></i></a>') in html
    assert '<a href="#cover" data-go="cover" data-i18n="nav.cover">Решения</a>' in html
    assert _en("nav.cover") == "Solutions"


def test_slide_classes_do_not_clash_with_canvas_mode_classes():
    """FR-SITE103, грабли: скрипт холста ставит <html> класс cv-d (компьютер) или cv-m (телефон). Черновик слайда
    назвал подписи схемы .cv-d — и правило «.cv-d i» превратило в кружки все значки страницы, а меню стало
    заглавным. Префикс слайда — cvr-; классов cv-… в разметке и CSS нет."""
    html = _html()
    assert "dE.className = dE.className.replace(/\\s*cv-[dm]\\b/g, '') + (m ? ' cv-m' : ' cv-d');" in html
    assert not re.search(r'class="[^"]*\bcv-', html)
    css = html[html.index("<style>"):html.index("</style>")]
    assert not re.search(r"\.cv-[a-z]", css)


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok  ", name)
            n += 1
    print("\nВсе тесты сайта пройдены:", n)
