# -*- coding: utf-8 -*-
"""Тесты сайта andre.technology (index.html). Без зависимостей — запускается
и как `python3 tests/test_site.py`, и через pytest.

FR-SITE1 — «Free AI Diagnostic» ведёт на strategy.andre.technology.
FR-SITE2 — роль/подпись «AI Consultant», а не «Chief AI Officer».
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _html():
    with open(os.path.join(_ROOT, "index.html"), encoding="utf-8") as f:
        return f.read()


# ── FR-SITE1 ──────────────────────────────────────────────────────────────

def test_free_diagnostic_links_to_strategy():
    html = _html()
    # найдём каждый элемент, содержащий текст «Free AI Diagnostic», и проверим,
    # что это ссылка <a> на strategy.andre.technology
    hits = [m.start() for m in re.finditer(r"Free AI Diagnostic", html)]
    # исключим упоминания в комментариях (<!-- ... -->)
    assert hits, "на сайте должна быть кнопка «Free AI Diagnostic»"
    for pos in hits:
        # начало тега элемента слева от текста
        tag_start = html.rfind("<", 0, pos)
        el = html[tag_start:pos]
        if el.strip().startswith("<!--"):
            continue  # это комментарий, не элемент
        assert el.lstrip().startswith("<a "), \
            "«Free AI Diagnostic» должна быть ссылкой <a>, а не кнопкой: " + el[:60]
        assert "https://strategy.andre.technology/" in el, \
            "«Free AI Diagnostic» должна вести на strategy.andre.technology: " + el[:80]


def test_no_free_diagnostic_button_with_contact():
    html = _html()
    # не должно быть <button ... data-action="contact" ...>Free AI Diagnostic
    bad = re.search(r'<button[^>]*data-action="contact"[^>]*>\s*Free AI Diagnostic', html)
    assert bad is None, "«Free AI Diagnostic» не должна быть кнопкой contact"


# ── FR-SITE2 ──────────────────────────────────────────────────────────────

def test_no_chief_ai_officer():
    assert "Chief AI Officer" not in _html(), "подпись «Chief AI Officer» должна быть убрана"


def test_role_and_subtitle_are_ai_consultant():
    html = _html()
    # бейдж-роль
    assert re.search(r'class="role"[^>]*>\s*AI Consultant\s*<', html), \
        "бейдж-роль должен быть «AI Consultant»"
    # анимированная подпись героя (CUES)
    assert re.search(r'text:\s*"your AI Consultant"', html), \
        "подпись героя должна быть «your AI Consultant»"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("\nВсе тесты сайта пройдены:", len(fns))
