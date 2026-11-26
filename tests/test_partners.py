# -*- coding: utf-8 -*-
"""Тесты сайта партнёров partners.andre.technology (partners/) — FR-SITE120…139, NFR-SITE106…110.

Запуск: `python3 tests/test_partners.py` или через pytest. Строковые проверки —
без зависимостей. Проверки в браузере (имя test_render_*) берут Playwright и
Chromium (/opt/pw-browsers/chromium или CHROMIUM_PATH); если их нет — пропускаются,
а не валят прогон. Страница поднимается в двух видах адреса, как на проде: как
GitHub Pages (/partners/) и как поддомен за Caddy (прокси переписывает /x →
/partners/x) — их даёт tools/partners_check.py.

FR-SITE120 — своя папка, стиль главной, главная не меняется.
FR-SITE121 — короткий первый экран: партнёры видны сразу.
FR-SITE122 — порядок «от лучших к худшим» (байесовский рейтинг).
FR-SITE123/124 — карточка каталога, LinkedIn в новой вкладке.
FR-SITE125…129 — поиск, фильтры, сортировка, порции, состояние в адресе.
FR-SITE130…133 — публичная карточка (окно и ?p=), цены по политике, заявка.
FR-SITE134…136 — как стать партнёром: шаги, заработок, заявка.
FR-SITE137/138 — partners.json по схеме, встроенная копия, три примера.
FR-SITE139 — русский и английский по правилу главной.
NFR-SITE106…110 — клавиатура, телефон, движение, качество, хостинг.
"""
import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

try:
    import pytest
except ImportError:  # запуск без pytest: python3 tests/test_partners.py
    pytest = None

NIKA, LUKAS, ARUZHAN = "example-nika-vetrova", "example-lukas-brenner", "example-aruzhan-seitova"
BEST = [NIKA, LUKAS, ARUZHAN]
ENDPOINT = "https://formsubmit.co/ajax/admin@andre.technology"
LOGO_URL = "https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png"


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _html():
    return _read("partners/index.html")


def _js():
    return _read("partners/partners.js")


def _css():
    return _read("partners/partners.css")


def _data():
    return json.loads(_read("partners/partners.json"))


def _i18n():
    from tools import build_partners
    return build_partners.read_i18n()


def _cents_half_up(num, den):
    return (2 * num + den) // (2 * den)


def _policy(rate):
    """Ценовая политика §4: клиент = вознаграждение ÷ 0,70, центы, half-up по позиции."""
    rc = round(rate * 100)
    review = _cents_half_up(rc * 10, 7)
    one = _cents_half_up(rc, 7)
    boot = _cents_half_up(rc * 120, 7)
    return {"review": review, "one": one, "boot": boot, "month": _cents_half_up(boot, 3), "pay_review": rc, "pay_boot": rc * 12}


# ── FR-SITE120: своя папка, стиль главной ───────────────────────────────────

def _money(cents, lang):
    """Как на странице: $2 057,14 (неразрывный пробел) по-русски, $2,057.14 по-английски, целые — без копеек."""
    d, r = divmod(cents, 100)
    g = "{:,}".format(d).replace(",", "\u00a0" if lang == "ru" else ",")
    return "$" + g + ("" if not r else ("," if lang == "ru" else ".") + "%02d" % r)


def test_page_is_self_contained_in_its_folder():
    """FR-SITE120: всё новое — в partners/; у страницы свои CSS и JS, данные и значки
    лежат рядом; ни на что из корня сайта она относительным путём не ссылается."""
    for rel in ("index.html", "partners.css", "partners.js", "partners.json", "og.png",
                "favicon.ico", "favicon-32x32.png", "favicon-16x16.png", "apple-touch-icon.png"):
        assert os.path.isfile(os.path.join(_ROOT, "partners", rel)), "нет partners/" + rel
    html = _html()
    assert re.search(r'<link rel="stylesheet" href="partners\.css\?v=[0-9a-f]{8}">', html)
    assert re.search(r'<script src="partners\.js\?v=[0-9a-f]{8}"></script>', html)
    assert "<style" not in html, "стили — в partners.css"
    for name in ("favicon.ico", "favicon-32x32.png", "favicon-16x16.png", "apple-touch-icon.png"):
        with open(os.path.join(_ROOT, name), "rb") as a, open(os.path.join(_ROOT, "partners", name), "rb") as b:
            assert a.read() == b.read(), "partners/%s — копия корневого значка байт в байт" % name


def test_style_tokens_match_the_main_page():
    """FR-SITE120: «в таком же стиле» — те же цвета, шрифт, кнопка, надзаголовок и
    заголовок, что на главной (index.html), но своим файлом."""
    css, main = _css(), _read("index.html")
    for token in ("--bg: #050505", "--p: #8854F3", "--p2: #a071ff", "--o: #F97316", "--o2: #ff8a33", "--tx3: #94a3b8"):
        assert token in css and token in main, token
    assert "--fd: 'JetBrains Mono'" in css and "family=JetBrains+Mono" in _html()
    btn_hover = "background: linear-gradient(100deg, #8854F3 0%, #F97316 50%, #8854F3 100%); background-size: 250% 250%;"
    assert btn_hover in css and btn_hover in main, "кнопка — белая пилюля с переливом, как на главной"
    assert ".kicker { display: flex; align-items: center;" in css and "letter-spacing: 0.18em; text-transform: uppercase; color: var(--tx3); }" in css
    assert ".h2 { margin: 0; font-weight: 800; text-transform: uppercase;" in css
    assert ".glow {" in css and "@keyframes glowW" in css and ".grain {" in css


def test_no_dead_links_and_logo_like_the_main_page():
    """FR-SITE120, FR-SITE11: без заглушек; логотип — с того же адреса, что на главной."""
    html = _html()
    assert 'href="#"' not in html and "заглушк" not in html.lower()
    assert 'src="%s"' % LOGO_URL in html
    logo = re.search(r'<a class="logo" href="([^"]+)" data-href-ru="([^"]+)" data-href-en="([^"]+)"', html)
    assert logo and logo.groups() == ("https://andre.technology/?lang=ru", "https://andre.technology/?lang=ru", "https://andre.technology/")
    for anchor in re.findall(r'href="#([\w-]+)"', html):
        assert 'id="%s"' % anchor in html, "якорь #%s ведёт в никуда" % anchor


# ── NFR-SITE110: хостинг ────────────────────────────────────────────────────

def test_paths_are_relative_and_main_site_links_are_absolute():
    """NFR-SITE110: одни и те же файлы на andre.technology/partners/ и на поддомене —
    свои ресурсы только относительными путями (без «/…» и «../»), чужие страницы —
    полными адресами."""
    html, js = _html(), _js()
    for m in re.finditer(r'\b(?:src|href)="([^"]+)"', html):
        url = m.group(1)
        assert not url.startswith("/") and not url.startswith("../"), "путь от корня не сработает на поддомене: " + url
        assert re.match(r"^(https://|mailto:|#|\?p=|partners\.(css|js)\?v=|favicon|apple-touch-icon)", url), url
    assert "fetch('partners.json'" in js and "'/partners" not in js and '"/partners' not in js
    assert "href=\"?p=' + encodeURIComponent(p.slug)" in js, "адрес профиля — относительный ?p=<slug>"
    for path in re.findall(r'(?:src|href)="(/[^"]*)"', html):
        assert not any(seg.startswith("_") for seg in path.split("/") if seg), path


def test_head_has_canonical_og_hreflang_and_icons():
    """NFR-SITE110: title, description, canonical и og:url — поддомен, hreflang,
    превью для соцсетей, значки — свои файлы рядом."""
    html = _html()
    head = html.split("</head>")[0]
    assert "<title>Партнёры Andre AI — консультанты по ИИ-трансформации</title>" in head
    assert '<meta name="description" content="' in head
    assert '<link rel="canonical" href="https://partners.andre.technology/">' in head
    assert '<meta property="og:url" content="https://partners.andre.technology/">' in head
    for lang in ("ru", "en"):
        assert '<link rel="alternate" hreflang="%s" href="https://partners.andre.technology/?lang=%s">' % (lang, lang) in head
    assert 'hreflang="x-default" href="https://partners.andre.technology/"' in head
    for prop in ("og:title", "og:description", "og:image", "og:image:width", "og:image:height"):
        assert 'property="%s"' % prop in head, prop
    assert '<meta property="og:image" content="https://andre.technology/partners/og.png">' in head
    with open(os.path.join(_ROOT, "partners/og.png"), "rb") as f:
        head_png = f.read(24)
    assert head_png[:8] == b"\x89PNG\r\n\x1a\n" and (int.from_bytes(head_png[16:20], "big"), int.from_bytes(head_png[20:24], "big")) == (1200, 630)
    for rel in re.findall(r'<link rel="(?:icon|apple-touch-icon)"[^>]*href="([^"]+)"', head):
        assert os.path.isfile(os.path.join(_ROOT, "partners", rel)), rel
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head, re.S).group(1))
    assert ld["@type"] == "CollectionPage" and ld["url"] == "https://partners.andre.technology/"
    ld_txt = json.dumps(ld)
    for kind in ('"Review"', "aggregateRating", '"Person"', "reviewRating"):
        assert kind not in ld_txt, "примеры — не настоящие отзывы и люди для поисковиков: " + kind


