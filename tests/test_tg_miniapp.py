# -*- coding: utf-8 -*-
"""FR-SITE87 — страницы сайта внутри Telegram Mini App.

Telegram-бот открывает /ai-strategy/ru/, /automation_ru/ и /about/ru как
Mini App. Страницы (и их английские пары) должны вести себя там нативно, а
вне Telegram — ровно как раньше и без лишних запросов. Поведение в браузере
проверяет tools/tg_miniapp_check.py (Chromium с заглушкой SDK Telegram),
здесь — разметка, генераторы и логика проверки запуска.

Без зависимостей: `python3 tests/test_tg_miniapp.py` или через pytest.
"""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import tg_miniapp  # noqa: E402

# страница → режим: «deck» листается экранами, «page» прокручивается
PAGES = {
    "ai-strategy/index.html": "deck",
    "ai-strategy/ru/index.html": "deck",
    "about/index.html": "deck",
    "about/ru/index.html": "deck",
    "automation/index.html": "page",
    "automation_ru/index.html": "page",
}
SDK = "https://telegram.org/js/telegram-web-app.js"


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _head(html):
    return html[html.index("<head>"):html.index("</head>")]


def _snippet_js():
    s = tg_miniapp.head_snippet("deck")
    return s[len("<script>"):-len("</script>")]


def _js_regex(src, marker):
    """Регэксп из JS-строки — по его окрестности (marker) — как re.Pattern."""
    i = src.index(marker)
    start = src.rindex("/", 0, i)
    m = re.match(r"/((?:\\.|[^/\\])+)/([gimsuy]*)", src[start:])
    assert m, "не нашёлся регэксп рядом с " + marker
    return re.compile(m.group(1), re.I if "i" in m.group(2) else 0)


# ── страницы ──────────────────────────────────────────────────────────────

def test_every_miniapp_page_checks_the_launch_in_head():
    """Проверка запуска стоит в <head> каждой из шести страниц, один раз и в
    режиме своей страницы: лендинг и «Обо мне» листаются экранами (deck),
    вход в курс — обычная прокрутка (page)."""
    for rel, mode in PAGES.items():
        html = _read(rel)
        head = _head(html)
        assert head.count(tg_miniapp.head_snippet(mode)) == 1, \
            "%s: нет проверки запуска Telegram в режиме %s" % (rel, mode)
        other = "page" if mode == "deck" else "deck"
        assert tg_miniapp.head_snippet(other) not in html, rel + ": чужой режим"
        # проверка раньше заголовка и стилей: класс html.tg ставится до первой отрисовки
        assert head.index("FR-SITE87") < head.index("<title>"), rel


def test_telegram_sdk_is_never_loaded_outside_telegram():
    """Вне Telegram — ни одного лишнего запроса: SDK и tg-miniapp.js не
    подключаются разметкой, нет и preconnect/preload на telegram.org —
    их вставляет только проверка запуска."""
    for rel in PAGES:
        html = _read(rel)
        assert not re.search(r'<script[^>]+src="[^"]*telegram', html), rel + ": SDK подключён тегом"
        assert not re.search(r'<script[^>]+src="[^"]*tg-miniapp', html), rel + ": скрипт подключён тегом"
        assert not re.search(r'<link[^>]+telegram\.org', html), rel + ": preconnect к telegram.org"
        # адрес SDK встречается ровно в одном месте — в проверке запуска
        assert html.count("telegram.org/js/") == 1, rel
        assert html.count("/assets/tg-miniapp.js") == 1, rel


def test_launch_check_only_fires_on_telegram_launch_params():
    """Логика проверки запуска: параметры берутся из hash (tgWebAppData или
    tgWebAppPlatform), в том числе после своего пути (#/x?tgWebApp…);
    запоминаются на вкладку — переход по сайту внутри мини-аппа hash
    теряет; без них скрипты не вставляются."""
    js = _snippet_js()
    keep = _js_regex(js, "tgWebApp\\w*=")
    fire = _js_regex(js, "tgWebApp(Data|Platform)=")

    def launch_params(hash_):
        parts = re.split(r"[?&]", hash_[1:])
        return "&".join(x for x in parts if keep.search(x))

    cases = {
        "#tgWebAppData=query_id%3DA%26user%3D%7B%7D&tgWebAppVersion=8.0&tgWebAppPlatform=ios": True,
        "#tgWebAppPlatform=android&tgWebAppVersion=7.0": True,          # кнопка клавиатуры: initData пуст
        "#/section?tgWebAppData=a%3Db&tgWebAppPlatform=tdesktop": True,
        "#tgWebAppVersion=8.0&tgWebAppThemeParams=%7B%7D": False,       # без Data/Platform — не запуск
        "#solution": False,
        "": False,
        "#xtgWebAppData=1": False,
    }
    for hash_, want in cases.items():
        p = launch_params(hash_)
        assert bool(fire.search(p)) is want, "%r: запуск=%s" % (hash_, not want)
    # в продукт уходят только параметры Telegram — чужой hash страницы не тянется
    assert launch_params("#/x?tgWebAppData=a&foo=1&tgWebAppPlatform=ios") == \
        "tgWebAppData=a&tgWebAppPlatform=ios"
    # порядок в скрипте: запомнить → без параметров выйти → только потом грузить
    i_store = js.index("sessionStorage.setItem('ait_tg', p)")
    i_recall = js.index("p = sessionStorage.getItem('ait_tg')")
    i_exit = js.index("if (!p) return;")
    i_load = js.index("document.createElement('script')")
    assert i_store < i_recall < i_exit < i_load, "скрипты вставляются только после проверки"
    assert js.index(SDK) > i_exit and js.index("/assets/tg-miniapp.js") > i_exit
    assert "s.async = false;" in js, "SDK выполняется раньше нашего скрипта"
    assert "try {" in js and "} catch (e) {}" in js, \
        "закрытый sessionStorage не должен ломать страницу"


