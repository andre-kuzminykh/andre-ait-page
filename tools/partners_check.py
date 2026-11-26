# -*- coding: utf-8 -*-
"""FR-SITE120…139, NFR-SITE106…110 — сайт партнёров в Chromium: оба адреса, снимки, ролик.

Поведение страницы (порядок «от лучших к худшим», поиск, фильтры, сортировка,
карточка по клику и по ?p=, «Назад», формы, 390 px без прокрутки вбок, ошибки
консоли) проверяет tests/test_partners.py — он берёт отсюда сервер, «Caddy» и
запуск браузера. Здесь же — то, что нужно человеку глазами:

  * страница поднимается в двух видах адреса, как на проде:
      http://127.0.0.1:N/partners/   — как andre.technology/partners/ (GitHub Pages);
      http://127.0.0.1:M/            — как partners.andre.technology: маленький прокси
                                       переписывает /x → /partners/x, как блок Caddy из
                                       SPEC-SITE.md (NFR-SITE110);
    в обоих — каталог из partners.json (не из встроенной копии), значки и данные
    без 404, в консоли пусто;
  * --shots DIR — снимки: каталог, открытая карточка, «Как стать партнёром»,
    заявка; компьютер 1440×900 и телефон 390×844, RU и EN;
  * --video DIR — ролик сценария «поиск → фильтр → карточка → как стать
    партнёром» (webm, и mp4, если есть ffmpeg).

Внешние шрифты и логотип по умолчанию закрыты, как в песочнице (JetBrains Mono
обычно стоит в системе); с --net они идут через прокси окружения — так делаются
снимки для владельца.

    python3 tools/partners_check.py                          → «PARTNERS OK»
    python3 tools/partners_check.py --net --shots DIR --video DIR
"""
import argparse
import functools
import http.server
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg_miniapp_check import serve  # noqa: E402 — тот же тихий локальный сервер, что у проверок цен и мини-аппа

CHROMIUM = os.environ.get("CHROMIUM_PATH") or "/opt/pw-browsers/chromium"
DESKTOP, PHONE = (1440, 900), (390, 844)


class _Rewrite(http.server.BaseHTTPRequestHandler):
    """Как Caddy из SPEC-SITE.md: `rewrite * /partners{uri}` + reverse_proxy на сайт."""
    upstream = ""
    _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # 127.0.0.1 — мимо прокси окружения

    def log_message(self, *a):
        pass

    def _relay(self, body):
        url = self.upstream + "/partners" + self.path
        req = urllib.request.Request(url, method=self.command)
        try:
            r = self._opener.open(req, timeout=10)
            code, headers, data = r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            code, headers, data = e.code, e.headers, e.read()
        self.send_response(code)
        for k in ("Content-Type", "Last-Modified", "Location"):
            if headers.get(k):
                self.send_header(k, headers.get(k))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if body:
            self.wfile.write(data)

    def do_GET(self):
        self._relay(True)

    def do_HEAD(self):
        self._relay(False)


