# -*- coding: utf-8 -*-
"""Проверка страницы практики лекции 3 в Chromium: 1440×900 и 390×844, обе темы.
Каждый граф отрисован (есть svg, нет строки ошибки), нет ошибок JS, нет прокрутки вбок.
Скриншоты — в build/l3/practice-shots/."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import start, chromium, route_ctx
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SHOTS = os.path.join(ROOT, "build/l3/practice-shots")
os.makedirs(SHOTS, exist_ok=True)
KEYS = ["consult", "hr", "marketing", "callcenter", "design", "software"]
SIZES = [("desk", 1440, 900), ("mob", 390, 844)]  # 1024 и 360 — в review.py
if len(sys.argv) > 1:
    SIZES = [s for s in SIZES if s[0] in sys.argv[1:]] or SIZES
FULL = "--full" in sys.argv

srv, port = start()
problems = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
    for theme in ("dark", "light"):
        for tag, w, hgt in SIZES:
            ctx = b.new_context(viewport={"width": w, "height": hgt},
                                device_scale_factor=2 if tag == "mob" else 1,
                                is_mobile=(tag == "mob"), has_touch=(tag == "mob"))
            route_ctx(ctx)
            pg = ctx.new_page()
            errs, net404 = [], []
            def on_console(m, errs=errs, net404=net404):
                if m.type == "error":
                    if "Failed to load resource" in m.text:
                        net404.append(m.text)
                    else:
                        errs.append(m.text)
            pg.on("console", on_console)
            pg.on("pageerror", lambda e, errs=errs: errs.append("PAGEERROR " + str(e)))
            pg.on("response", lambda r, net404=net404: net404.append("%d %s" % (r.status, r.url)) if r.status >= 400 else None)
            pg.goto("http://127.0.0.1:%d/automation/3/practice/?theme=%s" % (port, theme), wait_until="load")
            pg.wait_for_function("() => document.querySelector('#v-layer svg') || !document.getElementById('v-err').hidden", timeout=20000)
            pg.wait_for_timeout(600)
            # Снимки — про раскладку и графы, а не про появление: показываем
            # все блоки сразу (класс rv прячет то, до чего не дошла прокрутка).
            pg.evaluate("() => document.documentElement.classList.remove('rv')")
            for key in KEYS:
                pg.click('.v-tab[data-key="%s"]' % key)
                pg.wait_for_function("(k) => { const s = document.querySelector('#v-layer svg'); return (s && document.getElementById('v-input').value.length && !document.querySelector('#info-' + k).hidden) || !document.getElementById('v-err').hidden; }", arg=key, timeout=20000)
                pg.wait_for_timeout(700)
                st = pg.evaluate("""(k) => {
                  const e = document.getElementById('v-err');
                  const svg = document.querySelector('#v-layer svg');
                  const vb = svg && svg.viewBox.baseVal;
                  // срезанные подписи: текст узла шире своего foreignObject
                  let clipped = [];
                  document.querySelectorAll('#v-layer foreignObject').forEach(fo => {
                    const d = fo.firstElementChild; if(!d) return;
                    if (d.scrollWidth > fo.width.baseVal.value + 1.5) clipped.push(d.textContent.slice(0,40));
                  });
                  return { err: e.hidden ? '' : document.getElementById('v-err-text').textContent,
                           svg: !!svg, w: vb ? Math.round(vb.width) : 0, h: vb ? Math.round(vb.height) : 0,
                           level: document.getElementById('v-level').textContent,
                           nodes: document.querySelectorAll('#v-layer .node').length,
                           clipped,
                           sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
                           bsw: document.body.scrollWidth };
                }""", key)
                line = "%s %s %-10s svg=%s nodes=%d nat=%dx%d zoom=%s scroll=%d/%d" % (
                    theme, tag, key, st["svg"], st["nodes"], st["w"], st["h"], st["level"], st["sw"], st["cw"])
                print(line)
                if st["err"] or not st["svg"]:
                    problems.append("%s: ошибка схемы: %s" % (line, st["err"][:200]))
                if st["clipped"]:
                    problems.append("%s: срезаны подписи %s" % (line, st["clipped"]))
                if st["sw"] > st["cw"] or st["bsw"] > st["cw"]:
                    problems.append("%s: прокрутка вбок %d > %d" % (line, max(st["sw"], st["bsw"]), st["cw"]))
                if FULL or key in ("consult", "software"):
                    el = pg.query_selector("#viewer")
                    el.scroll_into_view_if_needed()
                    pg.evaluate("() => document.getElementById('viewer').scrollIntoView({block:'start', behavior:'instant'})")
                    pg.wait_for_timeout(300)
                    pg.screenshot(path=os.path.join(SHOTS, "%s-%s-viewer-%s.png" % (tag, theme, key)))
                    info = pg.query_selector("#info-" + key)
                    info.screenshot(path=os.path.join(SHOTS, "%s-%s-card-%s.png" % (tag, theme, key)))
            # вся страница
            pg.click('.v-tab[data-key="consult"]')
            pg.wait_for_timeout(900)
            pg.evaluate("() => window.scrollTo(0,0)")
            pg.screenshot(path=os.path.join(SHOTS, "%s-%s-full.png" % (tag, theme)), full_page=True)
            # переполнение отдельных элементов за правый край
            over = pg.evaluate("""() => {
              const W = document.documentElement.clientWidth, out = [];
              document.querySelectorAll('main *').forEach(el => {
                if (el.closest('#v-stage') || el.closest('.v-tabs') || el.closest('pre') || el.closest('textarea')) return;
                const r = el.getBoundingClientRect();
                if (r.width && (r.right > W + 0.5 || r.left < -0.5)) out.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
              });
              return out.slice(0, 15);
            }""")
            if over:
                problems.append("%s %s: элементы за краем: %s" % (theme, tag, over))
            bub = pg.evaluate("() => [getComputedStyle(document.getElementById('bubble')).display]")
            print("   bubble:", bub, "| console errors:", errs, "| 4xx:", len(net404))
            if errs:
                problems.append("%s %s: ошибки JS: %s" % (theme, tag, errs))
            for n in net404:
                if "/assets/video_l3/" not in n and "Failed to load" not in n:
                    problems.append("%s %s: сеть: %s" % (theme, tag, n))
            ctx.close()
    b.close()
srv.shutdown()
print("\nПРОБЛЕМ: %d" % len(problems))
for pr in problems:
    print(" -", pr)
