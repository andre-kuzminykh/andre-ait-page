# -*- coding: utf-8 -*-
"""FR-SITE87 — проверка страниц в Chromium: вне Telegram и внутри Mini App.

Строковые тесты (tests/test_tg_miniapp.py) видят разметку, но не то, что
происходит в браузере: сколько запросов ушло, какие методы Telegram
вызваны, куда уехала ссылка. Здесь это меряется по факту.

Вне Telegram:
  * ни одного запроса к telegram.org и /assets/tg-miniapp.js, html.tg нет;
  * с --baseline <ref> — раскладка шапки, экранов, кружка и точек совпадает
    с этой ревизией (её страницы достаются git archive и поднимаются рядом).

Внутри Telegram — эмуляция: SDK (telegram.org) подменён заглушкой
window.Telegram.WebApp, которая пишет вызовы в window.__tg, мост —
window.TelegramWebviewProxy; продуктовые домены отдают пустую страницу:
  * ready/expand/цвета, disableVerticalSwipes только на листающихся страницах;
  * нижний отступ из safeAreaInset поднимает кружок и точки;
  * t.me → openTelegramLink, чужие сайты → openLink, продукт — внутри мини-аппа
    с параметрами запуска в hash;
  * EN|RU сохраняет режим и показывает «Назад», «Назад» возвращает;
  * светлая тема /automation/ перекрашивает шапку Telegram;
  * полноэкранный режим — шапка под кнопками Telegram;
  * старый клиент, SDK не загрузился, нет моста — без ошибок.

Внешние шрифты и CDN закрыты (как в песочнице): на запасном шрифте слово героя
/automation/ на 390px шире колонки — это есть и на main, поэтому переполнение
в Telegram сравнивается с той же страницей вне Telegram.

    python3 tools/tg_miniapp_check.py                       → «TG MINIAPP OK»
    python3 tools/tg_miniapp_check.py --baseline origin/main
"""
import argparse
import functools
import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    ("/ai-strategy/ru/", "deck"), ("/ai-strategy/", "deck"),
    ("/about/ru/", "deck"), ("/about/", "deck"),
    ("/automation_ru/", "page"), ("/automation/", "page"),
]
VIEWPORTS = [(1440, 900), (1024, 768), (390, 844)]

_INIT_DATA = urllib.parse.urlencode({
    "query_id": "AAH", "user": json.dumps({"id": 42, "first_name": "Test", "language_code": "ru"}),
    "auth_date": "1790000000", "hash": "abc123"})
_THEME = json.dumps({"bg_color": "#ffffff", "text_color": "#000000", "button_color": "#2481cc"})
# так Telegram дописывает параметры запуска к адресу web_app
LAUNCH = ("tgWebAppData=" + urllib.parse.quote(_INIT_DATA, safe="") +
          "&tgWebAppVersion=8.0&tgWebAppPlatform=ios&tgWebAppThemeParams=" +
          urllib.parse.quote(_THEME, safe=""))

# Заглушка SDK: версия и отступы — из window.__tgCfg, вызовы — в window.__tg
SDK_STUB = r"""
(function(){
  var calls = window.__tg = window.__tg || [];
  var ev = window.__tgEv = {};
  function rec(name){ return function(){ calls.push([name].concat([].slice.call(arguments))); }; }
  var cfg = window.__tgCfg || {};
  window.Telegram = { WebApp: {
    version: cfg.version || '8.0', platform: 'ios',
    isVersionAtLeast: function(v){
      var a = this.version.split('.').map(Number), b = String(v).split('.').map(Number);
      for (var i = 0; i < Math.max(a.length, b.length); i++) {
        var x = a[i] || 0, y = b[i] || 0; if (x !== y) return x > y;
      }
      return true;
    },
    themeParams: {bg_color: '#ffffff'}, colorScheme: 'light',
    safeAreaInset: cfg.safe || {top: 0, bottom: 34, left: 0, right: 0},
    contentSafeAreaInset: cfg.content || {top: 0, bottom: 0, left: 0, right: 0},
    ready: rec('ready'), expand: rec('expand'), disableVerticalSwipes: rec('disableVerticalSwipes'),
    setHeaderColor: rec('setHeaderColor'), setBackgroundColor: rec('setBackgroundColor'),
    setBottomBarColor: rec('setBottomBarColor'), openLink: rec('openLink'),
    openTelegramLink: rec('openTelegramLink'),
    onEvent: function(n, f){ (ev[n] = ev[n] || []).push(f); },
    BackButton: { show: rec('BackButton.show'), hide: rec('BackButton.hide'),
      onClick: function(f){ window.__tgBack = f; calls.push(['BackButton.onClick']); } }
  } };
})();
"""
BRIDGE = "window.TelegramWebviewProxy = { postEvent: function(){} };"
READY = "window.__tg && window.__tg.some(c => c[0] === 'ready')"
IGNORED_ERR = ("fonts.googleapis", "fonts.gstatic", "cdnjs", "i.ibb.co", "ERR_", "Failed to load resource")

