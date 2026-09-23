# -*- coding: utf-8 -*-
"""PDF лекции 5: слайд на лист, шрифты вшиты, лист = слайд, текст целиком.

    python3 tools/lecture5/pdf.py prod      # /automation/5/    → build/lekciya-5-prod.pdf
    python3 tools/lecture5/pdf.py teoriya   # /automation/5/v2/ → build/lekciya-5-teoriya.pdf

Владелец 2026-09-23: «выдай мне лекцию последнюю в pdf, не забудь шрифты
все и чтобы без полосок и чтобы весь текст был на слайдах».

Печатается АВТОНОМНАЯ страница (tools/lecture5/standalone.py): без шапки,
стрелок и кнопки теста — теми же правками, что HTML для показа с ноутбука.
Отличие одно: Montserrat вшивается СТАТИЧЕСКИМИ начертаниями
(@fontsource/montserrat), потому что вариативный Chromium в PDF не вшивает и
молча печатает системным (LECTURE-GUIDE §13.2, грабля 1). Phosphor —
обычные woff2, вшиваются как есть. Печать — `page.pdf()`: вектор, текст
остаётся текстом и ищется.

Лист объявляет сама страница (`@page` + `prefer_css_page_size`), размер =
форма 1380×864 (§13.2, грабля 4): иначе раскладка печати расходится с
экраном, и по краю листа остаются полосы, куда не дошёл фон слайда.

После сборки — проверки, а не «файл собрался»:
  • листов столько же, сколько слайдов, все одного размера;
  • в файле только Montserrat и Phosphor, ни одного системного шрифта;
  • ни одного символа за краем листа (pypdfium2, каждый символ);
  • обрезанного текста нет: до печати каждого слайда обход DOM — текст не
    выходит ни за слайд, ни за предка с overflow:hidden/clip;
  • полос нет: у каждого листа кромка шириной 3px того же цвета, что
    соседняя полоса внутри (белая/чёрная кайма поймалась бы сразу).
"""
import argparse
import base64
import io
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import standalone                      # noqa: E402

DECKS = {
    "prod": ("automation/5/index.html", "assets/lecture-5.css", "lekciya-5-prod"),
    "teoriya": ("automation/5/v2/index.html", "assets/lecture-5-v2.css", "lekciya-5-teoriya"),
}
FORM = {"width": 1380, "height": 864}
# Полоса прогресса колоды (#progress-container, 6px у нижнего края с
# градиентом по номеру слайда) на листе — та самая «полоска» внизу каждой
# страницы. Прячем, а не вырезаем: на #progress-bar смотрит скрипт колоды.
PAGE_CSS = ('<style id="pdf-page">@page{size:14.375in 9in;margin:0}'
            'html,body{width:%dpx;height:%dpx;}'
            '#progress-container{display:none!important}</style>' % (FORM["width"], FORM["height"]))
STATIC = os.path.join(ROOT, "build", "fonts-static")      # build/ в .gitignore


