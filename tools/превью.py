# -*- coding: utf-8 -*-
"""Превью анимации сцены: короткий ролик на апрув, до полного рендера.

Картинка показывает КАДР, но не показывает, как он собирается: в каком
порядке выходят элементы, где горит кольцо, как сцена уходит. Владелец
это видел только в готовом ролике — то есть после десяти минут рендера и
четырёх минут кодирования.

Здесь рендерится ОДНА сцена (или указанный отрезок) тем же покадровым
способом, что и финальный слой, и склеивается в анимированный WebP —
его открывает любой браузер и показывает телефон.

Как звать (из корня репозитория, сервер поднят в папке ролика):

    python3 -m http.server 8903 --directory automation/1/overlay-roles &
    python3 tools/превью.py 8903 automation/1/overlay-roles 7      # сцена 7
    python3 tools/превью.py 8903 automation/1/overlay-roles все    # все сцены
    python3 tools/превью.py 8903 automation/1/overlay-roles 41 52  # отрезок

Кладёт в <папка ролика>/раскадровка/: s07-анимация.webp и т.д.

Частота превью — 15 к/с вместо 30 и половинный размер: движение видно
целиком, а ждать вдвое меньше. Для апрува этого достаточно; финальный
слой всегда рендерится в полный размер и 30 к/с (tools/render_overlay.py).
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
if not os.path.exists(CHROME):
    CHROME = "/opt/pw-browsers/chromium"

FPS = 15                      # превью: движение видно, кадров вдвое меньше
ШИРИНА, ВЫСОТА = 540, 960     # половина от 1080×1920
ХВОСТ = 0.4                   # чуть после конца сцены — виден уход графики


def сцены_страницы(pg):
    return pg.evaluate("""() => Array.from(document.querySelectorAll('.scene'))
        .map((s, i) => ({n: i + 1, id: s.id,
                         in: parseFloat(s.dataset.in || '0'),
                         out: parseFloat(s.dataset.out || '0')}))""")


def снять(pg, выход, имя, t0, t1):
    """Кадры отрезка → анимированный WebP.

    WebP, а не GIF: GIF режет цвет до 256 и превращает градиенты сияния в
    полосы — как раз то, что на этих роликах и смотрят. WebP умеет
    прозрачность и весит меньше.
    """
    from PIL import Image
    кадры, t, начало = [], t0, time.time()
    while t <= t1:
        pg.evaluate("v => window.__renderAt(v)", round(t, 3))
        буфер = pg.screenshot(omit_background=True)
        import io
        кадры.append(Image.open(io.BytesIO(буфер)).convert("RGBA"))
        t += 1.0 / FPS
    путь = os.path.join(выход, имя)
    кадры[0].save(путь, save_all=True, append_images=кадры[1:],
                  duration=int(1000 / FPS), loop=0, format="WEBP",
                  lossless=False, quality=70, method=4)
    сек = time.time() - начало
    print("  %s — %d кадров, %.1f c речи, собрано за %.0f c, %.1f МБ"
          % (имя, len(кадры), t1 - t0, сек,
             os.path.getsize(путь) / 1048576.0))
    return сек


def главное():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    порт, папка, что = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.isdir(папка):
        print("Нет папки ролика:", папка)
        return 1
    выход = os.path.join(папка, "раскадровка")
    os.makedirs(выход, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME,
                              args=["--no-sandbox", "--hide-scrollbars"])
        ctx = b.new_context(viewport={"width": ШИРИНА, "height": ВЫСОТА},
                            device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto("http://127.0.0.1:%s/index.html?bg=none&still=1&cover=0&subs=0"
                % порт)
        pg.wait_for_function("window.__ready === true", timeout=30000)
        pg.wait_for_timeout(1500)
        # Страница свёрстана под 1080 — ужимаем целиком, чтобы вся геометрия
        # осталась той же, что в финальном слое, и превью не врало.
        pg.evaluate("""(k) => {
            const b = document.body;
            b.style.transformOrigin = '0 0';
            b.style.transform = 'scale(' + k + ')';
        }""", ШИРИНА / 1080.0)

        сцены = сцены_страницы(pg)
        задания = []
        if что == "все":
            задания = [("s%02d-анимация.webp" % c["n"], c["in"], c["out"] + ХВОСТ)
                       for c in сцены]
        elif что.isdigit() and len(sys.argv) == 4:
            c = next((x for x in сцены if x["n"] == int(что)), None)
            if not c:
                print("Нет сцены", что, "— всего", len(сцены))
                b.close()
                return 1
            задания = [("s%02d-анимация.webp" % c["n"], c["in"], c["out"] + ХВОСТ)]
        else:
            t0, t1 = float(sys.argv[3]), float(sys.argv[4])
            задания = [("отрезок-%g-%g.webp" % (t0, t1), t0, t1)]

        всего = 0
        for имя, t0, t1 in задания:
            всего += снять(pg, выход, имя, t0, t1)
        b.close()
    print("\nГотово: %s (%d файлов, %.0f c всего)" % (выход, len(задания), всего))
    return 0


sys.exit(главное())
