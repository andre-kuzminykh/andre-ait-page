# -*- coding: utf-8 -*-
"""Чистая страница лекции: только слайды, без хрома.

Владелец попросил «страницу, где не будет лого, кнопок ТЕКСТ / ЗАДАНИЕ /
БУТКЕМП и смены темы, не будет стрелок и видео внизу, не будет теста, а
остальное выровнено так, будто этого всего нет».

    python3 tools/build_clean_lecture.py 3        # → automation/3/clean/index.html
    python3 tools/build_clean_lecture.py 3 --out ~/lecture3-clean.html

Почему генератор, а не руками отредактированная копия: колода правится
каждый день, и копия устарела бы к вечеру. Здесь исходник читается как есть
и преобразуется по правилам ниже, поэтому чистую страницу можно пересобрать
в любой момент.

ГЛАВНОЕ ПРАВИЛО ПРЕОБРАЗОВАНИЯ: хром ПРЯЧЕТСЯ, а не удаляется из разметки.
Скрипт лекции обращается к этим узлам напрямую —
`document.getElementById('start-overlay').addEventListener(...)` упадёт на
null, если узел вырезать, и вместе с ним умрёт вся подгонка. Поэтому узлы
остаются в DOM, а не видны они через один блок стилей.

Что меняется, кроме видимости:

* полосы REF. Холст формы резервирует сверху 128px под шапку и снизу 88px
  под стрелки (на телефоне 88 и 124). Без хрома этот резерв — просто пустота
  сверху и снизу, из-за которой слайд кажется мелким. Здесь он заменяется
  симметричным полем, и содержимое встаёт по центру экрана;
* videoIds обнуляется. Иначе страница тянет 42 ролика, которых нет, и
  получает 42 ответа 404 на каждую загрузку.
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Хром прячем ровно тем же списком, каким его гасит съёмка кадров в
# record_lecture.py (CHROME_OFF) — плюс тест, которого там нет.
CLEAN_CSS = """
<style id="clean-mode">
/* ЧИСТАЯ СТРАНИЦА: на экране только слайд.
   Узлы остаются в DOM — скрипт лекции обращается к ним по id и падает,
   если их вырезать. Прячем видимость, а не существование. */
#lecture-header,            /* лого, ТЕКСТ, ЗАДАНИЕ, смена темы, БУТКЕМП */
.nav-arrow,                 /* стрелки листания внизу */
#progress-container,        /* полоса прогресса */
#video-bubble,              /* кружок с говорящей головой */
#start-overlay,             /* «нажмите, чтобы начать» */
#intro-overlay,
#notes-panel,               /* панель «Текст» — её кнопка тоже убрана */
#quiz-modal,                /* тест */
#open-quiz-btn{             /* кнопка «Пройти тест» на последнем слайде */
  display:none !important;
}
/* Кнопка теста — прямой ребёнок content-z: без неё у последнего слайда
   остаётся её отступ сверху. Гасим и его. */
#open-quiz-btn{ margin:0 !important; }
html, body{ overflow:hidden; }
</style>
"""


def build(lecture, out_path):
    src = os.path.join(ROOT, "automation", str(lecture), "index.html")
    if not os.path.isfile(src):
        sys.exit("нет лекции %d: %s" % (lecture, src))
    html = open(src, encoding="utf-8").read()
    steps = []

    # 1. Полосы холста. Без шапки и стрелок резерв превращается в пустоту, из-за
    #    которой слайд кажется мелким: на компьютере это 128+88 = 216px из 864,
    #    четверть высоты формы. Ставим симметричное поле — содержимое встаёт по
    #    центру экрана, как и просил владелец.
    # ПОДГОНКУ НЕ ТРОГАЕМ ВООБЩЕ. Свободная высота задаёт зум, зум задаёт
    # ширину холста (availW/z) — измени полосы, и вырастет зум, сузится холст,
    # а весь текст, выверенный владельцем построчно, поедет в переносы, вплоть
    # до аварийного разрыва слова посреди («Проверк/а»). Цена центровки
    # оказалась выше самой центровки: страница повторяет вёрстку сайта
    # один в один, только без хрома.

    # 2. Ролики. Пустой массив скрипт лекции обрабатывает штатно: кружок
    #    прячется, загрузка не начинается. Иначе — 42 запроса в никуда.
    vid = re.search(r"const videoIds = \[.*?\];", html, re.S)
    if vid:
        html = html.replace(vid.group(0), "const videoIds = [];")
        steps.append("videoIds обнулён — страница не тянет ролики")

    # 3. Собранный Tailwind ВШИВАЕТСЯ в страницу. Ссылка на него корневая
    #    (/assets/lecture-3.css): по сети она находится, а у файла, открытого
    #    с диска двойным кликом, указывает в корень файловой системы — стилей
    #    нет вовсе, и страница превращается в простыню системным шрифтом.
    #    Иконки и Montserrat остаются внешними: они приезжают с CDN и без
    #    интернета всё равно не появятся, а весят несопоставимо больше.
    css_path = os.path.join(ROOT, "assets", "lecture-%d.css" % lecture)
    link = '<link rel="stylesheet" href="/assets/lecture-%d.css">' % lecture
    if link not in html:
        sys.exit("не найдена ссылка на собранный CSS — страница осталась бы без стилей")
    if not os.path.isfile(css_path):
        sys.exit("нет %s — сначала python3 tools/build_lecture_css.py %d" % (css_path, lecture))
    css = open(css_path, encoding="utf-8").read()
    html = html.replace(link, "<style id=\"lecture-css-inline\">\n%s\n</style>" % css, 1)
    steps.append("собранный CSS вшит в страницу (%.0f КБ) — файл работает с диска"
                 % (len(css) / 1024))

    # 4. Остальные корневые ссылки — иконки вкладки и манифест. С диска они
    #    не найдутся и дадут пустые запросы; на вид не влияют, но убираем.
    for dead in ('<link rel="icon" href="/favicon.ico"',):
        pass
    html = re.sub(r'\s*<link[^>]+href="/(?:favicon|apple-touch-icon|site\.webmanifest)[^"]*"[^>]*>',
                  "", html)
    steps.append("иконки вкладки и манифест убраны — с диска они не находятся")

    # 5. Сам блок сокрытия — последним в <head>, чтобы перебить всё остальное.
    if "</head>" not in html:
        sys.exit("нет </head> — не туда вставляю")
    html = html.replace("</head>", CLEAN_CSS + "</head>", 1)
    steps.append("хром скрыт одним блоком стилей")

    # 6. Заголовок вкладки — чтобы чистую страницу было видно в списке окон.
    html = re.sub(r"<title>(.*?)</title>", lambda m: "<title>%s — только слайды</title>"
                  % m.group(1), html, count=1, flags=re.S)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(html)
    for s in steps:
        print("   • %s" % s)
    print("собрана чистая страница: %s (%.0f КБ)"
          % (out_path, os.path.getsize(out_path) / 1024))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Чистая страница лекции: только слайды.")
    ap.add_argument("lecture", type=int)
    ap.add_argument("--out", help="куда положить (по умолчанию automation/<N>/clean/index.html)")
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, "automation", str(a.lecture), "clean", "index.html")
    return build(a.lecture, os.path.abspath(os.path.expanduser(out)))


if __name__ == "__main__":
    sys.exit(main())
