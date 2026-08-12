#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Инвентарь слайдов лекции для сценариев подсветки.

`animate_slide.py` ищет элемент по ТОЧНОМУ тексту (`text` в сценарии), поэтому
сценарии нельзя писать «на глаз»: пробелы, неразрывные дефисы и вложенность
решают всё. Инструмент открывает лекцию, проходит слайды и выкладывает по
каждому: какие тексты вообще есть, сколько у них потомков (по этому
`findTarget` выбирает элемент), что находится на уровень и два выше (поле `up`),
геометрию и слова речи с таймингом из `build/timings/`.

    python3 tools/fx_inventory.py --vendor <каталог>        # все слайды
    python3 tools/fx_inventory.py --slides 5,6,7            # только эти

Результат: build/fx-inventory/lecture1-slideNN.json (+ index.json со сводкой).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from record_lecture import (ROOT, W, H, CHROME_OFF, PORT, serve, vendor_route,
                            check_font)

BUILD = os.path.join(ROOT, "build")
OUT_DIR = os.path.join(BUILD, "fx-inventory")

# Снимаем всё, что несёт текст: заголовки, подписи, карточки, пункты списков.
# Сразу отдаём нормализованный текст — ровно в том виде, в каком его сравнивает
# findTarget (`replace(/\s+/g,' ').trim()`).
SCAN_JS = r"""
() => {
  const slide = document.querySelector('.slide-container.opacity-100');
  if (!slide) return null;
  const norm = e => (e.textContent || '').replace(/\s+/g, ' ').trim();
  const box = e => { const r = e.getBoundingClientRect();
    return [Math.round(r.left), Math.round(r.top),
            Math.round(r.width), Math.round(r.height)]; };
  const all = [...slide.querySelectorAll('*')];
  const seen = new Map();
  for (const el of all){
    const t = norm(el);
    if (!t || t.length > 140) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    const prev = seen.get(t);
    // Тот же критерий, что у findTarget: побеждает элемент с наименьшим
    // числом потомков — самый «узкий» носитель этого текста.
    if (!prev || el.children.length < prev.el.children.length)
      seen.set(t, {el: el, n: (seen.get(t)?.n || 0) + 1});
    else prev.n++;
  }
  const out = [];
  for (const [text, v] of seen){
    const el = v.el, p1 = el.parentElement, p2 = p1 && p1.parentElement;
    out.push({
      text: text,
      tag: el.tagName.toLowerCase(),
      cls: (el.className && el.className.baseVal !== undefined
              ? el.className.baseVal : el.className || '').slice(0, 120),
      kids: el.children.length,
      rect: box(el),
      dubl: v.n > 1,
      up1: p1 ? {text: norm(p1).slice(0, 90), rect: box(p1),
                 cls: (p1.className || '').toString().slice(0, 120)} : null,
      up2: p2 ? {text: norm(p2).slice(0, 90), rect: box(p2),
                 cls: (p2.className || '').toString().slice(0, 120)} : null,
    });
  }
  out.sort((a, b) => a.rect[1] - b.rect[1] || a.rect[0] - b.rect[0]);
  return {title: (slide.querySelector('h1,h2') || {}).textContent
            ? (slide.querySelector('h1,h2').textContent || '').replace(/\s+/g,' ').trim()
            : '', items: out};
}
"""


def words_of(lecture, slide):
    """Слова речи слайда с таймингом (что реально сказано голосом)."""
    p = os.path.join(BUILD, "timings",
                     "lecture%d-slide%02d.json" % (lecture, slide))
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding="utf-8")).get("words", [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lecture", type=int, default=1)
    ap.add_argument("--slides", help="список номеров через запятую (по умолчанию все)")
    ap.add_argument("--vendor")
    ap.add_argument("--allow-fallback-fonts", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    os.makedirs(OUT_DIR, exist_ok=True)
    want = ([int(x) for x in args.slides.split(",")] if args.slides else None)

    srv, index = serve(), []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                executable_path=os.environ.get("CHROMIUM_PATH") or None,
                args=["--no-sandbox", "--hide-scrollbars"])
            ctx = browser.new_context(viewport={"width": W, "height": H},
                                      device_scale_factor=1,
                                      reduced_motion="reduce")
            if args.vendor:
                ctx.route("**/*", vendor_route(args.vendor))
            page = ctx.new_page()
            page.goto("http://127.0.0.1:%d/automation/%d/" % (PORT, args.lecture),
                      wait_until="load", timeout=120000)
            page.wait_for_timeout(3000)
            page.add_style_tag(content=CHROME_OFF)
            page.evaluate("() => document.querySelectorAll("
                          "'#start-overlay,#intro-overlay').forEach(e => e.remove())")
            check_font(page, args.allow_fallback_fonts)
            total = page.evaluate(
                "() => document.querySelectorAll('.slide-container').length")
            print("слайдов: %d" % total)

            for n in range(1, total + 1):
                if n > 1:
                    page.evaluate("() => window.nextSlide && window.nextSlide()")
                    page.wait_for_timeout(220)
                if want and n not in want:
                    continue
                page.wait_for_timeout(400)
                data = page.evaluate(SCAN_JS)
                if not data:
                    print("  слайд %d — активного контейнера нет" % n)
                    continue
                data["slide"] = n
                data["words"] = words_of(args.lecture, n)
                data["speech"] = " ".join(w["w"] for w in data["words"])
                dst = os.path.join(OUT_DIR, "lecture%d-slide%02d.json"
                                   % (args.lecture, n))
                json.dump(data, open(dst, "w", encoding="utf-8"),
                          ensure_ascii=False, indent=1)
                index.append({"slide": n, "title": data["title"],
                              "элементов": len(data["items"]),
                              "слов": len(data["words"])})
                print("  слайд %2d · %-42s элементов %3d · слов %3d"
                      % (n, data["title"][:42], len(data["items"]),
                         len(data["words"])))
            ctx.close()
            browser.close()
    finally:
        srv.shutdown()

    json.dump(index, open(os.path.join(OUT_DIR, "index.json"), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nготово: %s" % os.path.relpath(OUT_DIR, ROOT))


if __name__ == "__main__":
    main()
