# -*- coding: utf-8 -*-
"""Замер слайдов ЛЮБОЙ лекции в обеих формах + кадры — как build/l3/probe.py.

    python3 tools/deck_probe.py 1 7            # лекция 1, слайд 7
    python3 tools/deck_probe.py 2 7 8 9        # лекция 2, несколько слайдов
    python3 tools/deck_probe.py 1 7 --light    # ещё кадры светлой темы
    python3 tools/deck_probe.py 1 7 --json     # машинный вывод

Слайды берутся из build/l<N>/out (их режет tools/deck_split.py extract N):
меряемые — целиком, остальные — заглушками. Каркас — сама колода
automation/<N>/index.html (её голова, стили и скрипты), CSS — свой, собранный
tailwind из меряемых слайдов и колоды, поэтому новый класс сразу существует
для браузера, а параллельные прогоны не мешают друг другу.

Метрики и нормы те же, что у лекции 3 (см. build/l3/probe.py): масштаб ПК
≥ 0.95, кегль телефона ≥ 10px, заступы, разрывы слов, наложения, «текст шире
карточки», ужатый подгонщиком кегль, висячие слова, блоки в 3+ строки.
Кадры: build/l<N>/frames/slide-NN-pc.png и -mob.png — их надо СМОТРЕТЬ.
Запускать из корня репозитория.
"""
import io, json, os, re, shutil, socket, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "build", "l3"))     # css.build — tailwind один раз
N = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
LN = os.path.join(ROOT, "build", "l%s" % N)
import record_lecture as rl        # noqa: E402
import lecture_check as lc         # noqa: E402

STUB = ('    <div class="slide-container px-3 sm:px-6 md:px-12 opacity-0 pointer-events-none '
        'translate-y-8" id="slide-%d">\n        <div class="content-z max-w-5xl w-full">\n'
        '            <h2 class="text-xl sm:text-3xl md:text-5xl font-black mb-3 md:mb-5 '
        'text-center text-black">Заглушка <span class="text-solar">%d</span></h2>\n'
        '            <p class="text-center text-black/60 mb-4 md:mb-7 text-[10px] md:text-lg '
        'font-medium max-w-3xl mx-auto">Слайд ещё верстается</p>\n        </div>\n    </div>\n')

AVAIL = {"pc": (1380 - 64, 864 - 128 - 88), "mob": (376 - 16, 844 - 88 - 72)}

