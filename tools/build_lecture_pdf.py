# -*- coding: utf-8 -*-
"""PDF-версия лекции: 42 слайда, по одному на страницу.

    python3 tools/build_lecture_pdf.py 3                 # → build/lecture-3-light.pdf
    python3 tools/build_lecture_pdf.py 3 --theme dark
    python3 tools/build_lecture_pdf.py 3 --out ~/preza.pdf

Печатает ЧИСТУЮ страницу (tools/build_clean_lecture.py): без лого, кнопок,
стрелок, кружка с видео и теста. Если её нет или она устарела — собирается
заново перед печатью, чтобы PDF не отставал от колоды.

Почему page.pdf(), а не скриншоты: Chromium отдаёт векторную страницу и
ВШИВАЕТ в файл подмножества всех использованных шрифтов — Montserrat и
иконочный Phosphor. Текст остаётся текстом: его можно выделить и найти
поиском, и он не рассыплется на чужой машине, где этих шрифтов нет.
Скриншоты дали бы картинки и потеряли бы и то, и другое.

ТРИ МЕСТА, ГДЕ ЭТО ЛЕГКО СЛОМАТЬ:

1. Размер бумаги обязан совпадать с формой (1380x864). page.pdf() подгоняет
   окно под бумагу, а подгонщик слушает resize: другая бумага — другое окно —
   другой зум — другие переносы, и PDF разойдётся с сайтом.
2. Печатать надо в режиме screen. По умолчанию Chromium переключается на
   print-стили, а колода под печать не размечена.
3. Тема форсится параметром ?theme=light. Без него страница берёт тему из
   localStorage, а по умолчанию путь ТЁМНЫЙ — и «белый вариант» вышел бы
   чёрным.
"""
import argparse
import io
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import record_lecture as rl          # noqa: E402  vendor_route + проба шрифта
import build_clean_lecture as clean  # noqa: E402

FORM = {"width": 1380, "height": 864}


def chromium_path():
    env = os.environ.get("CHROMIUM_PATH")
    if env and os.path.exists(env):
        return env
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    for name in sorted(os.listdir(base) if os.path.isdir(base) else [], reverse=True):
        if name.startswith("chromium-"):
            exe = os.path.join(base, name, "chrome-linux", "chrome")
            if os.path.exists(exe):
                return exe
    return None



def static_montserrat_css():
    """@font-face со СТАТИЧЕСКИМИ начертаниями Montserrat, вшитыми в base64.

    Зачем: Google отдаёт браузеру ВАРИАТИВНЫЙ Montserrat — один файл на
    подмножество с осью веса. На экране он безупречен, но Chromium не вшивает
    вариативные шрифты в PDF и молча печатает системным. В первом собранном
    файле так и вышло: внутри лежали только Phosphor и LiberationSans, а весь
    текст лекции был напечатан не своим шрифтом.

    Поэтому берём статические начертания (@fontsource/montserrat, тот же
    Montserrat под OFL) и вшиваем их в страницу как data-URI. Диапазоны
    unicode-range и веса читаем из кэша Google, чтобы разбиение по
    подмножествам осталось ровно тем же, что на сайте.
    """
    import base64
    static = os.path.join(ROOT, "vendor", "fonts-static")
    if not os.path.isdir(static):
        tmp = os.path.join(ROOT, "build", "fontsource")
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp, exist_ok=True)
        subprocess.run(["npm", "pack", "@fontsource/montserrat"], cwd=tmp,
                       check=True, stdout=subprocess.DEVNULL)
        tgz = [f for f in os.listdir(tmp) if f.endswith(".tgz")][0]
        subprocess.run(["tar", "xzf", tgz], cwd=tmp, check=True)
        shutil.copytree(os.path.join(tmp, "package", "files"), static)
        shutil.rmtree(tmp, ignore_errors=True)

    google = os.path.join(ROOT, "vendor", "fonts", "css2.css")
    if not os.path.isfile(google):
        sys.exit("нет %s — сначала python3 tools/lecture_check.py vendor" % google)
    src = open(google, encoding="utf-8").read()

    out, used, missing = [], 0, []
    for m in re.finditer(r"/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", src, re.S):
        subset, body = m.group(1), m.group(2)
        w = re.search(r"font-weight:\s*(\d+)", body)
        ur = re.search(r"unicode-range:\s*([^;]+);", body)
        if not w:
            continue
        path = os.path.join(static, "montserrat-%s-%s-normal.woff2" % (subset, w.group(1)))
        if not os.path.isfile(path):
            missing.append(os.path.basename(path))
            continue
        b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
        out.append("@font-face{font-family:'Montserrat';font-style:normal;"
                   "font-display:block;font-weight:%s;"
                   "src:url(data:font/woff2;base64,%s) format('woff2');%s}"
                   % (w.group(1),
                      b64,
                      ("unicode-range:%s;" % ur.group(1).strip()) if ur else ""))
        used += 1
    if not used:
        sys.exit("не собрал ни одного начертания Montserrat — PDF вышел бы системным шрифтом")
    if missing:
        print("   ВНИМАНИЕ: нет статических файлов: %s" % ", ".join(missing[:4]))
    print("   статических начертаний Montserrat вшито: %d" % used)
    return "\n".join(out)


def build(lecture, out_path, theme):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter

    # Чистую страницу пересобираем всегда: иначе PDF тихо отстанет от колоды.
    src = os.path.join(ROOT, "automation", str(lecture), "clean", "index.html")
    clean.build(lecture, src)

    url = "file://%s?theme=%s" % (src, theme)
    writer, pages = PdfWriter(), 0
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium_path(), args=["--no-sandbox"])
        ctx = br.new_context(viewport=dict(FORM), device_scale_factor=1,
                             reduced_motion="reduce")
        ctx.route("**/*", rl.vendor_route(os.path.join(ROOT, "vendor")))
        page = ctx.new_page()
        page.goto(url, wait_until="load", timeout=180000)
        page.wait_for_timeout(5000)
        # Печать в режиме screen: под печать колода не размечена.
        page.emulate_media(media="screen")
        # Статический Montserrat — ДО замера шрифта и до печати.
        page.add_style_tag(content=static_montserrat_css())
        page.wait_for_timeout(1200)
        page.evaluate("() => document.fonts.ready")

        actual = page.evaluate("() => document.documentElement.className || 'светлая'")
        rl.check_font(page, allow_fallback=False)      # Montserrat, а не системный
        total = page.evaluate("() => document.querySelectorAll('.slide-container').length")
        print("   тема: %s, слайдов: %d" % (actual, total))

        for i in range(total):
            page.wait_for_timeout(420)                 # дать подгонке встать
            writer.append(PdfReader(io.BytesIO(page.pdf(
                width="%dpx" % FORM["width"], height="%dpx" % FORM["height"],
                print_background=True, prefer_css_page_size=False,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}))))
            pages += 1
            if i < total - 1:
                page.evaluate("() => window.nextSlide && window.nextSlide()")
        ctx.close()
        br.close()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        writer.write(f)
    size = os.path.getsize(out_path) / 1024 / 1024
    print("собран PDF: %s (%d страниц, %.1f МБ)" % (out_path, pages, size))
    return 0


def main():
    ap = argparse.ArgumentParser(description="PDF-версия лекции, слайд на страницу.")
    ap.add_argument("lecture", type=int)
    ap.add_argument("--theme", choices=["light", "dark"], default="light")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, "build", "lecture-%d-%s.pdf" % (a.lecture, a.theme))
    return build(a.lecture, os.path.abspath(os.path.expanduser(out)), a.theme)


if __name__ == "__main__":
    sys.exit(main())