RECTS = """() => {
  const sel = ['header', '.header-row', '.deck', '.read', '.screen.active', '.head', '.media', '.dots',
               '#bubble', '.panel', '.hero', '.hero-cta .btn', 'button.hero-how', '.nav', '.cta-head', '.lang-switch'];
  const out = {};
  sel.forEach(s => document.querySelectorAll(s).forEach((el, i) => {
    const r = el.getBoundingClientRect();
    out[s + '#' + i] = [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)];
  }));
  return out;
}"""
# на лендинге в герое новая строка «Войти» — её соседи по колонке сдвигаются
HERO_MOVES = ("button.hero-how", ".hero-cta .btn", ".screen.active")


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(directory):
    handler = functools.partial(_QuietHandler, directory=directory)

    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, *a):
            pass

    srv = Quiet(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def export(ref):
    """Страницы ревизии ref — во временную папку (git archive, без ворктри).
    Ролики не берём: в репозитории их сотни мегабайт, а размер кружка задаёт
    CSS, не видео."""
    out = tempfile.mkdtemp(prefix="tg-baseline-")
    paths = ["ai-strategy", "about", "automation/index.html", "automation_ru", "assets",
             "andre_ai.jpg", "favicon.ico", ":(exclude)*.mp4"]
    arc = subprocess.run(["git", "archive", ref, "--"] + paths, cwd=ROOT, check=True,
                         capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", out], input=arc, check=True)
    return out


class Check:
    def __init__(self, browser, base):
        self.b, self.base, self.problems = browser, base, []

    def bad(self, msg):
        self.problems.append(msg)
        print("  !!", msg)

    def local_only(self, route):
        u = route.request.url
        return route.continue_() if u.startswith("http://127.0.0.1") else route.abort()

    def plain_page(self, w, h, base=None):
        ctx = self.b.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        page._reqs, page._errs = [], []
        page.on("request", lambda r: page._reqs.append(r.url))
        page.on("console", lambda m: m.type == "error" and page._errs.append(m.text))
        page.on("pageerror", lambda e: page._errs.append(str(e)))
        page.route("**/*", self.local_only)
        return ctx, page

    def tg_context(self, w, h, cfg=None, bridge=True, sdk=True):
        ctx = self.b.new_context(viewport={"width": w, "height": h})
        ctx.add_init_script("window.__tgCfg = %s;" % json.dumps(cfg or {}))
        if bridge:
            ctx.add_init_script(BRIDGE)
        ctx._reqs = []
        ctx.on("request", lambda r: ctx._reqs.append(r.url))

        def router(route):
            u = route.request.url
            if u.startswith("https://telegram.org/js/telegram-web-app.js") and sdk:
                return route.fulfill(status=200, content_type="application/javascript", body=SDK_STUB)
            if u.startswith(("https://strategy.andre.technology", "https://maturity.andre.technology")):
                return route.fulfill(status=200, content_type="text/html", body="<!doctype html><title>product</title>")
            return self.local_only(route)
        ctx.route("**/*", router)
        return ctx

    def errors(self, errs):
        return [e for e in errs if not any(k in e for k in IGNORED_ERR)]

    # ── вне Telegram ──────────────────────────────────────────────────────
    def outside(self, baseline):
        print("== вне Telegram")
        for w, h in VIEWPORTS:
            for path, _mode in PAGES:
                ctx, page = self.plain_page(w, h)
                page.goto(self.base + path, wait_until="load")
                page.wait_for_timeout(700)
                mine = page.evaluate(RECTS)
                extra = [u for u in page._reqs if "telegram.org" in u or "tg-miniapp" in u]
                if extra:
                    self.bad("%s %dx%d: лишние запросы вне Telegram: %s" % (path, w, h, extra))
                marked = page.evaluate("document.documentElement.classList.contains('tg') || "
                                       "document.documentElement.hasAttribute('data-tg')")
                if marked:
                    self.bad("%s: вне Telegram html помечен режимом мини-аппа" % path)
                if self.errors(page._errs):
                    self.bad("%s %dx%d: ошибки в консоли: %s" % (path, w, h, self.errors(page._errs)))
                ctx.close()
                note = ""
                if baseline:
                    ctx, page = self.plain_page(w, h)
                    page.goto(baseline + path, wait_until="load")
                    page.wait_for_timeout(700)
                    theirs = page.evaluate(RECTS)
                    ctx.close()
                    diff = [(k, theirs.get(k), mine.get(k)) for k in sorted(set(mine) | set(theirs))
                            if mine.get(k) != theirs.get(k)]
                    if path.startswith("/ai-strategy"):
                        diff = [d for d in diff if not d[0].startswith(HERO_MOVES)]
                    if diff:
                        self.bad("%s %dx%d: раскладка разошлась с базовой: %s" % (path, w, h, diff[:6]))
                    note = " раскладка = базовой"
                print("  ok %-18s %dx%d%s" % (path, w, h, note))

    # ── внутри Telegram ───────────────────────────────────────────────────
    def inside(self):
        print("== в эмуляции Telegram Mini App")
        for w, h in VIEWPORTS:
            for path, mode in PAGES:
                ctx, page = self.plain_page(w, h)
                page.goto(self.base + path, wait_until="load")
                plain_sw = page.evaluate("document.documentElement.scrollWidth")
                ctx.close()
                ctx = self.tg_context(w, h)
                page = ctx.new_page()
                errs = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.on("console", lambda m: m.type == "error" and errs.append(m.text))
                page.goto(self.base + path + "#" + LAUNCH, wait_until="load")
                page.wait_for_function(READY, timeout=5000)
                calls = page.evaluate("window.__tg")
                names = [c[0] for c in calls]
                for need in ("ready", "expand", "setHeaderColor", "setBackgroundColor", "setBottomBarColor"):
                    if need not in names:
                        self.bad("%s: нет вызова %s" % (path, need))
                hdr = [c[1] for c in calls if c[0] == "setHeaderColor"]
                if hdr[:1] != ["#050505"]:
                    self.bad("%s: цвет шапки Telegram %s, а страница #050505" % (path, hdr))
                if ("disableVerticalSwipes" in names) != (mode == "deck"):
                    self.bad("%s: disableVerticalSwipes не по режиму %s" % (path, mode))
                if "BackButton.show" in names:
                    self.bad("%s: на странице запуска показана «Назад»" % path)
                mark = page.evaluate("[document.documentElement.classList.contains('tg'), "
                                     "document.documentElement.getAttribute('data-tg')]")
                if mark != [True, mode]:
                    self.bad("%s: html.tg / data-tg = %s" % (path, mark))
                n_sdk = sum(u.startswith("https://telegram.org/js/telegram-web-app.js") for u in ctx._reqs)
                n_own = sum(u.endswith("/assets/tg-miniapp.js") for u in ctx._reqs)
                if (n_sdk, n_own) != (1, 1):
                    self.bad("%s: SDK запрошен %d раз, tg-miniapp.js — %d" % (path, n_sdk, n_own))
                if page.evaluate("document.documentElement.scrollWidth") > plain_sw:
                    self.bad("%s %dx%d: в Telegram страница шире, чем без него" % (path, w, h))
                if self.errors(errs):
                    self.bad("%s %dx%d: ошибки: %s" % (path, w, h, self.errors(errs)))
                print("  ok %-18s %dx%d  %s" % (path, w, h, ",".join(sorted(set(names)))))
                ctx.close()

        for path, sel in (("/ai-strategy/ru/", ".head"), ("/about/ru/", ".dots"), ("/automation_ru/", "#bubble")):
            ctx, page = self.plain_page(390, 844)
            page.goto(self.base + path, wait_until="load")
            page.wait_for_timeout(300)
            before = page.evaluate("document.querySelector(%r).getBoundingClientRect().bottom" % sel)
            ctx.close()
            ctx = self.tg_context(390, 844)
            page = ctx.new_page()
            page.goto(self.base + path + "#" + LAUNCH, wait_until="load")
            page.wait_for_function(READY)
            page.wait_for_timeout(300)
            after = page.evaluate("document.querySelector(%r).getBoundingClientRect().bottom" % sel)
            ctx.close()
            if abs(before - after - 34) > 1:
                self.bad("%s: %s поднят на %.1fpx вместо 34" % (path, sel, before - after))
            else:
                print("  ok отступ снизу %s %s: %.0f → %.0f" % (path, sel, before, after))

        ctx = self.tg_context(390, 844)
        page = ctx.new_page()
        page.goto(self.base + "/ai-strategy/ru/#" + LAUNCH, wait_until="load")
        page.wait_for_function(READY)
        page.evaluate("document.querySelector('a[href=\"https://t.me/andre_dataist\"]').click()")
        page.evaluate("document.querySelector('a[href*=\"youtube.com\"]').click()")
        calls = page.evaluate("window.__tg")
        if ["openTelegramLink", "https://t.me/andre_dataist"] not in calls:
            self.bad("t.me не ушёл в openTelegramLink")
        if ["openLink", "https://www.youtube.com/@andre_dataist"] not in calls:
            self.bad("YouTube не ушёл в openLink")
        if page.url.split("#")[0] != self.base + "/ai-strategy/ru/":
            self.bad("внешняя ссылка увела страницу: %s" % page.url)
        else:
            print("  ok t.me → openTelegramLink, YouTube → openLink, страница на месте")
        with page.expect_navigation():
            page.evaluate("document.querySelector('a.hero-login').click()")
        if not (page.url.startswith("https://strategy.andre.technology/?login=1&lang=ru#tgWebAppData=")
                and "tgWebAppPlatform=ios" in page.url):
            self.bad("«Войти» → продукт без параметров запуска: %s" % page.url)
        else:
            print("  ok «Войти» → %s…" % page.url[:72])
        ctx.close()

        ctx = self.tg_context(390, 844)
        page = ctx.new_page()
        page.goto(self.base + "/ai-strategy/ru/#" + LAUNCH, wait_until="load")
        page.wait_for_function(READY)
        with page.expect_navigation():
            page.evaluate("document.querySelector('.lang-opt[href=\"/ai-strategy/\"]').click()")
        page.wait_for_function(READY)
        names = [c[0] for c in page.evaluate("window.__tg")]
        if "BackButton.show" not in names or not page.evaluate("document.documentElement.classList.contains('tg')"):
            self.bad("после EN|RU режим мини-аппа или «Назад» пропали: %s" % names)
        else:
            print("  ok EN|RU внутри мини-аппа: режим остался, «Назад» показана")
        with page.expect_navigation():
            page.evaluate("window.__tgBack()")
        page.wait_for_function(READY)
        names = [c[0] for c in page.evaluate("window.__tg")]
        if page.url.split("#")[0] != self.base + "/ai-strategy/ru/" or "BackButton.show" in names:
            self.bad("«Назад» вернула не туда или кнопка осталась: %s" % page.url)
        else:
            print("  ok «Назад» → /ai-strategy/ru/, кнопка спрятана")
        page.goto(self.base + "/about/ru/", wait_until="load")
        page.wait_for_function(READY)
        with page.expect_navigation():
            page.evaluate("document.querySelector('a.cta').click()")
        if not page.url.startswith("https://maturity.andre.technology/?lang=ru#tgWebAppData="):
            self.bad("«Обо мне» → продукт без параметров запуска: %s" % page.url)
        else:
            print("  ok «Обо мне» → %s…" % page.url[:62])
        ctx.close()

        ctx = self.tg_context(1440, 900)
        page = ctx.new_page()
        page.goto(self.base + "/automation_ru/#" + LAUNCH, wait_until="load")
        page.wait_for_function(READY)
        page.click("#theme")
        page.wait_for_timeout(200)
        hdr = [c[1] for c in page.evaluate("window.__tg") if c[0] == "setHeaderColor"]
        if hdr[-1:] != ["#FAFAFA"]:
            self.bad("светлая тема не перекрасила шапку Telegram: %s" % hdr)
        else:
            print("  ok светлая тема /automation_ru/: шапка Telegram %s" % " → ".join(hdr))
        ctx.close()

        ctx = self.tg_context(390, 844, {"safe": {"top": 59, "bottom": 34, "left": 0, "right": 0},
                                         "content": {"top": 46, "bottom": 0, "left": 0, "right": 0}})
        page = ctx.new_page()
        for path in ("/ai-strategy/ru/", "/about/ru/", "/automation_ru/"):
            page.goto(self.base + path + "#" + LAUNCH, wait_until="load")
            page.wait_for_function(READY)
            page.wait_for_timeout(300)
            top = page.evaluate("document.querySelector('header').getBoundingClientRect().top")
            if abs(top - 105) > 1:
                self.bad("%s: в полноэкранном режиме шапка с %.0fpx вместо 105" % (path, top))
            else:
                print("  ok полноэкранный %s: шапка с %.0fpx" % (path, top))
        ctx.close()

        ctx = self.tg_context(390, 844, {"version": "6.0"})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(self.base + "/ai-strategy/ru/#" + LAUNCH, wait_until="load")
        page.wait_for_function(READY)
        names = set(c[0] for c in page.evaluate("window.__tg"))
        if names - {"ready", "expand"} or errs:
            self.bad("клиент 6.0: вызваны %s, ошибки %s" % (sorted(names), errs))
        else:
            print("  ok клиент 6.0: только ready, expand")
        ctx.close()

        for label, kw in (("SDK не загрузился", {"sdk": False}), ("нет моста Telegram", {"bridge": False})):
            ctx = self.tg_context(390, 844, **kw)
            page = ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(self.base + "/ai-strategy/ru/#" + LAUNCH, wait_until="load")
            page.wait_for_timeout(500)
            names = page.evaluate("(window.__tg || []).map(c => c[0])")
            if names or errs:
                self.bad("%s: вызовы %s, ошибки %s" % (label, names, errs))
            else:
                print("  ok %s — поведение не включается, ошибок нет" % label)
            ctx.close()


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", help="ревизия для сравнения раскладки вне Telegram, например origin/main")
    ap.add_argument("--only", choices=("outside", "inside"))
    args = ap.parse_args()

    srv, base = serve(ROOT)
    tmp = bsrv = baseline = None
    if args.baseline:
        tmp = export(args.baseline)
        bsrv, baseline = serve(tmp)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=os.environ.get("CHROMIUM_PATH") or "/opt/pw-browsers/chromium")
            check = Check(browser, base)
            if args.only != "inside":
                check.outside(baseline)
            if args.only != "outside":
                check.inside()
            browser.close()
    finally:
        srv.shutdown()
        if bsrv:
            bsrv.shutdown()
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    if check.problems:
        print("\nПРОБЛЕМ: %d" % len(check.problems))
        sys.exit(1)
    print("\nTG MINIAPP OK")


if __name__ == "__main__":
    main()
