# -*- coding: utf-8 -*-
"""Автономный HTML лекции 7 для владельца: build/l7/deliver/lecture-7.html.

    python3 build/l7/deliver.py

Колода automation/7/index.html подключает CSS корневой ссылкой
/assets/lecture-7.css — открытая двойным кликом, она показала бы простыню без
стилей (грабля §11.3 LECTURE-GUIDE). Здесь CSS вшивается в страницу, а
корневые ссылки на картинки переписываются на адрес сайта.
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "automation", "7", "index.html")
CSS = os.path.join(ROOT, "assets", "lecture-7.css")
OUT = os.path.join(ROOT, "build", "l7", "deliver", "lecture-7.html")

html = io.open(SRC, encoding="utf-8").read()
css = io.open(CSS, encoding="utf-8").read()
link = '<link rel="stylesheet" href="/assets/lecture-7.css">'
assert link in html
html = html.replace(link, "<style id=\"lecture-css\">\n" + css + "\n</style>", 1)
html = re.sub(r'(src|href)="/(?!/)', r'\1="https://andre.technology/', html)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8").write(html)
print("автономный HTML: %s (%d КБ)" % (OUT, len(html.encode("utf-8")) // 1024))
