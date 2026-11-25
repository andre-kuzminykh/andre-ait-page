# -*- coding: utf-8 -*-
"""FR-SITE103 — слайд «Как закрываем ИИ-трансформацию» на главной в Chromium.

Строковые тесты (tests/test_site.py) видят разметку и код, но не то, что
получается в браузере: не уехала ли схема вбок, не листается ли слайд, не
налезают ли решения друг на друга, не закрывает ли кружок с роликом кнопки.
Здесь это меряется по факту — компьютер и телефон, по-русски и по-английски:

  * в консоли нет ошибок; страница и слайд не уезжают вбок, слайд не
    листается внутри и ничего не срезает;
  * семь измерений и пять решений стоят каждое в своей строке и не налезают
    друг на друга; текст решений не вылезает за карточку; скобка «Нейрония»
    приходит в середины своих трёх строк;
  * пакет подсвечивает свою часть: стратегия — только Andre AI, платформа —
    ещё Нейроний, трансформация — ещё обучение и консультант; R&D не гаснет;
  * цена пакета — та же, что в карточке «Цен», и идёт за ползунком, периодом
    и валютой (у 1000+ — «от …»);
  * решения ведут на свои слайды, «Под вашу задачу» открывает заявку,
    «Пакеты и цены» — на «Цены»;
  * на телефоне кнопки не ниже 44px, кружок с роликом не закрывает ни одной
    кнопки слайда.

Внешние шрифты и значки по умолчанию закрыты, как в песочнице; с --net они
идут через прокси окружения, как у посетителя, — так делаются снимки.

    python3 tools/cover_check.py                        → «COVER OK»
    python3 tools/cover_check.py --net --shots DIR      # и снимки каждого состояния
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg_miniapp_check import serve  # noqa: E402 — тот же тихий локальный сервер

VIEWPORTS = [(1440, 900), (1024, 768), (390, 844)]
EXTRA = [(1920, 1080), (2560, 1080), (1366, 768), (1280, 1024), (430, 932), (375, 667), (360, 740), (768, 1024), (844, 390)]
PHONE_W = 600            # уже — телефонная вёрстка: там всё, что нажимают, не ниже 44px
IGNORED_ERR = ("fonts.googleapis", "fonts.gstatic", "cdnjs", "i.ibb.co", "ERR_", "Failed to load resource")
TXT = {
    "ru": {"cur": "₽", "other": "usd", "from": "от", "k": "Как закрываем", "train": "за обучение"},
    "en": {"cur": "$", "other": "rub", "from": "from", "k": "How we cover", "train": "for training"},
}
# что закрывает пакет: группы схемы (data-cv), которые не гаснут
COVER = {"strategy": ["s"], "tools": ["s", "p"], "mentor": ["s", "p", "t", "c"]}

STATE = r"""() => {
  const sl = document.querySelector('#cover'), fr = sl.querySelector('.frame'), inn = fr.firstElementChild;
  const R = e => { const b = e.getBoundingClientRect(); return {l: b.left, t: b.top, r: b.right, b: b.bottom, w: b.width, h: b.height}; };
  const vis = e => e && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden' && e.getBoundingClientRect().width > 0;
  const de = document.documentElement, ov = getComputedStyle(de).overflowX + getComputedStyle(document.body).overflowX;
  const cards = [...sl.querySelectorAll('.cvr-s')], dims = [...sl.querySelectorAll('.cvr-d')];
  const overlap = (a, b) => Math.min(a.r, b.r) - Math.max(a.l, b.l) > 1 && Math.min(a.b, b.b) - Math.max(a.t, b.t) > 1;
  const boxes = cards.map(R).concat(dims.map(R));
  let clash = 0; for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) if (overlap(boxes[i], boxes[j])) clash++;
  // текст карточки — в карточке (ни строка, ни слово не вылезает)
  const spill = cards.filter(c => { const b = R(c); return [...c.querySelectorAll('b, .cvr-t')].filter(vis).some(e => { const r = R(e); return r.r > b.r + 1 || r.l < b.l - 1 || r.b > b.b + 1; }) || c.scrollWidth > c.clientWidth + 1; }).length;
  // скобка «Нейрония»: середина каждой из трёх строк измерений — на высоте скобки (верх, середина, низ)
  const br = R(sl.querySelector('.cvr-l3')), d3 = dims.slice(2, 5).map(e => (R(e).t + R(e).b) / 2);
  const k = (window.__cv && window.__cv.k || 1) * (parseFloat(inn.style.zoom) || 1);
  const off6 = (br.h - 2 * parseFloat(getComputedStyle(sl.querySelector('.cvr-map')).rowGap) * k) / 6, bTop = br.t + off6, bMid = br.t + br.h / 2, bBot = br.b - off6;
  // кнопки слайда: решения, пакеты, «Пакеты и цены»
  const taps = [...sl.querySelectorAll('.cvr-s, #cvr-pkg button, #cvr-pr, .actions .link')].filter(vis);
  const hidden = taps.filter(e => { const b = R(e), x = b.l + b.w / 2, y = b.t + b.h / 2, hit = document.elementFromPoint(x, y); return !hit || !e.contains(hit); })
    .map(e => (e.textContent || '').trim().slice(0, 24));
  const sw = window.innerWidth;
  // текст слайда не под кружком с роликом (круг — его квадрат без углов): по строкам текста, а не по коробкам
  const head = document.querySelector('#head'), hb = head && head.classList.contains('bubble') ? R(head) : null, under = [];
  if (hb) { const k2 = hb.w * 0.12, H = {l: hb.l + k2, t: hb.t + k2, r: hb.r - k2, b: hb.b - k2}, wk = document.createTreeWalker(inn, NodeFilter.SHOW_TEXT);
    let n; while ((n = wk.nextNode())) { if (!n.nodeValue.trim() || !vis(n.parentElement)) continue; const rg = document.createRange(); rg.selectNodeContents(n);
      if ([...rg.getClientRects()].some(r => Math.min(r.right, H.r) - Math.max(r.left, H.l) > 1 && Math.min(r.bottom, H.b) - Math.max(r.top, H.t) > 1)) under.push(n.nodeValue.trim().slice(0, 24)); } }
  return {
    // вбок: документ или слайд шире окна, или видимое содержимое за краем (обёртку пары двигает deskCenter — её коробка в расчёт не идёт)
    side: (!/hidden|clip/.test(ov) && de.scrollWidth > de.clientWidth + 1) || fr.scrollWidth > fr.clientWidth + 1 ||
      [...sl.querySelectorAll('.kicker, .h2 .l, .actions .link, #cvr-pkg, .cvr-pr, .cvr-d, .cvr-s, .cvr-path')].filter(vis).some(e => { const b = R(e); return b.r > sw + 1 || b.l < -1; }),
    over: fr.scrollHeight - fr.clientHeight, zoom: parseFloat(inn.style.zoom) || 1, scale: k,
    clash, spill, bracket: [d3[0] - bTop, d3[1] - bMid, d3[2] - bBot].map(v => Math.round(v)),
    on: [...sl.querySelectorAll('.cvr-g[data-cv]')].filter(g => !g.classList.contains('off')).map(g => g.getAttribute('data-cv')),
    rnd: sl.querySelector('.cvr-g:not([data-cv])').classList.contains('off'),
    pressed: [...sl.querySelectorAll('#cvr-pkg [aria-pressed="true"]')].map(b => b.getAttribute('data-cvr-pkg')),
    price: sl.querySelector('#cvr-pr').innerText.replace(/\s+/g, ' ').trim(),
    card: { strategy: (document.querySelector('[data-pkg="strategy"] .pr-row') || {}).innerText, tools: (document.querySelector('[data-pkg="tools"] .pr-row') || {}).innerText,
            mentor: (document.querySelector('[data-pkg="mentor"] .pr-row') || {}).innerText },
    taps: taps.map(e => e.getBoundingClientRect().height), hidden, under,
    kicker: sl.querySelector('.kicker').textContent.trim(),
  };
}"""


def norm(s):
    return " ".join((s or "").replace("\u00a0", " ").split())


class Check:
    def __init__(self, browser, base, net, shots):
        self.b, self.base, self.net, self.shots, self.problems = browser, base, net, shots, []

    def bad(self, msg):
        self.problems.append(msg)
        print("  !!", msg)

    def page(self, w, h):
        ctx = self.b.new_context(viewport={"width": w, "height": h})
        ctx.route("**/*", lambda r: r.continue_() if (self.net or r.request.url.startswith("http://127.0.0.1")) else r.abort())
        pg = ctx.new_page()
        pg._errs = []
        pg.on("console", lambda m: m.type == "error" and pg._errs.append(m.text))
        pg.on("pageerror", lambda e: pg._errs.append(str(e)))
        return ctx, pg

    def shot(self, pg, name):
        if self.shots:
            os.makedirs(self.shots, exist_ok=True)
            pg.wait_for_timeout(500)  # приглушение частей схемы — переход 0,35 с: снимок после него
            pg.screenshot(path=os.path.join(self.shots, name + ".png"))

    def click(self, pg, tag, sel):
        """Нажатие как у посетителя: если кнопку закрывает другой элемент, это ошибка, а не зависание на 30 с."""
        try:
            pg.click(sel, timeout=4000)
            pg.wait_for_timeout(300)
            return True
        except Exception as e:  # noqa: BLE001 — Playwright бросает свой TimeoutError
            self.bad("%s: не нажимается %s: %s" % (tag, sel, str(e).splitlines()[0][:120]))
            return False

    def layout(self, tag, s, w):
        if s["side"]:
            self.bad("%s: страница или схема уезжает вбок" % tag)
        if s["over"] > 0:
            self.bad("%s: слайд листается внутри на %dpx" % (tag, s["over"]))
        if s["clash"]:
            self.bad("%s: измерения или решения налезают друг на друга (%d)" % (tag, s["clash"]))
        if s["spill"]:
            self.bad("%s: текст вылезает из карточки решения (%d)" % (tag, s["spill"]))
        if max(abs(v) for v in s["bracket"]) > 3:
            self.bad("%s: скобка «Нейрония» не в серединах своих строк: %s" % (tag, s["bracket"]))
        if s["hidden"]:
            self.bad("%s: кнопки закрыты другим элементом (кружок?): %s" % (tag, s["hidden"]))
        if s["under"]:
            self.bad("%s: текст под кружком с роликом: %s" % (tag, s["under"]))
        if w < PHONE_W:
            # высоты — в пикселях вёрстки (экранные делим на масштаб холста и ужатия); полпикселя — округление масштаба
            css = [round(x / s["scale"], 1) for x in s["taps"]]
            if min(css) < 43.5:
                self.bad("%s: на телефоне кнопка ниже 44px: %s" % (tag, css))
            elif min(s["taps"]) < 43.5:
                print("  ·· %s: окно меньше эталонного, всё ужато ×%.2f — на экране %dpx" % (tag, s["scale"], min(s["taps"])))

    def run(self, w, h, lang):
        t, tag, n0 = TXT[lang], "%s %dx%d" % (lang, w, h), len(self.problems)
        ctx, pg = self.page(w, h)
        pg.goto(self.base + "/index.html?lang=%s#cover" % lang, wait_until="load")
        pg.wait_for_timeout(2800)
        ev = lambda: pg.evaluate(STATE)  # noqa: E731
        s0 = ev()
        self.shot(pg, "cover-%s-%dx%d-1-transformation" % (lang, w, h))
        if not s0["kicker"].startswith(t["k"]):
            self.bad("%s: надзаголовок %r" % (tag, s0["kicker"]))
        if s0["pressed"] != ["mentor"] or sorted(s0["on"]) != sorted(COVER["mentor"]) or s0["rnd"]:
            self.bad("%s: по умолчанию не «ИИ-трансформация»: %s %s, R&D погашен: %s" % (tag, s0["pressed"], s0["on"], s0["rnd"]))
        if norm(s0["card"]["mentor"]).split(" /")[0].replace(" ", "") not in norm(s0["price"]).replace(" ", ""):
            self.bad("%s: цена «ИИ-трансформации» %r не та, что в карточке %r" % (tag, s0["price"], s0["card"]["mentor"]))
        if t["cur"] not in s0["price"]:
            self.bad("%s: цена не в %s: %r" % (tag, t["cur"], s0["price"]))
        self.layout(tag, s0, w)
        # пакеты: что подсвечено и какая цена
        for pk in ("strategy", "tools"):
            pg.click("#cvr-pkg [data-cvr-pkg=%s]" % pk)
            s = ev()
            if s["pressed"] != [pk] or sorted(s["on"]) != sorted(COVER[pk]) or s["rnd"]:
                self.bad("%s: пакет %s подсвечивает %s (ждали %s), R&D погашен: %s" % (tag, pk, s["on"], COVER[pk], s["rnd"]))
            if norm(s["card"][pk]).split(" /")[0].replace(" ", "") not in norm(s["price"]).replace(" ", ""):
                self.bad("%s: цена пакета %s %r не та, что в карточке %r" % (tag, pk, s["price"], s["card"][pk]))
            if pk == "strategy":
                self.shot(pg, "cover-%s-%dx%d-2-strategy" % (lang, w, h))
        pg.click("#cvr-pkg [data-cvr-pkg=mentor]")
        # цена идёт за ползунком, периодом и валютой «Цен»: 1000+, год, другая валюта
        pg.evaluate("""(o) => { const r = document.querySelector('#emp-n'); r.value = '38'; r.dispatchEvent(new Event('input', {bubbles: true}));
          document.querySelector('#period [data-period=year]').click(); document.querySelector('#cur [data-cur=' + o + ']').click(); }""", t["other"])
        s = ev()
        # «ИИ-трансформация» за год — как в её карточке: подписка за год и строкой обучение помесячно
        if not norm(s["price"]).startswith(t["from"] + " ") or t["cur"] in s["price"] or t["train"] not in s["price"]:
            self.bad("%s: цена не пошла за ползунком, периодом и валютой: %r" % (tag, s["price"]))
        self.shot(pg, "cover-%s-%dx%d-3-1000-year" % (lang, w, h))
        self.layout(tag + " (1000+, год)", s, w)
        pg.click("#cvr-pkg [data-cvr-pkg=strategy]")
        s = ev()
        if "1000+" not in s["price"] or norm(s["card"]["strategy"]).replace(" ", "") not in norm(s["price"]).replace(" ", ""):
            self.bad("%s: у 1000+ цена стратегии %r, в карточке %r" % (tag, s["price"], s["card"]["strategy"]))
        if s["over"] > 0:
            self.bad("%s: после смены пакета слайд листается внутри на %dpx" % (tag, s["over"]))
        # ссылки: решения — на свои слайды, R&D — заявка, «Пакеты и цены» — на «Цены»
        links = [('.cvr-s[data-go="strategy"]', "strategy"), ('.cvr-s3', "neuronium"), ('.cvr-s[data-go="training"]', "training"), ('#cvr-pr', "pricing")]
        if pg.is_visible('#cover .actions .link'):  # в телефонной вёрстке «Пакетов и цен» под заголовком нет — туда ведёт цена
            links.append(('#cover .actions .link', "pricing"))
        for sel, want in links:
            pg.goto(self.base + "/index.html?lang=%s#cover" % lang, wait_until="load")
            pg.wait_for_timeout(1200)
            if not self.click(pg, tag, sel):
                continue
            pg.wait_for_timeout(500)
            if pg.evaluate("document.querySelector('#%s').classList.contains('on')" % want) is not True:
                self.bad("%s: %s не ведёт на слайд %s" % (tag, sel, want))
        pg.goto(self.base + "/index.html?lang=%s#cover" % lang, wait_until="load")
        pg.wait_for_timeout(1200)
        if self.click(pg, tag, '.cvr-s[data-lead]') and pg.evaluate("!document.querySelector('#lead').hidden") is not True:
            self.bad("%s: «Под вашу задачу» не открывает заявку" % tag)
        errs = [e for e in pg._errs if not any(k in e for k in IGNORED_ERR)]
        if errs:
            self.bad("%s: ошибки в консоли: %s" % (tag, errs[:3]))
        ctx.close()
        if len(self.problems) == n0:
            print("  ok %-14s zoom %.2f · %s" % (tag, s0["zoom"], norm(s0["price"])))


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и значки из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков каждого состояния")
    ap.add_argument("--sizes", help="размеры окна через запятую, например 1440x900,390x844")
    ap.add_argument("--all", action="store_true", help="и ещё девять размеров: широкие, короткие, планшет, телефон в горизонте")
    args = ap.parse_args()
    sizes = [tuple(map(int, s.split("x"))) for s in args.sizes.split(",")] if args.sizes else VIEWPORTS + (EXTRA if args.all else [])
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    srv, base = serve(ROOT)
    try:
        with sync_playwright() as pw:
            opts = {"executable_path": os.environ.get("CHROMIUM_PATH") or "/opt/pw-browsers/chromium",
                    "args": ["--no-sandbox"]}
            if args.net and proxy:
                opts["proxy"] = {"server": proxy, "bypass": "127.0.0.1,localhost"}
            browser = pw.chromium.launch(**opts)
            check = Check(browser, base, args.net, args.shots)
            for w, h in sizes:
                print("== %dx%d" % (w, h))
                for lang in ("ru", "en"):
                    check.run(w, h, lang)
            browser.close()
    finally:
        srv.shutdown()
    if check.problems:
        print("\nПРОБЛЕМ: %d" % len(check.problems))
        sys.exit(1)
    print("\nCOVER OK")


if __name__ == "__main__":
    main()
