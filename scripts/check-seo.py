#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автоматическая SEO-проверка сайта andre.technology (статический GitHub Pages).

Запуск:  python3 scripts/check-seo.py
Выходит с ненулевым кодом при любой критической ошибке.

Проверяет индексируемые страницы (/, /ai-training/, /ai-agents/,
/business-process-automation/, /about/, /cases/, /contacts/):
  - ровно один <title>, один meta description, один canonical, один <h1>;
  - robots = index, follow; lang="en"; favicon; JSON-LD;
  - OG title/description/url + twitter card;
  - уникальность title и description между страницами;
  - canonical указывает на https://andre.technology/... (не GitHub Pages);
  - сайт нигде не ссылается на *.github.io;
  - sitemap.xml валиден, содержит только публичные страницы (без /backup/,
    /automation/, пользовательских и технических URL) и все его URL существуют;
  - robots.txt указывает на sitemap;
  - site.webmanifest — валидный JSON с обязательными полями;
  - технические страницы (/backup/, /kolesa/, /napoleon-it/, /workshop_2/,
    /workshop_3/, 404.html) закрыты noindex;
  - «Free AI Diagnostic» ведёт ТОЛЬКО на maturity.andre.technology
    (и никогда на strategy.), стратегические CTA — на корень strategy.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEXABLE = {
    "index.html": "https://andre.technology/",
    "ai-training/index.html": "https://andre.technology/ai-training/",
    "ai-agents/index.html": "https://andre.technology/ai-agents/",
    "business-process-automation/index.html": "https://andre.technology/business-process-automation/",
    "about/index.html": "https://andre.technology/about/",
    "cases/index.html": "https://andre.technology/cases/",
    "contacts/index.html": "https://andre.technology/contacts/",
}

NOINDEX_PAGES = [
    "backup/index-before-popups-2026-07-06.html",
    "kolesa/index.html",
    "napoleon-it/index.html",
    "workshop_2/index.html",
    "workshop_3/index.html",
    "404.html",
]

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)
    print("FAIL:", msg)


def warn(msg):
    WARNINGS.append(msg)
    print("warn:", msg)


def ok(msg):
    print("  ok:", msg)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def count(pattern, html, flags=0):
    return len(re.findall(pattern, html, flags))