JS_PROBE = lc.JS_SCALE + r"""
(() => {
  const slide = document.querySelector('.slide-container.opacity-100');
  if (!slide) return null;
  const cz = slide.querySelector('.content-z');
  const czr = cz.getBoundingClientRect();
  // видимая коробка содержимого — объединение прямоугольников видимых потомков
  let L = 1e9, T = 1e9, R = -1e9, B = -1e9;
  for (const el of cz.querySelectorAll('*')) {
    if (!seen(el)) continue;
    const st = getComputedStyle(el);
    const painted = ownText(el) || el.tagName === 'I' ||
      (st.backgroundColor && st.backgroundColor !== 'rgba(0, 0, 0, 0)') ||
      parseFloat(st.borderTopWidth) > 0;
    if (!painted) continue;
    const r = el.getBoundingClientRect();
    L = Math.min(L, r.left); T = Math.min(T, r.top); R = Math.max(R, r.right); B = Math.max(B, r.bottom);
  }
  // тексты: строки и висячие слова
  const texts = [];
  const leafs = [];
  const blocks = cz.querySelectorAll('h1,h2,h3,h4,p,li,span,button');
  for (const el of blocks) {
    if (!seen(el)) continue;
    const st = getComputedStyle(el);
    // берём «текстовый блок»: у него есть собственный текст или он строчный
    // контейнер без блочных детей
    const hasBlockKid = [...el.children].some(c => {
      const d = getComputedStyle(c).display; return d === 'block' || d === 'flex' || d === 'grid';
    });
    if (hasBlockKid) continue;
    if (el.tagName === 'SPAN' && st.display === 'inline' && el.parentElement &&
        el.parentElement.closest('h1,h2,h3,h4,p,li,button')) continue;
    const words = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const rg = document.createRange();
    let n;
    while ((n = walker.nextNode())) {
      const s = n.nodeValue;
      const re = /[^\s­]+(?:­[^\s­]+)*/g;
      let m;
      while ((m = re.exec(s))) {
        rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
        const rects = [...rg.getClientRects()].filter(r => r.width > 0.5);
        if (!rects.length) continue;
        for (const r of rects) words.push({w: m[0].replace(/­/g, ''), top: r.top, left: r.left, right: r.right, bottom: r.bottom});
      }
    }
    if (!words.length) continue;
    // строки — по вертикали
    const lines = [];
    for (const w of words.sort((a, b) => a.top - b.top || a.left - b.left)) {
      const ln = lines.find(l => Math.abs(l.top - w.top) < 3);
      if (ln) ln.words.push(w); else lines.push({top: w.top, words: [w]});
    }
    const full = words.map(w => w.w).join(' ');
    const last = lines[lines.length - 1];
    texts.push({tag: el.tagName.toLowerCase(), text: el.textContent.replace(/­/g, '').replace(/\s+/g, ' ').trim().slice(0, 90),
                lines: lines.length, lastWords: last.words.length,
                lastWord: last.words.map(w => w.w).join(' ')});
    for (const w of words) leafs.push({t: full.slice(0, 40), r: w});
  }
  // наложения: слово на слово из РАЗНЫХ блоков
  const over = [];
  for (let i = 0; i < leafs.length && over.length < 12; i++) {
    for (let j = i + 1; j < leafs.length; j++) {
      const a = leafs[i], b = leafs[j];
      if (a.t === b.t) continue;
      const ix = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const iy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (ix > 2 && iy > 2) { over.push(a.t + ' ⟷ ' + b.t); break; }
    }
  }
  // текст шире своей карточки: меряем САМ текст (Range), а не коробку элемента —
  // у nowrap-подписи коробка не растёт, а глифы вылезают за рамку узла
  const spill = [];
  const rg2 = document.createRange();
  for (const el of cz.querySelectorAll('*')) {
    if (!seen(el) || !ownText(el)) continue;
    let card = el.parentElement;
    while (card && card !== cz) {
      const cs = getComputedStyle(card);
      if (parseFloat(cs.borderTopWidth) > 0 || (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)')) break;
      card = card.parentElement;
    }
    if (!card || card === cz) continue;
    const cr = card.getBoundingClientRect(), cs = getComputedStyle(card);
    const bl = parseFloat(cs.borderLeftWidth) || 0, br = parseFloat(cs.borderRightWidth) || 0;
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.nodeValue.trim()) continue;
      rg2.selectNodeContents(n);
      for (const r of rg2.getClientRects()) {
        const over = Math.max(cr.left + bl - r.left, r.right - (cr.right - br));
        if (over > 1) { spill.push({text: ownText(el).slice(0, 40), out: Math.round(over * 10) / 10}); break; }
      }
    }
  }
  // подгонщик молча ужал кегль (textFit пишет инлайновый font-size): текст мельче задуманного
  const shrunk = [];
  for (const el of cz.querySelectorAll('*')) {
    if (!el.style.fontSize || !ownText(el) || !seen(el)) continue;
    const cur = parseFloat(el.style.fontSize), save = el.style.fontSize;
    el.style.fontSize = '';
    const nat = parseFloat(getComputedStyle(el).fontSize);
    el.style.fontSize = save;
    if (nat && cur < nat * 0.97) shrunk.push({text: ownText(el).slice(0, 40), nat: nat, cur: cur, ratio: Math.round(cur / nat * 100) / 100});
  }
  return {scale: effScale(cz), box: {l: L, t: T, r: R, b: B}, texts: texts, overlap: over, spill: spill, shrunk: shrunk};
})()
"""


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def build_probe(ids):
    """Пробная колода + её собственный CSS; возвращает (путь страницы, путь CSS)."""
    src = os.path.join(LN, "out")
    tmp = tempfile.mkdtemp(prefix="l%sprobe-" % N)
    have = set()
    for f in os.listdir(src):
        m = re.match(r"slide-(\d+)\.html$", f)
        if not m:
            continue
        i = int(m.group(1))
        have.add(i)
        if i in ids:
            shutil.copy(os.path.join(src, f), tmp)
        else:
            io.open(os.path.join(tmp, f), "w", encoding="utf-8").write(STUB % (i, i))
    tag = "_probe_%d" % os.getpid()
    page = os.path.join(ROOT, "automation", N, tag + ".html")
    css = os.path.join(ROOT, "assets", tag + ".css")
    os.environ["DECK_OUT"] = tmp
    os.environ["DECK_DST"] = page
    import deck_split
    buf, old = io.StringIO(), sys.stdout
    sys.stdout = buf
    try:
        deck_split.assemble(N)
    finally:
        sys.stdout = old
    import css as cssmod
    cssmod.build(css, [os.path.join(tmp, "*.html"), deck_split.deck_path(N)], strict=False)
    html = io.open(page, encoding="utf-8").read()
    html = html.replace('href="/assets/lecture-%s.css"' % N, 'href="/assets/%s.css"' % tag, 1)
    io.open(page, "w", encoding="utf-8").write(html)
    shutil.rmtree(tmp, ignore_errors=True)
    return page, css


