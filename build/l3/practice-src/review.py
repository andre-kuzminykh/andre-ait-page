# -*- coding: utf-8 -*-
"""Приёмка страницы практики лекции 3: 4 размера × 2 темы.
Метрики: ошибки JS, 4xx (кроме ролика), прокрутка вбок, мелкий текст,
кегль узлов графа на экране (15px × масштаб), срезанные подписи,
наложения текстовых блоков. Снимки экрана по высоте — в practice-shots/rv-*.
Запуск: python3 review.py [--shots] [--page 2|3] [размеры...]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import start, chromium, route_ctx
from playwright.sync_api import sync_playwright

ROOT = "/home/user/andre-ait-page"
SHOTS = os.path.join(ROOT, "build/l3/practice-shots")
KEYS = ["consult", "hr", "marketing", "callcenter", "design", "software"]
# 1920: у body zoom 1.3 (большие мониторы) — на нём ломалась мерка подписей mermaid
SIZES = [("1920", 1920, 1080), ("1440", 1440, 900), ("1024", 1024, 768), ("390", 390, 844), ("360", 360, 740)]
args = sys.argv[1:]
SHOT = "--shots" in args
PAGE = "3"
if "--page" in args:
    PAGE = args[args.index("--page") + 1]
sel = [a for a in args if a.isdigit() and a in {s[0] for s in SIZES}]
if sel:
    SIZES = [s for s in SIZES if s[0] in sel]
THEMES = ["dark", "light"]
if "--dark" in args: THEMES = ["dark"]
if "--light" in args: THEMES = ["light"]

METRICS = r"""() => {
  const W = document.documentElement.clientWidth, out = {};
  out.sw = document.documentElement.scrollWidth; out.cw = W; out.bsw = document.body.scrollWidth;
  // за краем
  const over = [];
  document.querySelectorAll('main *').forEach(el => {
    if (el.closest('#v-stage') || el.closest('.v-tabs') || el.closest('pre') || el.closest('textarea') || el.closest('[hidden]')) return;
    const r = el.getBoundingClientRect();
    if (r.width && (r.right > W + 0.5 || r.left < -0.5)) over.push(el.tagName + '.' + el.className + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  });
  out.over = over.slice(0, 12);
  // мелкий текст (без кода и окна схемы)
  const small = {};
  const walker = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
  let n; const leaves = [];
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue;
    const el = n.parentElement; if (!el || el.closest('#v-stage') || el.closest('[hidden]') || el.closest('#mmd-sources') || el.closest('details:not([open])')) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 11) { const k = el.tagName + '.' + el.className + ' ' + fs.toFixed(1); small[k] = (small[k] || 0) + 1; }
    leaves.push(el);
  }
  out.small = small;
  // наложения: текстовые листья разных блоков, пересекающиеся по площади
  const uniq = [...new Set(leaves)].filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; });
  const rects = uniq.map(el => { const range = document.createRange(); range.selectNodeContents(el); return [el, [...range.getClientRects()]]; });
  const hits = [];
  for (let i = 0; i < rects.length && hits.length < 10; i++) {
    for (let j = i + 1; j < rects.length && hits.length < 10; j++) {
      const [a, ra] = rects[i], [b, rb] = rects[j];
      if (a.contains(b) || b.contains(a)) continue;
      for (const x of ra) for (const y of rb) {
        const ix = Math.min(x.right, y.right) - Math.max(x.left, y.left);
        const iy = Math.min(x.bottom, y.bottom) - Math.max(x.top, y.top);
        if (ix > 2 && iy > 2) { hits.push(a.textContent.trim().slice(0, 30) + ' ⟂ ' + b.textContent.trim().slice(0, 30)); break; }
      }
    }
  }
  out.overlap = hits;
  out.H = document.documentElement.scrollHeight;
  return out;
}"""

GRAPH = r"""(k) => {
  const e = document.getElementById('v-err');
  const svg = document.querySelector('#v-layer svg');
  const vb = svg && svg.viewBox.baseVal;
  const lvl = parseFloat(document.getElementById('v-level').textContent) / 100;
  let clipped = [], minFs = 99;
  document.querySelectorAll('#v-layer foreignObject').forEach(fo => {
    const d = fo.firstElementChild; if (!d) return;
    if (d.scrollWidth > fo.width.baseVal.value + 1.5 || d.scrollHeight > fo.height.baseVal.value + 1.5) clipped.push(d.textContent.slice(0, 40));
    // блок подписи не совпал с текстом (мерка под zoom страницы) или текст
    // вылез из своего блока — подпись съехала или срезана
    else if (Math.abs(d.offsetWidth - fo.width.baseVal.value) > 1.5 || d.scrollWidth > d.offsetWidth + 1) clipped.push('≠ ' + d.textContent.slice(0, 36));
    d.querySelectorAll('*').forEach(x => { const r = x.getBoundingClientRect(); if (r.height) {} });
  });
  // реальный кегль подписи узла на экране
  let opFs = 99;
  document.querySelectorAll('#v-layer .node .nodeLabel').forEach(x => {
    const fs = parseFloat(getComputedStyle(x).fontSize); if (fs) minFs = Math.min(minFs, fs);
  });
  document.querySelectorAll('#v-layer .node .nodeLabel span[style]').forEach(x => {
    const fs = parseFloat(getComputedStyle(x).fontSize); if (fs) opFs = Math.min(opFs, fs);
  });
  const st = document.getElementById('v-stage');
  return { err: e.hidden ? '' : document.getElementById('v-err-text').textContent.slice(0, 160),
           svg: !!svg, w: vb ? Math.round(vb.width) : 0, h: vb ? Math.round(vb.height) : 0,
           k: lvl, nodeFs: minFs, screenFs: +(minFs * lvl).toFixed(1), opScreen: +(opFs * lvl).toFixed(1),
           nodes: document.querySelectorAll('#v-layer .node').length, clipped,
           stage: [st.clientWidth, st.clientHeight, st.scrollWidth, st.scrollHeight] };
}"""

srv, port = start()
problems = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
    for theme in THEMES:
        for tag, w, hgt in SIZES:
            mob = w < 760
            ctx = b.new_context(viewport={"width": w, "height": hgt}, device_scale_factor=2 if mob else 1,
                                is_mobile=mob, has_touch=mob)
            route_ctx(ctx)
            pg = ctx.new_page()
            errs, net = [], []
            pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
            pg.on("pageerror", lambda e, errs=errs: errs.append("PAGEERROR " + str(e)))
            pg.on("response", lambda r, net=net: net.append("%d %s" % (r.status, r.url)) if r.status >= 400 else None)
            pg.goto("http://127.0.0.1:%d/automation/%s/practice/?theme=%s" % (port, PAGE, theme), wait_until="load")
            pg.wait_for_function("() => document.querySelector('#v-layer svg') || !document.getElementById('v-err').hidden", timeout=20000)
            pg.wait_for_timeout(1200)
            label = "%s %s" % (theme, tag)
            if PAGE == "3":
                for key in KEYS:
                    pg.click('.v-tab[data-key="%s"]' % key)
                    pg.wait_for_function("(k) => { const s = document.querySelector('#v-layer svg'); return (s && !document.querySelector('#info-' + k).hidden) || !document.getElementById('v-err').hidden; }", arg=key, timeout=20000)
                    pg.wait_for_timeout(600)
                    g = pg.evaluate(GRAPH, key)
                    print("%s %-10s nat=%dx%d k=%.2f nodeFs=%s screen=%spx op=%spx stage=%s clipped=%s %s" % (label, key, g["w"], g["h"], g["k"], g["nodeFs"], g["screenFs"], g["opScreen"], g["stage"], len(g["clipped"]), g["err"]))
                    if g["err"] or not g["svg"]:
                        problems.append("%s %s: ошибка схемы %s" % (label, key, g["err"]))
                    if g["clipped"]:
                        problems.append("%s %s: срезаны %s" % (label, key, g["clipped"]))
                    if g["screenFs"] < 11.5 or g["opScreen"] < 10.5:
                        problems.append("%s %s: узлы мелко %spx / %spx" % (label, key, g["screenFs"], g["opScreen"]))
                pg.click('.v-tab[data-key="consult"]'); pg.wait_for_timeout(900)
            # промты раскрыты: кнопки копирования над кодом тоже проверяются на наложение
            pg.evaluate("() => document.querySelectorAll('details.src').forEach(d => d.open = true)")
            pg.wait_for_timeout(200)
            m = pg.evaluate(METRICS)
            pg.evaluate("() => document.querySelectorAll('details.src').forEach(d => d.open = false)")
            print("   H=%d scroll=%d/%d over=%s small=%s overlap=%s" % (m["H"], m["sw"], m["cw"], m["over"], m["small"], m["overlap"]))
            if m["sw"] > m["cw"] or m["bsw"] > m["cw"]: problems.append("%s: прокрутка вбок" % label)
            if m["over"]: problems.append("%s: за краем %s" % (label, m["over"]))
            if m["overlap"]: problems.append("%s: наложения %s" % (label, m["overlap"]))
            bad = [n for n in net if "/assets/video_l3/" not in n]
            if errs: problems.append("%s: JS %s" % (label, errs))
            if bad: problems.append("%s: сеть %s" % (label, bad))
            if SHOT:
                pg.evaluate("() => window.scrollTo(0,0)"); pg.wait_for_timeout(300)
                H = m["H"]; step = int(hgt * 0.92); y = 0; i = 0
                while y < H and i < 40:
                    pg.evaluate("(y) => window.scrollTo({top: y, behavior: 'instant'})", y); pg.wait_for_timeout(1000)
                    pg.screenshot(path=os.path.join(SHOTS, "rv%s-%s-%s-%02d.png" % (PAGE, tag, theme, i)))
                    y += step; i += 1
            ctx.close()
    b.close()
srv.shutdown()
print("\nПРОБЛЕМ: %d" % len(problems))
for x in problems:
    print(" -", x)
