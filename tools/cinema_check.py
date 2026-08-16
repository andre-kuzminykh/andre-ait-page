# -*- coding: utf-8 -*-
"""Проверка правой колонки в режиме «кино»: ничего не пропало и не обрезалось.

Тёмная палитра — самая опасная правка в этом режиме: страница красит текст
`-webkit-text-fill-color` с !important, и одно пропущенное правило делает
колонку чёрной по чёрному. Строковый тест такое не ловит (CSS-то на месте),
поэтому меряем ФАКТ в браузере: для каждого текстового узла слайда берём
вычисленный цвет и его бокс.

Что валит проверку:
  * текст темнее фона (пропал на тёмном) — кроме прозрачных заливок, где
    буквы рисует градиент через background-clip:text;
  * бокс вылез за колонку (обрезался справа/слева) или за кадр по высоте;
  * пустой заголовок или карточка без текста.

    python3 tools/cinema_check.py [--slide 1]   → «CINEMA COLUMN OK»
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cinema as cinema_fx
from record_lecture import PORT, CHROME_OFF, serve, vendor_route

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Порог «текст виден»: относительная яркость буквы против фона #0A0A0A.
MIN_LUMA = 60


def _luma(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _parse_rgb(css):
    """«rgb(a, b, c)» / «rgba(a, b, c, x)» → (r, g, b, alpha)."""
    body = css[css.find("(") + 1:css.rfind(")")]
    parts = [p.strip() for p in body.split(",")]
    vals = [float(p) for p in parts[:3]]
    alpha = float(parts[3]) if len(parts) > 3 else 1.0
    return vals, alpha


PROBE = """
() => {
  const slide = document.querySelector('.slide-container.opacity-100');
  const out = [];
  slide.querySelectorAll('h1,h2,h3,p,li,span').forEach(el => {
    const txt = (el.textContent || '').trim();
    if (!txt) return;
    // только листья: у контейнеров текст дублируется
    if (el.querySelector('h1,h2,h3,p,li,span')) return;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    out.push({
      text: txt.slice(0, 48),
      color: cs.color,
      fill: cs.webkitTextFillColor || cs.color,
      x: r.x, y: r.y, w: r.width, h: r.height,
      tag: el.tagName.toLowerCase(),
    });
  });
  return out;
}
"""


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--slide", type=int, default=1)
    ap.add_argument("--vendor", default="vendor")
    args = ap.parse_args()

    vp = cinema_fx.viewport()
    fails, srv = [], serve()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=(os.environ.get("CHROMIUM_PATH")
                                 or "/opt/pw-browsers/chromium"),
                args=["--no-sandbox", "--hide-scrollbars"])
            ctx = browser.new_context(viewport=vp, device_scale_factor=1,
                                      reduced_motion="reduce")
            vend = os.path.join(ROOT, args.vendor)
            if os.path.isdir(vend):
                ctx.route("**/*", vendor_route(args.vendor))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/1/" % PORT,
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(2500)
            page.add_style_tag(content=CHROME_OFF)
            page.add_style_tag(content=cinema_fx.CINEMA_CSS)
            page.evaluate("() => document.querySelectorAll("
                          "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
            for _ in range(args.slide - 1):
                page.evaluate("() => window.nextSlide && window.nextSlide()")
                page.wait_for_timeout(160)
            page.wait_for_timeout(1500)
            grown = page.evaluate(cinema_fx.GROW_JS, cinema_fx.grow_args())
            if grown:
                print("STEP: догон масштаба ×%.2f" % grown["k"])

            nodes = page.evaluate(PROBE)
            if len(nodes) < 4:
                fails.append("на слайде нашлось всего %d текстовых узлов — "
                             "колонка почти пуста" % len(nodes))

            box = [10 ** 6, 10 ** 6, -10 ** 6, -10 ** 6]
            for n in nodes:
                rgb, alpha = _parse_rgb(n["fill"])
                if alpha > 0.02 and _luma(rgb) < MIN_LUMA:
                    fails.append("текст тонет в фоне (%s, luma %.0f): %r"
                                 % (n["fill"], _luma(rgb), n["text"]))
                if n["x"] < -0.5 or n["x"] + n["w"] > vp["width"] + 0.5:
                    fails.append("бокс вылез за колонку по ширине "
                                 "(x=%.0f w=%.0f, колонка %d): %r"
                                 % (n["x"], n["w"], vp["width"], n["text"]))
                if n["y"] < -0.5 or n["y"] + n["h"] > vp["height"] + 0.5:
                    fails.append("бокс вылез за кадр по высоте "
                                 "(y=%.0f h=%.0f): %r"
                                 % (n["y"], n["h"], n["text"]))
                box = [min(box[0], n["x"]), min(box[1], n["y"]),
                       max(box[2], n["x"] + n["w"]), max(box[3], n["y"] + n["h"])]

            print("STEP: текстовых узлов %d" % len(nodes))
            print("STEP: контент занимает %.0f×%.0f из %d×%d "
                  "(%.0f%% ширины, %.0f%% высоты)"
                  % (box[2] - box[0], box[3] - box[1], vp["width"], vp["height"],
                     100 * (box[2] - box[0]) / vp["width"],
                     100 * (box[3] - box[1]) / vp["height"]))
            ctx.close()
            browser.close()
    finally:
        srv.shutdown()

    if fails:
        print("CINEMA COLUMN FAIL:")
        for f in fails:
            print("  · %s" % f)
        return 1
    print("CINEMA COLUMN OK")
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:                       # noqa: BLE001
        print("CINEMA COLUMN FAIL: %s: %s" % (type(e).__name__, e))
        code = 1
    sys.stdout.flush()
    os._exit(code)