def test_spec_has_the_caddy_block():
    """NFR-SITE110: владельцу — готовый блок Caddy: /x → /partners/x на GitHub Pages."""
    spec = _read("SPEC-SITE.md")
    sec = spec[spec.index("## Сайт партнёров partners.andre.technology"):]
    assert "partners.andre.technology {" in sec
    assert "rewrite * /partners{uri}" in sec
    assert "reverse_proxy https://andre.technology {" in sec and "header_up Host andre.technology" in sec
    assert "proxy_pass https://andre.technology/partners/;" in sec, "и вариант для nginx"


def test_spec_lists_every_requirement_and_its_tests():
    """Трассировка: у каждого FR-SITE120…139 и NFR-SITE106…110 — раздел в спеке, а
    каждый названный там тест есть в этом файле."""
    spec = _read("SPEC-SITE.md")
    sec = spec[spec.index("## Сайт партнёров partners.andre.technology"):]
    for n in range(120, 140):
        assert "### FR-SITE%d — " % n in sec, "нет FR-SITE%d" % n
    for n in range(106, 111):
        assert "### NFR-SITE%d — " % n in sec, "нет NFR-SITE%d" % n
    named = set(re.findall(r"test_partners\.(test_\w+)", sec))
    assert len(named) >= 30
    missing = sorted(t for t in named if t not in globals())
    assert not missing, "в спеке названы тесты, которых нет: %s" % missing


# ── FR-SITE137/138: данные ──────────────────────────────────────────────────

def test_partners_json_follows_the_schema():
    """FR-SITE137: массив профилей по схеме SPEC-SITE.md; та же проверка — в сборщике."""
    from tools import build_partners
    data = _data()
    assert isinstance(data, list)
    assert build_partners.validate(data) == [], build_partners.validate(data)
    # проверка ловит ошибки, а не пропускает всё
    bad = json.loads(json.dumps(data[0]))
    bad.update(slug="Bad Slug", rate_usd=30, services=["consulting"], linkedin="https://example.com/x", joined="2026-13-40")
    bad["industries"] = ["unknown"]
    errs = " ".join(build_partners.validate([bad]))
    for word in ("slug", "rate_usd", "services", "linkedin", "joined", "industries"):
        assert word in errs, word
    dup = build_partners.validate([data[0], data[0]])
    assert any("повторяется" in e for e in dup)


def test_inline_copy_and_versions_are_built_from_the_files():
    """FR-SITE137: встроенная копия = partners.json; метки ?v= = содержимое CSS и JS —
    правка без пересборки ловится здесь (`python3 tools/build_partners.py`)."""
    from tools import build_partners
    html = _html()
    inline = re.search(r'<script type="application/json" id="partners-data">(.*?)</script>', html, re.S).group(1)
    assert json.loads(inline.replace("<\\/", "</")) == _data()
    assert "</" not in inline.replace("<\\/", ""), "«</» в данных экранирован"
    for name in ("partners.css", "partners.js"):
        with open(os.path.join(_ROOT, "partners", name), "rb") as f:
            v = hashlib.sha1(f.read()).hexdigest()[:8]
        assert "%s?v=%s" % (name, v) in html, name + ": метка версии устарела — пересоберите страницу"
    assert build_partners.render_index(html, _data()) == html


def test_three_example_profiles_are_marked_and_fictional():
    """FR-SITE138: ровно три примера, все помечены example, LinkedIn — демо-адреса."""
    data = _data()
    assert len(data) == 3 and all(p.get("example") is True for p in data)
    assert [p["linkedin"] for p in data] == ["https://www.linkedin.com/in/andre-ai-partner-example-%d" % i for i in (1, 2, 3)]
    assert all(p["slug"].startswith("example-") for p in data)
    i18n = _i18n()
    assert i18n["ru"]["bdg.ex"] == "Пример профиля" and i18n["en"]["bdg.ex"] == "Example profile"
    assert "вымышлены" in i18n["ru"]["pf.ex"] and "fictional" in i18n["en"]["pf.ex"]
    for p in data:  # отзывы — без названий настоящих компаний: «сеть магазинов косметики, 120 сотрудников»
        for r in p["reviews"]:
            assert re.search(r"\d+ (сотрудников|человек)$", r["company"]["ru"]) and re.search(r"\d+ people$", r["company"]["en"])


def test_examples_make_every_filter_and_sort_visible():
    """FR-SITE138: ставки $50, около $120 и $300, разные рейтинги, услуги, отрасли,
    языки и «удалённо / очно» — каждый фильтр и каждая сортировка дают другой список."""
    data = {p["slug"]: p for p in _data()}
    assert sorted(p["rate_usd"] for p in data.values()) == [50, 120, 300]
    assert len({p["rating"] for p in data.values()}) == 3
    for svc in ("review", "bootcamp", "neuronium"):
        n = sum(svc in p["services"] for p in data.values())
        assert n == 2, svc
    assert sum(p["location"]["remote"] for p in data.values()) == 2
    assert len({p["location"]["country_code"] for p in data.values()}) == 3
    by = lambda key, rev: [s for s, _ in sorted(data.items(), key=lambda kv: kv[1][key], reverse=rev)]
    assert by("rate_usd", False) != by("projects", True) != BEST


def test_ranking_is_bayesian_and_examples_rank_as_designed():
    """FR-SITE122: score = (5 × 4,0 + rating × отзывы) / (5 + отзывы); примеры — Ника,
    Лукас, Аружан."""
    js = _js()
    assert "var PRIOR_RATING = 4.0, PRIOR_WEIGHT = 5;" in js
    assert "p._score = (PRIOR_WEIGHT * PRIOR_RATING + p.rating * p.reviews_count) / (PRIOR_WEIGHT + p.reviews_count);" in js
    assert "return (b._score - a._score) || (b.projects - a.projects) || (b.reviews_count - a.reviews_count) ||" in js
    score = lambda p: (5 * 4.0 + p["rating"] * p["reviews_count"]) / (5 + p["reviews_count"])
    assert [p["slug"] for p in sorted(_data(), key=lambda p: (-score(p), -p["projects"]))] == BEST
    # один отзыв на 5,0 не обгоняет 4,8 по тридцати отзывам
    assert score({"rating": 5.0, "reviews_count": 1}) < score({"rating": 4.8, "reviews_count": 30})


# ── FR-SITE132/135: цены по политике ────────────────────────────────────────

def test_prices_follow_the_pricing_policy():
    """FR-SITE132: контрольные примеры политики (§4, §7): $50/ч — 10 схем $71,43,
    1 схема $7,14, 5 схем $35,71, буткемп $857,14 (≈ $285,71 в месяц); $200/ч —
    $285,71 и $3 428,57 (≈ $1 142,86); промокод: $500 → $450, партнёру $45."""
    p50, p200 = _policy(50), _policy(200)
    assert (p50["review"], p50["one"], p50["boot"], p50["month"], p50["pay_boot"]) == (7143, 714, 85714, 28571, 60000)
    assert _cents_half_up(5000 * 5, 7) == 3571
    assert p50["review"] - p50["pay_review"] == 2143, "Andre AI с 10 схем по $50/ч — $21,43"
    assert (p200["review"], p200["boot"], p200["month"]) == (28571, 342857, 114286)
    js = _js()
    for line in ("var client = divHalfUp(rc * k, 7), consultant = divHalfUp(rc * k, 10);",
                 "var rc = Math.round(rate * 100), client = divHalfUp(rc * 120, 7), consultant = rc * 12;",
                 "return { client: client, consultant: consultant, andre: client - consultant, month: divHalfUp(client, 3) };",
                 "var discount = divHalfUp(listCents, 10), client = listCents - discount, commission = divHalfUp(client, 10);",
                 "function divHalfUp(num, den) { return Math.floor((2 * num + den) / (2 * den)); }"):
        assert line in js, line
    spec = _read("SPEC-SITE.md")
    for rate, row in ((50, "| $50 | $71,43 | $7,14 | $857,14 | $285,71 |"), (120, "| $120 | $171,43 | $17,14 | $2 057,14 | $685,71 |"),
                      (200, "| $200 | $285,71 | $28,57 | $3 428,57 | $1 142,86 |"), (300, "| $300 | $428,57 | $42,86 | $5 142,86 | $1 714,29 |")):
        assert row in spec, "таблица цен в спеке расходится с формулой: %s" % row


