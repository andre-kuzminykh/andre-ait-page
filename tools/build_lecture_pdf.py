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

# Лист печати описывает САМА страница: 1380x864 CSS-пикселя = 14.375x9 дюйма
# при 96 dpi. Только так раскладка печати совпадает с экранной один в один —
# см. комментарий у page.pdf ниже. Жёсткие размеры html/body гарантируют ровно
# одну страницу на слайд.
PAGE_CSS = ('<style id="pdf-page">@page{size:14.375in 9in;margin:0}'
            'html,body{width:%dpx;height:%dpx;}</style>'
            % (FORM["width"], FORM["height"]))


# Градиентный заголовок печатается слоем прозрачности, и край этого слоя
# Chromium рисует волоском — в PDF вокруг цветной половины заголовка
# появлялась тонкая рамка (на экране её нет). Убираем сам слой: перед печатью
# каждая буква получает СПЛОШНОЙ цвет, взятый из той же линейной шкалы
# #8B5CF6 → #F97316 по её месту в строке. Вид тот же, текст остаётся текстом,
# а background-clip:text со страницы уходит вместе с рамкой.
JS_SPLIT_GRADIENT = """
() => {
  const slide = document.querySelector('.slide-container.opacity-100')
             || document.querySelector('.slide-container');
  if (!slide) return [];
  const A = [0x8B, 0x5C, 0xF6], B = [0xF9, 0x73, 0x16];
  const hex = c => '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
  const out = [];
  for (const el of slide.querySelectorAll('h1 .text-solar, h2 .text-solar')) {
    if (el.dataset.pdfSplit) continue;
    const w0 = el.getBoundingClientRect().width;
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = []; let n;
    while ((n = walker.nextNode())) nodes.push(n);
    for (const node of nodes) {
      const frag = document.createDocumentFragment();
      // Мягкий перенос остаётся ПРИ своей букве: в отдельном span он
      // перестал бы работать как место переноса, и длинные заголовки
      // («остано-виться») сломали бы строку не там.
      const chars = [];
      for (const ch of node.nodeValue) {
        if (ch === '\u00AD' && chars.length) chars[chars.length - 1] += ch;
        else chars.push(ch);
      }
      for (const ch of chars) {
        const sp = document.createElement('span');
        sp.className = 'pdf-ch';
        sp.textContent = ch;
        frag.appendChild(sp);
      }
      node.parentNode.replaceChild(frag, node);
    }
    const box = el.getBoundingClientRect();
    for (const sp of el.querySelectorAll('.pdf-ch')) {
      const r = sp.getBoundingClientRect();
      let t = box.width > 0 ? ((r.left + r.width / 2) - box.left) / box.width : 0;
      t = Math.max(0, Math.min(1, t));
      const c = hex(A.map((a, i) => Math.round(a + (B[i] - a) * t)));
      sp.setAttribute('style', 'background:none !important;background-image:none !important;'
        + 'color:' + c + ' !important;-webkit-text-fill-color:' + c + ' !important');
    }
    el.setAttribute('style', 'background:none !important;background-image:none !important;'
      + '-webkit-text-fill-color:currentColor !important');
    el.dataset.pdfSplit = '1';
    out.push([w0, el.getBoundingClientRect().width]);
  }
  return out;
}
"""


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

    # Шрифт вшиваем В САМУ СТРАНИЦУ, до первой загрузки. Через add_style_tag
    # после открытия — нельзя: подгонщик к тому моменту уже измерил колоду
    # вариативным Montserrat, метрики статического чуть шире, и заголовок
    # обложки вылезал за края страницы срезанным с обеих сторон. Пересчёт
    # после подмены шрифта не происходит, потому что содержимое не менялось.
    printable = os.path.join(ROOT, "build", "lecture-%d-print.html" % lecture)
    html = open(src, encoding="utf-8").read()
    html = html.replace("</head>", "<style id=\"pdf-fonts\">%s</style>%s</head>"
                        % (static_montserrat_css(), PAGE_CSS), 1)
    os.makedirs(os.path.dirname(printable), exist_ok=True)
    open(printable, "w", encoding="utf-8").write(html)

    url = "file://%s?theme=%s" % (printable, theme)
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
        # Начертания с data-ссылками браузер тянет ЛЕНИВО, по мере надобности,
        # и document.fonts.ready успевает разрешиться раньше них. Подгонщик в
        # этот момент меряет колоду ещё запасным шрифтом — на обложке заголовок
        # от этого вылезал за края страницы срезанным с обеих сторон.
        # Поэтому: догружаем ВСЕ начертания принудительно...
        page.evaluate("""async () => {
          await Promise.all([...document.fonts].map(f => f.load().catch(() => {})));
          await document.fonts.ready;
        }""")
        # ...и заставляем пересчитать раскладку уже с ними. Полный пересчёт
        # запускает только смена ФОРМЫ, поэтому уходим на телефонную и
        # возвращаемся: ресайз внутри одной формы кегли не трогает.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(1500)
        page.set_viewport_size(dict(FORM))
        page.wait_for_timeout(2500)

        actual = page.evaluate("() => document.documentElement.className || 'светлая'")
        rl.check_font(page, allow_fallback=False)      # Montserrat, а не системный
        total = page.evaluate("() => document.querySelectorAll('.slide-container').length")
        print("   тема: %s, слайдов: %d" % (actual, total))

        drift = 0.0
        for i in range(total):
            page.wait_for_timeout(420)                 # дать подгонке встать
            # Заголовок разбираем на буквы ПОСЛЕ того, как подгонка встала:
            # кегль и переносы уже посчитаны, меняются только заливки.
            for w0, w1 in (page.evaluate(JS_SPLIT_GRADIENT) or []):
                drift = max(drift, abs(w1 - w0))
            # Размер листа берётся ИЗ СТРАНИЦЫ (@page в PAGE_CSS), а не из
            # аргументов. С width/height Chromium раскладывал печать сам и
            # разъезжался с экраном: содержимое выходило шире листа, и обложку
            # срезало с обеих сторон, а фон последних слайдов не доходил до краёв.
            writer.append(PdfReader(io.BytesIO(page.pdf(
                print_background=True, prefer_css_page_size=True))))
            pages += 1
            if i < total - 1:
                page.evaluate("() => window.nextSlide && window.nextSlide()")
        if drift:
            print("   заголовки разобраны на буквы, ширина сдвинулась не больше чем на %.2f px" % drift)
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
