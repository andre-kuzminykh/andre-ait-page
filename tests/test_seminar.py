# -*- coding: utf-8 -*-
"""Тесты семинара к лекции 1 — /automation/1/seminar/ (FR-SITE27).

Семинар — не лекция: это отдельная колода из 13 слайдов по 10 плиток, где
каждая плитка открывает карточку-схему. Общего кода с лекциями у него нет,
но канон владельца тот же: две формы, один масштаб, ничего не листается,
теней нет, термины по-русски.

Запускается и как `python3 tests/test_seminar.py`, и через pytest.
"""
import json
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_lectures import _ANGLICISMS, _AI_KEEP, _TERM_KEEP  # noqa: E402

_PAGE = "automation/1/seminar/index.html"
_MAIN_SITE = "index.html"
_SLIDES = 13
_TILES = 10


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _html():
    return _read(_PAGE)


def _json_block(html, block_id):
    m = re.search(r'<script id="%s"[^>]*>(.*?)</script>' % block_id, html, re.S)
    assert m, "нет блока данных " + block_id
    return json.loads(m.group(1))


# ── Страница собрана и цела ───────────────────────────────────────────────

def test_page_exists_with_thirteen_slides_of_ten_tiles():
    html = _html()
    slides = re.findall(r'<section class="slide(?: acc-warm)?" data-i=', html)
    assert len(slides) == _SLIDES, "ожидается %d слайдов, найдено %d" % (_SLIDES, len(slides))
    tiles = re.findall(r'<button class="tile"', html)
    assert len(tiles) == _SLIDES * _TILES, \
        "ожидается %d плиток, найдено %d" % (_SLIDES * _TILES, len(tiles))
    for s in range(_SLIDES):
        got = len(re.findall(r'data-s="%d" data-t="' % s, html))
        assert got == _TILES, "на слайде %d плиток %d, а должно быть %d" % (s + 1, got, _TILES)


def test_hundred_employees_are_all_numbered():
    """Сотня — это ровно сто карточек с номерами от 1 до 100, без пропусков."""
    deck = _json_block(_html(), "seminar-data")
    nums = []
    for s in deck["slides"]:
        for t in s["tiles"]:
            m = re.match(r"№ (\d+) из 100", t.get("no") or "")
            if m:
                nums.append(int(m.group(1)))
    assert sorted(nums) == list(range(1, 101)), "номера сотрудников должны идти 1..100 без дыр"


def test_every_tile_card_has_all_fields():
    deck = _json_block(_html(), "seminar-data")
    assert len(deck["slides"]) == _SLIDES
    for s in deck["slides"]:
        assert len(s["tiles"]) == _TILES, s["key"]
        for t in s["tiles"]:
            where = "%s / %s" % (s["key"], t.get("ru"))
            for f in ("ru", "icon", "mission", "handoffs"):
                assert t.get(f), where + ": пустое поле " + f
            if t.get("roles"):                      # плитка направления — состав из десяти ролей
                assert len(t["roles"]) == _TILES, where
                continue
            for f, n in (("in", 4), ("do", 4), ("out", 4), ("tools", 4), ("metrics", 3)):
                assert len(t.get(f) or []) == n, "%s: в поле %s должно быть %d строк" % (where, f, n)
            assert len(t["handoffs"]) == 3, where
            for f in ("human", "guard", "trigger"):
                assert t.get(f), where + ": пустое поле " + f
            assert 0 <= int(t["autonomy"]) <= 4, where
            assert 0 <= int(t["risk"]) <= 4, where


def test_notes_cover_every_slide():
    html = _html()
    notes = _json_block(html, "slide-notes")
    assert len(notes) == _SLIDES, "текст нужен ко всем %d слайдам" % _SLIDES
    for i, n in enumerate(notes):
        assert n.get("title"), "слайд %d: нет заголовка в панели" % (i + 1)
        assert n.get("lead") or n.get("paras"), "слайд %d: нет подводки" % (i + 1)


def test_narration_is_about_an_hour():
    """Речь семинара — час с небольшим: меньше не наберётся на сто ролей."""
    notes = _json_block(_html(), "slide-notes")
    words = 0
    for n in notes:
        words += len((n.get("lead") or "").split())
        for p in n.get("paras") or []:
            words += len(p.split())
        for it in n.get("items") or []:
            words += len(it["text"].split())
        for p in n.get("outro") or []:
            words += len(p.split())
    # 135 слов в минуту — темп спокойной дикторской начитки
    minutes = words / 135.0
    assert 55 <= minutes <= 95, "речь на %.0f минут (%d слов) — не тот хронометраж" % (minutes, words)


# ── Канон владельца ───────────────────────────────────────────────────────

def test_two_forms_and_a_single_breakpoint():
    """Форм ровно две, граница одна — 768px и только по ширине."""
    html = _html()
    medias = set(m.strip() for m in re.findall(r"@media\s*\(([^)]*width[^)]*)\)", html))
    bad = [m for m in medias if not re.fullmatch(r"(min-width:768px|max-width:767px)", m.replace(" ", ""))]
    assert not bad, "контентные брейкпоинты только на границе формы, а найдено: " + ", ".join(sorted(bad))
    assert "REF = { pc: { w:1380, h:864 }, mob: { w:376, h:844 } }" in html, \
        "формы 1380x864 и 376x844 зашиты в подгонку"


def test_nothing_scrolls():
    html = _html()
    head = html.split("<body")[0]
    assert re.search(r"html,body\{height:100%;overflow:hidden;overflow:clip", head), \
        "ни страница, ни слайд не прокручиваются"
    assert ".slide{" in html and "overflow-y:auto" not in html.split(".slide{")[1][:400], \
        "у слайда не должно быть собственной прокрутки"