def test_become_a_partner_copy_follows_the_policy():
    """FR-SITE134/135: три шага и «от $50 до $300 в час»; 70 % услуги, +10 % по
    промокоду (клиенту −10 % на стратегию и первый месяц Нейрония)."""
    html, en = _html(), _i18n()["en"]
    sec = html[html.index('<section class="become"'):html.index("</section>", html.index('<section class="become"'))]
    assert re.findall(r'<span class="step-n">(\d\d)</span>', sec) == ["01", "02", "03"]
    assert 'data-i18n="be.s1.h">Пройдите Академию Andre AI<' in sec
    assert 'data-i18n="be.s2.h">Получите сертификат<' in sec
    assert 'data-i18n="be.s3.h">Пройдите собеседование<' in sec
    assert 'Зарабатывайте от <span class="go">$50</span> до <span class="go">$300</span> в час' in sec
    assert en["be.earn"] == 'Earn from <span class="go">$50</span> to <span class="go">$300</span> an hour'
    assert "70 % каждой услуги — ваши" in sec and "÷ 0,70" in sec and "Andre AI — 30 %" in sec
    assert "+10 % за клиентов по вашему промокоду" in sec and "−10 %" in sec and "первый месяц Нейрония" in sec
    assert 'id="calc-rate" type="range" min="50" max="300" step="5" value="120"' in sec
    assert "pr = PRICING.promo(50000)" in _js(), "пример промокода — стратегия за $500 (политика §7)"


def test_academy_step_leads_to_the_course():
    """FR-SITE134: своей страницы у Академии нет — шаг ведёт на курс для будущих
    ИИ-консультантов на языке посетителя, полным адресом."""
    html = _html()
    a = re.search(r'<a class="link" id="academy" href="([^"]+)" data-href-ru="([^"]+)" data-href-en="([^"]+)">', html)
    assert a and a.groups() == ("https://andre.technology/automation_ru/", "https://andre.technology/automation_ru/",
                                "https://andre.technology/automation/")
    assert os.path.isfile(os.path.join(_ROOT, "automation_ru/index.html")) and os.path.isfile(os.path.join(_ROOT, "automation/index.html"))
    assert "будущих ИИ-консультантов" in _read("automation_ru/index.html")


# ── FR-SITE124/133/136: LinkedIn и формы ────────────────────────────────────

def test_linkedin_is_required_and_opens_in_a_new_tab():
    """FR-SITE124: LinkedIn обязателен; открывается в новой вкладке с rel=noopener."""
    js = _js()
    assert "if (typeof p.linkedin !== 'string' || !IN_RE.test(p.linkedin)) return 'linkedin';" in js
    assert "'\" target=\"_blank\" rel=\"noopener\" aria-label=\"' + esc(fmt(tx('c.in'), { s: L(p.name) }))" in js
    assert all(p["linkedin"].startswith("https://www.linkedin.com/in/") for p in _data())


def test_forms_post_to_formsubmit_like_the_main_page():
    """FR-SITE133/136: тот же канал, что у заявок главной — FormSubmit на
    admin@andre.technology, ловушка _honey, очередь ait_lead_queue при сбое сети;
    в заявке консультанту — slug партнёра."""
    js, html, main = _js(), _html(), _read("index.html")
    assert "var ENDPOINT = '%s';" % ENDPOINT in js and "var LEAD_ENDPOINT = '%s';" % ENDPOINT in main
    assert "headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }" in js
    assert "sget('ait_lead_queue')" in js and "sget('ait_lead_queue')" in main
    assert "_template: 'table', _captcha: 'false'" in js
    assert html.count('name="_honey"') == 2
    assert "type: 'consultant_request'" in js and "partner: p.slug," in js
    assert "type: 'partner_application'" in js and "linkedin: inUrl" in js and "rate_usd: rate" in js
    for field in ("req-name", "req-email", "req-company", "req-msg", "app-name", "app-email", "app-in", "app-exp", "app-rate"):
        assert 'id="%s"' % field in html, field


# ── FR-SITE139: языки ───────────────────────────────────────────────────────

def test_i18n_covers_both_languages():
    """FR-SITE139: у каждого текста разметки есть английский; строки скрипта — на обоих
    языках; подписи отраслей, языков и услуг из данных — тоже."""
    html, i18n = _html(), _i18n()
    en, ru = i18n["en"], i18n["ru"]
    static = set(re.findall(r'data-i18n(?:-ph|-aria)?="([^"]+)"', html))
    assert static and not sorted(static - set(en)), "нет английского для %s" % sorted(static - set(en))
    assert not sorted(set(ru) - set(en)), sorted(set(ru) - set(en))
    orphans = sorted(set(en) - static - set(ru))
    assert not orphans, "английские строки без места на странице: %s" % orphans
    for k, v in list(en.items()) + list(ru.items()):
        assert v not in ("", []), k
        if isinstance(v, list) and k in ("found", "reviews", "projects"):
            assert len(v) == 3 and all("%n" in x for x in v), k
    assert len(en["months"]) == len(ru["months"]) == 12
    for p in _data():
        for k in p["industries"]:
            assert "ind." + k in en and "ind." + k in ru
        for k in p["languages"]:
            assert "lng." + k in en and "lng." + k in ru
        for k in p["services"]:
            assert all(x + k in en and x + k in ru for x in ("svc.", "svcl.", "sd."))


def test_language_rule_is_the_main_page_rule():
    """FR-SITE139: ?lang= → ait_lang → язык браузера — как на главной."""
    html, main = _html(), _read("index.html")
    for line in ("try { l = localStorage.getItem('ait_lang'); } catch (e) {}",
                 "var q = (location.search.match(/[?&]lang=(ru|en)\\b/) || [])[1];",
                 "l = q || l || ((navigator.language || '').toLowerCase().indexOf('ru') === 0 ? 'ru' : 'en');"):
        assert line in html and line in main, line
    assert 'data-lang="en"' in html and 'data-lang="ru"' in html
    assert "sset('ait_lang', lang);" in _js()


# ── NFR-SITE106/108/109 ─────────────────────────────────────────────────────

def test_accessibility_markup():
    """NFR-SITE106: окна — role=dialog aria-modal с заголовком; у полей подписи; ошибки
    связаны с полями; «Найдено» — status; первая ссылка — к каталогу."""
    html = _html()
    assert html.index('<a class="skip" href="#catalog"') < html.index("<header")
    for dlg, head in (("profile", "pf-name"), ("req", "req-h"), ("app", "app-h")):
        block = html[html.index('id="%s"' % dlg):]
        assert re.search(r'role="dialog" aria-modal="true" aria-labelledby="%s"' % head, block[:400]), dlg
    for inp in re.findall(r'<input id="(\w+-\w+)"', html):
        if inp in ("req-company",):
            continue
        assert 'aria-describedby="%s-err"' % inp in html, inp
        assert 'id="%s-err"' % inp in html, inp
    assert '<label class="sr" for="q"' in html and 'role="status" aria-live="polite"' in html
    js = _js()
    assert "if (e.key === 'Escape' || e.key === 'Esc') { e.preventDefault(); closeTop(); return; }" in js
    assert "if (top && el !== top) el.setAttribute('inert', ''); else el.removeAttribute('inert');" in js
    assert "esc(fmt(tx('rating.sr'), { r: rateTxt(p.rating) }))" in js, "звёзды — ещё и текстом"


