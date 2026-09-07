# -*- coding: utf-8 -*-
"""Браузерный стенд семинара: automation/1/seminar/.

Правка вёрстки проверяется РЕАЛЬНЫМ рендером, а не строковым тестом
(LECTURE-GUIDE §8). Свип: 13 слайдов × набор окон × две темы. Ищем ровно то,
что заказчик называет дефектом: прокрутку, выход за экран, наезд на шапку,
выезд текста за карточку и зазор у края меньше 12px.

    python3 tools/seminar_check.py            # весь свип
    python3 tools/seminar_check.py --shots DIR  # ещё и снимки экрана
"""
import http.server
import os
import socketserver
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
URL_PATH = "/automation/1/seminar/"

# Набор из LECTURE-GUIDE §8 плюс граничные окна семинара: 1380x864 — это
# ровно веб-форма (там боковые стрелки и налезали на плитки), 768x820 —
# первая точка веб-формы, 360x640 — самый узкий телефон.
SIZES = [
    (1440, 900), (1920, 1080), (1590, 1644), (1380, 864),
    (868, 826), (795, 822), (768, 820),
    (490, 826), (390, 844), (376, 667), (360, 640),
]
MIN_GAP = 12


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


# Один замер на слайд: всё, что нужно проверить, снимается за один заход
# в страницу — иначе свип на 13 слайдов × 12 окон × 2 темы идёт минутами.
PROBE = r"""
(minGap) => {
  const bad = [];
  const de = document.documentElement;
  const W = window.innerWidth, H = window.innerHeight;
  const idx = (() => { const s = [...document.querySelectorAll('.slide')];
    return s.findIndex(x => x.classList.contains('is-on')); })();
  const tag = 'слайд ' + (idx + 1);

  if (de.scrollWidth > W + 1) bad.push(tag + ': страница шире окна (' + de.scrollWidth + ' > ' + W + ')');
  if (de.scrollHeight > H + 1) bad.push(tag + ': страница выше окна (' + de.scrollHeight + ' > ' + H + ')');

  const deck = document.getElementById('deck').getBoundingClientRect();
  if (deck.left < minGap - 0.5) bad.push(tag + ': зазор слева ' + deck.left.toFixed(1));
  if (W - deck.right < minGap - 0.5) bad.push(tag + ': зазор справа ' + (W - deck.right).toFixed(1));
  if (deck.top < -0.5) bad.push(tag + ': холст выше экрана на ' + (-deck.top).toFixed(1));
  if (deck.bottom > H + 0.5) bad.push(tag + ': холст ниже экрана на ' + (deck.bottom - H).toFixed(1));

  const slide = document.querySelector('.slide.is-on');
  const hdr = document.getElementById('lecture-header').getBoundingClientRect();
  const head = slide.querySelector('.s-head').getBoundingClientRect();
  if (head.top < hdr.bottom - 0.5)
    bad.push(tag + ': заголовок под шапкой на ' + (hdr.bottom - head.top).toFixed(1));

  const arrow = document.getElementById('nav-next').getBoundingClientRect();
  const grid = slide.querySelector('.grid').getBoundingClientRect();
  const overlapsArrow = !(grid.right < arrow.left || grid.left > arrow.right ||
                          grid.bottom < arrow.top || grid.top > arrow.bottom);
  if (overlapsArrow) bad.push(tag + ': плитки заходят под стрелку листания');

  slide.querySelectorAll('.tile').forEach((t, i) => {
    const r = t.getBoundingClientRect();
    if (r.left < deck.left - 0.5 || r.right > deck.right + 0.5)
      bad.push(tag + ' плитка ' + (i + 1) + ': выходит за холст по ширине');
    if (r.top < deck.top - 0.5 || r.bottom > deck.bottom + 0.5)
      bad.push(tag + ' плитка ' + (i + 1) + ': выходит за холст по высоте');
    if (t.scrollHeight > t.clientHeight + 1)
      bad.push(tag + ' плитка ' + (i + 1) + ': содержимое выше карточки на ' + (t.scrollHeight - t.clientHeight));
    if (t.scrollWidth > t.clientWidth + 1)
      bad.push(tag + ' плитка ' + (i + 1) + ': содержимое шире карточки на ' + (t.scrollWidth - t.clientWidth));
    t.querySelectorAll('.t-name,.t-lead,.t-trig').forEach(el => {
      if (el.offsetParent === null) return;                 // скрыт на этой форме
      const er = el.getBoundingClientRect();
      if (er.right > r.right - 1 || er.left < r.left - 1 || er.bottom > r.bottom - 1)
        bad.push(tag + ' плитка ' + (i + 1) + ': текст «' + el.textContent.slice(0, 18) + '» вышел за карточку');
      if (el.scrollWidth > el.clientWidth + 1)
        bad.push(tag + ' плитка ' + (i + 1) + ': строка «' + el.textContent.slice(0, 18) + '» не помещается');
    });
  });

  // Плитки не должны налезать друг на друга
  const rects = [...slide.querySelectorAll('.tile')].map(t => t.getBoundingClientRect());
  for (let a = 0; a < rects.length; a++)
    for (let b = a + 1; b < rects.length; b++) {
      const p = rects[a], q = rects[b];
      const ov = Math.min(p.right, q.right) - Math.max(p.left, q.left);
      const oy = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
      if (ov > 1 && oy > 1) bad.push(tag + ': плитки ' + (a + 1) + ' и ' + (b + 1) + ' налезают друг на друга');
    }
  return bad;
}
"""