def test_no_shadows_anywhere():
    html = _html()
    assert "box-shadow:none!important" in html and "text-shadow:none!important" in html, \
        "теней нет нигде — должно стоять правило-глушитель"
    body = html.split("<body", 1)[1]
    live = re.findall(r"box-shadow:\s*(?!none)", body)
    assert not live, "в разметке остались тени: %d штук" % len(live)


def test_palette_is_the_lecture_palette():
    html = _html()
    assert "--pur:#8B5CF6" in html and "--org:#F97316" in html, "палитра лекций: фиолетовый + оранжевый"
    for mint in ("#35F0C7", "rgba(53,240,199", "rgba(53, 240, 199"):
        assert mint not in html, "остался мятный цвет старого стиля " + mint


def test_window_only_scales_the_ready_picture():
    """Окно меняет ОДИН масштаб; раскладка внутри формы от окна не зависит."""
    html = _html()
    assert "transform:translateX(var(--deck-shift,0px)) scale(var(--view-scale))" in html
    assert "window.addEventListener('resize', fit, { passive:true })" in html
    assert "setTimeout(fit" not in html, "подгонка при ресайзе не откладывается — картинка не должна «дышать»"


# ── Иконки и внешние зависимости ──────────────────────────────────────────

def test_icons_are_inlined_not_hotlinked():
    """Значки вшиты спрайтом: с внешнего CDN они пропадают при плохой сети."""
    html = _html()
    assert "unpkg.com" not in html and "cdn.jsdelivr.net" not in html, \
        "значки не должны тянуться со стороннего CDN"
    assert "cdn.tailwindcss.com" not in html, "Tailwind Play-CDN запрещён"
    # Значки приходят из разметки (href="#i-…") и из скриптов карточки:
    # список служебных значков страницы держит сам сборщик, его и берём,
    # иначе «лишними» окажутся те, что рисуются во время работы.
    import importlib
    ui = set(importlib.import_module("tools.build_seminar").UI_ICONS)
    used = set(re.findall(r'href="#i-([a-z0-9-]+)"', html)) | ui
    have = set(re.findall(r'<symbol id="i-([a-z0-9-]+)"', html))
    assert used <= have, "нет значков в спрайте: " + ", ".join(sorted(used - have))
    assert have <= used, "в спрайте лишние значки: " + ", ".join(sorted(have - used))


def test_favicons_match_the_main_site():
    site = _read(_MAIN_SITE)
    hrefs = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', site))
    page = set(re.findall(r'href="(/(?:favicon|apple-touch|site\.web)[^"]*)"', _html()))
    assert hrefs <= page, "набор фавиконов должен совпадать с главной"


def test_no_underscore_asset_paths():
    """Пути с ведущим подчёркиванием Pages выбрасывает из сборки."""
    for src in re.findall(r'(?:src|href)="(/[^"]+)"', _html()):
        assert not os.path.basename(src).startswith("_"), src


def test_links_back_to_the_lecture():
    assert 'href="/automation/1/"' in _html(), "с семинара должен быть путь назад в лекцию"


def test_seminar_is_linked_from_the_lecture():
    """В семинар должно быть куда войти: ссылка с экрана результатов теста."""
    lec = _read("automation/1/index.html")
    assert "/automation/1/seminar/" in lec, "лекция 1 должна вести на свой семинар"


# ── Термины по-русски ─────────────────────────────────────────────────────

def _visible_text(html):
    body = html.split("<body", 1)[1]
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
    body = re.sub(r"<svg.*?</svg>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", body)


def _strip_keep(text, extra=()):
    text = text.replace("‑", "-")
    for keep in sorted(_TERM_KEEP + tuple(extra), key=len, reverse=True):
        text = text.replace(keep, " ")
    return text


def test_slides_and_notes_speak_russian():
    html = _html()
    notes = json.dumps(_json_block(html, "slide-notes"), ensure_ascii=False)
    for name, blob in (("слайды", _visible_text(html)), ("панель текста", notes)):
        blob = _strip_keep(blob)
        for word in _ANGLICISMS:
            assert not re.search(re.escape(word), blob, re.I), \
                "%s: остался англицизм %r" % (name, word)
        assert not re.search(r"\bAI\b", _strip_keep(blob, _AI_KEEP)), \
            name + ": остался «AI» вместо «ИИ»"


def test_english_names_live_only_in_the_catalogue_field():
    """Латиница на слайдах не показывается: английское имя — только в карточке."""
    text = _visible_text(_html())
    latin = set(re.findall(r"[A-Za-z]{3,}", text))
    assert not latin, "на слайдах появилась латиница: " + ", ".join(sorted(latin)[:8])


# ── Страница пересобирается из данных ─────────────────────────────────────

def test_page_is_reproducible_from_its_data():
    """Правится не HTML, а данные: сборщик обязан давать тот же файл."""
    import importlib
    mod = importlib.import_module("tools.build_seminar")
    importlib.reload(mod)
    saved = _html()
    tmp = os.path.join(_ROOT, "automation", "1", "seminar", ".rebuild.html")
    real_out = mod.OUT
    mod.OUT = tmp
    try:
        mod.build()
        with open(tmp, encoding="utf-8") as f:
            fresh = f.read()
    finally:
        mod.OUT = real_out
        if os.path.exists(tmp):
            os.remove(tmp)
    assert fresh == saved, "страница разошлась с данными — пересобери tools/build_seminar.py"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print("ok   " + fn.__name__)
        except AssertionError as e:
            bad += 1
            print("FAIL " + fn.__name__ + ": " + str(e)[:300])
    print("\nТестов семинара: %d, провалено: %d" % (len(fns), bad))
    sys.exit(1 if bad else 0)
