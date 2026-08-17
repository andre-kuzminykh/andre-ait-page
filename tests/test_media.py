# -*- coding: utf-8 -*-
"""Ролики курса: раздаём со своего домена, файлы на месте, Pages их отдаёт.

История. Ролики хот-линкались с raw.githubusercontent.com, и однажды у
зрителей они перестали показываться: файлы лежали на месте, ветка была жива,
деплой свежий — но raw не CDN и режет по лимитам (залп из 20 запросов дал
5×429 и 1×503). Ни один тест этого не видел, потому что ссылка в HTML была.
Здесь сторожим три вещи, каждая из которых уже роняла выдачу.

Фактическую доставку в браузере проверяет tools/media_check.py — он гоняет
все страницы курса и требует у каждого медиазапроса честный 200/206.
"""
import glob
import os
import re
import urllib.parse

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _course_pages():
    pats = ("automation/**/index.html", "automation/index.html",
            "automation_ru/**/index.html", "automation_ru/index.html")
    out = set()
    for p in pats:
        out.update(glob.glob(os.path.join(_ROOT, p), recursive=True))
    return sorted(out)


def test_pages_exist():
    """Если глоб перестанет находить страницы, остальные тесты станут
    зелёными на пустом множестве и перестанут что-либо охранять."""
    pages = _course_pages()
    assert len(pages) >= 8, "страниц курса нашлось всего %d" % len(pages)


def test_no_video_hotlinking_from_github_raw():
    """raw.githubusercontent.com — не CDN: он отдаёт cache-control на 5 минут,
    не кеширует (x-cache: MISS) и режет по лимитам. Свои ролики обязаны идти
    со своего домена."""
    bad = []
    for p in _course_pages():
        s = open(p, encoding="utf-8").read()
        for m in re.findall(r"https://raw\.githubusercontent\.com/[^\"']+", s):
            if m.endswith(".mp4") or "/video_sq/" in m:
                bad.append((os.path.relpath(p, _ROOT), m))
    assert not bad, "ролики снова тянутся с raw.githubusercontent:\n" + "\n".join(
        "  %s → %s" % b for b in bad)


def test_every_referenced_clip_is_in_the_repo():
    """Ссылка есть, файла нет — ровно то, что зритель видит как «видео
    пропало». Пути в разметке percent-encoded (имена файлов русские),
    поэтому перед проверкой разворачиваем."""
    miss, checked = [], 0
    for p in _course_pages():
        s = open(p, encoding="utf-8").read()
        for m in re.findall(r"['\"](/(?:assets/video_sq|automation/[a-z]+)/"
                            r"[^'\"]+\.mp4)['\"]", s):
            checked += 1
            f = os.path.join(_ROOT, urllib.parse.unquote(m.lstrip("/")))
            if not os.path.isfile(f):
                miss.append((os.path.relpath(p, _ROOT), m))
    assert checked, "в разметке не нашлось ни одной локальной ссылки на ролик"
    assert not miss, "ссылки без файлов:\n" + "\n".join(
        "  %s → %s" % m for m in miss)


def test_nojekyll_keeps_underscore_files_served():
    """Имена роликов начинаются с подчёркивания (_auto_1-кв-1.mp4). Jekyll
    такие файлы и каталоги ВЫКИДЫВАЕТ из сборки, то есть на Pages они стали
    бы 404 при живом файле в репозитории. Спасает только .nojekyll в корне."""
    assert os.path.isfile(os.path.join(_ROOT, ".nojekyll")), \
        "нет .nojekyll — Pages выкинет все файлы, начинающиеся с подчёркивания"
    under = [p for p in glob.glob(os.path.join(_ROOT, "assets/video_sq/*.mp4"))
             if os.path.basename(p).startswith("_")]
    assert under, "роликов с подчёркиванием не нашлось — проверять нечего"


def test_local_server_serves_byte_ranges():
    """Видео без Range не играет: Chromium на первом seek обрывает запрос.
    Живой хостинг диапазоны поддерживает, и стенд обязан тоже — иначе он
    «ломает» ровно то, что должен проверять."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "tools"))
    from record_lecture import RangeHandler
    assert hasattr(RangeHandler, "send_head")
    src = open(os.path.join(_ROOT, "tools", "record_lecture.py"),
               encoding="utf-8").read()
    assert "handler = functools.partial(RangeHandler" in src, \
        "serve() снова поднимает раздатчик без поддержки Range"


if __name__ == "__main__":
    ok = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS %s" % name)
            ok += 1
    print("\nВсе тесты медиа пройдены: %d" % ok)