def test_reduced_motion_is_respected_in_css():
    """NFR-SITE108: при prefers-reduced-motion — без анимаций и плавной прокрутки,
    скрытое для появления видно сразу; без скрипта ничего не прячется."""
    css, html = _css(), _html()
    rm = css[css.index("@media (prefers-reduced-motion: reduce)"):]
    assert "html { scroll-behavior: auto; }" in rm and "html.rv-on .rv:not(.in) { opacity: 1; transform: none; }" in rm
    assert "animation-duration: 0.001s !important;" in rm and "transition-duration: 0.001s !important;" in rm
    assert "html.rv-on .rv:not(.in) { opacity: 0;" in css, "прячется только при работающем скрипте"
    assert "if (!window.__pjs) d.className = d.className.replace(/\\s*rv-on\\b/g, '');" in html, "страховка, если скрипт не загрузился"
    assert "var REDUCED = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);" in _js()


def test_js_syntax_and_escaping():
    """NFR-SITE109: partners.js — валидный JS (node --check, если node есть); всё из
    профиля выводится экранированным."""
    js = _js()
    node = shutil.which("node")
    if node:
        r = subprocess.run([node, "--check", os.path.join(_ROOT, "partners/partners.js")], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    assert "'use strict';" in js
    assert "function esc(s) { return String(s == null ? '' : s).replace(/[&<>\"']/g," in js
    assert "function nb(s) { return esc(s)." in js, "перенос по дефису — поверх экранирования"
    # всё, что вставляется как HTML из профиля, проходит через esc()/nb() — это проверяет test_render_partner_text_is_escaped


# ── проверки в браузере ─────────────────────────────────────────────────────

class Skip(Exception):
    pass


_B = {}


def _skip(msg):
    if pytest is not None:
        pytest.skip(msg)
    raise Skip(msg)


def _env():
    """Браузер и оба адреса страницы — один раз на весь файл."""
    if "browser" in _B:
        return _B
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _skip("нет Playwright")
    import partners_check as C
    if not os.path.exists(C.CHROMIUM):
        _skip("нет Chromium: " + C.CHROMIUM)
    base, base2, site, sub, stop = C.servers()
    pw = sync_playwright().start()
    browser = C.launch(pw)
    _B.update(C=C, pw=pw, browser=browser, site=site, sub=sub, stop=stop)

    def close():
        try:
            browser.close()
            pw.stop()
        finally:
            stop()
    atexit.register(close)
    return _B


def _page(size=(1440, 900), lang="ru", url=None, query="", **kw):
    e = _env()
    C = e["C"]
    ctx, pg = C.new_page(e["browser"], size, lang=lang, **kw)
    target = (url or e["sub"]) + (query or "")
    if lang and "lang=" not in target:
        target += ("&" if "?" in target else "?") + "lang=" + lang
    pg.goto(target, wait_until="load")
    C.wait_ready(pg)
    return ctx, pg


def _settle(pg):
    """Дождаться конца разовых анимаций (окно «въезжает» с масштабом 0,98 — мерить размеры рано)."""
    pg.evaluate("Promise.all(document.getAnimations().filter(a => a.effect && a.effect.getTiming().iterations !== Infinity)"
                ".map(a => a.finished.catch(() => null)))")


def _order(pg):
    return pg.evaluate("[...document.querySelectorAll('#grid .pc')].map(c => c.dataset.slug)")


def _clean(pg, what):
    assert not pg.errors, "%s: ошибки в консоли %s" % (what, pg.errors)
    assert not pg.bad, "%s: свои запросы с ошибкой %s" % (what, pg.bad)


SIZES = [(1440, 900), (390, 844)]


def test_render_default_order_best_to_worst():
    """FR-SITE121/122: компьютер и телефон, RU и EN — по умолчанию Ника, Лукас, Аружан;
    на компьютере первый ряд карточек начинается в первом окне."""
    for size in SIZES:
        for lang in ("ru", "en"):
            ctx, pg = _page(size, lang, touch=size[0] < 600)
            assert _order(pg) == BEST, (size, lang, _order(pg))
            assert pg.evaluate("window.AndrePartners.view()") == BEST
            found = pg.text_content(".found")
            assert ("3 консультанта" in found) if lang == "ru" else ("3 consultants found" in found), found
            top = pg.evaluate("document.querySelector('#grid .pc').getBoundingClientRect().top")
            if size[0] >= 1024:
                assert top < size[1] - 120, "карточки не видны в первом окне: %d" % top
            else:
                assert pg.evaluate("document.querySelector('#q').getBoundingClientRect().bottom") < size[1], "поиск — в первом окне"
            _clean(pg, "%s %s" % (size, lang))
            ctx.close()


def test_render_card_shows_every_field():
    """FR-SITE123/124: аватар с инициалами, имя, заголовок, бейджи, рейтинг, проекты,
    ставка, отрасли, услуги, место, языки, LinkedIn в новой вкладке."""
    ctx, pg = _page()
    card = pg.evaluate("""() => { const c = document.querySelector('#grid .pc[data-slug="example-nika-vetrova"]'), a = c.querySelector('.pc-in');
      return { ava: c.querySelector('.ava').textContent, name: c.querySelector('.pc-name').textContent, head: c.querySelector('.pc-head').textContent,
        badges: [...c.querySelectorAll('.bdg')].map(b => b.textContent), rating: c.querySelector('.rating').innerText, sr: c.querySelector('.rating .sr').textContent,
        fill: c.querySelector('.stars .fill').style.width, kv: c.querySelector('.kv').innerText, tags: [...c.querySelectorAll('.tags .tag')].map(t => t.textContent),
        meta: c.querySelector('.meta').innerText, href: a.getAttribute('href'), target: a.getAttribute('target'), rel: a.getAttribute('rel'), label: a.getAttribute('aria-label'),
        link: c.querySelector('.pc-link').getAttribute('href') }; }""")
    assert card["ava"] == "НВ" and card["name"] == "Ника Ветрова" and card["head"].startswith("ИИ-трансформация ритейла")
    assert card["badges"] == ["Andre AI Certified", "Пример профиля"]
    assert "4,9" in card["rating"] and "32 отзыва" in card["rating"] and card["sr"] == "Рейтинг 4,9 из 5" and float(card["fill"].rstrip("%")) == 98
    assert "41" in card["kv"] and "$120" in card["kv"] and "/ч" in card["kv"]
    assert card["tags"] == ["Ритейл", "E-commerce", "Логистика"]
    for part in ("Проверка схем · Буткемп", "Лиссабон, Португалия · удалённо", "RU · EN"):
        assert part in card["meta"], part
    assert card["href"] == "https://www.linkedin.com/in/andre-ai-partner-example-1" and card["target"] == "_blank" and card["rel"] == "noopener"
    assert card["label"].startswith("LinkedIn — Ника Ветрова") and card["link"] == "?p=" + NIKA
    # LinkedIn в карточке — своя ссылка поверх растянутой ссылки профиля
    with pg.expect_popup() as pop:
        pg.click('#grid .pc[data-slug="%s"] .pc-in' % NIKA)
    pop.value.close()
    assert pg.evaluate("document.querySelector('#profile').hidden") is True, "клик по LinkedIn не открывает профиль"
    aru = pg.evaluate("document.querySelector('#grid .pc[data-slug=\"%s\"] .meta').innerText" % ARUZHAN)
    assert "Алматы, Казахстан · очно" in aru and "RU · KK · EN" in aru
    _clean(pg, "карточка")
    ctx.close()


def test_render_search_narrows_the_list():
    """FR-SITE125/128: поиск по имени, навыку, отрасли и тексту; без учёта регистра и
    «ё»; пусто — «Никого не нашли» и сброс."""
    for lang, cases in (("ru", (("бреннер", [LUKAS]), ("N8N", [NIKA]), ("клиник", [ARUZHAN]), ("ритейл", [NIKA]),
                                ("нейрони", [NIKA, LUKAS, ARUZHAN]), ("финансы берлин", [LUKAS]), ("удаленно", [NIKA, LUKAS]))),
                        ("en", (("brenner", [LUKAS]), ("retail", [NIKA]), ("Kazakh", [ARUZHAN]), ("bootcamp", [NIKA, LUKAS])))):
        ctx, pg = _page(lang=lang)
        for q, want in cases:
            pg.fill("#q", q)
            pg.press("#q", "Enter")
            assert _order(pg) == want, (lang, q, _order(pg))
        pg.fill("#q", "zzzz-nobody")
        pg.press("#q", "Enter")
        assert _order(pg) == [] and pg.is_visible("#empty") and pg.is_visible("#reset")
        pg.click("#empty-reset")
        assert _order(pg) == BEST and pg.input_value("#q") == "" and pg.is_hidden("#empty")
        _clean(pg, "поиск " + lang)
        ctx.close()


def _set_rate(pg, lo, hi):
    """Как рукой: бегунки не перескакивают друг через друга, поэтому сначала «от» — к началу, потом «до», потом «от»."""
    pg.evaluate("""([lo, hi]) => { const a = document.querySelector('#rmin'), b = document.querySelector('#rmax'),
        set = (el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles: true})); };
      set(a, 50); set(b, hi); set(a, lo); }""", [lo, hi])
    pg.wait_for_timeout(50)


def test_render_each_filter_works():
    """FR-SITE126: услуга, отрасль, язык, локация, ставка — каждый сужает список;
    фильтры складываются; «Сбросить фильтры» возвращает всё. Компьютер и телефон."""
    for size in SIZES:
        ctx, pg = _page(size, touch=size[0] < 600)
        if size[0] < 768:
            assert pg.is_hidden("#filters"), "на телефоне фильтры свёрнуты"
            pg.click("#ftoggle")
            assert pg.get_attribute("#ftoggle", "aria-expanded") == "true" and pg.is_visible("#filters")
        for svc, want in (("review", [NIKA, ARUZHAN]), ("bootcamp", [NIKA, LUKAS]), ("neuronium", [LUKAS, ARUZHAN]), ("", BEST)):
            pg.click(".chip:has(input[value='%s'])" % svc)
            assert _order(pg) == want, (size, svc, _order(pg))
        for sel, val, want in (("#ind", "manufacturing", [LUKAS]), ("#ind", "healthcare", [ARUZHAN]), ("#ind", "", BEST),
                               ("#lng", "kk", [ARUZHAN]), ("#lng", "de", [LUKAS]), ("#lng", "", BEST),
                               ("#loc", "remote", [NIKA, LUKAS]), ("#loc", "c:KZ", [ARUZHAN]), ("#loc", "c:PT", [NIKA]), ("#loc", "", BEST)):
            pg.select_option(sel, val)
            assert _order(pg) == want, (size, sel, val, _order(pg))
        opts = pg.evaluate("[...document.querySelectorAll('#loc option')].map(o => o.textContent)")
        assert opts == ["Любая локация", "Удалённо", "Германия", "Казахстан", "Португалия"], opts
        _set_rate(pg, 50, 100)
        assert _order(pg) == [ARUZHAN] and pg.inner_text("#rate-v") == "$50 — $100"
        _set_rate(pg, 250, 300)
        assert _order(pg) == [LUKAS] and pg.inner_text("#rate-v") == "$250 — $300+"
        _set_rate(pg, 100, 300)
        pg.click(".chip:has(input[value='review'])")
        assert _order(pg) == [NIKA], "фильтры складываются"
        if size[0] < 768:
            assert pg.inner_text("#fcount") == "2"
        pg.click("#reset")
        assert _order(pg) == BEST and pg.is_hidden("#reset")
        _clean(pg, "фильтры %s" % (size,))
        ctx.close()


def test_render_sort_changes_the_order():
    """FR-SITE127: по ставке вверх и вниз, по проектам; «Сначала лучшие» — обратно."""
    ctx, pg = _page()
    for val, want in (("rate_up", [ARUZHAN, NIKA, LUKAS]), ("rate_down", [LUKAS, NIKA, ARUZHAN]),
                      ("projects", [LUKAS, NIKA, ARUZHAN]), ("best", BEST)):
        pg.select_option("#sort", val)
        assert _order(pg) == want, (val, _order(pg))
        assert pg.is_visible("#rank") == (val == "best"), "пояснение порядка — только у «Сначала лучшие»"
    _clean(pg, "сортировка")
    ctx.close()


def test_render_filters_live_in_the_address():
    """FR-SITE129: фильтры и сортировка — в адресе (без новой записи в истории);
    заход по такому адресу их восстанавливает; чужие метки не теряются."""
    ctx, pg = _page(query="?utm_source=test")
    n0 = pg.evaluate("history.length")
    pg.click(".chip:has(input[value='review'])")
    pg.select_option("#sort", "rate_up")
    pg.fill("#q", "схем")
    pg.press("#q", "Enter")
    pg.wait_for_timeout(400)
    url = pg.url
    for part in ("utm_source=test", "svc=review", "sort=rate_up", "q=%D1%81%D1%85%D0%B5%D0%BC"):
        assert part in url, (part, url)
    assert pg.evaluate("history.length") == n0, "фильтры не плодят записи в истории"
    ctx.close()
    ctx, pg = _page(query="?svc=bootcamp&sort=rate_down&rate=100-300&ind=retail")
    assert _order(pg) == [NIKA], _order(pg)
    assert pg.input_value("#sort") == "rate_down" and pg.input_value("#ind") == "retail" and pg.inner_text("#rate-v") == "$100 — $300+"
    assert pg.evaluate("document.querySelector('#svc input[value=bootcamp]').checked")
    ctx.close()
    ctx, pg = _page(query="?ind=no-such-industry&sort=weird")
    assert _order(pg) == BEST and pg.input_value("#ind") == "" and pg.input_value("#sort") == "best"
    _clean(pg, "плохие параметры адреса")
    ctx.close()


def test_render_paging_scales_to_hundreds():
    """FR-SITE128, NFR-SITE109: 500 профилей — в DOM 12, автоподгрузка не больше трёх
    порций подряд, дальше «Показать ещё»; поиск по 500 — быстро."""
    base = _data()
    many = []
    for i in range(500):
        p = json.loads(json.dumps(base[i % 3]))
        p["slug"] = "gen-%03d" % i
        p["name"] = {"ru": "Партнёр %03d" % i, "en": "Partner %03d" % i}
        p["rate_usd"] = 50 + (i * 7) % 251
        p["rating"] = round(3.5 + (i % 15) / 10, 1)
        p["reviews_count"] = 3 + i % 40
        p["projects"] = i % 60
        many.append(p)
    e = _env()
    ctx, pg = e["C"].new_page(e["browser"], (1440, 900), lang="ru")
    pg.route("**/partners.json*", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(many, ensure_ascii=False)))
    pg.goto(e["sub"] + "?lang=ru", wait_until="load")
    e["C"].wait_ready(pg)
    assert pg.evaluate("window.AndrePartners.source") == "fetch"
    assert pg.evaluate("document.querySelectorAll('#grid .pc').length") == 12
    assert "500" in pg.inner_text("#found")
    assert pg.text_content("#more") == "Показать ещё · 488"
    for _ in range(8):
        pg.evaluate("document.querySelector('#sentinel').scrollIntoView({block: 'end'})")
        pg.wait_for_timeout(250)
    n = pg.evaluate("document.querySelectorAll('#grid .pc').length")
    assert n == 48, "автоподгрузка — не больше трёх порций подряд: %d" % n
    pg.click("#more")
    assert pg.evaluate("document.querySelectorAll('#grid .pc').length") >= 60
    assert pg.evaluate("document.activeElement.closest('.pc').dataset.slug") == pg.evaluate("window.AndrePartners.view()[48]"), \
        "фокус — на первой новой карточке"
    t = pg.evaluate("""() => { const q = document.querySelector('#q'), t0 = performance.now(); q.value = 'партнёр 123';
      q.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true})); return performance.now() - t0; }""")
    assert t < 150, "поиск по 500 профилям занял %.0f мс" % t
    assert pg.evaluate("window.AndrePartners.view()") == ["gen-123"]
    _clean(pg, "500 профилей")
    ctx.close()


