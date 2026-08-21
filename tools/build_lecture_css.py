# -*- coding: utf-8 -*-
"""Сборка статического Tailwind для лекции: assets/lecture-<N>.css.

Зачем. Play-CDN Tailwind компилирует классы в браузере ПОСЛЕ первой
отрисовки — кнопки секунду стоят «квадратными» (см. LECTURE-GUIDE и
test_tailwind_is_prebuilt_not_cdn). Поэтому CSS собирается заранее, а
инлайновый tailwind.config в самой лекции остаётся ЕДИНСТВЕННЫМ описанием
палитры и брейкпоинтов — этот сборщик его повторяет один в один.

Канон владельца: форм ровно две, граница одна — 768px. Поэтому ВСЕ
брейкпоинты (sm/md/lg/xl/2xl) равны 768px, и в собранном файле обязан
остаться один-единственный @media (это стережёт
test_content_breakpoints_live_on_the_form_boundary). Готовый
assets/lecture-2-8.css сюда НЕ подходит: он собран со стандартной сеткой
640/768/1024/1280 и вернул бы «переключение вёрстки посреди формы».

    python3 tools/build_lecture_css.py 2          # соберёт assets/lecture-2.css

Нужен node/npx; tailwindcss@3.4 ставится во временный каталог npm-ом.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = """\
module.exports = {
  content: [%(content)r],
  theme: {
    screens: { sm: '768px', md: '768px', lg: '768px', xl: '768px', '2xl': '768px' },
    extend: {
      fontFamily: { sans: ['Montserrat', 'sans-serif'] },
      colors: { solar: '#8B5CF6', grayBase: '#E9E9E9', black: '#000000', white: '#FFFFFF' },
    },
  },
};
"""


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    page = os.path.join(ROOT, "automation/%d/index.html" % n)
    if not os.path.exists(page):
        sys.exit("нет %s" % page)
    out = os.path.join(ROOT, "assets/lecture-%d.css" % n)
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "tailwind.config.js"), "w").write(
            CONFIG % {"content": page})
        open(os.path.join(tmp, "in.css"), "w").write(
            "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n")
        subprocess.run(["npm", "install", "-s", "tailwindcss@3.4.17"],
                       cwd=tmp, check=True)
        subprocess.run([os.path.join(tmp, "node_modules/.bin/tailwindcss"),
                        "-c", "tailwind.config.js", "-i", "in.css",
                        "-o", out, "--minify"], cwd=tmp, check=True)
    css = open(out, encoding="utf-8").read()
    medias = set(m.strip() for m in re.findall(r"@media[^{]+", css))
    bad = [m for m in medias if "768px" not in m]
    if bad:
        sys.exit("в собранном CSS чужие брейкпоинты: %s" % bad)
    print("собран %s (%d байт), медиа: %s" % (out, len(css), sorted(medias)))


if __name__ == "__main__":
    main()
