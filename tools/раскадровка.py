# -*- coding: utf-8 -*-
"""Раскадровка на апрув: по одной картинке на сцену + контактный лист.

Этап, ради которого всё: владелец смотрит СЦЕНЫ и правит их ДО того, как
запускается десятиминутный рендер и кодирование слоя. Раньше эти снимки
делались руками, и каждый раз по-новому — отсюда инструмент.

Снимок берётся не «по часам браузера», а через ту же window.__renderAt(t),
которой снимается финальный слой: иначе на апрув уходит одна картинка, а в
ролик попадает другая (переходы играют по своему времени — грабли §8
гайдбука).

Как звать (из корня репозитория, сервер поднят в папке ролика):

    python3 -m http.server 8903 --directory automation/1/overlay-roles &
    python3 tools/раскадровка.py 8903 automation/1/overlay-roles

    # только перечислить сцены, без снимков
    python3 tools/раскадровка.py 8903 automation/1/overlay-roles --список

Кладёт в <папка ролика>/раскадровка/: s01.png … sNN.png, лист.png (сетка
всех сцен) и сцены.md — таблицу «сцена · секунда · что в кадре», которую
владельцу и показывают.
"""
import os
import re
import sys

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
if not os.path.exists(CHROME):
    CHROME = "/opt/pw-browsers/chromium"

# Сколько ждать после перемотки: у появления элемента переход ~0.5 c, но
# __renderAt выставляет время явно, поэтому ждём только раскладку шрифтов.
ПАУЗА_МС = 120


def сцены_из_страницы(pg):
    """Сцены и их содержимое — из живого DOM, а не разбором HTML регэкспом.

    Разбор текста врёт: часть подписей собирается скриптом страницы, а
    часть лежит внутри svg. Спрашиваем у браузера то, что реально видно.
    """
    return pg.evaluate("""() => {
        const out = [];
        document.querySelectorAll('.scene').forEach((s, i) => {
            const in_ = parseFloat(s.dataset.in || '0');
            const out_ = parseFloat(s.dataset.out || '0');
            const подписи = [];
            s.querySelectorAll('.label,.title,.core,.chip,.cap').forEach(el => {
                const t = (el.textContent || '').trim();
                if (t && подписи.indexOf(t) < 0) подписи.push(t);
            });
            out.push({n: i + 1, id: s.id, in: in_, out: out_,
                      подписи: подписи});
        });
        return out;
    }""")


def момент(сцена):
    """Когда снимать сцену.

    Не середина: к середине часть элементов ещё не вышла. Берём момент
    появления ПОСЛЕДНЕГО элемента сцены плюс полсекунды на его переход —
    так на снимке стоит весь кадр целиком, каким владелец его и увидит.
    """
    t = сцена["in"] + 0.6
    for el in сцена.get("элементы") or []:
        t = max(t, el + 0.6)
    конец = сцена["out"] - 0.1
    return round(min(t, конец) if конец > сцена["in"] else t, 2)


def элементы_сцены(pg, ид):
    return pg.evaluate("""(id) => {
        const s = document.getElementById(id);
        if (!s) return [];
        return Array.from(s.querySelectorAll('[data-in]'))
                    .map(el => parseFloat(el.dataset.in || '0'))
                    .filter(v => v > 0);
    }""", ид)


def лист(pg, снимки, выход, колонок=4):
    """Контактный лист: все сцены одной картинкой.

    Владельцу так быстрее: он видит ритм ролика целиком и тычет в ту
    сцену, которая не нравится, а не открывает двадцать файлов подряд.

    Собирается БРАУЗЕРОМ, а не ffmpeg-ом: сборка ffmpeg рядом с Playwright
    урезана (нет ни демультиплексора image2, ни PNG-декодера — проверено,
    «Error opening input»), а полного ffmpeg на машине агента может не
    быть вовсе. Браузер тут уже открыт и png читает всегда.
    """
    плитки = "".join(
        '<figure><img src="s%02d.png"><figcaption>%d · %.1f c</figcaption>'
        "</figure>" % (c["n"], c["n"], c["кадр"]) for c in снимки)
    html = """<!doctype html><meta charset="utf-8">
<style>
  body { margin:0; background:#0b0b0d; color:#cbd5e1; padding:16px;
         font:13px/1.3 system-ui, sans-serif; }
  .grid { display:grid; grid-template-columns:repeat(%d, 1fr); gap:12px; }
  figure { margin:0; }
  img { width:100%%; display:block; background:#151519; border-radius:6px; }
  figcaption { padding-top:4px; text-align:center; }
</style><div class="grid">%s</div>""" % (колонок, плитки)
    путь_html = os.path.abspath(os.path.join(выход, "лист.html"))
    open(путь_html, "w", encoding="utf-8").write(html)
    ширина = колонок * 260 + 40
    pg.set_viewport_size({"width": ширина, "height": 900})
    pg.goto("file://" + путь_html)
    pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(выход, "лист.png"), full_page=True)
    os.unlink(путь_html)
    return True


def главное():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    порт, папка = sys.argv[1], sys.argv[2]
    только_список = "--список" in sys.argv
    if not os.path.isdir(папка):
        print("Нет папки ролика:", папка)
        return 1
    выход = os.path.join(папка, "раскадровка")
    os.makedirs(выход, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME,
                              args=["--no-sandbox",
                                    "--force-device-scale-factor=1",
                                    "--hide-scrollbars"])
        ctx = b.new_context(viewport={"width": 1080, "height": 1920})
        pg = ctx.new_page()
        # bg=none — прозрачный фон: на апруве смотрят ГРАФИКУ, а дубля
        # может ещё не быть. cover=0 — обложка не закрывает первую сцену.
        pg.goto("http://127.0.0.1:%s/index.html?bg=none&still=1&cover=0&subs=0"
                % порт)
        pg.wait_for_function("window.__ready === true", timeout=30000)
        pg.wait_for_timeout(1500)                # шрифты и первая раскладка

        сцены = сцены_из_страницы(pg)
        if not сцены:
            print("На странице нет ни одной .scene — не тот адрес?")
            b.close()
            return 1
        for c in сцены:
            c["элементы"] = элементы_сцены(pg, c["id"])
            c["кадр"] = момент(c)

        строки = ["# Раскадровка на апрув",
                  "",
                  "| # | секунда | длит. | что в кадре |",
                  "|---|---|---|---|"]
        for c in сцены:
            строки.append("| %d | %.2f | %.1f c | %s |"
                          % (c["n"], c["кадр"], c["out"] - c["in"],
                             " · ".join(c["подписи"]) or "—"))
            print("сцена %2d  %6.2f c  %4.1f c  %s"
                  % (c["n"], c["кадр"], c["out"] - c["in"],
                     " · ".join(c["подписи"])[:70]))

        if только_список:
            b.close()
            return 0

        for c in сцены:
            pg.evaluate("t => window.__renderAt(t)", c["кадр"])
            pg.wait_for_timeout(ПАУЗА_МС)
            pg.screenshot(path=os.path.join(выход, "s%02d.png" % c["n"]),
                          omit_background=True)
        лист(pg, сцены, выход)
        b.close()

    строки += ["", "Снято: %d сцен. Контактный лист — `лист.png`." % len(сцены)]
    open(os.path.join(выход, "сцены.md"), "w", encoding="utf-8").write(
        "\n".join(строки) + "\n")
    print("\nГотово: %s (%d кадров + лист.png + сцены.md)" % (выход, len(сцены)))
    return 0


sys.exit(главное())