def test_render_card_opens_by_click_and_back_closes_it():
    """FR-SITE130/131, NFR-SITE106: клик открывает профиль поверх каталога с адресом
    ?p=<slug>; в нём все разделы; «Назад» закрывает, фокус — на карточке; Esc и
    крестик тоже закрывают. Компьютер и телефон, RU и EN."""
    for size in SIZES:
        for lang in ("ru", "en"):
            ctx, pg = _page(size, lang, touch=size[0] < 600)
            n0 = pg.evaluate("history.length")
            pg.click('#grid .pc[data-slug="%s"]' % LUKAS)
            pg.wait_for_selector("#profile:not([hidden])")
            assert "p=" + LUKAS in pg.url and pg.evaluate("history.length") == n0 + 1
            assert pg.title() == ("Лукас Бреннер — Партнёры Andre AI" if lang == "ru" else "Lukas Brenner — Andre AI Partners")
            heads = pg.evaluate("[...document.querySelectorAll('#profile .pf-h')].map(h => h.textContent)")
            want = (["О консультанте", "Услуги и цены", "Отзывы", "Навыки", "Отрасли", "Языки", "Сертификаты"] if lang == "ru" else
                    ["About", "Services and prices", "Reviews", "Skills", "Industries", "Languages", "Certificates"])
            assert heads == want, heads
            body = pg.text_content("#profile")
            for part in (("Пример профиля: человек, отзывы", "Выбрать консультанта", "LinkedIn", "Andre AI Certified Consultant", "В каталоге с февраля 2026",
                          "Берлин, Германия · удалённо", "Немецкий, Английский, Русский", "Маркус Л., финансовый директор", "3 ноября 2026")
                         if lang == "ru" else
                         ("Example profile: the person, the reviews", "Choose this consultant", "In the catalog since February 2026",
                          "Berlin, Germany · remote", "German, English, Russian", "Markus L., CFO", "November 3, 2026")):
                assert part in body, (lang, part)
            assert pg.evaluate("document.activeElement.closest('#profile') !== null"), "фокус — в окне"
            assert pg.evaluate("document.querySelector('main').inert") is True, "каталог под окном неактивен"
            pg.go_back()
            pg.wait_for_selector("#profile", state="hidden")
            assert "p=" not in pg.url and pg.evaluate("document.activeElement.dataset.open") == LUKAS
            assert pg.title() in ("Партнёры Andre AI — консультанты по ИИ-трансформации", "Andre AI Partners — AI transformation consultants")
            # Esc и крестик
            pg.click('#grid .pc[data-slug="%s"]' % NIKA)
            pg.wait_for_selector("#profile:not([hidden])")
            pg.keyboard.press("Escape")
            pg.wait_for_selector("#profile", state="hidden")
            assert "p=" not in pg.url
            pg.click('#grid .pc[data-slug="%s"]' % ARUZHAN)
            pg.click("#profile .dlg-x")
            pg.wait_for_selector("#profile", state="hidden")
            assert pg.evaluate("document.activeElement.dataset.open") == ARUZHAN
            _clean(pg, "профиль %s %s" % (size, lang))
            ctx.close()


