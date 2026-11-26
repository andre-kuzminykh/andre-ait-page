# -*- coding: utf-8 -*-
"""FR-SITE150…152, NFR-SITE114 — юридические страницы в Chromium: оба адреса условий партнёров, снимки.

Строки и структуру страниц проверяет tests/test_legal.py; здесь — то, что видно только в браузере:

  * шесть страниц (политика, условия использования, условия партнёров; RU и EN) на компьютере 1440×900
    и телефоне 390×844: без прокрутки вбок, без ошибок в консоли и 404 своих запросов, значки отдаются,
    у каждой ссылки оглавления есть раздел, переключатель языка ведёт на страницу другого языка;
  * условия партнёров — в двух видах адреса, как на проде (NFR-SITE110): http://127.0.0.1:N/partners/terms/
    (как andre.technology/partners/terms/, GitHub Pages) и http://127.0.0.1:M/terms/ — прокси переписывает
    /x → /partners/x, как блок Caddy из SPEC-SITE.md (partners.andre.technology/terms/); в обоих работают
    значки, ссылка «Партнёры» и переключатель языка;
  * сайт партнёров ведёт на условия: ссылка в подвале и строка у формы заявки в партнёры (FR-SITE152);
  * --shots DIR — снимки: верх каждой страницы и страница целиком (компьютер и телефон, RU и EN), подвал
    сайта партнёров и форма заявки со строкой об условиях.

Внешние шрифты и логотип по умолчанию закрыты, как в песочнице (JetBrains Mono обычно стоит в системе);
с --net они идут через прокси окружения.

    python3 tools/legal_check.py                    → «LEGAL OK»
    python3 tools/legal_check.py --net --shots DIR
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_legal  # noqa: E402
from partners_check import DESKTOP, OVERFLOW, PHONE, launch, new_page, servers  # noqa: E402

LANGS = ("ru", "en")


def pages(base, base2):
    """(подпись, вид документа, язык, адрес) — каждая страница по каждому своему адресу."""
    out = []
    for kind in build_legal.ORDER:
        for lang in LANGS:
            path = build_legal.PATHS[kind][lang]
            out.append(("сайт", kind, lang, base + path))
            if build_legal.is_partners(kind):
                out.append(("поддомен", kind, lang, base2 + path[len("/partners"):]))
    return out


PROBE = """() => {
  const icons = [...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon], link[rel=manifest]')]
    .map(l => new URL(l.getAttribute('href'), location.href).href);
  const home = new URL(document.querySelector('.hdr-r > a').getAttribute('href'), location.href).href;
  const toc = [...document.querySelectorAll('.toc a')].map(a => a.getAttribute('href'));
  return { icons, home, toc, missing: toc.filter(h => !document.getElementById(h.slice(1))),
    h2: document.querySelectorAll('main h2[id]').length, h1: document.querySelector('h1').textContent,
    en: new URL(document.querySelector('[data-lang=en]').getAttribute('href'), location.href).href,
    ru: new URL(document.querySelector('[data-lang=ru]').getAttribute('href'), location.href).href }; }"""

STATUS = "u => fetch(u + (u.indexOf('?') < 0 ? '?probe' : '&probe')).then(r => r.status, () => 0)"


def check_page(browser, tag, kind, lang, url, size, problems):
    """Одна страница: вёрстка, ошибки, значки, оглавление, «домой» и переключатель языка."""
    name = "%s %s %s %dx%d" % (tag, kind, lang, size[0], size[1])
    ctx, pg = new_page(browser, size, lang=lang, touch=size == PHONE)
    try:
        pg.goto(url, wait_until="load")
        info = pg.evaluate(PROBE)
        over = pg.evaluate(OVERFLOW)
        if over["doc"] > 0 or over["wide"]:
            problems.append("%s: страница уезжает вбок на %dpx (%s)" % (name, over["doc"], over["wide"]))
        if info["h1"] != build_legal.LEGAL[kind][lang]["title"]:
            problems.append("%s: заголовок «%s»" % (name, info["h1"]))
        if info["missing"] or len(info["toc"]) != info["h2"] or not info["toc"]:
            problems.append("%s: оглавление и разделы не сходятся (%s)" % (name, info["missing"][:3]))
        for u in info["icons"] + [info["home"]]:
            if u.startswith("http://127.0.0.1"):
                st = pg.evaluate(STATUS, u)
                if st != 200:
                    problems.append("%s: %s отдаёт %s" % (name, u, st))
        # переключатель языка: из этой страницы — на неё же другого языка (и обратно), по месту адреса
        want = {"en": url if lang == "en" else None, "ru": url if lang == "ru" else None}
        other = "en" if lang == "ru" else "ru"
        if build_legal.is_partners(kind):
            here = url.rstrip("/")
            want[other] = (here + "/ru/") if other == "ru" else here[: -len("/ru")] + "/"
        else:
            want[other] = url.replace(build_legal.PATHS[kind][lang], build_legal.PATHS[kind][other])
        for l2 in LANGS:
            got = info[l2]
            if os.path.normpath(got.split("//", 1)[1]) != os.path.normpath(want[l2].split("//", 1)[1]):
                problems.append("%s: язык %s ведёт на %s, а не %s" % (name, l2, got, want[l2]))
        pg.click("[data-lang=%s]" % other)
        pg.wait_for_load_state("load")
        if pg.evaluate("document.documentElement.lang") != other:
            problems.append("%s: после переключения язык страницы не %s" % (name, other))
        if pg.errors or pg.bad:
            problems.append("%s: ошибки %s %s" % (name, pg.errors[:3], pg.bad[:3]))
    finally:
        ctx.close()
    print("  ..", name)


def check_partners_links(browser, sub_url, problems):
    """FR-SITE152: подвал и форма заявки сайта партнёров ведут на условия на языке страницы."""
    from partners_check import open_page
    for lang in LANGS:
        ctx, pg = open_page(browser, sub_url, DESKTOP, lang)
        try:
            foot = pg.evaluate("new URL(document.querySelector('.legal [data-i18n=\"legal.partner\"]').getAttribute('href'), location.href).href")
            want = sub_url + ("terms/ru/" if lang == "ru" else "terms/")
            if foot != want:
                problems.append("сайт партнёров %s: подвал ведёт на %s, а не %s" % (lang, foot, want))
            pg.evaluate("document.querySelector('#become').scrollIntoView()")
            pg.click("#apply")
            pg.wait_for_selector("#app:not([hidden])")
            hrefs = pg.evaluate("[...document.querySelectorAll('#app-form .m-legal a')].map(a => new URL(a.getAttribute('href'), location.href).href)")
            want_p = "https://andre.technology" + build_legal.PATHS["privacy"][lang]
            if hrefs != [want, want_p]:
                problems.append("сайт партнёров %s: строка у заявки ведёт на %s" % (lang, hrefs))
            st = pg.evaluate(STATUS, want)
            if st != 200:
                problems.append("сайт партнёров %s: условия по ссылке отдают %s" % (lang, st))
            if pg.errors or pg.bad:
                problems.append("сайт партнёров %s: ошибки %s %s" % (lang, pg.errors[:3], pg.bad[:3]))
        finally:
            ctx.close()
        print("  .. сайт партнёров", lang)


def shots(browser, base, base2, outdir, net):
    os.makedirs(outdir, exist_ok=True)
    made = []
    for kind in build_legal.ORDER:
        for lang in LANGS:
            path = build_legal.PATHS[kind][lang]
            url = (base2 + path[len("/partners"):]) if build_legal.is_partners(kind) else base + path
            for size, tag in ((DESKTOP, "desktop"), (PHONE, "phone")):
                ctx, pg = new_page(browser, size, net=net, lang=lang, touch=size == PHONE)
                pg.goto(url, wait_until="load")
                pg.wait_for_timeout(600 if net else 150)
                for full in (False, True):
                    p = os.path.join(outdir, "%s-%s-%s-%s.png" % (kind.replace("_", "-"), tag, lang, "full" if full else "top"))
                    pg.screenshot(path=p, full_page=full)
                    made.append(p)
                ctx.close()
    from partners_check import open_page
    for lang in LANGS:
        for size, tag in ((DESKTOP, "desktop"), (PHONE, "phone")):
            ctx, pg = open_page(browser, base2 + "/", size, lang, net=net, touch=size == PHONE)
            # плавная прокрутка страницы и появление блоков — сразу в конец, без кадра на полпути
            pg.evaluate("document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(0, document.documentElement.scrollHeight)")
            pg.wait_for_timeout(1200)
            p = os.path.join(outdir, "partners-footer-%s-%s.png" % (tag, lang))
            pg.screenshot(path=p)
            made.append(p)
            pg.evaluate("document.querySelector('#become').scrollIntoView()")
            pg.click("#apply")
            pg.wait_for_selector("#app:not([hidden])")
            pg.evaluate("document.querySelector('#app-btn').scrollIntoView({block: 'center'})")
            pg.wait_for_timeout(500)
            p = os.path.join(outdir, "partners-application-%s-%s.png" % (tag, lang))
            pg.screenshot(path=p)
            made.append(p)
            ctx.close()
    return made


def run(browser, base, base2, problems):
    for tag, kind, lang, url in pages(base, base2):
        for size in (DESKTOP, PHONE):
            check_page(browser, tag, kind, lang, url, size, problems)
    check_partners_links(browser, base2 + "/", problems)


def main():
    from playwright.sync_api import sync_playwright
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", action="store_true", help="пускать шрифты и логотип из сети (через прокси окружения)")
    ap.add_argument("--shots", help="папка для снимков")
    a = ap.parse_args()
    base, base2, _, _, stop = servers()
    problems = []
    try:
        with sync_playwright() as pw:
            b = launch(pw, a.net)
            run(b, base, base2, problems)
            if a.shots:
                for p in shots(b, base, base2, a.shots, a.net):
                    print("  снимок", p)
            b.close()
    finally:
        stop()
    if problems:
        print("\nПРОБЛЕМ: %d\n  %s" % (len(problems), "\n  ".join(problems)))
        sys.exit(1)
    print("\nLEGAL OK")


if __name__ == "__main__":
    main()
