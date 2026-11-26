# -*- coding: utf-8 -*-
"""FR-SITE140…148, NFR-SITE111…113 — вход с сайта в продукт и партнёры через продукт, в Chromium.

Строковые тесты видят код, но не то, что получается в браузере: какой адрес стоит у кнопки пакета при
данном размере команды, периоде и языке, доезжают ли до продукта промокод и партнёр из ссылки партнёра,
уводит ли нажатие в той же вкладке; откуда сайт партнёров взял каталог, когда продукт отвечает, молчит,
отдаёт пустой список или закрыт CORS, и куда ушла заявка. Здесь это видно по факту.

Стенд — один на прогон: сайт как GitHub Pages, сайт партнёров ещё и как поддомен за Caddy (те же серверы,
что у tools/partners_check.py), заглушка продукта (tools/api_stub.py — CORS только для этих двух адресов,
как у продукта) и Chromium без выхода наружу. Подробные проверки — tests/test_site.py,
tests/test_strategy.py, tests/test_partners.py (test_render_*): они берут стенд отсюда.

    python3 tools/entry_check.py                     → «ENTRY OK»
    python3 tools/entry_check.py --urls              # адреса кнопок на 5, 50, 150 сотрудниках (RU и EN, «Месяц» и «Год»)
    python3 tools/entry_check.py --shots DIR         # и снимки изменённых кнопок и состояний
    python3 tools/entry_check.py --net --shots DIR   # то же со шрифтами и значками из сети (через прокси окружения)
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_strategy as B  # noqa: E402 — адрес входа (entry_href), сетка и деления ползунка
import partners_check as PC  # noqa: E402 — серверы сайта и поддомена, запуск браузера, сбор ошибок
from api_stub import ApiStub  # noqa: E402 — заглушка продукта

PROBES = (5, 50, 150)
PERIODS = ("month", "year")
PROMO_QS = "promo=NIKA10&partner=nika-vetrova"
PROMO_REF = "&" + PROMO_QS
PRODUCT = B.PRODUCT_ENTRY
FORMSUBMIT = "https://formsubmit.co/ajax/admin@andre.technology"
DESKTOP, PHONE = (1440, 900), (390, 844)
# страница «продукта» на стенде: показывает адрес, с которым её открыли (снимок перехода)
PRODUCT_PAGE = """<!doctype html><meta charset="utf-8"><title>strategy.andre.technology</title>
<body style="margin:0;background:#050505;color:#e5e7eb;font:15px/1.6 'JetBrains Mono',monospace;display:flex;align-items:center;justify-content:center;height:100vh">
<div style="max-width:90vw;padding:2rem;border:1px solid #333;border-radius:20px"><p style="margin:0 0 .6rem;color:#94a3b8">Andre AI — вход с сайта (стенд)</p>
<p id="u" style="margin:0;word-break:break-all;color:#c4a6ff"></p></div><script>document.getElementById('u').textContent = location.href;</script></body>"""


def expected(pkg, n, period, lang, ref=""):
    """Адрес кнопки пакета до 250 сотрудников (FR-SITE140, FR-SITE141): тот же, что собирают главная, assets/strategy.js и сборщик."""
    return B.entry_href(pkg, n, period, lang) + ref


def lead_source(n, period, pkg):
    """FR-SITE118: источник заявки 250+ — как на главной (без валюты)."""
    return B.lead_subject(n, n >= B.EMP_STOPS[-1], B.band_of(n), period, pkg)


def stand_partner(src, slug, promo=None):
    """Партнёр «из продукта» для стенда: профиль-пример без пометки примера, свой slug и (если задан) промокод."""
    p = json.loads(json.dumps(src))
    p.update(slug=slug, example=False)
    if promo:
        p["promo_code"] = promo
    return p


class Stand:
    """Серверы сайта и поддомена, заглушка продукта и браузер."""

    def __init__(self, pw, net=False):
        self.base, self.base2, self.partners_site, self.partners_sub, self._stop = PC.servers()
        self.stub = ApiStub(origins=[self.base, self.base2])
        self.browser = PC.launch(pw, net)
        self.net = net

    def close(self):
        try:
            self.browser.close()
        finally:
            self.stub.stop()
            self._stop()

    def page(self, size=DESKTOP, lang="ru", touch=False, reduced=True, api=False):
        """Страница со сбором ошибок (partners_check.new_page). Заявки FormSubmit наружу не уходят — тела копятся в pg.leads; переход в
        продукт тоже — «продукт» отвечает страницей стенда с адресом. api=True — страница партнёров берёт продукт у заглушки."""
        ctx, pg = PC.new_page(self.browser, size, net=self.net, lang=lang, reduced=reduced, touch=touch)
        pg.leads = []

        def lead(route):
            if route.request.method == "POST":
                pg.leads.append(json.loads(route.request.post_data or "{}"))
            route.fulfill(status=200, content_type="application/json", body='{"success":"true"}')
        ctx.route("https://formsubmit.co/**", lead)
        ctx.route(PRODUCT + "**", lambda r: r.fulfill(status=200, content_type="text/html; charset=utf-8", body=PRODUCT_PAGE))
        if api:
            ctx.add_init_script("window.AIT_API = %s;" % json.dumps(self.stub.url))
        return ctx, pg

    def bare_page(self, size=DESKTOP, lang="ru"):
        """Страница БЕЗ перехвата запросов: только так браузер сам шлёт предзапрос CORS к заглушке (с перехватом его отвечает Playwright).
        Наружу её не пускает запуск браузера (partners_check.launch): FormSubmit недоступен — заявка ложится в очередь ait_lead_queue."""
        ctx = self.browser.new_context(viewport={"width": size[0], "height": size[1]}, locale="en-US" if lang == "en" else "ru-RU",
                                       reduced_motion="reduce")
        ctx.add_init_script("window.AIT_API = %s;" % json.dumps(self.stub.url))
        pg = ctx.new_page()
        pg.errors = []
        pg.on("console", lambda m: m.type == "error" and pg.errors.append(m.text))
        pg.on("pageerror", lambda e: pg.errors.append(str(e)))
        return ctx, pg


# ── главная: слайд «Цены» ─────────────────────────────────────────────────

def open_home(pg, base, lang="ru", query=""):
    """Главная сразу на слайде цен; query — метки адреса без «?» (например, промокод партнёра)."""
    qs = "lang=" + lang + ("&" + query if query else "")
    pg.goto(base + "/?" + qs + "#pricing", wait_until="load")
    pg.wait_for_function("document.querySelector('#pricing').classList.contains('on') && /pkg=/.test(document.querySelector('#pkgs .t-go').getAttribute('href') || '')")


def home_set(pg, n=None, period=None):
    if period:
        pg.click("#period [data-period=%s]" % period)
    if n is not None:
        pg.evaluate("i => { const r = document.querySelector('#emp-n'); r.value = i; r.dispatchEvent(new Event('input', { bubbles: true })); }",
                    B.EMP_STOPS.index(n))


def home_links(pg):
    """{пакет: (адрес, aria-haspopup, тег)} кнопок пакетов главной."""
    return {k: tuple(v) for k, v in pg.evaluate(
        "Object.fromEntries([...document.querySelectorAll('#pkgs .t-go')].map(a => [a.dataset.pick, [a.getAttribute('href'), a.getAttribute('aria-haspopup'), a.tagName]]))").items()}


# ── лендинг ИИ-стратегии: экран «Тарифы» ─────────────────────────────────

def open_landing(pg, base, lang="ru", query=""):
    pg.goto(base + ("/ai-strategy/ru/" if lang == "ru" else "/ai-strategy/") + ("?" + query if query else ""), wait_until="load")
    pg.evaluate("document.querySelector('[data-go=\"pricing\"]').click()")
    pg.wait_for_function("document.querySelector('#pricing').classList.contains('active')")


def landing_set(pg, n=None, period=None):
    if period:
        pg.click("#calc [data-period=%s]" % period)
    if n is not None:
        pg.evaluate("i => { const r = document.querySelector('#calc-n'); r.value = i; r.dispatchEvent(new Event('input', { bubbles: true })); }",
                    B.EMP_STOPS.index(n))


def landing_links(pg):
    return pg.evaluate("Object.fromEntries([...document.querySelectorAll('#calc .pk')].map(c => [c.dataset.pkg, c.querySelector('.pk-go').getAttribute('href')]))")


# ── прогон для человека ───────────────────────────────────────────────────

def urls_table():
    """Адреса кнопок на 5, 50, 150 сотрудниках — для отчёта владельцу."""
    for lang in ("ru", "en"):
        print("\n%s:" % lang.upper())
        for n in PROBES:
            for period in PERIODS:
                for pkg in B.PACKAGES:
                    print("  %3d %-5s %-14s %s" % (n, period, pkg, expected(pkg, n, period, lang)))
    print("\nпо ссылке партнёра (?%s) к каждому адресу дописывается %s" % (PROMO_QS, PROMO_REF))


class Check:
    def __init__(self, stand, shots=None):
        self.s, self.shots, self.problems = stand, shots, []

    def bad(self, msg):
        self.problems.append(msg)
        print("  !!", msg)

    def shot(self, pg, name, full=False):
        if self.shots:
            os.makedirs(self.shots, exist_ok=True)
            pg.screenshot(path=os.path.join(self.shots, name + ".png"), full_page=full)

    def caption(self, pg, sel, label):
        """Для снимка: строка состояния браузера с адресом кнопки, на которую навели (сайт её не рисует — это подпись стенда)."""
        pg.hover(sel)
        pg.evaluate("""([sel, label]) => { const a = document.querySelector(sel), d = document.createElement('div');
          d.id = '__cap'; d.textContent = label + ' ' + a.href;
          d.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:99999;max-width:calc(100vw - 16px);padding:4px 9px;border-radius:6px;' +
            'background:#e9e9ee;color:#111;font:12px/1.35 system-ui,sans-serif;word-break:break-all;box-shadow:0 2px 8px rgba(0,0,0,.4)';
          document.body.appendChild(d); }""", [sel, label])

    def uncaption(self, pg):
        pg.evaluate("document.getElementById('__cap') && document.getElementById('__cap').remove()")

    def fonts(self, pg):
        """С --net шрифт заголовков приходит из Google Fonts позже загрузки страницы и после себя переукладывает цены (fitPricing на
        loadingdone) — снимок до этого показал бы цену, ещё не ужатую под новый шрифт. Без сети шрифт системный, ждать нечего."""
        if not self.s.net:
            return
        try:
            pg.wait_for_function("[...document.fonts].some(f => /JetBrains Mono/.test(f.family) && f.status === 'loaded') && document.fonts.status === 'loaded'",
                                 timeout=8000)
        except Exception:  # шрифт так и не пришёл — снимаем как есть
            pass
        pg.wait_for_timeout(400)

    def home(self, size, lang):
        tag = "главная %s %dx%d" % (lang, size[0], size[1])
        ctx, pg = self.s.page(size, lang, touch=size == PHONE)
        open_home(pg, self.s.base, lang, PROMO_QS)
        self.fonts(pg)
        if "promo=" in pg.url:
            self.bad("%s: адрес страницы не переписан — проверка промокода ничего не доказывает" % tag)
        for period in PERIODS:
            for n in PROBES:
                home_set(pg, n, period)
                got = home_links(pg)
                for pkg in B.PACKAGES:
                    want = expected(pkg, n, period, lang, PROMO_REF)
                    if got[pkg][0] != want:
                        self.bad("%s (%d %s): %s ведёт на %r, а не %r" % (tag, n, period, pkg, got[pkg][0], want))
        # снимок — 50 сотрудников, «Месяц» («Год» — на снимке лендинга): с шрифтом из Google Fonts цена «ИИ-трансформации» на компьютере
        # в «Год» бывает не ужата под ширину карточки — так и на 8bc935c (подгонка цены, FR-SITE116), к входу в продукт отношения не имеет
        home_set(pg, 50, "month")
        pg.wait_for_timeout(300)
        self.caption(pg, '#pkgs .t-go[data-pick="%s"]' % ("transformation" if size == PHONE else "platform"),
                     "кнопка ведёт:" if lang == "ru" else "button opens:")
        self.shot(pg, "home-%s-%dx%d-1-50-month-promo" % (lang, size[0], size[1]))
        self.uncaption(pg)
        # 250+: «Связаться» — прежняя заявка с прежним источником
        home_set(pg, 1000, "year")
        pg.click('#pkgs .t-go[data-pick="transformation"]')
        pg.wait_for_selector("#lead:not([hidden])")
        self.shot(pg, "home-%s-%dx%d-2-1000-lead-form" % (lang, size[0], size[1]))
        pg.fill("#lead-email", "entry-check@example.com")
        pg.evaluate("document.querySelector('#lead-form').requestSubmit()")
        pg.wait_for_selector("#lead-done:not([hidden])")
        got = [x.get("interested_in") for x in pg.leads]
        if got != [lead_source(1000, "year", "transformation")]:
            self.bad("%s: заявка 250+ ушла с %r" % (tag, got))
        pg.evaluate("document.querySelector('[data-lead-close]').click()")
        # нажатие до 250 — переход в продукт в той же вкладке
        home_set(pg, 50, "month")
        pg.click('#pkgs .t-go[data-pick="transformation"]')
        pg.wait_for_url(PRODUCT + "**")
        want = expected("transformation", 50, "month", lang, PROMO_REF)
        if pg.url != want or len(ctx.pages) != 1:
            self.bad("%s: переход %r (вкладок %d), а не %r" % (tag, pg.url, len(ctx.pages), want))
        self.shot(pg, "home-%s-%dx%d-3-product-opened" % (lang, size[0], size[1]))
        errs = [e for e in pg.errors if "Failed to load resource" not in e]
        if errs:
            self.bad("%s: ошибки в консоли %s" % (tag, errs[:3]))
        ctx.close()
        print("  ok", tag)

    def landing(self, size, lang):
        tag = "ИИ-стратегия %s %dx%d" % (lang, size[0], size[1])
        ctx, pg = self.s.page(size, lang, touch=size == PHONE)
        open_landing(pg, self.s.base, lang, PROMO_QS)
        self.fonts(pg)
        for period in PERIODS:
            for n in PROBES:
                landing_set(pg, n, period)
                got = landing_links(pg)
                for pkg in B.PACKAGES:
                    want = expected(pkg, n, period, lang, PROMO_REF)
                    if got[pkg] != want:
                        self.bad("%s (%d %s): %s ведёт на %r, а не %r" % (tag, n, period, pkg, got[pkg], want))
        landing_set(pg, 150, "year")
        pg.evaluate("window.dispatchEvent(new Event('resize'))")
        pg.wait_for_timeout(600)
        self.caption(pg, '#calc .pk[data-pkg="platform"] .pk-go', "кнопка ведёт:" if lang == "ru" else "button opens:")
        self.shot(pg, "landing-%s-%dx%d-1-150-year-promo" % (lang, size[0], size[1]))
        self.uncaption(pg)
        landing_set(pg, 300, "month")
        got = landing_links(pg)
        want = "mailto:%s?subject=%s" % (B.CONTACT_MAIL, B.mail_quote(lead_source(300, "month", "platform")))
        if got["platform"] != want:
            self.bad("%s: у 250+ кнопка ведёт на %r" % (tag, got["platform"]))
        landing_set(pg, 5, "month")
        pg.click('#calc .pk[data-pkg="strategy"] .pk-go')
        pg.wait_for_url(PRODUCT + "**")
        want = expected("strategy", 5, "month", lang, PROMO_REF)
        if pg.url != want or len(ctx.pages) != 1:
            self.bad("%s: переход %r (вкладок %d), а не %r" % (tag, pg.url, len(ctx.pages), want))
        errs = [e for e in pg.errors if "Failed to load resource" not in e]
        if errs:
            self.bad("%s: ошибки в консоли %s" % (tag, errs[:3]))
        ctx.close()
        print("  ok", tag)

    def partners(self, size, lang):
        tag = "партнёры %s %dx%d" % (lang, size[0], size[1])
        st = self.s.stub
        with open(os.path.join(ROOT, "partners", "partners.json"), encoding="utf-8") as f:
            ex = json.load(f)
        st.partners = [stand_partner(ex[0], "nika-vetrova", "NIKA10"), stand_partner(ex[1], "lukas-brenner")]
        st.reset("ok", "ok")
        ctx, pg = self.s.page(size, lang, touch=size == PHONE, api=True)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.s.base2)
        pg.goto(self.s.partners_sub + "?lang=" + lang, wait_until="load")
        PC.wait_ready(pg)
        src = pg.evaluate("window.AndrePartners.source")
        cards = pg.evaluate("[...document.querySelectorAll('#grid .pc')].map(c => c.dataset.slug)")
        if src != "api" or cards != ["nika-vetrova", "lukas-brenner"]:
            self.bad("%s: каталог %s %s, а не из продукта" % (tag, src, cards))
        pg.evaluate("document.querySelector('#catalog').scrollIntoView()")
        pg.wait_for_timeout(500)
        self.shot(pg, "partners-%s-%dx%d-1-catalog-from-product" % (lang, size[0], size[1]))
        pg.click('#grid .pc[data-slug="nika-vetrova"] .pc-link')
        pg.wait_for_selector("#profile:not([hidden])")
        pg.click("#profile [data-invite]")
        pg.wait_for_function("document.querySelector('#profile [data-invite] span').textContent !== %s" % json.dumps("Пригласить клиента" if lang == "ru" else "Invite a client"))
        clip = pg.evaluate("navigator.clipboard.readText()")
        if clip != "https://andre.technology/?promo=NIKA10&partner=nika-vetrova":
            self.bad("%s: «Пригласить клиента» скопировала %r" % (tag, clip))
        self.shot(pg, "partners-%s-%dx%d-2-invite-copied" % (lang, size[0], size[1]))
        pg.click("#profile [data-choose]")
        pg.wait_for_selector("#req:not([hidden])")
        pg.fill("#req-name", "Наталья" if lang == "ru" else "Natalia")
        pg.fill("#req-email", "natalia@example.com")
        pg.click("#req-btn")
        pg.wait_for_selector("#req-done:not([hidden])")
        reqs = st.posts("/api/partners/requests")
        if len(reqs) != 1 or reqs[0].get("partner_slug") != "nika-vetrova" or pg.leads:
            self.bad("%s: заявка партнёру — в продукт %r, письмом %r" % (tag, reqs, pg.leads))
        pg.keyboard.press("Escape")
        pg.keyboard.press("Escape")
        pg.wait_for_selector("#profile", state="hidden")
        pg.evaluate("document.querySelector('#become').scrollIntoView()")
        pg.click("#apply")
        pg.wait_for_selector("#app:not([hidden])")
        pg.fill("#app-name", "Иван" if lang == "ru" else "Ivan")
        pg.fill("#app-email", "ivan@example.com")
        pg.fill("#app-in", "linkedin.com/in/ivan-example")
        pg.fill("#app-exp", "Пять лет в операционном консалтинге: BPMN, n8n, ИИ-агенты" if lang == "ru" else "Five years of operations consulting: BPMN, n8n, AI agents")
        pg.fill("#app-rate", "100")
        pg.click("#app-btn")
        pg.wait_for_selector("#app-done:not([hidden])")
        if not pg.is_visible("#app-stage") or "ivan@example.com" not in pg.inner_text("#app-stage"):
            self.bad("%s: после заявки в партнёры нет ступени" % tag)
        self.shot(pg, "partners-%s-%dx%d-3-application-stage" % (lang, size[0], size[1]))
        if pg.errors or pg.bad:
            self.bad("%s: ошибки %s %s" % (tag, pg.errors[:3], pg.bad[:3]))
        ctx.close()
        # продукт молчит — примеры из partners.json, как прежде
        st.reset("error", "error")
        ctx, pg = self.s.page(size, lang, touch=size == PHONE, api=True)
        pg.goto(self.s.partners_sub + "?lang=" + lang, wait_until="load")
        PC.wait_ready(pg)
        if pg.evaluate("window.AndrePartners.source") != "fetch":
            self.bad("%s: при сбое продукта каталог не из partners.json" % tag)
        pg.evaluate("document.querySelector('#catalog').scrollIntoView()")
        pg.wait_for_timeout(500)
        self.shot(pg, "partners-%s-%dx%d-4-product-down-examples" % (lang, size[0], size[1]))
        ctx.close()
        print("  ok", tag)


def main():
    from playwright.sync_api import sync_playwright
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и значки из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков")
    ap.add_argument("--urls", action="store_true", help="напечатать адреса кнопок на 5, 50, 150 сотрудниках")
    a = ap.parse_args()
    if a.urls:
        urls_table()
    with sync_playwright() as pw:
        stand = Stand(pw, a.net)
        try:
            check = Check(stand, a.shots)
            for size in (DESKTOP, PHONE):
                print("== %dx%d" % size)
                for lang in ("ru", "en"):
                    check.home(size, lang)
                    check.landing(size, lang)
                    check.partners(size, lang)
        finally:
            stand.close()
    if check.problems:
        print("\nПРОБЛЕМ: %d" % len(check.problems))
        sys.exit(1)
    print("\nENTRY OK")


if __name__ == "__main__":
    main()
