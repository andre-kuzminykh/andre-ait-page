# -*- coding: utf-8 -*-
"""Тесты анимированной графики поверх видео лекции 1 (FR-SITE23, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_overlay.py`, и через pytest.

Оверлей ложится на «говорящую голову» 1080×1920: слайды 1–3 лекции появляются
поэлементно под озвучку. Проверяем то, что ломается молча: внешние зависимости
(в записи их не будет), рассинхрон таймингов и расхождение текста с деком.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_OVERLAY = os.path.join(_ROOT, "automation", "1", "overlay", "index.html")
_LECTURE = os.path.join(_ROOT, "automation", "1", "index.html")
_DURATION = 142.0          # 02:22 — длина озвучки ролика


def _html(path=_OVERLAY):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _scenes(html):
    """[(id, in, out, [(порядок в DOM, data-in элемента)])] по разметке сцен."""
    out = []
    for m in re.finditer(
            r'<section class="scene" id="(\w+)" data-in="([\d.]+)" data-out="([\d.]+)">',
            html):
        start = m.end()
        end = html.index("</section>", start)
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', html[start:end])]
        out.append((m.group(1), float(m.group(2)), float(m.group(3)), cues))
    return out


# ── FR-SITE23: страница自足на, в записи и офлайн выглядит так же ──────────

def test_overlay_is_self_contained():
    html = _html()
    external = re.findall(r'(?:src|href)="(https?:)?//[^"]+"', html)
    assert not external, "оверлей тянет внешние ресурсы, в записи их не будет: %r" % external
    assert "cdn.tailwindcss.com" not in html, "оверлей не должен зависеть от Tailwind CDN"
    assert "fonts.googleapis.com" not in html, "шрифт должен лежать локально в overlay/fonts/"
    assert "unpkg.com" not in html, "иконки Phosphor должны быть вклеены инлайновым SVG"


def test_fonts_present():
    html = _html()
    files = re.findall(r"url\((fonts/[^)]+\.woff2)\)", html)
    assert len(set(files)) == 8, "ожидались 8 подмножеств Montserrat, найдено %d" % len(set(files))
    base = os.path.dirname(_OVERLAY)
    for rel in set(files):
        assert os.path.exists(os.path.join(base, rel)), "нет файла шрифта %s" % rel


# ── FR-SITE23: тайминги ──────────────────────────────────────────────────

def test_scenes_do_not_overlap():
    scenes = _scenes(_html())
    assert len(scenes) == 3, "ожидались три сцены (слайды 1–3), найдено %d" % len(scenes)
    prev_out = 0.0
    for sid, t_in, t_out, _ in scenes:
        assert t_in < t_out, "%s: сцена начинается позже, чем кончается" % sid
        assert t_in >= prev_out, "%s: сцена наезжает на предыдущую (%s < %s)" % (sid, t_in, prev_out)
        assert t_out <= _DURATION, "%s: сцена выходит за 02:22 озвучки" % sid
        prev_out = t_out


def test_cues_are_within_scenes():
    for sid, t_in, t_out, cues in _scenes(_html()):
        assert cues, "%s: в сцене нет ни одного data-in" % sid
        for c in cues:
            assert t_in <= c < t_out, "%s: элемент на %.1fs вне окна сцены %.1f–%.1f" % (sid, c, t_in, t_out)


def test_list_items_appear_top_down():
    """Внутри списка порядок в DOM обязан совпадать с порядком озвучки: место
    под невидимый пункт зарезервировано, и пункт «не в очереди» оставил бы дыру.
    Между колонками порядок как раз перемешан — это нормально."""
    html = _html()
    for block in re.findall(r"<ul>(.*?)</ul>", html, re.S):
        cues = [float(c) for c in re.findall(r'data-in="([\d.]+)"', block)]
        assert cues == sorted(cues), "пункты списка появляются не сверху вниз: %r" % cues


def test_highlights_land_inside_their_scene():
    html = _html()
    for sid, t_in, t_out, _ in _scenes(html):
        start = html.index('id="%s"' % sid)
        end = html.index("</section>", start)
        for group in re.findall(r'data-hl="([\d.\s]+)"', html[start:end]):
            for t in (float(x) for x in group.split()):
                assert t_in <= t < t_out, "%s: подсветка на %.1fs вне окна сцены" % (sid, t)


# ── FR-SITE23: текст дословно из дека, своего не досочиняем ──────────────

def _plain(fragment):
    """Голый текст: <br> — это пробел, мягкий перенос не считается символом."""
    txt = re.sub(r"<br[^>]*>", " ", fragment)
    txt = re.sub(r"<[^>]+>", "", txt).replace("&shy;", "")
    return re.sub(r"\s+", " ", txt).strip()


def test_texts_match_lecture_slides():
    lecture = _plain(_html(_LECTURE))
    html = _html()
    body = html[html.index('<div id="layer">'):html.index('<div id="guides">')]
    checked = 0
    for raw in re.findall(r"<(?:h1|h2|h3|p|li)[^>]*>(.*?)</(?:h1|h2|h3|p|li)>", body, re.S):
        txt = _plain(raw)
        if len(txt) < 12:
            continue
        checked += 1
        assert txt in lecture, "текста нет в деке лекции, значит он досочинён: %r" % txt
    assert checked >= 15, "проверено подозрительно мало текстов (%d)" % checked


# ── FR-SITE23: переносы ──────────────────────────────────────────────────

def test_no_break_anywhere():
    html = _html()
    assert "overflow-wrap:anywhere" not in html.replace(" ", ""), \
        "anywhere рвёт слова посреди слога — только break-word + &shy;"
    for word in ("конкуренто&shy;способность", "Механи&shy;зация",
                 "Электри&shy;чество", "Интеллек&shy;туальная"):
        assert word in html, "длинное слово без мягкого переноса: %s" % word


# ── FR-SITE23: служебный интерфейс не попадает в кадр ────────────────────

def test_hud_outside_stage():
    html = _html()
    stage_end = html.index('<div id="drop">')
    for panel in ('id="hud"', 'id="drop"'):
        assert html.index(panel) > stage_end, "%s лежит внутри #stage и попадёт в запись" % panel


def test_zone_stays_above_the_head():
    """Макушка в кадре начинается на y816 — графика обязана кончаться выше."""
    html = _html()
    top = int(re.search(r"--zone-top:(\d+)px", html).group(1))
    height = int(re.search(r"--zone-h:(\d+)px", html).group(1))
    assert top + height <= 816, "зона графики (%d..%d) заходит на голову" % (top, top + height)


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except Exception as e:  # AssertionError и любые сбои разбора
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    raise SystemExit(1 if failed else 0)