def goto_slide(page, n):
    page.evaluate("""(n) => {
      const act = [...document.querySelectorAll('.slide-container')]
        .findIndex(s => s.classList.contains('opacity-100'));
      let d = n - (act < 0 ? 0 : act);
      while (d > 0) { window.nextSlide(); d--; }
      while (d < 0) { window.prevSlide(); d++; }
    }""", n)
    page.wait_for_timeout(1100)


def main():
    lc.must_run_from_root()
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if not N:
        sys.exit(__doc__)
    as_json = "--json" in sys.argv
    shots = "--no-shots" not in sys.argv
    light = "--light" in sys.argv      # ещё и кадры светлой темы (?theme=light)
    ids = [int(a) for a in args]
    if not ids:
        sys.exit(__doc__)
    page_path, css_path = build_probe(set(ids))
    name = os.path.basename(page_path)
    rl.PORT = free_port()
    rl.RangeHandler.log_message = lambda *a, **k: None   # без простыни запросов
    srv = rl.serve()
    report = {i: {} for i in ids}
    frames = os.path.join(LN, "frames")
    os.makedirs(frames, exist_ok=True)
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=lc.chromium_path(),
                                    args=["--no-sandbox", "--hide-scrollbars"])
            for form, vp in (("pc", lc.PC), ("mob", lc.MOB)):
                ctx = br.new_context(viewport=dict(vp), device_scale_factor=1, reduced_motion="reduce")
                v = lc.vendor_dir()
                if v:
                    ctx.route("**/*", rl.vendor_route(v))
                page = ctx.new_page()
                page.goto("http://127.0.0.1:%d/automation/%s/%s" % (rl.PORT, N, name),
                          wait_until="load", timeout=120000)
                page.wait_for_timeout(3000)
                page.evaluate("() => document.querySelectorAll('#start-overlay,#intro-overlay').forEach(e => e.remove())")
                rl.check_font(page, allow_fallback=False)
                for i in ids:
                    goto_slide(page, i)
                    r = page.evaluate(JS_PROBE)
                    k = page.evaluate(lc._js(lc.JS_KEGL))
                    kr = page.evaluate(lc._js(lc.JS_KRAYA))
                    pe = [e for e in page.evaluate(lc._js(lc.JS_PERENOS)) if e["torn"]]
                    aw, ah = AVAIL[form]
                    b = r["box"]
                    report[i][form] = {
                        "scale": round(r["scale"], 3),
                        "fill_w": round((b["r"] - b["l"]) / aw, 2),
                        "fill_h": round((b["b"] - b["t"]) / ah, 2),
                        "kegl": k["min"], "kegl_items": k["items"][:3],
                        "kraya": kr, "torn": pe, "overlap": r["overlap"], "spill": r["spill"], "shrunk": r["shrunk"],
                        "texts": r["texts"],
                    }
                    if shots:
                        page.screenshot(path=os.path.join(frames, "slide-%02d-%s.png" % (i, form)))
                ctx.close()
            if light and shots:
                for form, vp in (("pc", lc.PC), ("mob", lc.MOB)):
                    ctx = br.new_context(viewport=dict(vp), device_scale_factor=1, reduced_motion="reduce")
                    v = lc.vendor_dir()
                    if v:
                        ctx.route("**/*", rl.vendor_route(v))
                    page = ctx.new_page()
                    page.goto("http://127.0.0.1:%d/automation/%s/%s?theme=light" % (rl.PORT, N, name),
                              wait_until="load", timeout=120000)
                    page.wait_for_timeout(3000)
                    page.evaluate("() => document.querySelectorAll('#start-overlay,#intro-overlay').forEach(e => e.remove())")
                    for i in ids:
                        goto_slide(page, i)
                        page.screenshot(path=os.path.join(frames, "slide-%02d-%s-light.png" % (i, form)))
                    ctx.close()
            br.close()
    finally:
        srv.shutdown()
        for p in (page_path, css_path):
            if os.path.exists(p):
                os.remove(p)

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0
    bad_total = 0
    for i in ids:
        pc, mob = report[i]["pc"], report[i]["mob"]
        probs = []
        if pc["scale"] < 0.95:
            probs.append("ПК масштаб %.2f < 0.95 — слайд переполнен, выглядит мелко" % pc["scale"])
        if pc["fill_h"] < 0.62 and pc["fill_w"] < 0.75:
            probs.append("ПК заполнение %.0f%%×%.0f%% — пустовато, укрупнить" % (pc["fill_w"] * 100, pc["fill_h"] * 100))
        if (mob["kegl"] or 0) < 10:
            probs.append("телефон кегль %.2fpx < 10 (%s)" % (mob["kegl"] or 0,
                         "; ".join("%s «%s»" % (x["px"], x["text"][:30]) for x in mob["kegl_items"][:2])))
        for form in ("pc", "mob"):
            f = report[i][form]
            for e in f["kraya"]:
                probs.append("%s заступ %s +%.1fpx «%s»" % (form, e["kind"], e["out"], e["text"][:40]))
            for e in f["torn"]:
                probs.append("%s разорвано слово в «%s»" % (form, e["text"][:50]))
            for e in f["shrunk"]:
                if e["ratio"] < 0.9:
                    probs.append("%s подгонщик ужал кегль до %d%% «%s» (%.1f→%.1fpx) — текст не влезает, сократить или дать место"
                                 % (form, e["ratio"] * 100, e["text"], e["nat"], e["cur"]))
            for e in f["spill"]:
                probs.append("%s текст шире карточки на %.1fpx «%s»" % (form, e["out"], e["text"]))
            for o in f["overlap"]:
                probs.append("%s наложение текста: %s" % (form, o[:90]))
        subs = [t for t in pc["texts"] if t["tag"] == "p"][:1]
        for t in pc["texts"]:
            if t["tag"] in ("h1", "h2") and t["lines"] > 1:
                probs.append("ПК заголовок в %d строки" % t["lines"])
        for t in subs:
            if t["lines"] > 1:
                probs.append("ПК подзаголовок в %d строки: «%s»" % (t["lines"], t["text"][:50]))
        widows = []
        for form in ("pc", "mob"):
            for t in report[i][form]["texts"]:
                if t["lines"] >= 2 and t["lastWords"] == 1 and len(t["text"].split()) >= 4:
                    widows.append("%s: «%s» — висит «%s»" % (form, t["text"][:60], t["lastWord"]))
        print("── слайд %d ──  ПК: масштаб %.2f, заполнение %d%%×%d%% │ телефон: масштаб %.2f, кегль %.2fpx"
              % (i, pc["scale"], pc["fill_w"] * 100, pc["fill_h"] * 100, mob["scale"], mob["kegl"] or 0))
        if probs:
            bad_total += len(probs)
            print("   ПРОБЛЕМЫ:")
            for p in probs:
                print("     ✗ " + p)
        if widows:
            print("   висячие слова (проверить глазами, по смыслу ли перенос):")
            for w in widows[:14]:
                print("     · " + w)
        multi = [t for t in pc["texts"] if t["lines"] >= 3]
        if multi:
            print("   ПК блоки в 3+ строки (канон: максимум 3):")
            for t in multi[:8]:
                print("     · %d стр.: «%s»" % (t["lines"], t["text"][:70]))
        if not probs:
            print("   механика чистая")
        if shots:
            print("   кадры: build/l%s/frames/slide-%02d-pc.png, slide-%02d-mob.png%s"
                  % (N, i, i, " (+ -pc-light, -mob-light)" if light else ""))
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
