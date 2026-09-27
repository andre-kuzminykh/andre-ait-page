# -*- coding: utf-8 -*-
"""Автономный HTML колоды: открывается двойным щелчком, без сервера и сети.

Зачем. Отправленный владельцу `automation/5/v2/index.html` ссылался на
`/assets/lecture-5-v2.css` абсолютным путём. С диска это 404: Tailwind не
подгружался, и вся колода ехала в узкую колонку шрифтом по умолчанию —
«вот что я вижу в html». Поэтому здесь ВСЁ складывается внутрь файла:
CSS колоды, Montserrat и нужные начертания Phosphor (base64 из `vendor/`).
Файл перестаёт зависеть и от сети — в зале вайфай подводит.

Заодно снимается экранная обвязка, как просил владелец: «убери кнопки
сверху и снизу стрелки и тест убери кнопку». Остаётся чистый слайд.

Панель «Текст» при этом НЕ выбрасывается: её скрипт завязан на кнопку
(`if(!panel || !toggle || !dataEl) return;`), поэтому кнопка остаётся в
разметке, но скрыта, а открывается панель клавишей «T». Иначе второй
слой лекции пропал бы вместе с кнопкой.

    python3 tools/lecture5/standalone.py automation/5/v2/index.html \
        assets/lecture-5-v2.css build/lecture-5-v2-standalone.html
"""
import base64
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENDOR = os.path.join(ROOT, "vendor")


def die(msg):
    sys.exit("standalone: " + msg)


def read(path):
    return io.open(path, encoding="utf-8").read()


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def cut_element(html, marker, what):
    """Вырезает элемент целиком по балансу тегов, начиная с `marker`.

    Регуляркой такое не берут: у шапки и модального окна теста внутри
    вложенные div'ы, и «до первого </div>» отрезало бы половину.
    """
    a = html.find(marker)
    if a < 0:
        die("не найден %s" % what)
    tag = re.match(r"<\s*([a-zA-Z0-9]+)", html[a:]).group(1)
    open_re = re.compile(r"<\s*%s\b" % tag, re.I)
    close_re = re.compile(r"<\s*/\s*%s\s*>" % tag, re.I)
    depth, i = 0, a
    while i < len(html):
        mo = open_re.search(html, i)
        mc = close_re.search(html, i)
        if mc is None:
            die("не закрыт %s" % what)
        if mo is not None and mo.start() < mc.start():
            depth += 1
            i = mo.end()
            continue
        depth -= 1
        i = mc.end()
        if depth == 0:
            break
    else:
        die("не закрыт %s" % what)
    # Подчищаем осиротевший отступ и перевод строки
    b = i
    while a > 0 and html[a - 1] in " \t":
        a -= 1
    if b < len(html) and html[b] == "\n":
        b += 1
    return html[:a] + html[b:]


def inline_fonts(html):
    """Montserrat: 35 правил @font-face на пять woff2-подмножеств."""
    css = read(os.path.join(VENDOR, "fonts", "css2.css"))
    used = set(re.findall(r"url\(https://fonts\.gstatic\.com/[^)]*?/([^/)]+\.woff2)\)", css))
    if not used:
        die("в vendor/fonts/css2.css нет ссылок на woff2")
    for name in sorted(used):
        f = os.path.join(VENDOR, "fonts", "files", name)
        if not os.path.exists(f):
            die("нет файла шрифта %s" % f)
        css = css.replace("https://fonts.gstatic.com/s/montserrat/v31/" + name,
                          "data:font/woff2;base64," + b64(f))
    if "fonts.gstatic.com" in css:
        die("в CSS шрифтов остались внешние ссылки")
    html = re.sub(r'\n?\s*<link rel="preconnect" href="https://fonts\.[^"]*"[^>]*>', "", html)
    html, k = re.subn(r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">',
                      "<style>\n%s\n</style>" % css, html)
    if k != 1:
        die("ссылка на Google Fonts не заменена (найдено %d)" % k)
    return html


