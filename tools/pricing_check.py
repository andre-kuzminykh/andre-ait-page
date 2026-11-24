# -*- coding: utf-8 -*-
"""FR-SITE101/102 — цены главной и лендинга ИИ-стратегии в Chromium.

Строковые тесты (tests/test_site.py, tests/test_strategy.py) видят разметку и
код, но не то, что получается в браузере: переносится ли цена, растут ли
карточки, не листается ли слайд, не закрывает ли кружок главную кнопку. Здесь
это меряется по факту — компьютер и телефон, по-русски и по-английски:

  * в консоли нет ошибок; страница не уезжает вбок, слайд (экран) не листается
    внутри и не срезается;
  * ползунок «сколько сотрудников» сам выбирает тариф: 1 — Соло, 5 — Микро,
    1000+ — Крупный; двигается клавишами (Home / End), а слайд при этом стоит;
  * «Месяц / Год» и «$ / ₽» меняют все цены; по умолчанию русская версия — в
    рублях, английская — в долларах;
  * у 250+ — «от …» и «Связаться»; карточки (на главной — пакеты) не меняют
    размер ни при каком тарифе, периоде и валюте, цена не вылезает за карточку;
  * на телефоне переключатели, ползунок и кнопки не ниже 44px, главная кнопка
    «Начать бесплатно» не под кружком с роликом.

Внешние шрифты и значки по умолчанию закрыты, как в песочнице (JetBrains Mono
обычно стоит в системе); с --net они идут через прокси окружения, как у
посетителя, — так делаются снимки.

    python3 tools/pricing_check.py                        → «PRICING OK»
    python3 tools/pricing_check.py --net --shots DIR      # и снимки каждого состояния
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg_miniapp_check import serve  # noqa: E402 — тот же тихий локальный сервер

VIEWPORTS = [(1440, 900), (1024, 768), (390, 844)]
PHONE_W = 600            # уже — телефонная вёрстка: там всё, что нажимают, не ниже 44px
IGNORED_ERR = ("fonts.googleapis", "fonts.gstatic", "cdnjs", "i.ibb.co", "ERR_", "Failed to load resource")
TXT = {
    "ru": {"micro": "Микро", "solo": "Соло", "large": "Крупный", "from": "от", "contact": "Связаться",
           "cur": "₽", "other": "usd", "year": "/год", "free": "Начать бесплатно"},
    "en": {"micro": "Micro", "solo": "Solo", "large": "Large", "from": "from", "contact": "Contact us",
           "cur": "$", "other": "rub", "year": "/yr", "free": "Start free"},
}

# главная: слайд «Цены»
MAIN = r"""() => {
  const sl = document.querySelector('#pricing'), fr = sl.querySelector('.frame');
  const vis = el => el && el.offsetParent !== null && getComputedStyle(el).visibility !== 'hidden';
  const box = el => { const b = el.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; };
  // вбок: у корня прокрутка открыта и документ шире окна — или слайд (экран) шире себя и срезает содержимое
  // (лента пакетов на телефоне листается внутри себя, это задумано и сюда не попадает)
  const side = (box) => { const de = document.documentElement, ov = getComputedStyle(de).overflowX + getComputedStyle(document.body).overflowX;
    return (!/hidden|clip/.test(ov) && de.scrollWidth > de.clientWidth + 1) || box.scrollWidth > box.clientWidth + 1; };
  const free = [...sl.querySelectorAll('.pr-go')].filter(vis)[0];
  let hit = null;
  if (free) { const b = free.getBoundingClientRect(); const e = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); hit = !!e && free.contains(e); }
  return {
    side: side(fr), frameOver: fr.scrollHeight - fr.clientHeight,
    scale: ((window.__cv && window.__cv.k) || 1) * (parseFloat(sl.querySelector('.frame > .inner').style.zoom) || 1),
    emp: sl.querySelector('#emp-v').textContent.trim(),
    prices: [...sl.querySelectorAll('[data-price] .pr-row')].map(p => p.innerText.replace(/\s+/g, ' ').trim()),
    froms: [...sl.querySelectorAll('[data-price] .pr-row')].map(p => (p.querySelector('.from') || {}).textContent || ''),
    lines: [...sl.querySelectorAll('.t-c')].map(p => p.innerText.replace(/\s+/g, ' ').trim()),
    gos: [...sl.querySelectorAll('.t-go')].map(b => b.textContent.trim()),
    cards: [...sl.querySelectorAll('.tier')].map(box),
    over: [...sl.querySelectorAll('.pr-row, .t-add, .t-inc button')].filter(e => e.scrollWidth > e.clientWidth + 1).length,
    spill: [...sl.querySelectorAll('.tier')].filter(c => { const b = c.getBoundingClientRect();
      return [...c.querySelectorAll('.pr-row, .t-add, .t-inc button, .t-go')].some(e => { const r = e.getBoundingClientRect(); return r.left < b.left - 1 || r.right > b.right + 1; }); }).length,
    taps: [...sl.querySelectorAll('#period button, #cur button, .tier .t-go, #emp-n')].concat(free ? [free] : []).map(e => Math.round(e.getBoundingClientRect().height)),
    free: !!free, freeHit: hit,
  };
}"""

# лендинг ИИ-стратегии: экран «Тарифы»
STRAT = r"""() => {
  const sc = document.querySelector('#pricing'), w = sc.querySelector(':scope > .wrap'), c = sc.querySelector('#calc');
  const s = sc.getBoundingClientRect(), wb = w.getBoundingClientRect(), card = sc.querySelector('.calc-card').getBoundingClientRect();
  const pr = sc.querySelector('.calc-price'), ct = sc.querySelector('.calc-contact');
  // вбок: у корня прокрутка открыта и документ шире окна — или слайд (экран) шире себя и срезает содержимое
  // (лента пакетов на телефоне листается внутри себя, это задумано и сюда не попадает)
  const side = (box) => { const de = document.documentElement, ov = getComputedStyle(de).overflowX + getComputedStyle(document.body).overflowX;
    return (!/hidden|clip/.test(ov) && de.scrollWidth > de.clientWidth + 1) || box.scrollWidth > box.clientWidth + 1; };
  return {
    side: side(sc), scale: parseFloat(w.style.zoom) || 1, clipped: wb.top < s.top - 1 || wb.bottom > s.bottom + 1,
    emp: sc.querySelector('#calc-v').textContent.trim(), plan: sc.querySelector('.calc-plan').textContent.replace(/\s+/g, ' ').trim(),
    price: pr.innerText.replace(/\s+/g, ' ').trim(), priceOver: pr.scrollWidth - pr.clientWidth,
    contact: getComputedStyle(ct).visibility === 'visible', card: [Math.round(card.width), Math.round(card.height)],
    taps: [...sc.querySelectorAll('.seg button, .calc-free, #calc-n')].concat(getComputedStyle(ct).visibility === 'visible' ? [ct] : [])
      .map(e => Math.round(e.getBoundingClientRect().height)),
  };
}"""


def same(a, b):
    return len(a) == len(b) and all(abs(x - y) <= 1 for p, q in zip(a, b) for x, y in zip(p, q))


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
            pg.screenshot(path=os.path.join(self.shots, name + ".png"))

    def common(self, tag, pg, s, w):
        errs = [e for e in pg._errs if not any(k in e for k in IGNORED_ERR)]
        if errs:
            self.bad("%s: ошибки в консоли: %s" % (tag, errs[:3]))
        if s["side"]:
            self.bad("%s: страница уезжает вбок или блок цен выходит за окно" % tag)
        if w < PHONE_W:
            # 44px — в пикселях вёрстки; на телефоне уже эталонного (390) холст ужат целиком, и
            # на экране кнопки пропорционально меньше — это не правка цен, а масштаб всей страницы
            css = [round(x / s["scale"]) for x in s["taps"]]
            if min(css) < 44:
                self.bad("%s: на телефоне кнопка или ползунок ниже 44px: %s" % (tag, css))
            elif min(s["taps"]) < 44:
                print("  ·· %s: окно меньше эталонного, всё ужато ×%.2f — на экране %dpx" % (tag, s["scale"], min(s["taps"])))

    # ── главная ───────────────────────────────────────────────────────────
    def main(self, w, h, lang):
        t, tag = TXT[lang], "главная %s %dx%d" % (lang, w, h)
        ctx, pg = self.page(w, h)
        pg.goto(self.base + "/index.html?lang=%s#pricing" % lang, wait_until="load")
        pg.wait_for_timeout(2600)
        states, s0 = {}, pg.evaluate(MAIN)
        states["месяц"] = s0
        self.shot(pg, "main-%s-%dx%d-1-month" % (lang, w, h))
        if s0["emp"] != "5 · " + t["micro"]:
            self.bad("%s: ползунок по умолчанию — %r, а не «5 · %s»" % (tag, s0["emp"], t["micro"]))
        if not all(t["cur"] in p for p in s0["prices"]):
            self.bad("%s: по умолчанию цены не в %s: %s" % (tag, t["cur"], s0["prices"]))
        if not s0["free"]:
            self.bad("%s: нет видимой кнопки «%s»" % (tag, t["free"]))
        elif not s0["freeHit"]:
            self.bad("%s: главную кнопку закрывает другой элемент (кружок?)" % tag)
        pg.click("#period [data-period=year]")
        s1 = states["год"] = pg.evaluate(MAIN)
        if any(a == b for a, b in zip(s0["prices"], s1["prices"])) or not all(t["year"] in x for x in s1["lines"][1:2]):
            self.bad("%s: «Год» поменял не все цены: %s → %s" % (tag, s0["prices"], s1["prices"]))
        pg.click("#cur [data-cur=%s]" % t["other"])
        s2 = states["другая валюта"] = pg.evaluate(MAIN)
        if any(a == b for a, b in zip(s1["prices"], s2["prices"])) or any(t["cur"] in p for p in s2["prices"]):
            self.bad("%s: валюта поменяла не все цены: %s → %s" % (tag, s1["prices"], s2["prices"]))
        pg.click("#cur [data-cur=%s]" % ("rub" if t["other"] == "usd" else "usd"))
        pg.focus("#emp-n")
        pg.keyboard.press("End")
        pg.wait_for_timeout(200)
        s3 = states["1000+"] = pg.evaluate(MAIN)
        self.shot(pg, "main-%s-%dx%d-2-year-1000" % (lang, w, h))
        if not s3["emp"].startswith("1000+") or t["large"] not in s3["emp"]:
            self.bad("%s: End на ползунке дал %r, а не 1000+ · %s" % (tag, s3["emp"], t["large"]))
        if set(s3["froms"]) != {t["from"]} or any(s0["froms"]) or set(s3["gos"]) != {t["contact"]}:
            self.bad("%s: у 250+ нет «%s …» и «%s»: %s %s" % (tag, t["from"], t["contact"], s3["prices"], s3["gos"]))
        if pg.evaluate("document.querySelector('#pricing').classList.contains('on')") is not True:
            self.bad("%s: клавиша на ползунке перелистнула слайд" % tag)
        pg.keyboard.press("Home")
        s4 = states["1"] = pg.evaluate(MAIN)
        if s4["emp"] != "1 · " + t["solo"]:
            self.bad("%s: Home на ползунке дал %r, а не «1 · %s»" % (tag, s4["emp"], t["solo"]))
        for name, s in states.items():
            if not same(s["cards"], s0["cards"]):
                self.bad("%s: карточки пакетов поменяли размер (%s): %s → %s" % (tag, name, s0["cards"], s["cards"]))
            if s["frameOver"] > 0:
                self.bad("%s: слайд листается внутри на %dpx (%s)" % (tag, s["frameOver"], name))
            if s["over"] or s["spill"]:
                self.bad("%s: цена или строка чека вылезает за карточку (%s)" % (tag, name))
        self.common(tag, pg, s0, w)
        ctx.close()
        print("  ok %-28s %s → %s" % (tag, s0["prices"][0], s3["prices"][0]))

    # ── лендинг ИИ-стратегии ─────────────────────────────────────────────
    def strategy(self, w, h, lang):
        t, tag = TXT[lang], "ИИ-стратегия %s %dx%d" % (lang, w, h)
        ctx, pg = self.page(w, h)
        pg.goto(self.base + ("/ai-strategy/ru/" if lang == "ru" else "/ai-strategy/"), wait_until="load")
        pg.wait_for_timeout(800)
        pg.evaluate("document.querySelector('[data-go=\"pricing\"]').click()")
        pg.wait_for_timeout(1500)
        states, s0 = {}, pg.evaluate(STRAT)
        states["месяц"] = s0
        self.shot(pg, "strategy-%s-%dx%d-1-month" % (lang, w, h))
        if s0["emp"] != "5" or not s0["plan"].lower().startswith(t["micro"].lower()) or t["cur"] not in s0["price"] or s0["contact"]:
            self.bad("%s: по умолчанию %r %r %r, «Связаться» %s" % (tag, s0["emp"], s0["plan"], s0["price"], s0["contact"]))
        pg.click("#calc [data-period=year]")
        s1 = states["год"] = pg.evaluate(STRAT)
        pg.click("#calc [data-cur=%s]" % t["other"])
        s2 = states["другая валюта"] = pg.evaluate(STRAT)
        if len({s0["price"], s1["price"], s2["price"]}) != 3 or t["cur"] in s2["price"]:
            self.bad("%s: переключатели не меняют цену: %s / %s / %s" % (tag, s0["price"], s1["price"], s2["price"]))
        pg.click("#calc [data-cur=%s]" % ("rub" if t["other"] == "usd" else "usd"))
        pg.focus("#calc-n")
        pg.keyboard.press("End")
        pg.wait_for_timeout(200)
        s3 = states["1000+"] = pg.evaluate(STRAT)
        self.shot(pg, "strategy-%s-%dx%d-2-year-1000" % (lang, w, h))
        if s3["emp"] != "1000+" or not s3["plan"].lower().startswith(t["large"].lower()) or \
                not s3["price"].startswith(t["from"] + " ") or not s3["contact"]:
            self.bad("%s: у 1000+ %r %r, «Связаться» %s" % (tag, s3["plan"], s3["price"], s3["contact"]))
        if pg.evaluate("document.querySelector('#pricing').classList.contains('active')") is not True:
            self.bad("%s: клавиша на ползунке перелистнула экран" % tag)
        for name, s in states.items():
            if not same([s["card"]], [s0["card"]]):
                self.bad("%s: карточка тарифа поменяла размер (%s): %s → %s" % (tag, name, s0["card"], s["card"]))
            if s["clipped"]:
                self.bad("%s: экран срезает содержимое (%s)" % (tag, name))
            if s["priceOver"] > 0:
                self.bad("%s: цена вылезает за карточку (%s): %s" % (tag, name, s["price"]))
        self.common(tag, pg, s3, w)
        ctx.close()
        print("  ok %-28s %s → %s" % (tag, s0["price"], s3["price"]))


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и значки из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков каждого состояния")
    ap.add_argument("--sizes", help="размеры окна через запятую, например 1440x900,390x844")
    args = ap.parse_args()
    sizes = [tuple(map(int, s.split("x"))) for s in args.sizes.split(",")] if args.sizes else VIEWPORTS
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
                    check.main(w, h, lang)
                    check.strategy(w, h, lang)
            browser.close()
    finally:
        srv.shutdown()
    if check.problems:
        print("\nПРОБЛЕМ: %d" % len(check.problems))
        sys.exit(1)
    print("\nPRICING OK")


if __name__ == "__main__":
    main()