def check_indexable_pages():
    titles, descriptions = {}, {}
    for rel, url in INDEXABLE.items():
        html = read(rel)
        name = rel

        n = count(r"<title>", html)
        if n != 1:
            err(f"{name}: должно быть ровно один <title>, найдено {n}")
        n = count(r'<meta name="description"', html)
        if n != 1:
            err(f"{name}: должно быть ровно одно meta description, найдено {n}")
        n = count(r'<link rel="canonical"', html)
        if n != 1:
            err(f"{name}: должен быть ровно один canonical, найдено {n}")
        if f'<link rel="canonical" href="{url}">' not in html:
            err(f"{name}: canonical должен быть self-referencing: {url}")
        if count(r"<h1[\s>]", html) != 1:
            err(f"{name}: должен быть ровно один <h1>")
        if '<meta name="robots" content="index, follow' not in html:
            err(f"{name}: robots должен быть index, follow")
        if '<html lang="en">' not in html:
            err(f"{name}: должен быть lang=\"en\"")
        if '<link rel="icon"' not in html:
            err(f"{name}: нет favicon")
        if 'application/ld+json' not in html:
            err(f"{name}: нет JSON-LD")
        for prop in ("og:title", "og:description", "og:url", "og:image"):
            if f'property="{prop}"' not in html:
                err(f"{name}: нет Open Graph {prop}")
        if f'<meta property="og:url" content="{url}">' not in html:
            err(f"{name}: og:url должен совпадать с canonical {url}")
        if 'name="twitter:card"' not in html:
            err(f"{name}: нет twitter:card")
        if '<meta name="keywords"' in html:
            err(f"{name}: meta keywords запрещён")

        m = re.search(r"<title>(.*?)</title>", html, re.S)
        if m:
            t = m.group(1).strip()
            if t in titles:
                err(f"{name}: title дублирует {titles[t]}: «{t}»")
            titles[t] = name
        m = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
        if m:
            d = m.group(1).strip()
            if d in descriptions:
                err(f"{name}: description дублирует {descriptions[d]}")
            descriptions[d] = name

        # JSON-LD должен быть валидным JSON
        for i, block in enumerate(re.findall(
                r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                err(f"{name}: JSON-LD #{i + 1} невалиден: {exc}")

        if ".github.io" in html:
            err(f"{name}: содержит ссылку на GitHub Pages (*.github.io)")
    ok(f"проверено индексируемых страниц: {len(INDEXABLE)}")


def check_cta_links():
    """«Free AI Diagnostic» → maturity (никогда strategy); стратегия → корень strategy."""
    for rel in INDEXABLE:
        html = read(rel)
        for m in re.finditer(r"Free AI Diagnostic", html):
            tag_start = html.rfind("<", 0, m.start())
            el = html[tag_start:m.start()]
            if el.strip().startswith("<!--"):
                continue
            if "https://maturity.andre.technology/" not in el:
                err(f"{rel}: «Free AI Diagnostic» должна вести на maturity.: {el[:80]}")
            if "strategy.andre.technology" in el:
                err(f"{rel}: «Free AI Diagnostic» НЕ должна вести на strategy.: {el[:80]}")
        # стратегические CTA ведут на корень strategy. (без внутренних путей)
        for m in re.finditer(r'href="(https://strategy\.andre\.technology/[^"]*)"', html):
            if m.group(1) != "https://strategy.andre.technology/":
                err(f"{rel}: ссылка на strategy должна вести на корень: {m.group(1)}")
        for m in re.finditer(r'href="(https://maturity\.andre\.technology/[^"]*)"', html):
            if m.group(1) != "https://maturity.andre.technology/":
                err(f"{rel}: ссылка на maturity должна вести на корень: {m.group(1)}")
    # обе продуктовые ссылки присутствуют на главной
    home = read("index.html")
    if 'href="https://maturity.andre.technology/"' not in home:
        err("index.html: нет ссылки на maturity.andre.technology")
    if 'href="https://strategy.andre.technology/"' not in home:
        err("index.html: нет ссылки на strategy.andre.technology")
    ok("ссылки maturity/strategy корректны")


def check_sitemap():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.isfile(path):
        err("sitemap.xml отсутствует")
        return
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        err(f"sitemap.xml невалиден: {exc}")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [el.text.strip() for el in tree.getroot().findall("sm:url/sm:loc", ns)]
    expected = set(INDEXABLE.values())
    if set(locs) != expected:
        err(f"sitemap.xml: URL-набор не совпадает с индексируемыми страницами: {sorted(set(locs) ^ expected)}")
    for bad in ("/backup/", "/automation/", "/kolesa/", "/napoleon-it/", "/workshop",
                ".github.io", "/report/", "/cabinet/", "/login", "/dashboard"):
        for loc in locs:
            if bad in loc:
                err(f"sitemap.xml: запрещённый URL {loc}")
    if len(locs) != len(set(locs)):
        err("sitemap.xml: дублирующиеся URL")
    ok(f"sitemap.xml валиден, {len(locs)} URL")


def check_robots():
    path = os.path.join(ROOT, "robots.txt")
    if not os.path.isfile(path):
        err("robots.txt отсутствует")
        return
    body = read("robots.txt")
    if "User-agent: *" not in body or "Allow: /" not in body:
        err("robots.txt: нет User-agent: * / Allow: /")
    if "Sitemap: https://andre.technology/sitemap.xml" not in body:
        err("robots.txt: нет ссылки на sitemap")
    for blocked in ("Disallow: /assets", "Disallow: /favicon", "Disallow: /*.css", "Disallow: /*.js"):
        if blocked in body:
            err(f"robots.txt: нельзя блокировать ресурсы рендеринга: {blocked}")
    ok("robots.txt корректен")


def check_manifest():
    try:
        manifest = json.loads(read("site.webmanifest"))
    except (OSError, json.JSONDecodeError) as exc:
        err(f"site.webmanifest: {exc}")
        return
    for field in ("name", "short_name", "description", "start_url", "scope", "icons",
                  "theme_color", "background_color", "display"):
        if field not in manifest:
            err(f"site.webmanifest: нет поля {field}")
    sizes = {icon.get("sizes") for icon in manifest.get("icons", [])}
    if not {"192x192", "512x512"} <= sizes:
        err("site.webmanifest: нужны иконки 192x192 и 512x512")
    ok("site.webmanifest валиден")


def check_noindex_pages():
    for rel in NOINDEX_PAGES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            warn(f"{rel}: файла нет (пропущено)")
            continue
        html = read(rel)
        if 'name="robots" content="noindex' not in html:
            err(f"{rel}: техническая страница должна быть noindex")
        if re.search(r'<link rel="canonical" href="https://andre\.technology/"\s*>', html):
            err(f"{rel}: canonical на главную для скрытия запрещён")
    ok("технические страницы закрыты noindex")


def check_assets():
    for rel in ("favicon.ico", "favicon-16x16.png", "favicon-32x32.png",
                "favicon-48x48.png", "favicon-96x96.png", "apple-touch-icon.png",
                "icon-192.png", "icon-512.png", "assets/og/andre-ai-technologies.png",
                "assets/hero-poster.jpg", "404.html"):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            err(f"нет файла {rel}")
    ok("favicon/OG/404 файлы на месте")


def main():
    print("== SEO check: andre.technology ==")
    check_indexable_pages()
    check_cta_links()
    check_sitemap()
    check_robots()
    check_manifest()
    check_noindex_pages()
    check_assets()
    print()
    if ERRORS:
        print(f"ПРОВАЛ: {len(ERRORS)} ошибок, {len(WARNINGS)} предупреждений")
        sys.exit(1)
    print(f"OK: все проверки пройдены ({len(WARNINGS)} предупреждений)")


if __name__ == "__main__":
    main()