def test_render_card_opens_by_direct_address():
    """FR-SITE130: заход по ?p=<slug> — профиль поверх каталога; «Назад» закрывает его и
    оставляет каталог; неизвестный slug — просто каталог. На обоих адресах."""
    e = _env()
    for url in (e["sub"], e["site"]):
        ctx, pg = _page(url=url, query="?p=" + ARUZHAN)
        pg.wait_for_selector("#profile:not([hidden])")
        assert pg.text_content("#pf-name") == "Аружан Сейтова" and "p=" + ARUZHAN in pg.url
        pg.go_back()
        pg.wait_for_selector("#profile", state="hidden")
        assert "p=" not in pg.url and _order(pg) == BEST, "«Назад» закрыл профиль и остался в каталоге"
        assert pg.evaluate("document.activeElement.dataset.open") == ARUZHAN
        _clean(pg, "прямой заход " + url)
        ctx.close()
    ctx, pg = _page(query="?p=no-such-partner")
    assert pg.is_hidden("#profile") and "p=" not in pg.url and _order(pg) == BEST
    ctx.close()


def test_render_prices_in_the_card_follow_the_policy():
    """FR-SITE132: в профиле цены — по формуле политики для ставки партнёра; функции
    страницы дают контрольные примеры политики."""
    ctx, pg = _page()
    P = pg.evaluate("""() => { const P = window.AndrePartners.pricing;
      return { r50: P.review(50, 10), r50one: P.review(50, 1), r50five: P.review(50, 5), b50: P.bootcamp(50), r200: P.review(200, 10), b200: P.bootcamp(200),
        promo: P.promo(50000) }; }""")
    assert P["r50"] == {"client": 7143, "consultant": 5000, "andre": 2143}
    assert P["r50one"]["client"] == 714 and P["r50five"]["client"] == 3571
    assert P["b50"] == {"client": 85714, "consultant": 60000, "andre": 25714, "month": 28571}
    assert P["r200"]["client"] == 28571 and P["b200"]["client"] == 342857 and P["b200"]["andre"] == 102857
    assert P["promo"] == {"discount": 5000, "client": 45000, "commission": 4500, "andre": 40500}
    for p in _data():
        pg.click('#grid .pc[data-slug="%s"]' % p["slug"])
        pg.wait_for_selector("#profile:not([hidden])")
        want = _policy(p["rate_usd"])
        got = pg.evaluate("Object.fromEntries([...document.querySelectorAll('#profile .sv')].map(s => [s.dataset.svc, s.querySelector('.sv-p').textContent]))")
        assert set(got) == set(p["services"]), got
        if "review" in got:
            assert pg.get_attribute('#profile .sv[data-svc=review] [data-price]', "data-price") == str(want["review"])
            assert "за 10 схем" in got["review"] and "за схему" in got["review"]
        if "bootcamp" in got:
            assert pg.get_attribute('#profile .sv[data-svc=bootcamp] [data-price]', "data-price") == str(want["boot"])
            assert "за 3 месяца" in got["bootcamp"] and "в месяц" in got["bootcamp"]
        if "neuronium" in got:
            assert got["neuronium"].startswith("По смете")
        pg.keyboard.press("Escape")
        pg.wait_for_selector("#profile", state="hidden")
    pg.click('#grid .pc[data-slug="%s"]' % NIKA)
    txt = pg.inner_text("#profile .svcs")
    assert "$171,43" in txt and "$17,14 за схему" in txt and "$2 057,14" in txt and "$685,71" in txt
    ctx.close()
    ctx, pg = _page(lang="en", query="?p=" + NIKA)
    txt = pg.inner_text("#profile .svcs")
    assert "$171.43" in txt and "$2,057.14" in txt and "for 3 months" in txt
    ctx.close()


def _capture_formsubmit(pg):
    sent = []

    def handle(route):
        sent.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body='{"success":"true"}')
    pg.route(ENDPOINT, handle)
    return sent


def test_render_request_form_validates_and_sends_the_slug():
    """FR-SITE133: «Выбрать консультанта» → форма; пустые поля — подсказки и ничего не
    уходит; верные — заявка на FormSubmit со slug партнёра; Esc закрывает только форму."""
    for size in SIZES:
        ctx, pg = _page(size, touch=size[0] < 600)
        sent = _capture_formsubmit(pg)
        pg.click('#grid .pc[data-slug="%s"]' % LUKAS)
        pg.click("#profile [data-choose]")
        pg.wait_for_selector("#req:not([hidden])")
        assert pg.evaluate("document.activeElement.id") == "req-name"
        assert pg.inner_text("#req-sub") == "Лукас Бреннер · ставка $300/ч" and pg.is_visible("#req-ex")
        pg.click("#req-btn")
        assert pg.is_visible("#req-name-err") and pg.is_visible("#req-email-err") and not sent
        assert pg.get_attribute("#req-name", "aria-invalid") == "true" and pg.evaluate("document.activeElement.id") == "req-name"
        pg.fill("#req-name", "Тест Тестов")
        pg.fill("#req-email", "not-an-email")
        pg.click("#req-btn")
        assert pg.is_hidden("#req-name-err") and pg.is_visible("#req-email-err") and not sent
        pg.fill("#req-email", "test@example.com")
        pg.fill("#req-company", "Тест и Ко")
        pg.fill("#req-msg", "Нужен буткемп для отдела продаж")
        pg.click("#req-btn")
        pg.wait_for_selector("#req-done:not([hidden])")
        assert len(sent) == 1
        s = sent[0]
        assert s["partner"] == LUKAS and s["partner_rate_usd"] == 300 and s["partner_example"] is True and s["type"] == "consultant_request"
        assert (s["name"], s["email"], s["company"], s["message"]) == ("Тест Тестов", "test@example.com", "Тест и Ко", "Нужен буткемп для отдела продаж")
        assert s["_subject"] == "Consultant request — partners.andre.technology" and s["_captcha"] == "false" and s["lang"] == "ru"
        assert "p=" + LUKAS in s["page"]
        pg.keyboard.press("Escape")
        pg.wait_for_selector("#req", state="hidden")
        assert pg.is_visible("#profile"), "Esc закрывает верхнее окно — заявку, профиль остаётся"
        assert pg.evaluate("document.activeElement.hasAttribute('data-choose')"), "фокус вернулся на «Выбрать консультанта»"
        _clean(pg, "заявка консультанту %s" % (size,))
        ctx.close()


