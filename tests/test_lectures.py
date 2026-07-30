# -*- coding: utf-8 -*-
"""Тесты лекций-презентаций /automation/1..8 (FR-SITE13, SPEC-SITE.md).
Без зависимостей — запускается и как `python3 tests/test_lectures.py`, и через pytest.

Лекции — отдельные слайд-страницы (Tailwind, Montserrat), их стиль НЕ приводится
к главной. Проверяем инварианты «портального» стиля: палитра, портальные блоки,
навигация, видео-кружок.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LECTURES = tuple("automation/%d/index.html" % n for n in range(1, 9))
_VIMEO = ("automation/3/index.html", "automation/4/index.html", "automation/5/index.html")
_NATIVE_CDN = {
    "automation/6/index.html": "corp/6/videos",
    "automation/7/index.html": "corp/7/videos",
    "automation/8/index.html": "corp/8/videos",
}


def _pages(only=None):
    for rel in (only or _LECTURES):
        with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
            yield rel, f.read()


# ── FR-SITE13: палитра портала, мяты старого стиля не осталось ────────────

def test_portal_palette():
    for rel, html in _pages():
        assert "solar: '#8B5CF6'" in html, rel + ": solar должен быть фиолетовым #8B5CF6"
        for mint in ("#35F0C7", "rgba(53,240,199", "rgba(53, 240, 199"):
            assert mint not in html, "%s: остался мятный цвет старого стиля (%s)" % (rel, mint)


# ── FR-SITE13: портальные блоки стиля и скриптов на месте ─────────────────

def test_portal_blocks_present():
    for rel, html in _pages():
        for block in ('id="portal-deck"', 'id="portal-dark"', 'id="lecture-chrome"',
                      'id="portal-theme"', 'id="portal-autostart"', 'id="portal-fit"',
                      'id="lecture-header"'):
            assert block in html, "%s: нет портального блока %s" % (rel, block)


# ── FR-SITE13: слайдер управляем извне (portal-fit, стрелки, свайп) ───────

def test_slider_api_and_swipe():
    for rel, html in _pages():
        for api in ("window.updateSlides", "window.nextSlide", "window.prevSlide"):
            assert api in html, "%s: %s должен выставляться на window" % (rel, api)
        # эталонный блок («Свайп-навигация») или родной свайп компактного шаблона (swipeStartX)
        assert "Свайп-навигация" in html or "swipeStartX" in html, \
            rel + ": нет свайп-навигации по слайдам"


# ── FR-SITE13: видео-кружок — источники видео корректны ───────────────────

def test_video_sources():
    for rel, html in _pages(_VIMEO):
        assert "player.vimeo.com/api/player.js" in html, rel + ": лекции 3-5 играют головы с Vimeo"
    for rel, html in _pages(tuple(_NATIVE_CDN)):
        path = _NATIVE_CDN[rel]
        assert "raw.githubusercontent.com/andre-kuzminykh/automation/" in html and path in html, \
            "%s: лекции 6-8 играют головы с CDN (%s)" % (rel, path)
    for rel, html in _pages():
        assert "{{VIDEO_SHA}}" not in html, rel + ": не подставлен SHA коммита с видео"


# ── FR-SITE13: число слайдов сходится с totalSlides ───────────────────────

def test_total_slides_consistent():
    for rel, html in _pages():
        real = html.count('class="slide-container')
        m = re.search(r"const totalSlides = (\d+);", html)
        if m:  # у лекций 7-8 totalSlides вычисляется динамически
            assert int(m.group(1)) == real, \
                "%s: totalSlides=%s, а слайдов в разметке %d" % (rel, m.group(1), real)
        else:
            assert "document.querySelectorAll('.slide-container').length" in html, \
                rel + ": totalSlides не задан ни константой, ни подсчётом DOM"
        assert real >= 30, "%s: подозрительно мало слайдов (%d)" % (rel, real)




# ── FR-SITE14: панель «Текст к слайду» ────────────────────────────────────

def test_notes_panel_present():
    for rel, html in _pages():
        for part in ('id="notes-panel-style"', 'id="notes-panel"', 'id="notes-panel-script"',
                     'id="notes-toggle"', 'id="notes-close"', 'id="slide-notes"'):
            assert part in html, "%s: нет части панели текста (%s)" % (rel, part)
        # кнопка живёт в шапке лекции, слева от переключателя темы
        assert re.search(r'<button id="notes-toggle".*?<button id="lec-theme"', html, re.S), \
            rel + ": кнопка текста должна стоять в шапке перед переключателем темы"


def test_notes_data_valid():
    import json
    for rel, html in _pages():
        m = re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>', html, re.S)
        assert m, rel + ": нет данных slide-notes"
        data = json.loads(m.group(1))
        total = html.count('class="slide-container')
        for key, note in data.items():
            assert key.isdigit() and int(key) < total, \
                "%s: ключ %r вне диапазона слайдов (0..%d)" % (rel, key, total - 1)
            for b in note.get("blocks", []):
                assert b.get("t") in ("p", "h", "ul", "ol", "note"), \
                    "%s: слайд %s — неизвестный тип блока %r" % (rel, key, b.get("t"))
                assert b.get("v"), "%s: слайд %s — пустой блок" % (rel, key)


def test_notes_coverage():
    import json
    for rel, html in _pages():
        data = json.loads(re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>', html, re.S).group(1))
        total = html.count('class="slide-container')
        # допускаем один непокрытый слайд (финальный экран с кнопкой теста)
        assert len(data) >= total - 1, \
            "%s: текст есть только к %d слайдам из %d" % (rel, len(data), total)


def test_no_shadows():
    """FR-SITE14: теней нет нигде — правило-глушитель есть на каждой странице."""
    for rel, html in _pages():
        assert "box-shadow:none !important" in html, rel + ": нет правила, снимающего тени"
        assert "text-shadow:none !important" in html, rel + ": нет правила, снимающего text-shadow"
        assert '[class*="drop-shadow"]{ filter:none !important; }' in html, \
            rel + ": drop-shadow-утилиты Tailwind не сняты"


def test_notes_lists_are_cards():
    """FR-SITE14: пункты перечислений — карточки, маркер на уровне первой строки."""
    for rel, html in _pages():
        assert 'class="n-li"' in html, rel + ": содержимое пункта не обёрнуто (жирный ломает флекс)"
        assert re.search(r'\.notes-body ul\.n-ul li[^{]*\{[^}]*display:flex', html), \
            rel + ": пункты списка должны быть флекс-карточками"


def test_shared_blocks_identical():
    """FR-SITE15: общие блоки во всех лекциях побайтово одинаковы.

    Лекции правятся по отдельности, и блок легко разъезжается: часть правил
    попадает в одни файлы и не попадает в другие. Тест ловит это сразу.
    """
    import hashlib
    for block, tag in (("slide-polish", "style"), ("notes-panel-style", "style"),
                       ("notes-panel-script", "script")):
        seen = {}
        for rel, html in _pages():
            m = re.search(r'<%s id="%s">(.*?)</%s>' % (tag, block, tag), html, re.S)
            assert m, "%s: нет блока %s" % (rel, block)
            seen.setdefault(hashlib.md5(m.group(1).encode()).hexdigest(), []).append(rel)
        assert len(seen) == 1, \
            "блок %s разъехался между лекциями: %s" % (block, list(seen.values()))


# ── FR-SITE16: термины панели и книги — по-русски, как на слайдах ─────────

_BOOK = "automation/AI_Automation Engineer_Book.txt"

# Англицизмы, у которых есть принятый русский эквивалент (см. FR-SITE16).
_ANGLICISMS = (
    "baseline", "payback", "hard savings", "cost avoidance", "capacity value",
    "unit economics", "governance", "guardrail", "human-in-the-loop", "human review",
    "adoption", "fine-tuning", "revenue uplift", "fully loaded", "utilization factor",
    "gross margin", "scalability ratio", "workflow", "reasoning", "retrieval",
    "backend", "webhook", "backlog", "circuit breaker", "refinement loop",
    "task grooming", "task grooming",
)

# Имена продуктов, нод и расшифровки аббревиатур латиницей остаются, плюс
# сознательно оставленные пояснения в скобках.
_TERM_KEEP = (
    "Retrieval-Augmented Generation", "Custom n8n Workflow Tool",
    "MCP Server Trigger", "MCP Client Tool",
    "идеальный путь (happy path)", "(touch time)", "(lead time)",
)

# «AI» остаётся только там, где это часть имени.
_AI_KEEP = (
    "AI-First", "AI-first", "AI-Native", "AI-native", "AI-Driven", "AI-driven",
    "AI-powered", "AI Maturity", "Chief AI Officer", "AI Product",
    "AI Automation Engineer", "AI Agent",
)


def _strip_keep(text, extra=()):
    for keep in sorted(_TERM_KEEP + tuple(extra), key=len, reverse=True):
        text = text.replace(keep, " ")
    return text


def _notes_text(html):
    import json
    data = json.loads(re.search(r'<script id="slide-notes"[^>]*>(.*?)</script>',
                                html, re.S).group(1))
    return json.dumps(data, ensure_ascii=False)


def test_notes_terms_are_russian():
    """Термин в панели должен читаться так же, как на слайде."""
    for rel, html in _pages():
        blob = _strip_keep(_notes_text(html))
        for word in _ANGLICISMS:
            assert not re.search(re.escape(word), blob, re.I), \
                "%s: в тексте панели остался англицизм %r" % (rel, word)
        blob = _strip_keep(blob, _AI_KEEP)
        assert not re.search(r"\bAI\b", blob), rel + ": в тексте панели остался «AI» вместо «ИИ»"


def test_book_terms_are_russian():
    """Книга — первоисточник панели, правится синхронно с ней."""
    with open(os.path.join(_ROOT, _BOOK), encoding="utf-8-sig") as f:
        blob = _strip_keep(f.read())
    for word in _ANGLICISMS:
        assert not re.search(re.escape(word), blob, re.I), \
            "книга: остался англицизм %r — панель и книга разъедутся" % word
    blob = _strip_keep(blob, _AI_KEEP)
    assert not re.search(r"\bAI\b", blob), "книга: остался «AI» вместо «ИИ»"


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