def inline_phosphor(html):
    """Только те начертания, что реально стоят в разметке (обычно fill и bold)."""
    weights = []
    for w, cls in (("regular", "ph"), ("bold", "ph-bold"),
                   ("fill", "ph-fill"), ("duotone", "ph-duotone")):
        # Класс начертания — отдельное слово в атрибуте: либо сразу после
        # `class="`, либо после пробела, и обязательно кончается пробелом или
        # кавычкой. Иначе `ph` поймалось бы внутри `ph-fill`, а `ph-bold` —
        # не поймалось бы вовсе.
        if re.search(r'class="(?:[^"]*\s)?%s(?=[\s"])' % re.escape(cls), html):
            weights.append(w)
    if "fill" not in weights:
        weights.append("fill")           # страховка: без fill колода останется без значков
    blocks = []
    for w in weights:
        d = os.path.join(VENDOR, "phosphor", "src", w)
        css = read(os.path.join(d, "style.css"))
        woff2 = [f for f in os.listdir(d) if f.endswith(".woff2")]
        if len(woff2) != 1:
            die("в %s не один woff2: %s" % (d, woff2))
        data = "data:font/woff2;base64," + b64(os.path.join(d, woff2[0]))
        # Оставляем один формат: ttf/woff/svg из того же каталога не нужны.
        css = re.sub(r"src:\s*url\([^)]*\)[^;]*;",
                     "src: url(%s) format('woff2');" % data, css, count=1)
        css = re.sub(r"url\(['\"]?\.?/?[A-Za-z0-9._-]+\.(ttf|woff|svg|eot)[^)]*\)",
                     "url(%s)" % data, css)
        blocks.append(css)
    html = re.sub(r'\n?\s*<link rel="stylesheet" href="https://unpkg\.com/@phosphor-icons[^"]*">',
                  "", html)
    # Скрипт-страховка дотягивал бы те же значки с запасного CDN — теперь вредна.
    html = cut_element(html, "<script>\n    (function(){\n        var VARIANTS", "скрипт запасного CDN Phosphor")
    html = html.replace("</head>", "<style>\n%s\n</style>\n</head>" % "\n".join(blocks), 1)
    return html, weights