def test_render_become_a_partner():
    """FR-SITE134/135: три шага, «от $50 до $300», Академия — курс на языке
    посетителя; калькулятор считает по политике."""
    for lang in ("ru", "en"):
        ctx, pg = _page(lang=lang)
        pg.evaluate("document.querySelector('#become').scrollIntoView()")
        steps = pg.evaluate("[...document.querySelectorAll('#steps .step h3')].map(h => h.textContent)")
        assert steps == (["Пройдите Академию Andre AI", "Получите сертификат", "Пройдите собеседование"] if lang == "ru" else
                         ["Complete the Andre AI Academy", "Get certified", "Pass the interview"]), steps
        big = pg.inner_text("#earn-big")
        assert "$50" in big and "$300" in big
        assert pg.get_attribute("#academy", "href") == ("https://andre.technology/automation_ru/" if lang == "ru" else "https://andre.technology/automation/")
        rows = lambda: pg.evaluate("[...document.querySelectorAll('.calc-row dd')].map(d => d.textContent)")
        for v in (120, 50, 200, 300):
            if v != 120:
                pg.evaluate("(v) => { const r = document.querySelector('#calc-rate'); r.value = v; r.dispatchEvent(new Event('input')); }", v)
            w = _policy(v)
            assert pg.text_content("#calc-v") == _money(v * 100, lang) + ("/ч" if lang == "ru" else "/h")
            assert rows() == [_money(w["review"], lang) + _money(w["pay_review"], lang), _money(w["boot"], lang) + _money(w["pay_boot"], lang),
                              _money(45000, lang) + _money(4500, lang)], (lang, v, rows())
        _clean(pg, "как стать партнёром " + lang)
        ctx.close()


def test_render_application_form_validates():
    """FR-SITE136: заявка в партнёры — имя, email, LinkedIn, опыт, ставка 50…300;
    ошибки у полей, верная — на FormSubmit; LinkedIn без https:// дописывается."""
    ctx, pg = _page((390, 844), touch=True)
    sent = _capture_formsubmit(pg)
    pg.evaluate("document.querySelector('#become').scrollIntoView()")
    pg.click("#apply")
    pg.wait_for_selector("#app:not([hidden])")
    pg.click("#app-btn")
    for f in ("name", "email", "in", "exp", "rate"):
        assert pg.is_visible("#app-%s-err" % f), f
    assert not sent and pg.evaluate("document.activeElement.id") == "app-name"
    pg.fill("#app-name", "Мария Пример")
    pg.fill("#app-email", "maria@example.com")
    pg.fill("#app-in", "https://example.com/maria")
    pg.fill("#app-exp", "Пять лет в операционном консалтинге, BPMN, n8n")
    pg.fill("#app-rate", "40")
    pg.click("#app-btn")
    assert pg.is_visible("#app-in-err") and pg.is_visible("#app-rate-err") and not sent
    assert pg.evaluate("document.activeElement.id") == "app-in"
    pg.fill("#app-in", "linkedin.com/in/maria-example")
    pg.fill("#app-rate", "301")
    pg.click("#app-btn")
    assert pg.is_hidden("#app-in-err") and pg.is_visible("#app-rate-err") and not sent
    pg.fill("#app-rate", "150")
    pg.click("#app-btn")
    pg.wait_for_selector("#app-done:not([hidden])")
    assert len(sent) == 1
    s = sent[0]
    assert s["type"] == "partner_application" and s["linkedin"] == "https://linkedin.com/in/maria-example" and s["rate_usd"] == 150
    assert s["name"] == "Мария Пример" and s["email"] == "maria@example.com" and s["experience"].startswith("Пять лет")
    assert s["_subject"] == "Partner application — partners.andre.technology"
    pg.click("#app-done [data-close]")
    pg.wait_for_selector("#app", state="hidden")
    assert pg.evaluate("document.activeElement.id") == "apply"
    _clean(pg, "заявка в партнёры")
    ctx.close()


def test_render_languages_switch_everything():
    """FR-SITE139: язык по ?lang=, по ait_lang и по языку браузера; EN | RU меняет
    тексты, данные и открытый профиль, пишет ?lang= и ait_lang."""
    e = _env()
    C = e["C"]
    for locale, want in (("en-US", "en"), ("ru-RU", "ru")):
        ctx = e["browser"].new_context(locale=locale)
        ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://127.0.0.1") else r.abort())
        pg = ctx.new_page()
        pg.goto(e["sub"], wait_until="load")
        C.wait_ready(pg)
        assert pg.evaluate("document.documentElement.lang") == want, (locale, want)
        ctx.close()
    ctx, pg = _page(lang="en", query="?p=" + NIKA)
    assert pg.text_content("#pf-name") == "Nika Vetrova" and pg.title() == "Nika Vetrova — Andre AI Partners"
    assert "AI transformation for retail" in pg.inner_text("#profile .pf-head")
    pg.keyboard.press("Escape")
    pg.wait_for_selector("#profile", state="hidden")
    assert pg.inner_text(".h1").lower().startswith("certified")
    assert pg.get_attribute("#q", "placeholder") == "Name, skill, industry…"
    pg.click(".lang button[data-lang=ru]")
    assert "lang=ru" in pg.url and pg.evaluate("localStorage.getItem('ait_lang')") == "ru"
    assert pg.inner_text(".h1").startswith("СЕРТИФИЦИРОВАННЫЕ") or pg.inner_text(".h1").startswith("Сертифицированные")
    assert pg.text_content('#grid .pc[data-slug="%s"] .pc-name' % NIKA) == "Ника Ветрова"
    assert pg.get_attribute("#academy", "href") == "https://andre.technology/automation_ru/"
    assert pg.get_attribute(".logo", "href") == "https://andre.technology/?lang=ru"
    assert pg.evaluate("document.documentElement.classList.contains('i18n-wait')") is False
    ctx.close()
    # выбор посетителя (ait_lang) — сильнее языка браузера
    ctx = e["browser"].new_context(locale="ru-RU")
    ctx.add_init_script("try { localStorage.setItem('ait_lang', 'en'); } catch (e) {}")
    ctx.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://127.0.0.1") else r.abort())
    pg = ctx.new_page()
    pg.goto(e["sub"], wait_until="load")
    C.wait_ready(pg)
    assert pg.evaluate("document.documentElement.lang") == "en"
    ctx.close()


def test_render_keyboard_and_focus():
    """NFR-SITE106: первая по Tab — ссылка «Перейти к каталогу»; карточка открывается
    с клавиатуры; Tab не выходит из окна; Esc закрывает, фокус — обратно."""
    ctx, pg = _page()
    pg.keyboard.press("Tab")
    assert pg.evaluate("document.activeElement.className") == "skip"
    pg.focus('#grid .pc[data-slug="%s"] .pc-link' % NIKA)
    pg.keyboard.press("Enter")
    pg.wait_for_selector("#profile:not([hidden])")
    inside = []
    for _ in range(14):
        pg.keyboard.press("Tab")
        inside.append(pg.evaluate("!!document.activeElement.closest('#profile')"))
    assert all(inside), "Tab вышел из окна профиля"
    pg.keyboard.press("Shift+Tab")
    assert pg.evaluate("!!document.activeElement.closest('#profile')")
    pg.keyboard.press("Escape")
    pg.wait_for_selector("#profile", state="hidden")
    assert pg.evaluate("document.activeElement.dataset.open") == NIKA
    # радиокнопки услуг — стрелками
    pg.focus("#svc input[value='']")
    pg.keyboard.press("ArrowRight")
    assert _order(pg) == [NIKA, ARUZHAN], "стрелка выбрала «Проверка схем»"
    _clean(pg, "клавиатура")
    ctx.close()