def test_generators_share_one_launch_check():
    """Проверка запуска одна на три генератора (tools/tg_miniapp.py), и
    страницы на диске совпадают со сборкой: руками их не правят."""
    for gen in ("build_strategy.py", "build_about.py", "build_course_entry.py"):
        src = _read("tools/" + gen)
        assert "from tg_miniapp import head_snippet" in src, gen
    assert 'head_snippet("deck")' in _read("tools/build_strategy.py")
    assert 'head_snippet("deck")' in _read("tools/build_about.py")
    assert 'head_snippet("page")' in _read("tools/build_course_entry.py")

    import build_strategy
    import build_about
    import build_course_entry
    from strategy_copy import EN as SEN, RU as SRU
    from about_copy import EN as AEN, RU as ARU
    from typo import bind_copy
    built = {
        "ai-strategy/index.html": build_strategy.page(bind_copy(SEN, "en"), "en"),
        "ai-strategy/ru/index.html": build_strategy.page(bind_copy(SRU, "ru"), "ru"),
        "about/index.html": build_about.page(bind_copy(AEN, "en")),
        "about/ru/index.html": build_about.page(bind_copy(ARU, "ru")),
    }
    built.update(build_course_entry.build())
    for rel in PAGES:
        assert _read(rel) == built[rel], rel + " разошёлся с генератором — пересоберите"


# ── поведение в Telegram (assets/tg-miniapp.js) ───────────────────────────

def _js():
    return _read("assets/tg-miniapp.js")


def test_miniapp_script_is_native():
    """ready + expand, цвета Telegram — цвет страницы (сайт тёмный), свайп
    «свернуть» выключен только на листающихся страницах, методы — только
    если клиент их знает."""
    js = _js()
    assert "var W = window.Telegram && window.Telegram.WebApp;\n  if (!W) return;" in js, \
        "SDK не загрузился — страница остаётся обычной"
    assert "W.ready();" in js and "W.expand();" in js
    assert "if (deck && at('7.7')) safe(function () { W.disableVerticalSwipes(); });" in js
    assert "root.getAttribute('data-tg') === 'deck'" in js
    for call, ver in (("setBackgroundColor", "6.1"), ("setHeaderColor", "6.9"), ("setBottomBarColor", "7.10")):
        assert "if (at('%s')) safe(function () { W.%s(c); });" % (ver, call) in js, call
    # цвет — из meta theme-color: у /automation/ светлая тема переписывает его на лету
    assert "document.querySelector('meta[name=\"theme-color\"]')" in js
    assert "new MutationObserver" in js and "attributeFilter: ['content']" in js
    assert "W.onEvent('themeChanged'" in js
    # у всех страниц есть свой цвет — и он тёмный, как сайт
    for rel in PAGES:
        assert '<meta name="theme-color" content="#050505">' in _read(rel), rel