def serve_rewrite(upstream):
    """Поддомен на столе: всё, что пришло на /x, берётся с upstream/partners/x."""
    handler = type("Rewrite", (_Rewrite,), {"upstream": upstream})

    class Quiet(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

        def handle_error(self, *a):
            pass

    srv = Quiet(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def servers():
    """(сайт, поддомен, адрес_страницы_на_сайте, адрес_страницы_на_поддомене, остановить)."""
    site, base = serve(ROOT)
    sub, base2 = serve_rewrite(base)

    def stop():
        sub.shutdown()
        site.shutdown()
    return base, base2, base + "/partners/", base2 + "/", stop


def launch(pw, net=False):
    opts = {"executable_path": CHROMIUM, "args": ["--no-sandbox"]}
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if net and proxy:
        opts["proxy"] = {"server": proxy, "bypass": "127.0.0.1,localhost"}
    return pw.chromium.launch(**opts)


def new_page(browser, size, net=False, lang=None, reduced=False, touch=False, record=None):
    """Страница со сбором ошибок: консоль, исключения, а также ответы ≥ 400 и сбои своих запросов
    (чужие хосты без --net закрыты — их сбои не считаются)."""
    kw = {"viewport": {"width": size[0], "height": size[1]}, "locale": "en-US" if lang == "en" else "ru-RU"}
    if reduced:
        kw["reduced_motion"] = "reduce"
    if touch:
        kw.update(has_touch=True, is_mobile=True, device_scale_factor=2)
    if record:
        kw["record_video_dir"] = record
        kw["record_video_size"] = {"width": size[0], "height": size[1]}
    ctx = browser.new_context(**kw)
    ctx.route("**/*", lambda r: r.continue_() if (net or r.request.url.startswith(("http://127.0.0.1", "file:"))) else r.abort())
    pg = ctx.new_page()
    pg.errors, pg.bad = [], []

    def console(m):
        if m.type != "error":
            return
        url = (m.location or {}).get("url", "")
        if "Failed to load resource" in m.text and url and not url.startswith("http://127.0.0.1"):
            return                                   # закрытый внешний хост (шрифт, логотип) — не ошибка страницы
        pg.errors.append(m.text)
    pg.on("console", console)
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.on("response", lambda r: r.url.startswith("http://127.0.0.1") and r.status >= 400 and pg.bad.append("%d %s" % (r.status, r.url)))
    pg.on("requestfailed", lambda r: r.url.startswith("http://127.0.0.1") and pg.bad.append("failed %s" % r.url))
    return ctx, pg


def wait_ready(pg):
    pg.wait_for_function("window.AndrePartners && window.AndrePartners.ready === true", timeout=10000)


def open_page(browser, url, size=DESKTOP, lang="ru", **kw):
    ctx, pg = new_page(browser, size, lang=lang, **kw)
    sep = "&" if "?" in url else "?"
    pg.goto(url + ("" if "lang=" in url else sep + "lang=" + lang), wait_until="load")
    wait_ready(pg)
    return ctx, pg


OVERFLOW = """() => { const de = document.documentElement;
  return { doc: de.scrollWidth - de.clientWidth,
    wide: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.right > de.clientWidth + 1 || r.left < -1)
      && getComputedStyle(e).position !== 'fixed' && !e.closest('.sr, .sprite, .hp, [hidden]'); }).slice(0, 5).map(e => e.className || e.tagName) }; }"""

TAPS = """() => [...document.querySelectorAll('a[href], button, input:not(.hp):not([type=hidden]), select, textarea')]
  .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden' && !e.closest('[hidden], .sr'); })
  .map(e => { const r = e.getBoundingClientRect(), t = e.closest('label.chip') ? e.closest('label.chip').getBoundingClientRect() : r;
    return { w: Math.round(Math.max(r.width, t.width)), h: Math.round(Math.max(r.height, t.height)), what: (e.id || e.className || e.tagName) + ' ' + (e.textContent || '').trim().slice(0, 24) }; })"""


# ── сценарий для снимков и ролика ──────────────────────────────────────────

def shots(browser, url, outdir, net):
    os.makedirs(outdir, exist_ok=True)
    made = []
    for lang in ("ru", "en"):
        for size, tag in ((DESKTOP, "desktop"), (PHONE, "phone")):
            ctx, pg = open_page(browser, url, size, lang, net=net, touch=size == PHONE)
            pg.wait_for_timeout(1200)

            def snap(name, full=False):
                path = os.path.join(outdir, "%s-%s-%s.png" % (tag, lang, name))
                pg.screenshot(path=path, full_page=full)
                made.append(path)
            snap("1-catalog")
            pg.evaluate("document.querySelector('#catalog').scrollIntoView()")
            pg.wait_for_timeout(900)
            snap("2-catalog-list")
            pg.click(".pc-link >> nth=0")
            pg.wait_for_timeout(700)
            snap("3-card")
            pg.evaluate("document.querySelector('#profile .svcs').scrollIntoView({block: 'center'})")
            pg.wait_for_timeout(400)
            snap("4-card-prices")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(400)
            pg.evaluate("document.querySelector('#become').scrollIntoView()")
            pg.wait_for_timeout(1200)
            snap("5-become")
            pg.evaluate("document.querySelector('.earn').scrollIntoView({block: 'center'})")
            pg.wait_for_timeout(900)
            snap("6-earn")
            pg.click("#apply")
            pg.wait_for_timeout(500)
            snap("7-apply-form")
            ctx.close()
    return made


def video(browser, url, outdir, net):
    """Сценарий владельца: поиск → фильтр → карточка → как стать партнёром. Шаги — с паузами, чтобы глаз успевал."""
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "_rec")
    shutil.rmtree(tmp, ignore_errors=True)
    ctx, pg = open_page(browser, url, DESKTOP, "ru", net=net, record=tmp)
    pg.wait_for_timeout(1500)
    pg.evaluate("window.scrollTo({top: document.querySelector('#catalog').offsetTop - 70, behavior: 'smooth'})")
    pg.wait_for_timeout(1400)
    pg.click("#q")
    pg.keyboard.type("Нейрони", delay=110)
    pg.wait_for_timeout(1300)
    pg.fill("#q", "")
    pg.wait_for_timeout(500)
    pg.click(".chip:has(input[value=review])")
    pg.wait_for_timeout(1300)
    pg.select_option("#sort", "rate_up")
    pg.wait_for_timeout(1300)
    pg.click(".chip:has(input[value=''])")
    pg.select_option("#sort", "best")
    pg.wait_for_timeout(900)
    pg.hover(".pc >> nth=0")
    pg.wait_for_timeout(600)
    pg.click(".pc-link >> nth=0")
    pg.wait_for_timeout(1600)
    for y in (380, 760, 1140):
        pg.evaluate("document.querySelector('#profile').scrollTo({top: %d, behavior: 'smooth'})" % y)
        pg.wait_for_timeout(1000)
    pg.go_back()
    pg.wait_for_timeout(900)
    pg.evaluate("window.scrollTo({top: document.querySelector('#become').offsetTop - 70, behavior: 'smooth'})")
    pg.wait_for_timeout(1800)
    pg.evaluate("window.scrollBy({top: 520, behavior: 'smooth'})")
    pg.wait_for_timeout(1000)
    for v in (60, 150, 250, 120):
        pg.evaluate("(v) => { const r = document.querySelector('#calc-rate'); r.value = v; r.dispatchEvent(new Event('input')); }", v)
        pg.wait_for_timeout(500)
    pg.click("#apply")
    pg.wait_for_timeout(1500)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(500)
    path = pg.video.path()
    ctx.close()
    webm = os.path.join(outdir, "partners-demo.webm")
    shutil.move(path, webm)
    shutil.rmtree(tmp, ignore_errors=True)
    out = [webm]
    ff = shutil.which("ffmpeg")
    if ff:
        mp4 = os.path.join(outdir, "partners-demo.mp4")
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-crf", "24", mp4], check=True)
        out.append(mp4)
    return out


def smoke(browser, url, tag, problems):
    """Минимум для обоих адресов: данные из partners.json, три карточки, без 404 и ошибок, без прокрутки вбок."""
    for size in (DESKTOP, PHONE):
        for lang in ("ru", "en"):
            ctx, pg = open_page(browser, url, size, lang)
            src = pg.evaluate("window.AndrePartners.source")
            cards = pg.evaluate("document.querySelectorAll('#grid .pc').length")
            # каждый значок по своему относительному адресу; «?probe» — перехват запросов Playwright не пропускает голый /favicon.ico
            icon = pg.evaluate("Promise.all([...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon]')].map(l => "
                               "fetch(new URL(l.getAttribute('href') + '?probe', location.href)).then(r => r.status))).then(a => Math.max(...a))")
            over = pg.evaluate(OVERFLOW)
            name = "%s %s %dx%d" % (tag, lang, size[0], size[1])
            if src != "fetch":
                problems.append("%s: каталог не из partners.json (%s)" % (name, src))
            if cards != 3:
                problems.append("%s: карточек %d, а не 3" % (name, cards))
            if icon != 200:
                problems.append("%s: значок сайта отдаёт %s" % (name, icon))
            if over["doc"] > 0:
                problems.append("%s: страница уезжает вбок на %dpx (%s)" % (name, over["doc"], over["wide"]))
            if pg.errors or pg.bad:
                problems.append("%s: ошибки %s %s" % (name, pg.errors[:3], pg.bad[:3]))
            print("  ok" if not problems else "  ..", name, src, cards)
            ctx.close()


def main():
    from playwright.sync_api import sync_playwright
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и логотип из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков")
    ap.add_argument("--video", help="папка для ролика сценария")
    a = ap.parse_args()
    base, base2, site_url, sub_url, stop = servers()
    problems = []
    try:
        with sync_playwright() as pw:
            b = launch(pw, a.net)
            print("== andre.technology/partners/ →", site_url)
            smoke(b, site_url, "сайт", problems)
            print("== partners.andre.technology →", sub_url)
            smoke(b, sub_url, "поддомен", problems)
            if a.shots:
                for p in shots(b, sub_url, a.shots, a.net):
                    print("  снимок", p)
            if a.video:
                for p in video(b, sub_url, a.video, a.net):
                    print("  ролик", p)
            b.close()
    finally:
        stop()
    if problems:
        print("\nПРОБЛЕМ: %d\n  %s" % (len(problems), "\n  ".join(problems)))
        sys.exit(1)
    print("\nPARTNERS OK")


if __name__ == "__main__":
    main()