def build_html(page, css_rel, font_css=None):
    """Автономная страница колоды строкой. `font_css` — свои @font-face
    вместо вариативного Montserrat из vendor/fonts (PDF-сборщику нужны
    статические начертания: вариативные Chromium в PDF не вшивает)."""
    html = read(page)
    css = read(css_rel)

    # 1. CSS колоды внутрь — ровно то, из-за чего файл ехал с диска.
    link = re.search(r'<link rel="stylesheet" href="(/assets/lecture-[^"]+\.css)">', html)
    if not link:
        die("не найдена ссылка на CSS колоды")
    html = html.replace(link.group(0), "<style>\n%s\n</style>" % css, 1)

    # 2. Значки и шрифт — тоже внутрь, чтобы файл не зависел от сети.
    html, weights = inline_phosphor(html)
    if font_css is None:
        html = inline_fonts(html)
    else:
        html = re.sub(r'\n?\s*<link rel="preconnect" href="https://fonts\.[^"]*"[^>]*>', "", html)
        html, k = re.subn(r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">',
                          "<style>\n%s\n</style>" % font_css, html)
        if k != 1:
            die("ссылка на Google Fonts не заменена (найдено %d)" % k)

    # 3. Иконки вкладки и манифест: с диска это только 404 в консоли.
    html = re.sub(r'\n?\s*<link rel="(icon|apple-touch-icon|manifest)"[^>]*>', "", html)

    # 4. Шапка целиком. Кнопка панели переезжает отдельно и скрытой:
    #    на ней висит инициализация всего второго слоя лекции.
    html = cut_element(html, '<header id="lecture-header">', "шапка лекции")
    hidden = ('    <button id="notes-toggle" type="button" style="display:none"'
              ' aria-label="Текст к слайду" aria-expanded="false"></button>\n')
    html = html.replace("<body class=", hidden + "<body class=") \
        if "<body class=" not in html else html
    m = re.search(r"<body[^>]*>\n", html)
    if not m:
        die("не найден <body>")
    html = html[:m.end()] + hidden + html[m.end():]

    # 5. Стрелки листания.
    for eid in ('<div id="nav-prev"', '<div id="nav-next"'):
        html = cut_element(html, eid, "стрелка " + eid)

    # 6. Кнопка теста. Владелец просил убрать именно КНОПКУ; само окно
    #    остаётся в разметке скрытым и недостижимым. Вырезать и окно нельзя:
    #    его скрипт держит десяток узлов (quizModal, quiz-options, счётчики),
    #    первый же null роняет обработчик, а следом падает и всё остальное
    #    в том же замыкании — проверено, 11 ошибок в консоли.
    html = cut_element(html, '<button id="open-quiz-btn"', "кнопка теста")
    before = html
    html = re.sub(r"document\.getElementById\('open-quiz-btn'\)"
                  r"\.addEventListener\('click', \w+\);",
                  "/* кнопка теста снята в автономной версии */", html)
    if html == before:
        die("привязка кнопки теста не обезврежена")

    # 7. Постер «видео-головы» в фоне пузыря — последняя ссылка на диск.
    #    Сам пузырь НЕ трогаем: на нём висит пара `bubble.addEventListener`
    #    без проверки на null, и первый же промах роняет всё замыкание —
    #    вместе с ним обработчики теста уходят в TDZ по quizModal
    #    (проверено: 11 ошибок в консоли). У лекции 5 videoIds пуст, так что
    #    пузырь и так стоит visibility:hidden и на экране его нет.
    m = re.search(r"url\((/assets/[^)]+\.(?:jpg|jpeg|png|webp))\)", html)
    if m:
        f = os.path.join(ROOT, m.group(1).lstrip("/"))
        if not os.path.exists(f):
            die("нет постера %s" % f)
        mime = "jpeg" if f.endswith((".jpg", ".jpeg")) else f.rsplit(".", 1)[1]
        html = html.replace(m.group(0),
                            "url(data:image/%s;base64,%s)" % (mime, b64(f)))

    # 8. Панель «Текст» без кнопки открывается клавишей.
    html = html.replace("</body>", """<script>
// Кнопки «Текст» в автономной версии нет — панель открывается клавишей «T»
// (и русской «Е» на той же клавише). Закрывается ею же или Escape.
(function(){
  document.addEventListener('keydown', function(e){
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var k = (e.key || '').toLowerCase();
    if (k !== 't' && k !== 'е') return;
    var b = document.getElementById('notes-toggle');
    if (b) { e.preventDefault(); b.click(); }
  });
})();
</script>
</body>""", 1)

    for bad, what in (("/assets/lecture-", "ссылка на CSS колоды"),
                      ("unpkg.com/@phosphor", "CDN Phosphor"),
                      ("fonts.googleapis.com", "Google Fonts"),
                      ('id="lecture-header"', "шапка"),
                      ('id="nav-prev"', "стрелка назад"),
                      ('id="nav-next"', "стрелка вперёд"),
                      ('id="open-quiz-btn"', "кнопка теста"),
                      ("/assets/video_sq/", "постер видео")):
        if bad in html:
            die("в готовом файле остался %s" % what)
    return html, weights


def main():
    if len(sys.argv) < 4:
        die("нужно: <страница> <css> <куда>")
    page, css_rel, out = (os.path.join(ROOT, a) for a in sys.argv[1:4])
    html, weights = build_html(page, css_rel)
    io.open(out, "w", encoding="utf-8").write(html)
    print("собран %s (%.1f МБ), начертания Phosphor: %s"
          % (out, len(html.encode("utf-8")) / 1048576.0, ", ".join(weights)))
    print("   слайдов: %d, статей панели: %s"
          % (html.count('class="slide-container'),
             "есть" if 'id="slide-notes"' in html else "НЕТ"))


if __name__ == "__main__":
    main()