def test_render_phone_has_no_side_scroll_and_44px_targets():
    """NFR-SITE107: 390×844, RU и EN — нет прокрутки вбок в каталоге, в открытых
    фильтрах, профиле и формах; всё нажимаемое — не меньше 44×44."""
    e = _env()
    C = e["C"]
    for lang in ("ru", "en"):
        ctx, pg = _page((390, 844), lang, touch=True)
        pg.click("#ftoggle")
        ov = pg.evaluate(C.OVERFLOW)
        assert ov["doc"] <= 0 and not ov["wide"], (lang, "каталог с открытыми фильтрами", ov)
        # имя в карточке — растянутая ссылка: нажимается вся карточка (её размер и меряем)
        small = [t for t in pg.evaluate(C.TAPS) if (t["h"] < 44 or t["w"] < 44) and not t["what"].startswith("pc-link")]
        assert not small, (lang, small[:6])
        pg.click('#grid .pc[data-slug="%s"]' % LUKAS)
        pg.wait_for_selector("#profile:not([hidden])")
        _settle(pg)
        ov = pg.evaluate("() => { const p = document.querySelector('#profile'); return p.scrollWidth - p.clientWidth; }")
        assert ov <= 0, (lang, "профиль шире экрана", ov)
        small = [t for t in pg.evaluate(C.TAPS) if (t["h"] < 44 or t["w"] < 44) and not t["what"].startswith("pc-link")]
        assert not small, (lang, "профиль", small[:6])
        pg.click("#profile [data-choose]")
        ov = pg.evaluate("() => { const p = document.querySelector('#req'); return p.scrollWidth - p.clientWidth; }")
        assert ov <= 0, (lang, "форма шире экрана", ov)
        pg.keyboard.press("Escape")
        pg.keyboard.press("Escape")
        pg.wait_for_selector("#profile", state="hidden")
        for sel in ("#become", ".earn", ".foot"):
            pg.evaluate("document.querySelector('%s').scrollIntoView()" % sel)
            assert pg.evaluate(C.OVERFLOW)["doc"] <= 0, (lang, sel)
        _clean(pg, "телефон " + lang)
        ctx.close()


def test_render_reduced_motion_shows_everything_at_once():
    """NFR-SITE108: при reduced motion блоки видны сразу, без анимаций; без него —
    блоки ниже первого экрана появляются при прокрутке."""
    ctx, pg = _page(reduced=True)
    st = pg.evaluate("""() => ({ hidden: [...document.querySelectorAll('.rv')].filter(e => getComputedStyle(e).opacity !== '1').length,
      anim: [...document.querySelectorAll('.pc, .glow, .kicker .dot')].map(e => parseFloat(getComputedStyle(e).animationDuration) || 0),
      smooth: getComputedStyle(document.documentElement).scrollBehavior })""")
    assert st["hidden"] == 0 and max(st["anim"]) < 0.01 and st["smooth"] == "auto", st
    ctx.close()
    ctx, pg = _page()
    pg.wait_for_timeout(300)
    below = pg.evaluate("getComputedStyle(document.querySelector('#steps .step')).opacity")
    assert below == "0", "шаги ниже первого экрана ждут прокрутки"
    pg.evaluate("document.querySelector('#steps').scrollIntoView()")
    pg.wait_for_function("getComputedStyle(document.querySelector('#steps .step')).opacity === '1'", timeout=4000)
    ctx.close()


def test_render_partner_text_is_escaped():
    """NFR-SITE109: данные профиля (их опубликует кабинет партнёра) выводятся только как
    текст — разметка в имени, заголовке, «О себе», навыках и отзывах не исполняется."""
    e = _env()
    evil = json.loads(json.dumps(_data()[0]))
    bad = '<img src=x onerror="window.__xss=1"><b>x</b>'
    evil["name"] = {"ru": "Злой " + bad, "en": "Evil " + bad}
    evil["headline"] = {"ru": bad, "en": bad}
    evil["about"] = {"ru": bad + " </script><script>window.__xss=2</script>", "en": bad}
    evil["skills"] = {"ru": [bad], "en": [bad]}
    evil["reviews"][0]["text"] = {"ru": bad, "en": bad}
    evil["reviews"][0]["author"] = {"ru": bad, "en": bad}
    ctx, pg = e["C"].new_page(e["browser"], (1440, 900), lang="ru")
    pg.route("**/partners.json*", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps([evil], ensure_ascii=False)))
    pg.goto(e["sub"] + "?lang=ru&p=" + evil["slug"], wait_until="load")
    e["C"].wait_ready(pg)
    pg.wait_for_selector("#profile:not([hidden])")
    assert pg.evaluate("window.__xss === undefined"), "разметка из данных исполнилась"
    assert pg.evaluate("document.querySelectorAll('#grid img, #profile img').length") == 0
    assert pg.evaluate("[...document.querySelectorAll('#grid b, #profile b')].filter(b => b.textContent === 'x').length") == 0
    assert bad in pg.text_content("#pf-name") and bad in pg.text_content("#profile .pf-about")
    ctx.close()


def test_render_both_addresses_work_without_errors():
    """NFR-SITE109/110: andre.technology/partners/ и partners.andre.technology (Caddy:
    /x → /partners/x) — каталог из partners.json, значки без 404, консоль чистая."""
    e = _env()
    for url in (e["site"], e["sub"]):
        for size in SIZES:
            ctx, pg = _page(size, url=url, touch=size[0] < 600)
            assert pg.evaluate("window.AndrePartners.source") == "fetch", url
            st = pg.evaluate("Promise.all([...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon]')].map(l => "
                             "fetch(new URL(l.getAttribute('href') + '?probe', location.href)).then(r => r.status)))")
            assert st and set(st) == {200}, (url, st)
            assert pg.evaluate("fetch('og.png?probe').then(r => r.status)") == 200
            _clean(pg, url)
            ctx.close()


def test_render_loads_json_and_falls_back_to_the_inline_copy():
    """FR-SITE137: данные берутся из partners.json (подмена файла видна на странице);
    сбой загрузки и file:// — встроенная копия, без ошибок страницы."""
    e = _env()
    C = e["C"]
    one = [_data()[2]]
    ctx, pg = C.new_page(e["browser"], (1440, 900), lang="ru")
    pg.route("**/partners.json*", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(one, ensure_ascii=False)))
    pg.goto(e["sub"] + "?lang=ru", wait_until="load")
    C.wait_ready(pg)
    assert pg.evaluate("window.AndrePartners.source") == "fetch" and _order(pg) == [ARUZHAN]
    ctx.close()
    for broken in ("abort", "404", "garbage"):
        ctx, pg = C.new_page(e["browser"], (1440, 900), lang="ru")
        if broken == "abort":
            pg.route("**/partners.json*", lambda r: r.abort())
        elif broken == "404":
            pg.route("**/partners.json*", lambda r: r.fulfill(status=404, body="nope"))
        else:
            pg.route("**/partners.json*", lambda r: r.fulfill(status=200, content_type="application/json", body='{"not": "an array"}'))
        pg.goto(e["sub"] + "?lang=ru", wait_until="load")
        C.wait_ready(pg)
        assert pg.evaluate("window.AndrePartners.source") == "inline" and _order(pg) == BEST, broken
        assert not [x for x in pg.errors if "Failed to load resource" not in x], (broken, pg.errors)
        ctx.close()
    ctx, pg = C.new_page(e["browser"], (1440, 900), lang="ru")
    pg.goto("file://" + os.path.join(_ROOT, "partners/index.html") + "?lang=ru", wait_until="load")
    C.wait_ready(pg)
    assert pg.evaluate("window.AndrePartners.source") == "inline" and _order(pg) == BEST
    assert not pg.errors, pg.errors
    pg.click('#grid .pc[data-slug="%s"]' % NIKA)
    pg.wait_for_selector("#profile:not([hidden])")
    ctx.close()


if __name__ == "__main__":
    failed = skipped = 0
    t0 = time.time()
    for name, fn in sorted(globals().items(), key=lambda kv: (kv[0].startswith("test_render"), kv[0])):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Skip as e:
                skipped += 1
                print("skip %s: %s" % (name, e))
            except ModuleNotFoundError as e:
                skipped += 1
                print("skip %s: нет модуля %s" % (name, e.name))
            except Exception as e:  # AssertionError и любые сбои
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    print("\nСайт партнёров: %s, пропущено %d, %.0f с" % ("ПРОВАЛОВ %d" % failed if failed else "все тесты пройдены", skipped, time.time() - t0))
    raise SystemExit(1 if failed else 0)