def static_montserrat_css():
    """@font-face Montserrat статическими начертаниями, с теми же
    unicode-range и весами, что у Google на сайте (vendor/fonts/css2.css)."""
    if not os.path.isdir(STATIC):
        tmp = os.path.join(ROOT, "build", "fontsource")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        subprocess.run(["npm", "pack", "@fontsource/montserrat"], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        tgz = [f for f in os.listdir(tmp) if f.endswith(".tgz")][0]
        subprocess.run(["tar", "xzf", tgz], cwd=tmp, check=True)
        shutil.copytree(os.path.join(tmp, "package", "files"), STATIC)
        shutil.rmtree(tmp, ignore_errors=True)
    src = open(os.path.join(ROOT, "vendor", "fonts", "css2.css"), encoding="utf-8").read()
    out, missing = [], []
    for m in re.finditer(r"/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", src, re.S):
        subset, body = m.group(1), m.group(2)
        w = re.search(r"font-weight:\s*(\d+)", body)
        ur = re.search(r"unicode-range:\s*([^;]+);", body)
        if not w:
            continue
        path = os.path.join(STATIC, "montserrat-%s-%s-normal.woff2" % (subset, w.group(1)))
        if not os.path.isfile(path):
            missing.append(os.path.basename(path))
            continue
        out.append("@font-face{font-family:'Montserrat';font-style:normal;font-display:block;"
                   "font-weight:%s;src:url(data:font/woff2;base64,%s) format('woff2');%s}"
                   % (w.group(1), base64.b64encode(open(path, "rb").read()).decode("ascii"),
                      ("unicode-range:%s;" % ur.group(1).strip()) if ur else ""))
    if missing:
        sys.exit("нет статических начертаний: %s" % ", ".join(missing))
    if not out:
        sys.exit("не собрал ни одного начертания Montserrat")
    return "\n".join(out)


def chromium():
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for name in sorted(os.listdir(base), reverse=True):
        exe = os.path.join(base, name, "chrome-linux", "chrome")
        if name.startswith("chromium-") and os.path.exists(exe):
            return exe
    sys.exit("не найден Chromium в %s" % base)


# Обрезанный текст: текстовый узел, чей прямоугольник выходит за слайд или за
# предка с overflow hidden/clip (там его и срежет). Допуск — 1px на округление.
CLIPPED_JS = """(idx) => {
  const slide = document.querySelectorAll('.slide-container')[idx];
  const S = slide.getBoundingClientRect();
  const W = window.innerWidth, H = window.innerHeight, bad = [];
  const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.replace(/\\s+/g, ' ').trim();
    if (!t) continue;
    const el = n.parentElement, cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    if (el.closest('[aria-hidden="true"], .sr-only, #slide-notes')) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const b of r.getClientRects()) {
      if (b.width < 1 || b.height < 1) continue;
      if (b.left < -1 || b.top < -1 || b.right > W + 1 || b.bottom > H + 1 ||
          b.left < S.left - 1 || b.right > S.right + 1 || b.top < S.top - 1 || b.bottom > S.bottom + 1) {
        bad.push({t: t.slice(0, 50), why: 'за краем'}); break; }
      let p = el, cut = null;
      while (p && p !== slide) {
        const ps = getComputedStyle(p);
        if (/(hidden|clip)/.test(ps.overflowX + ps.overflowY)) {
          const q = p.getBoundingClientRect();
          if (b.left < q.left - 1 || b.right > q.right + 1 || b.top < q.top - 1 || b.bottom > q.bottom + 1) {
            cut = p.className || p.tagName; break; }
        }
        p = p.parentElement;
      }
      if (cut) { bad.push({t: t.slice(0, 50), why: 'срезан: ' + String(cut).slice(0, 40)}); break; }
    }
    if (bad.length > 6) break;
  }
  return bad;
}"""


# Градиентный текст (`background-clip: text`) Chromium переносит в PDF маской
# по прямоугольнику заливки, и у акцентных слов заголовков по краям этого
# прямоугольника остаются волосяные линии: подчёркивание, черта справа или над
# словом (на экране их нет — это только печать). Поэтому перед печатью слайда
# такие слова раскрашиваются ПО БУКВАМ цветом того же градиента в точке буквы:
# текст остаётся векторным и ищется, маски нет — линий нет. Ширина слова
# сверяется до и после: разойдись она — подгонка слайда была бы уже неверна.
GRADIENT_TEXT_JS = """(idx) => {
  const slide = document.querySelectorAll('.slide-container')[idx];
  const stopsOf = (bg) => {
    const m = [...bg.matchAll(/rgba?\\(([^)]+)\\)\\s*([\\d.]+%)?/g)];
    return m.map((x, i, a) => ({c: x[1].split(',').map(Number),
      p: x[2] ? parseFloat(x[2]) / 100 : (a.length > 1 ? i / (a.length - 1) : 0)}));
  };
  const colorAt = (st, t) => {
    t = Math.max(0, Math.min(1, t));
    for (let i = 0; i < st.length - 1; i++) {
      const a = st[i], b = st[i + 1];
      if (t <= b.p || i === st.length - 2) {
        const k = b.p > a.p ? Math.max(0, Math.min(1, (t - a.p) / (b.p - a.p))) : 0;
        const c = [0, 1, 2].map(j => Math.round(a.c[j] + (b.c[j] - a.c[j]) * k));
        const al = (a.c[3] == null ? 1 : a.c[3]) + ((b.c[3] == null ? 1 : b.c[3]) - (a.c[3] == null ? 1 : a.c[3])) * k;
        return 'rgba(' + c.join(',') + ',' + al.toFixed(3) + ')';
      }
    }
    return 'rgb(' + st[0].c.slice(0, 3).join(',') + ')';
  };
  let done = 0, drift = [];
  slide.querySelectorAll('*').forEach(el => {
    if (el.dataset.pdfGrad) return;
    const cs = getComputedStyle(el);
    if ((cs.webkitBackgroundClip || cs.backgroundClip) !== 'text' || !/gradient/.test(cs.backgroundImage)) return;
    const st = stopsOf(cs.backgroundImage);
    if (st.length < 2) return;
    const box = el.getBoundingClientRect();
    if (box.width < 1) return;
    const plan = [];
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) {
      const chars = Array.from(n.textContent), cols = [];
      let off = 0;
      for (const ch of chars) {
        const r = document.createRange(); r.setStart(n, off); r.setEnd(n, off + ch.length);
        const b = r.getBoundingClientRect();
        cols.push(/\\s/.test(ch) ? null : colorAt(st, (b.left + b.width / 2 - box.left) / box.width));
        off += ch.length;
      }
      plan.push([n, chars, cols]);
    }
    for (const [node, chars, cols] of plan) {
      const frag = document.createDocumentFragment();
      chars.forEach((ch, i) => {
        if (!cols[i]) { frag.appendChild(document.createTextNode(ch)); return; }
        const sp = document.createElement('span');
        sp.textContent = ch;
        sp.style.cssText = 'color:' + cols[i] + ';-webkit-text-fill-color:' + cols[i];
        frag.appendChild(sp);
      });
      node.parentNode.replaceChild(frag, node);
    }
    el.style.setProperty('background', 'none', 'important');
    el.style.setProperty('-webkit-background-clip', 'border-box', 'important');
    el.style.setProperty('background-clip', 'border-box', 'important');
    el.style.setProperty('-webkit-text-fill-color', 'currentcolor', 'important');
    el.dataset.pdfGrad = '1';
    const after = el.getBoundingClientRect();
    if (Math.abs(after.width - box.width) > 0.5 || Math.abs(after.height - box.height) > 0.5)
      drift.push((el.textContent || '').slice(0, 30) + ': ' + box.width.toFixed(1) + '→' + after.width.toFixed(1));
    done++;
  });
  return {done, drift};
}"""


def build(deck, theme):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter

    page_rel, css_rel, name = DECKS[deck]
    html, weights = standalone.build_html(os.path.join(ROOT, page_rel), os.path.join(ROOT, css_rel),
                                          font_css=static_montserrat_css())
    html = html.replace("</head>", PAGE_CSS + "</head>", 1)
    printable = os.path.join(ROOT, "build", name + "-print.html")
    out = os.path.join(ROOT, "build", name + ".pdf")
    os.makedirs(os.path.dirname(printable), exist_ok=True)
    io.open(printable, "w", encoding="utf-8").write(html)

    writer, clipped = PdfWriter(), {}
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        ctx = br.new_context(viewport=dict(FORM), device_scale_factor=1, reduced_motion="reduce")
        # Сеть не нужна: всё внутри файла. Любой внешний запрос — ошибка сборки.
        ext = []
        ctx.route("**/*", lambda r: (ext.append(r.request.url), r.abort())
                  if not r.request.url.startswith(("file:", "data:")) else r.continue_())
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://%s?theme=%s" % (printable, theme), wait_until="load", timeout=180000)
        pg.wait_for_timeout(3000)
        pg.emulate_media(media="screen")
        pg.evaluate("""async () => {
          await Promise.all([...document.fonts].map(f => f.load().catch(() => {})));
          await document.fonts.ready; }""")
        # полный пересчёт подгонки уже со статическим шрифтом — только сменой формы
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.wait_for_timeout(1500)
        pg.set_viewport_size(dict(FORM))
        pg.wait_for_timeout(2500)
        fam = pg.evaluate("() => getComputedStyle(document.querySelector('.slide-container h1, "
                          ".slide-container h2, .slide-container p')).fontFamily")
        ok = pg.evaluate("() => document.fonts.check('700 20px Montserrat')")
        if "Montserrat" not in fam or not ok:
            sys.exit("колода не на Montserrat: %s" % fam)
        total = pg.evaluate("() => document.querySelectorAll('.slide-container').length")
        grad, drift = 0, []
        for i in range(total):
            pg.wait_for_timeout(450)
            g = pg.evaluate(GRADIENT_TEXT_JS, i)
            grad += g["done"]
            drift += ["слайд %d, %s" % (i + 1, d) for d in g["drift"]]
            bad = pg.evaluate(CLIPPED_JS, i)
            if bad:
                clipped[i + 1] = bad
            writer.append(PdfReader(io.BytesIO(pg.pdf(print_background=True,
                                                      prefer_css_page_size=True))))
            if i < total - 1:
                pg.evaluate("() => window.nextSlide()")
        ctx.close()
        br.close()
    with open(out, "wb") as f:
        writer.write(f)
    print("   градиентных слов раскрашено по буквам: %d" % grad)
    if drift:
        print("   ВНИМАНИЕ, ширина слова изменилась: %s" % drift[:4])
    if errs:
        print("   ОШИБКИ СТРАНИЦЫ: %s" % errs[:3])
    if ext:
        print("   ВНЕШНИЕ ЗАПРОСЫ (заблокированы): %s" % ext[:3])
    return out, total, clipped, bool(errs or ext or drift)


def verify(path, total):
    """Листы, шрифты, символы за краем, полосы по кромке."""
    import pypdfium2 as pdfium
    from pypdf import PdfReader

    problems = []
    rd = PdfReader(path)
    sizes = {(round(float(p.mediabox.width), 1), round(float(p.mediabox.height), 1)) for p in rd.pages}
    if len(rd.pages) != total:
        problems.append("листов %d, слайдов %d" % (len(rd.pages), total))
    # 14.375×9 дюйма = 1035×648 пт; Chromium пишет ширину 1035.1 — округление
    if len(sizes) != 1 or any(abs(w - 1035) > 0.5 or abs(h - 648) > 0.5 for w, h in sizes):
        problems.append("размеры листов: %s" % sorted(sizes))
    fonts = set()
    for p in rd.pages:
        res = p.get("/Resources") or {}
        for f in (res.get("/Font") or {}).values():
            fonts.add(str(f.get_object().get("/BaseFont", "")).split("+")[-1])
    foreign = sorted(f for f in fonts if not re.match(r"(Montserrat|Phosphor)", f.lstrip("/")))
    if foreign:
        problems.append("чужие шрифты: %s" % foreign)

    doc = pdfium.PdfDocument(path)
    edge_bad = []
    for i in range(len(doc)):
        page = doc[i]
        w, h = page.get_size()
        tp = page.get_textpage()
        for c in range(tp.count_chars()):
            l, b, r, t = tp.get_charbox(c)
            if r - l <= 0 or t - b <= 0:
                continue
            if l < -0.5 or b < -0.5 or r > w + 0.5 or t > h + 0.5:
                problems.append("лист %d: символ за краем" % (i + 1))
                break
        img = page.render(scale=1).to_pil().convert("RGB")
        W, H = img.size
        px = img.load()

        def band(xs, ys):
            vals = [px[x, y] for x in xs for y in ys]
            return tuple(sum(v[k] for v in vals) / len(vals) for k in range(3))

        # кромка 3px против соседней полосы 4–10px внутри — по четырём сторонам
        mid_x, mid_y = range(W // 4, 3 * W // 4, 7), range(H // 4, 3 * H // 4, 7)
        sides = {"верх": (band(mid_x, range(0, 3)), band(mid_x, range(4, 10))),
                 "низ": (band(mid_x, range(H - 3, H)), band(mid_x, range(H - 10, H - 4))),
                 "лево": (band(range(0, 3), mid_y), band(range(4, 10), mid_y)),
                 "право": (band(range(W - 3, W), mid_y), band(range(W - 10, W - 4), mid_y))}
        for side, (e, inner) in sides.items():
            if max(abs(e[k] - inner[k]) for k in range(3)) > 24:
                edge_bad.append("лист %d, %s: кромка %s против %s" % (
                    i + 1, side, tuple(int(v) for v in e), tuple(int(v) for v in inner)))
    return problems, sorted(fonts), edge_bad


def contact_sheet(path, out_png, cols=6, scale=0.18):
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw

    doc = pdfium.PdfDocument(path)
    thumbs = [doc[i].render(scale=scale * 96 / 72).to_pil().convert("RGB") for i in range(len(doc))]
    tw, th = thumbs[0].size
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 22) + 8), (60, 60, 60))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(thumbs):
        x, y = 8 + (k % cols) * (tw + 8), 8 + (k // cols) * (th + 22)
        sheet.paste(im, (x, y + 14))
        d.text((x, y), str(k + 1), fill=(255, 255, 255))
    sheet.save(out_png)


def main():
    ap = argparse.ArgumentParser(description="PDF лекции 5, слайд на лист.")
    ap.add_argument("deck", choices=sorted(DECKS))
    ap.add_argument("--theme", choices=["light", "dark"], default="dark")
    ap.add_argument("--sheet", help="куда положить обзорный лист PNG")
    a = ap.parse_args()
    out, total, clipped, page_err = build(a.deck, a.theme)
    problems, fonts, edges = verify(out, total)
    print("собран %s: %d листов, %.1f МБ" % (out, total, os.path.getsize(out) / 1048576.0))
    print("   шрифты: %s" % ", ".join(fonts))
    for n, bad in sorted(clipped.items()):
        print("   слайд %d — текст не целиком: %s" % (n, bad[:3]))
    for p in problems + edges:
        print("   ПРОБЛЕМА: " + p)
    if a.sheet:
        contact_sheet(out, a.sheet)
    return 1 if (problems or edges or clipped or page_err) else 0


if __name__ == "__main__":
    sys.exit(main())
