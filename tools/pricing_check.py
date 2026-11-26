# -*- coding: utf-8 -*-
"""FR-SITE113…119, NFR-SITE103…105 — цены главной и лендинга ИИ-стратегии в Chromium.

Строковые тесты (tests/test_site.py, tests/test_strategy.py) видят разметку и
код, но не то, что получается в браузере: что показывает карточка при данном
числе сотрудников и периоде, меняется ли цена во время перетаскивания, растут ли
карточки, не листается ли слайд. Здесь это меряется по факту — компьютер и
телефон, по-русски и по-английски:

  * в консоли нет ошибок; страница не уезжает вбок, слайд (экран) не листается
    внутри и не срезается;
  * ползунок протаскивается мышью — цена меняется ДО отпускания (событие input);
  * ползунок проходит через границы групп 10 | 11, 100 | 101, 249 | 250 (и 5, 50,
    150, 300) в «Месяц» и «Год»: подсвечена нужная группа, у каждого пакета цена,
    период, зачёркнутая прежняя (только «Год» и только у пакетов с Нейронием),
    продление и «≈ на сотрудника» — те же, что считает ценовая политика
    (tools/build_strategy.py: package_price, per_employee), тексты — из
    tools/strategy_copy.py; у 250+ — «По запросу» и «Связаться»;
  * клавиши на ползунке (End / Home) двигают ползунок, слайд при этом стоит;
  * главная: кнопка пакета у 250+ открывает заявку, и FormSubmit получает
    «Pricing: 1000+ (250+) / year / platform»; лендинг: «Связаться» — письмо с той
    же темой;
  * ни ₽, ни «Start free — 1 process» в блоке цен; под каждой карточкой —
    «Первый процесс — бесплатно»; карточки не меняют размер ни в одном состоянии,
    цена не вылезает за карточку; на телефоне переключатель, ползунок и кнопки не
    ниже 44px.

Внешние шрифты и значки по умолчанию закрыты, как в песочнице (JetBrains Mono
обычно стоит в системе); с --net они идут через прокси окружения, как у
посетителя, — так делаются снимки.

    python3 tools/pricing_check.py                        → «PRICING OK»
    python3 tools/pricing_check.py --net --shots DIR      # и снимки состояний
    python3 tools/pricing_check.py --table                # и цены на 5, 50, 150, 300 сотрудниках
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg_miniapp_check import serve  # noqa: E402 — тот же тихий локальный сервер
import build_strategy as B  # noqa: E402 — сетка и формулы ценовой политики
from strategy_copy import EN, RU  # noqa: E402 — тексты цен (те же слова на главной)

VIEWPORTS = [(1440, 900), (1024, 768), (390, 844)]
PHONE_W = 600            # уже — телефонная вёрстка: там всё, что нажимают, не ниже 44px
IGNORED_ERR = ("fonts.googleapis", "fonts.gstatic", "cdnjs", "i.ibb.co", "ERR_", "Failed to load resource")
PROBES = (5, 10, 11, 50, 100, 101, 150, 249, 250, 300)    # границы групп и примеры из отчёта
TXT = {
    # прежняя кнопка «Начать бесплатно — 1 процесс» (заголовок лендинга «Start free / Начните бесплатно» — не она)
    "ru": {"contact": "Связаться", "first": "Первый процесс — бесплатно", "free": ("— 1 процесс", "— 1 process")},
    "en": {"contact": "Contact us", "first": "First process free", "free": ("— 1 process", "— 1 процесс")},
}
COPY = {"en": EN["pr_calc"], "ru": RU["pr_calc"]}


def norm(s):
    """Сравниваем текст без пробелов: разряды на главной — узкие промежутки-span, на лендинге — неразрывный пробел."""
    return re.sub(r"\s+", "", (s or "").replace(u"‑", "-"))


def expected(lang, n, period):
    """Что должна показать каждая карточка (ценовая политика §2–§3 и тексты лендинга)."""
    c, band = COPY[lang], B.band_of(n)
    sep, dec = c["sep"], c["dec"]
    out = {"band": band[0]}
    for k in B.PACKAGES:
        p = B.package_price(k, band, period)
        if p is None:
            out[k] = {"now": c["ask"], "per": "", "was": "", "next": "", "emp": ""}
            continue
        m = lambda v: B.money(v, sep, dec)  # noqa: E731
        out[k] = {
            "now": m(p["now"]),
            "per": c["per"]["strategy"] if k == "strategy" else c["per"]["year" if period == "year" else k],
            "was": (c["was"] + " " + m(p["was"])) if p["was"] else "",
            "next": c["next"][period].replace("{m}", m(p["next"])) if p["next"] else "",
            "emp": c["emp_line"].replace("{m}", m(100 * B.per_employee(band, period, n))) if p["next"] else "",
        }
    return out


def table():
    """Цены на 5, 50, 150, 300 сотрудниках в «Месяц» и «Год» — для отчёта владельцу."""
    for lang in ("ru", "en"):
        print("\n%s:" % lang.upper())
        for n in (5, 50, 150, 300):
            for period in ("month", "year"):
                e = expected(lang, n, period)
                cells = []
                for k in B.PACKAGES:
                    x = e[k]
                    s = x["now"] + (" " + x["per"] if x["per"] else "")
                    if x["was"]:
                        s = "~~%s~~ %s" % (x["was"].split(" ", 1)[1], s)
                    if x["next"]:
                        s += "; " + x["next"]
                    cells.append(s)
                emp = e["platform"]["emp"]
                print(("  %4d (%s) %-5s | " % (n, e["band"], period)) + " | ".join(cells) + ((" | " + emp) if emp else ""))


# главная: слайд «Цены»
MAIN = r"""() => {
  const sl = document.querySelector('#pricing'), fr = sl.querySelector('.frame');
  const vis = el => el && el.offsetParent !== null && getComputedStyle(el).visibility !== 'hidden';
  const box = el => { const b = el.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; };
  // вбок: у корня прокрутка открыта и документ шире окна — или слайд шире себя и срезает содержимое
  // (лента пакетов на телефоне листается внутри себя, это задумано и сюда не попадает)
  const side = (box) => { const de = document.documentElement, ov = getComputedStyle(de).overflowX + getComputedStyle(document.body).overflowX;
    return (!/hidden|clip/.test(ov) && de.scrollWidth > de.clientWidth + 1) || box.scrollWidth > box.clientWidth + 1; };
  return {
    side: side(fr), frameOver: fr.scrollHeight - fr.clientHeight, on: sl.classList.contains('on'),
    scale: ((window.__cv && window.__cv.k) || 1) * (parseFloat(sl.querySelector('.frame > .inner').style.zoom) || 1),
    emp: sl.querySelector('#emp-v').textContent.trim(), band: (sl.querySelector('#bands li.on') || {}).textContent || '',
    bandsOn: sl.querySelectorAll('#bands li.on').length,
    period: (sl.querySelector('#period [aria-pressed=true]') || {}).getAttribute ? sl.querySelector('#period [aria-pressed=true]').getAttribute('data-period') : '',
    cards: [...sl.querySelectorAll('.tier')].map(c => { const row = c.querySelector('.pr-row'), ask = row.classList.contains('ask');
      return { key: c.getAttribute('data-pkg'), now: (ask ? '' : row.querySelector('.cur').textContent) + row.querySelector('.num').textContent,
        per: row.querySelector('.per').textContent, was: c.querySelector('.t-was').textContent, struck: !!c.querySelector('.t-was s'),
        next: c.querySelector('.t-next').textContent, emp: c.querySelector('.t-emp').textContent,
        go: c.querySelector('.t-go').textContent.trim(), foot: (c.querySelector('.t-foot') || {}).textContent || '', size: box(c) }; }),
    text: sl.innerText,
    over: [...sl.querySelectorAll('.pr-row, .t-add, .t-was, .t-inc button')].filter(e => e.scrollWidth > e.clientWidth + 1).length,
    spill: [...sl.querySelectorAll('.tier')].filter(c => { const b = c.getBoundingClientRect();
      return [...c.querySelectorAll('.pr-row, .t-add, .t-was, .t-inc button, .t-go, .t-foot')].some(e => { const r = e.getBoundingClientRect(); return r.left < b.left - 1 || r.right > b.right + 1; }); }).length,
    taps: [...sl.querySelectorAll('#period button, .tier .t-go, #emp-n')].filter(vis).map(e => Math.round(e.getBoundingClientRect().height)),
  };
}"""

# лендинг ИИ-стратегии: экран «Тарифы»
STRAT = r"""() => {
  const sc = document.querySelector('#pricing'), w = sc.querySelector(':scope > .wrap');
  const s = sc.getBoundingClientRect(), wb = w.getBoundingClientRect();
  const box = el => { const b = el.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; };
  const side = (box) => { const de = document.documentElement, ov = getComputedStyle(de).overflowX + getComputedStyle(document.body).overflowX;
    return (!/hidden|clip/.test(ov) && de.scrollWidth > de.clientWidth + 1) || box.scrollWidth > box.clientWidth + 1; };
  return {
    side: side(sc), scale: parseFloat(w.style.zoom) || 1, clipped: wb.top < s.top - 1 || wb.bottom > s.bottom + 1, on: sc.classList.contains('active'),
    emp: sc.querySelector('#calc-v').textContent.trim(), band: (sc.querySelector('.calc-bands li.on') || {}).textContent || '',
    bandsOn: sc.querySelectorAll('.calc-bands li.on').length,
    period: sc.querySelector('[data-period][aria-pressed=true]').getAttribute('data-period'),
    cards: [...sc.querySelectorAll('.pk')].map(c => ({ key: c.getAttribute('data-pkg'), now: c.querySelector('.pk-num').textContent,
      per: c.querySelector('.pk-per').textContent, was: c.querySelector('.pk-was').textContent, struck: c.querySelector('.pk-was').textContent !== '',
      next: c.querySelector('.pk-ren').textContent, emp: c.querySelector('.pk-emp').textContent,
      go: c.querySelector('.pk-go').textContent.trim(), href: c.querySelector('.pk-go').getAttribute('href'),
      foot: c.querySelector('.pk-free').textContent, size: box(c) })),
    card: box(sc.querySelector('.calc-card')),
    text: sc.innerText,
    over: [...sc.querySelectorAll('.pk-price, .pk-next, .pk-name, .pk-free')].filter(e => e.scrollWidth > e.clientWidth + 1).length,
    taps: [...sc.querySelectorAll('.seg button, .pk-go, #calc-n')].map(e => Math.round(e.getBoundingClientRect().height)),
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
        pg._errs, pg._leads = [], []

        # заявки FormSubmit не уходят наружу: тело запоминаем и отвечаем «принято»
        def lead(route):
            if route.request.method == "POST":
                pg._leads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body='{"success":"true"}')
        ctx.route("https://formsubmit.co/**", lead)
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

    def compare(self, tag, s, lang, n, period, landing):
        """Карточки против ценовой политики: цена, период, зачёркнутая, продление, «на сотрудника», кнопка, строка под ней."""
        e, more = expected(lang, n, period), n >= B.EMP_STOPS[-1]
        state = "%d %s" % (n, period)
        if s["emp"] != "%d%s" % (n, "+" if more else ""):
            self.bad("%s (%s): у ползунка %r" % (tag, state, s["emp"]))
        if s["band"] != e["band"] or s["bandsOn"] != 1:
            self.bad("%s (%s): подсвечена группа %r (%d шт.), а не %s" % (tag, state, s["band"], s["bandsOn"], e["band"]))
        if s["period"] != period:
            self.bad("%s (%s): нажат период %r" % (tag, state, s["period"]))
        for card in s["cards"]:
            want = e[card["key"]]
            for f in ("now", "per", "was", "next", "emp"):
                if norm(card[f]) != norm(want[f]):
                    self.bad("%s (%s): %s.%s = %r, а по политике %r" % (tag, state, card["key"], f, card[f], want[f]))
            if card["struck"] != bool(want["was"]):
                self.bad("%s (%s): %s — зачёркнутая цена %s" % (tag, state, card["key"], "есть" if card["struck"] else "нет"))
            ask = want["now"] == COPY[lang]["ask"]
            if ask != (card["go"] == TXT[lang]["contact"]):
                self.bad("%s (%s): %s — кнопка %r" % (tag, state, card["key"], card["go"]))
            if norm(card["foot"]) != norm(TXT[lang]["first"]):
                self.bad("%s (%s): под %s нет «%s»: %r" % (tag, state, card["key"], TXT[lang]["first"], card["foot"]))
            if landing:
                subj = B.lead_subject(n, more, B.band_of(n), period, card["key"])
                want_href = ("mailto:%s?subject=%s" % (B.CONTACT_MAIL, B.mail_quote(subj))) if ask else \
                    ("https://strategy.andre.technology/" + ("?lang=ru" if lang == "ru" else ""))
                if card["href"] != want_href:
                    self.bad("%s (%s): %s ведёт на %r, а не %r" % (tag, state, card["key"], card["href"], want_href))
        if "₽" in s["text"] or any(x in s["text"] for x in TXT[lang]["free"]):
            self.bad("%s (%s): в блоке цен рубли или «Начать бесплатно — 1 процесс»" % (tag, state))
        if s["over"] or s.get("spill"):
            self.bad("%s (%s): строка цены вылезает за карточку (%d / %d)" % (tag, state, s["over"], s.get("spill", 0)))

    def set_emp(self, pg, sel, n):
        pg.evaluate("([s, i]) => { const r = document.querySelector(s); r.value = i; r.dispatchEvent(new Event('input', { bubbles: true })); }",
                    [sel, B.EMP_STOPS.index(n)])

    def drag(self, tag, pg, sel, probe, lang, landing):
        """Мышью: бегунок тянется вправо — цена меняется ещё до отпускания (input, а не change)."""
        r = pg.evaluate("s => { const b = document.querySelector(s).getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }", sel)
        i0 = pg.evaluate("s => +document.querySelector(s).value", sel)
        x0 = r[0] + 10 + (r[2] - 20) * i0 / (len(B.EMP_STOPS) - 1)
        y = r[1] + r[3] / 2
        pg.mouse.move(x0, y)
        pg.mouse.down()
        pg.mouse.move(r[0] + r[2] * 0.62, y, steps=8)
        mid = pg.evaluate(probe)
        i1 = pg.evaluate("s => +document.querySelector(s).value", sel)
        pg.mouse.up()
        n = B.EMP_STOPS[i1]
        if i1 == i0:
            self.bad("%s: ползунок не сдвинулся мышью" % tag)
        else:
            before = len(self.problems)
            self.compare(tag + " (тянется мышью)", mid, lang, n, "month", landing)
            if len(self.problems) == before:
                print("  ok %-28s мышью до отпускания: %s → %s" % (tag, B.EMP_STOPS[i0], mid["emp"]))

    def walk(self, tag, pg, sel, probe, period_sel, lang, landing):
        """Обе границы каждой группы и примеры в «Месяц» и «Год»; карточки одного размера во всех состояниях."""
        sizes = None
        for period in ("month", "year"):
            pg.click(period_sel % period)
            for n in PROBES:
                self.set_emp(pg, sel, n)
                s = pg.evaluate(probe)
                self.compare(tag, s, lang, n, period, landing)
                now = [c["size"] for c in s["cards"]]
                if sizes is None:
                    sizes = now
                elif not same(now, sizes):
                    self.bad("%s (%d %s): карточки пакетов поменяли размер: %s → %s" % (tag, n, period, sizes, now))
                if not landing and s["frameOver"] > 0:
                    self.bad("%s (%d %s): слайд листается внутри на %dpx" % (tag, n, period, s["frameOver"]))
                if landing and s["clipped"]:
                    self.bad("%s (%d %s): экран срезает содержимое" % (tag, n, period))
        pg.click(period_sel % "month")

    # ── главная ───────────────────────────────────────────────────────────
    def main(self, w, h, lang):
        tag = "главная %s %dx%d" % (lang, w, h)
        ctx, pg = self.page(w, h)
        pg.goto(self.base + "/index.html?lang=%s#pricing" % lang, wait_until="load")
        pg.wait_for_timeout(2600)
        s0 = pg.evaluate(MAIN)
        self.shot(pg, "main-%s-%dx%d-1-month-5" % (lang, w, h))
        self.compare(tag, s0, lang, 5, "month", False)
        self.drag(tag, pg, "#emp-n", MAIN, lang, False)
        self.walk(tag, pg, "#emp-n", MAIN, "#period [data-period=%s]", lang, False)
        pg.click("#period [data-period=year]")
        self.set_emp(pg, "#emp-n", 150)
        pg.wait_for_timeout(400)
        self.shot(pg, "main-%s-%dx%d-2-year-150" % (lang, w, h))
        # клавиши: End — 1000+, «По запросу»; слайд стоит
        pg.focus("#emp-n")
        pg.keyboard.press("End")
        pg.wait_for_timeout(300)
        s3 = pg.evaluate(MAIN)
        self.shot(pg, "main-%s-%dx%d-3-year-1000" % (lang, w, h))
        self.compare(tag + " End", s3, lang, 1000, "year", False)
        if not s3["on"]:
            self.bad("%s: клавиша на ползунке перелистнула слайд" % tag)
        # FR-SITE118: заявка у 250+ называет размер, группу, период и пакет без валюты
        pg.evaluate("document.querySelector('#pkgs [data-pick=platform]').click()")
        pg.wait_for_timeout(300)
        if pg.evaluate("document.querySelector('#lead').hidden"):
            self.bad("%s: «%s» не открыла заявку" % (tag, TXT[lang]["contact"]))
        else:
            pg.fill("#lead-email", "pricing-check@example.com")
            pg.evaluate("document.querySelector('#lead-form').requestSubmit()")
            pg.wait_for_timeout(600)
            got = [x.get("interested_in") for x in pg._leads]
            if got != ["Pricing: 1000+ (250+) / year / platform"]:
                self.bad("%s: заявка ушла с %r" % (tag, got))
            pg.evaluate("document.querySelector('[data-lead-close]').click()")
        pg.keyboard.press("Home")
        s4 = pg.evaluate(MAIN)
        self.compare(tag + " Home", s4, lang, 1, "year", False)
        self.common(tag, pg, s0, w)
        ctx.close()
        print("  ok %-28s %s → %s" % (tag, norm(s0["cards"][2]["now"]), norm(s3["cards"][2]["now"])))

    # ── лендинг ИИ-стратегии ─────────────────────────────────────────────
    def strategy(self, w, h, lang):
        tag = "ИИ-стратегия %s %dx%d" % (lang, w, h)
        ctx, pg = self.page(w, h)
        pg.goto(self.base + ("/ai-strategy/ru/" if lang == "ru" else "/ai-strategy/"), wait_until="load")
        pg.wait_for_timeout(800)
        pg.evaluate("document.querySelector('[data-go=\"pricing\"]').click()")
        pg.wait_for_timeout(1500)
        s0 = pg.evaluate(STRAT)
        self.shot(pg, "strategy-%s-%dx%d-1-month-5" % (lang, w, h))
        self.compare(tag, s0, lang, 5, "month", True)
        self.drag(tag, pg, "#calc-n", STRAT, lang, True)
        self.walk(tag, pg, "#calc-n", STRAT, "#calc [data-period=%s]", lang, True)
        pg.click("#calc [data-period=year]")
        self.set_emp(pg, "#calc-n", 150)
        pg.wait_for_timeout(400)
        self.shot(pg, "strategy-%s-%dx%d-2-year-150" % (lang, w, h))
        pg.focus("#calc-n")
        pg.keyboard.press("End")
        pg.wait_for_timeout(300)
        s3 = pg.evaluate(STRAT)
        self.shot(pg, "strategy-%s-%dx%d-3-year-1000" % (lang, w, h))
        self.compare(tag + " End", s3, lang, 1000, "year", True)
        if not s3["on"]:
            self.bad("%s: клавиша на ползунке перелистнула экран" % tag)
        if not same([s3["card"]], [s0["card"]]):
            self.bad("%s: карточка с ползунком поменяла размер: %s → %s" % (tag, s0["card"], s3["card"]))
        self.common(tag, pg, s3, w)
        ctx.close()
        print("  ok %-28s %s → %s" % (tag, norm(s0["cards"][2]["now"]), norm(s3["cards"][2]["now"])))


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и значки из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков состояний")
    ap.add_argument("--sizes", help="размеры окна через запятую, например 1440x900,390x844")
    ap.add_argument("--table", action="store_true", help="напечатать цены на 5, 50, 150, 300 сотрудниках")
    args = ap.parse_args()
    if args.table:
        table()
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
