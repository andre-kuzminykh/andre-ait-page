# -*- coding: utf-8 -*-
"""Быстрая пересборка assets/lecture-3.css для промежуточных замеров.

    python3 build/l3/css.py

Канонический tools/build_lecture_css.py 6 смотрит только в готовую колоду
automation/3/index.html и каждый раз ставит tailwind заново. Пока слайды
правятся, этого мало: новый класс, которого ещё нет в собранном CSS, не
существует для браузера, и замер кегля соврёт. Здесь tailwind стоит один раз
в build/l3/tw, а содержимым служат ВСЕ заготовки слайдов плюс каркас лекции 4.
Файл пишется атомарно (временный + rename): параллельные замеры не прочтут
его наполовину записанным. Конфиг повторяет tools/build_lecture_css.py.
"""
import os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(HERE, "tw", "node_modules", ".bin", "tailwindcss")

CONFIG = """\
module.exports = {
  content: [%s],
  theme: {
    screens: { sm: '768px', md: '768px', lg: '768px', xl: '768px', '2xl': '768px' },
    extend: {
      fontFamily: { sans: ['Montserrat', 'sans-serif'] },
      colors: { solar: '#8B5CF6', grayBase: '#E9E9E9', black: '#000000', white: '#FFFFFF' },
    },
  },
};
"""


def build(dst, content, strict=True):
    """strict: ровно один @media 768 (лекции 3–6). У лекций 1–2 есть max-md:,
    это второй запрос на той же границе — tools/deck_probe.py зовёт strict=False
    и проверяет, как канонический tools/build_lecture_css.py: все запросы на 768px."""
    with tempfile.TemporaryDirectory() as tmp:
        cfg = os.path.join(tmp, "tailwind.config.js")
        open(cfg, "w").write(CONFIG % ", ".join(repr(c) for c in content))
        inp = os.path.join(tmp, "in.css")
        open(inp, "w").write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        out = os.path.join(tmp, "out.css")
        r = subprocess.run([BIN, "-c", cfg, "-i", inp, "-o", out, "--minify"],
                           cwd=tmp, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stderr[-800:])
        css = open(out, encoding="utf-8").read()
        medias = set(m.strip() for m in re.findall(r"@media[^{]+", css))
        if strict and medias != {"@media (min-width:768px)"}:
            sys.exit("в CSS не один брейкпоинт 768: %s" % medias)
        if [m for m in medias if "768px" not in m]:
            sys.exit("в CSS чужие брейкпоинты: %s" % medias)
        fd, part = tempfile.mkstemp(dir=os.path.dirname(dst), prefix=".lecture-3.")
        os.close(fd)
        open(part, "w", encoding="utf-8").write(css)
        os.replace(part, dst)
    return css


def main():
    content = [os.path.join(HERE, "out", "*.html"),
               os.path.join(ROOT, "automation", "4", "index.html")]
    dst = os.path.join(ROOT, "assets", "lecture-3.css")
    css = build(dst, content)
    print("CSS пересобран: %s (%d КБ)" % (dst, len(css) // 1024))


if __name__ == "__main__":
    main()