def test_miniapp_links_open_natively():
    """Чужие сайты — openLink (внешний браузер), t.me — openTelegramLink,
    свой сайт и продукт — внутри мини-аппа; в продукт уезжают параметры
    запуска Telegram (hash), и только в продукт."""
    js = _js()
    site = _js_regex(js, "andre\\.technology$/i;\n  var PRODUCT")
    product = _js_regex(js, "(strategy|maturity)")
    tme = _js_regex(js, "(t|telegram)\\.me")
    for host in ("strategy.andre.technology", "maturity.andre.technology", "STRATEGY.andre.technology"):
        assert product.search(host), host
    for host in ("andre.technology", "strategy.andre.technology.evil.io", "evilstrategy.andre.technology",
                 "t.me", "dataist.ai"):
        assert not product.search(host), host
    assert site.search("andre.technology") and site.search("www.andre.technology")
    assert not site.search("strategy.andre.technology")
    assert tme.search("t.me") and tme.search("telegram.me") and not tme.search("t.me.evil.io")
    assert "if (PRODUCT.test(u.hostname)) { location.href = intoProduct(u.href); return; }" in js
    assert "W.openTelegramLink(u.href)" in js and "W.openLink(u.href)" in js
    assert "if (u.protocol !== 'https:' && u.protocol !== 'http:') return;" in js, "mailto: — как есть"
    assert "if (u.host === location.host || SITE.test(u.hostname)) return;" in js
    assert "if (e.defaultPrevented" in js, "клик, который страница обработала сама, не трогаем"
    # параметры запуска — те, что запомнила проверка запуска
    assert "sessionStorage.getItem('ait_tg')" in js
    assert "href + (href.indexOf('#') < 0 ? '#' : '&') + p" in js
    # без моста Telegram (ссылку открыли в браузере) ссылки не перехватываются
    i_bridge = js.index("if (!bridge) return;")
    assert "TelegramWebviewProxy" in js[:i_bridge]
    assert i_bridge < js.index("document.addEventListener('click'")


def test_miniapp_back_button_and_safe_area():
    """«Назад» Telegram — когда внутри мини-аппа есть куда вернуться;
    безопасные отступы — из safeAreaInset/contentSafeAreaInset."""
    js = _js()
    assert "W.BackButton.onClick(function () { history.back(); })" in js
    assert "if (s.length > 1) W.BackButton.show(); else W.BackButton.hide();" in js
    assert "window.addEventListener('pagehide'" in js, "кнопка не остаётся на чужой странице"
    assert "e.persisted" in js, "возврат из кэша «назад» пересчитывает стек"
    assert "W.safeAreaInset" in js and "W.contentSafeAreaInset" in js
    assert "root.style.setProperty('--safe-t', top + 'px');" in js
    assert "'max(env(safe-area-inset-bottom, 0px), ' + bottom + 'px)'" in js
    for ev in ("safeAreaChanged", "contentSafeAreaChanged", "fullscreenChanged", "viewportChanged"):
        assert "'%s'" % ev in js, ev


def test_safe_area_defaults_keep_the_site_unchanged():
    """Страницы берут отступы из --safe-b / --safe-t, а задаёт их только
    tg-miniapp.js. Значения по умолчанию — прежние: env() снизу, 0 сверху, —
    поэтому вне Telegram раскладка та же (замер в Chromium — совпадение с
    main на 1440×900, 1024×768, 390×844)."""
    for rel in ("assets/strategy.css", "assets/about.css"):
        css = _read(rel)
        assert css.count("env(safe-area-inset-bottom, 0px)") == \
            css.count("var(--safe-b, env(safe-area-inset-bottom, 0px))") >= 7, \
            rel + ": каждый нижний отступ должен идти через --safe-b"
        assert not re.search(r"--safe-[bt]\s*:", css), rel + ": переменные задаёт только tg-miniapp.js"
        assert "header { position: fixed; top: calc(var(--safe-t, 0px) / var(--z, 1));" in css, rel
    assert ".deck { position: fixed; inset: calc(var(--safe-t, 0px) / var(--z, 1)) 0 0;" in _read("assets/strategy.css")
    assert ".read { position: fixed; inset: calc(var(--safe-t, 0px) / var(--z, 1)) 0 0;" in _read("assets/about.css")
    for rel in ("automation/index.html", "automation_ru/index.html"):
        html = _read(rel)
        assert "header{position:fixed;top:var(--safe-t,0px);" in html, rel
        assert "bottom:calc(15px + var(--safe-b,0px))" in html, rel + ": кружок над полосой «домой»"
        assert not re.search(r"--safe-[bt]\s*:", html), rel


def test_spec_describes_fr_site87():
    spec = _read("SPEC-SITE.md")
    sec = spec[spec.index("### FR-SITE87"):]
    for word in ("tgWebAppData", "openLink", "openTelegramLink", "disableVerticalSwipes",
                 "BackButton", "?login=1", "initData", "tests/test_tg_miniapp.py"):
        assert word in sec, "в FR-SITE87 не описано: " + word


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   " + name)
            except AssertionError as e:
                fails += 1
                print("FAIL " + name + ": " + str(e))
            except Exception as e:
                fails += 1
                print("ERR  " + name + ": " + type(e).__name__ + ": " + str(e))
    print("ВСЕ ТЕСТЫ МИНИ-АППА ПРОЙДЕНЫ" if not fails else "ПРОВАЛЕНО: %d" % fails)
    sys.exit(1 if fails else 0)
