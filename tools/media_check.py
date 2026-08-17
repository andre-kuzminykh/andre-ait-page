# -*- coding: utf-8 -*-
"""Проверка, что ролики курса РЕАЛЬНО доезжают до страницы.

Зачем стенд. Ролики жили на raw.githubusercontent.com, и однажды у зрителей
они просто перестали показываться: файлы на месте, ветка жива, деплой свежий
— но raw не CDN и режет по лимитам. Залп из 20 запросов давал 5×429 и 1×503,
то есть треть роликов до страницы не доходила. Строковый тест такое не видит:
ссылка-то в HTML есть. Поэтому меряем ФАКТ доставки в браузере.

Что проверяем:
  * каждый медиазапрос вернул 200 или 206 — ни одного 4xx/5xx;
  * ни один ролик не тянется с внешнего хоста (та самая мина);
  * у <video> выставился источник и запрос по нему действительно ушёл.

Чего НЕ проверяем — и почему. Проигрывание. Chromium из playwright собран
без проприетарных кодеков: canPlayType('video/mp4; codecs="avc1.42E01E"')
возвращает пустую строку, значит H.264 он не декодирует ни при каких
условиях. В этом браузере у любого mp4 останется readyState=0 и
error.code=4 (MEDIA_ERR_SRC_NOT_SUPPORTED) — к сайту это отношения не
имеет. Поэтому состояние <video> печатаем справочно и стенд им не валим:
иначе следующий агент пойдёт «починять» несуществующую поломку.

    python3 tools/media_check.py                 → «MEDIA OK»
    python3 tools/media_check.py --slides 5      # + переключения слайдов
"""
import argparse
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_lecture import PORT, serve, vendor_route

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Страницы курса: у каждой свой ролик говорящей головы.
PAGES = ("/automation/1/", "/automation/", "/automation_ru/",
         "/automation/main/", "/automation/roles/", "/automation/skills/",
         "/automation/bootcamp/", "/automation/1/practice/")


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", type=int, default=1,
                    help="сколько слайдов пролистать на /automation/1/ — "
                         "каждый тянет СВОЙ ролик, а сломалось именно на "
                         "череде запросов")
    ap.add_argument("--vendor", default="vendor")
    ap.add_argument("--pages", help="только эти пути, через запятую")
    args = ap.parse_args()

    pages = args.pages.split(",") if args.pages else PAGES
    fails, media, srv = [], [], serve()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=(os.environ.get("CHROMIUM_PATH")
                                 or "/opt/pw-browsers/chromium"),
                args=["--no-sandbox", "--hide-scrollbars",
                      "--autoplay-policy=no-user-gesture-required"])
            ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                      reduced_motion="reduce")
            vend = os.path.join(ROOT, args.vendor)
            if os.path.isdir(vend):
                ctx.route("**/*", vendor_route(args.vendor))
            page = ctx.new_page()

            def on_response(r):
                u = r.url
                if not (u.endswith(".mp4") or "/video_sq/" in u):
                    return
                media.append((r.status, u))
                if r.status not in (200, 206):
                    fails.append("медиа отдалось с кодом %d: %s" % (r.status, u))
                if "raw.githubusercontent.com" in u:
                    fails.append("ролик тянется с raw.githubusercontent — "
                                 "это тот хост, который режет по лимитам: %s" % u)

            page.on("response", on_response)

            for path in pages:
                before = len(media)
                page.goto("http://127.0.0.1:%d%s" % (PORT, path),
                          wait_until="load", timeout=120000)
                page.wait_for_timeout(1500)
                page.evaluate("() => document.querySelectorAll("
                              "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
                if path == "/automation/1/":
                    for _ in range(max(0, args.slides - 1)):
                        page.evaluate("() => window.nextSlide && window.nextSlide()")
                        page.wait_for_timeout(800)
                state = page.evaluate("""() => {
                    const v = document.querySelector('video');
                    if (!v) return {none: true};
                    return {src: v.currentSrc || v.src || '', ready: v.readyState,
                            err: v.error ? v.error.code : 0};
                }""")
                if state.get("none"):
                    print("STEP: %-26s <video> на странице нет" % path)
                    continue
                got = len(media) - before
                src = state.get("src") or ""
                print("STEP: %-26s медиазапросов %d · src=%s%s"
                      % (path, got,
                         urllib.parse.unquote(os.path.basename(src)) or "—",
                         " · readyState=%s (кодеков нет — справочно)" % state["ready"]))
                if not src:
                    fails.append("%s: у <video> не выставился источник" % path)
                elif not got:
                    fails.append("%s: источник выставлен (%s), но запрос за "
                                 "файлом не ушёл" % (path, src))
            ctx.close()
            browser.close()
    finally:
        srv.shutdown()

    bad = [(s, u) for s, u in media if s not in (200, 206)]
    print("STEP: медиаответов всего %d, не 200/206: %d" % (len(media), len(bad)))
    if fails:
        print("MEDIA FAIL:")
        for f in dict.fromkeys(fails):
            print("  · %s" % f)
        return 1
    print("MEDIA OK")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:                       # noqa: BLE001
        print("MEDIA FAIL: %s: %s" % (type(e).__name__, e))
        code = 1
    sys.stdout.flush()
    os._exit(code)