POP_PROBE = r"""
(noScroll) => {
  const bad = [];
  const W = window.innerWidth, H = window.innerHeight;
  const card = document.getElementById('pop-card');
  const r = card.getBoundingClientRect();
  if (r.left < -0.5 || r.right > W + 0.5) bad.push('карточка шире окна');
  if (r.top < -0.5 || r.bottom > H + 0.5) bad.push('карточка выше окна');
  if (card.scrollWidth > card.clientWidth + 1) bad.push('в карточке появилась горизонтальная прокрутка');
  // На компьютере карточка обязана помещаться целиком: заказчик просил
  // «чтобы всплывающие штуки вмещались без пролистывания». На телефоне
  // листать вниз разрешено — там столько места просто нет.
  if (noScroll && card.scrollHeight > card.clientHeight + 2)
    bad.push('карточка не помещается: нужно листать на ' + (card.scrollHeight - card.clientHeight) + 'px');
  if (document.documentElement.scrollWidth > W + 1) bad.push('страница поехала вбок при открытой карточке');
  if (document.documentElement.scrollHeight > H + 1) bad.push('страница поехала вниз при открытой карточке');
  card.querySelectorAll('.flow-col li,.chip-lg,.row-v,.meter-v,.pop-name,.roles li').forEach(el => {
    if (el.scrollWidth > el.clientWidth + 1)
      bad.push('в карточке не помещается «' + el.textContent.trim().slice(0, 22) + '»');
  });
  return bad;
}
"""


def main():
    shots = None
    if "--shots" in sys.argv:
        shots = sys.argv[sys.argv.index("--shots") + 1]
        os.makedirs(shots, exist_ok=True)

    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    from playwright.sync_api import sync_playwright

    srv, port = serve()
    base = "http://127.0.0.1:%d%s" % (port, URL_PATH)
    problems, checked = [], 0

    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME,
                                args=["--no-sandbox", "--disable-dev-shm-usage"])
        for theme in ("dark", "light"):
            for w, h in SIZES:
                page = br.new_page(viewport={"width": w, "height": h})
                page.goto(base + "?theme=" + theme, wait_until="load")
                page.wait_for_selector("body.fit-ready", timeout=15000)
                total = page.eval_on_selector_all(".slide", "n => n.length")
                for i in range(total):
                    page.evaluate("i => window.gotoSlide(i)", i)
                    page.wait_for_timeout(30)
                    for msg in page.evaluate(PROBE, MIN_GAP):
                        problems.append("%dx%d %s: %s" % (w, h, theme, msg))
                    checked += 1
                    if shots and (w, h) in ((1440, 900), (390, 844)) and theme == "dark":
                        page.screenshot(path=os.path.join(shots, "s%02d-%dx%d.png" % (i + 1, w, h)))
                # Карточки: первая и последняя плитка каждого слайда
                for i in (0, total // 2, total - 1):
                    page.evaluate("i => window.gotoSlide(i)", i)
                    for t in (0, 9):
                        page.evaluate(
                            "([i,t]) => document.querySelector('.slide.is-on').querySelectorAll('.tile')[t].click()",
                            [i, t])
                        page.wait_for_timeout(80)
                        for msg in page.evaluate(POP_PROBE, w >= 768):
                            problems.append("%dx%d %s слайд %d плитка %d: %s" % (w, h, theme, i + 1, t + 1, msg))
                        if shots and (w, h) in ((1440, 900), (390, 844)) and theme == "dark" and t == 0:
                            page.screenshot(path=os.path.join(shots, "pop-s%02d-%dx%d.png" % (i + 1, w, h)))
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(60)
                # Панель «Текст»
                page.click("#notes-toggle")
                page.wait_for_timeout(520)
                for msg in page.evaluate(PROBE, MIN_GAP):
                    problems.append("%dx%d %s (панель открыта): %s" % (w, h, theme, msg))
                if shots and (w, h) in ((1440, 900), (390, 844)) and theme == "dark":
                    page.screenshot(path=os.path.join(shots, "notes-%dx%d.png" % (w, h)))
                page.click("#notes-close")
                page.wait_for_timeout(420)
                page.close()
        br.close()
    srv.shutdown()

    if problems:
        print("НАЙДЕНО %d дефектов (проверено %d слайдо-замеров):" % (len(problems), checked))
        seen = set()
        for p in problems:
            if p in seen:
                continue
            seen.add(p)
            print("  ·", p)
        sys.exit(1)
    print("Свип чистый: %d слайдо-замеров, %d окон × 2 темы, карточки и панель — без дефектов"
          % (checked, len(SIZES)))


if __name__ == "__main__":
    main()
