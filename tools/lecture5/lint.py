# -*- coding: utf-8 -*-
"""Механическая проверка разметки слайда лекции 5 (до браузерных сканеров).

    python3 tools/lecture5/lint.py                 # все файлы out/
    python3 tools/lecture5/lint.py out/slide-07.html
"""
import io, os, re, sys

# L5_DIR — каталог колоды внутри build/: у второй версии лекции (l5v2) свои
# слайды и свой словарь иконок.
HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "build", os.environ.get("L5_DIR", "l5"))
ROOT = os.path.dirname(os.path.dirname(HERE))
ICONS = set(io.open(os.path.join(HERE, "icons.txt"), encoding="utf-8").read().split())

BANNED = ("workflow", "reasoning", "retrieval", "fallback", "polling", "guardrail",
          "governance", "throughput", "human review", "backlog", "adoption",
          "baseline", "продакшен", "чекпоинт", "снапшот", "оркестрац")
ALLOWED_STYLE = 'style="color:#111;-webkit-text-fill-color:#111"'
SIZE = re.compile(r"^(?:(sm|md|lg|xl|2xl):)?text-(\[[^\]]+\]|xs|sm|base|lg|xl|[2-9]xl)$")


def check(path):
    name = os.path.basename(path)
    html = io.open(path, encoding="utf-8").read()
    bad = []
    add = lambda m: bad.append("%s: %s" % (name, m))

    sid = re.search(r'id="slide-(\d+)"', html)
    if not sid:
        add("нет id слайда"); return bad
    if not html.lstrip().startswith('<div class="slide-container'):
        add("файл не начинается с <div class=\"slide-container\"")
    if html.count('class="slide-container') != 1:
        add("в файле должен быть ровно один слайд")
    if '<div class="content-z' not in html:
        add("нет обёртки content-z")

    # структура заголовка
    if sid.group(1) == "0":
        if html.count("<h1") != 1:
            add("на обложке должен быть ровно один <h1>")
    else:
        if html.count("<h2") != 1:
            add("должен быть ровно один <h2> (сейчас %d)" % html.count("<h2"))
        if html.count("<h1"):
            add("<h1> бывает только на обложке")

    # запреты
    for tag in ("<style", "<script", "<svg", ":has(", "hidden md:", "md:hidden",
                "sr-only", "shadow-", "h-screen", "overflow-auto", "overflow-y-auto"):
        if tag in html:
            add("запрещено: %s" % tag)
    for m in re.finditer(r'style="[^"]*"', html):
        if m.group(0) != ALLOWED_STYLE:
            add("посторонний style=: %s" % m.group(0)[:60])
    if re.search(r"\b\d+vw\b|\b\d+vh\b", html):
        add("размеры в vw/vh запрещены")

    # пробел перед <br>
    for m in re.finditer(r"(.)<br\s*/?>", html):
        if m.group(1) not in " >\n":
            add("нет пробела перед <br>: ...%s" % html[max(0, m.start() - 34):m.end()].strip()[-46:])

    # парность кеглей
    for m in re.finditer(r'class="([^"]*)"', html):
        toks = m.group(1).split()
        base = [t for t in toks if SIZE.match(t) and ":" not in t]
        wide = [t for t in toks if SIZE.match(t) and ":" in t]
        if base and not wide:
            add("кегль без пары для компьютера: %s" % " ".join(base))
        if wide and not base:
            add("кегль без пары для телефона: %s" % " ".join(wide))

    # иконки
    for n in set(re.findall(r"\bph-[a-z0-9-]+", html)):
        if n in ("ph-fill", "ph-bold", "ph-duotone", "ph-light", "ph-thin"):
            continue
        if n not in ICONS:
            add("несуществующая иконка %s" % n)

    # язык
    low = html.lower()
    for w in BANNED:
        if w.lower() in low:
            add("англицизм/запрещённое слово: %s" % w)
    text = re.sub(r"<[^>]+>", " ", html)
    if re.search(r"(?<![A-Za-z])AI(?![A-Za-z])", text):
        add("в тексте «AI» — должно быть «ИИ»")

    # плотность
    cards = len(re.findall(r'class="[^"]*(?:bg-white|bg-black|bg-grayBase|bg-white/10)[^"]*rounded', html))
    if cards > 18:
        add("слишком много карточек: %d" % cards)
    for m in re.finditer(r">([^<>]{120,})<", text):
        pass
    for m in re.finditer(r"<p[^>]*>([^<]{140,})", html):
        add("слишком длинный текст в абзаце (%d знаков)" % len(m.group(1)))

    # баланс div
    if html.count("<div") != html.count("</div>"):
        add("не сходится число <div>/</div>: %d и %d" % (html.count("<div"), html.count("</div>")))
    return bad


def main():
    files = sys.argv[1:] or sorted(
        os.path.join(HERE, "out", f) for f in os.listdir(os.path.join(HERE, "out"))
        if f.endswith(".html"))
    bad = []
    for f in files:
        bad += check(f)
    if bad:
        print("НАРУШЕНИЯ (%d):" % len(bad))
        for b in bad:
            print("  " + b)
        return 1
    print("чисто: %d файлов" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
