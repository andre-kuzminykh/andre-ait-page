# -*- coding: utf-8 -*-
"""Рендер оверлея прозрачным слоем, кадр в кадр (см. window.__renderAt).

Время анимаций страница выставляет сама по таймлайну — виртуальное время
браузера не используется: под паузой он не отдаёт снимок вообще.
Кадр N — ровно N/FPS секунды таймлайна ВИДЕО (?cover=0, обложки в слое нет).
"""
import os, sys, time, glob
from playwright.sync_api import sync_playwright

FPS = 30
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 143.0
BASE = "/tmp/claude-0/-home-user/5d638d64-9e0d-50f3-9130-4246e6d37007/scratchpad"
OUT, LOG = BASE + "/frames", BASE + "/render.log"
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(OUT + "/*.png"):
    os.unlink(f)
open(LOG, "w").write("")
def log(m): open(LOG, "a").write(m + "\n")

n, t0 = int(DUR * FPS), time.time()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                          args=["--no-sandbox", "--force-device-scale-factor=1", "--hide-scrollbars"])
    ctx = b.new_context(viewport={"width": 1080, "height": 1920})
    pg = ctx.new_page()
    pg.goto("http://127.0.0.1:8903/index.html?bg=none&still=1&cover=0")
    pg.wait_for_function("window.__ready === true", timeout=30000)
    pg.wait_for_timeout(1500)                        # шрифты и первая раскладка
    for i in range(n):
        pg.evaluate("t => window.__renderAt(t)", i / FPS)
        pg.screenshot(path="%s/f%05d.png" % (OUT, i), omit_background=True)
        if i and i % 200 == 0:
            el = time.time() - t0
            log("кадр %d из %d (%.0f%%), %.0f c прошло, ~%.0f c осталось"
                % (i, n, 100.0 * i / n, el, el / i * (n - i)))
    b.close()
log("КАДРЫ ГОТОВЫ: %d за %.0f c" % (n, time.time() - t0))
