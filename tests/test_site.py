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


# ── FR-SITE3 ──────────────────────────────────────────────────────────────

def test_apply_expanded_toggles_list_open():
    html = _html()
    # applyExpanded помечает раскрытый список классом body.list-open
    body = html[html.find("function applyExpanded"):html.find("function toggleExpand")]
    assert "anyOpen" in body, "applyExpanded должен считать, открыт ли хоть один список"
    assert re.search(r"classList\.toggle\(\s*'list-open'\s*,\s*anyOpen\s*\)", body), \
        "applyExpanded должен тогглить body.list-open по anyOpen"


def test_list_open_scroll_is_full_viewport():
    html = _html()
    # правило full-viewport для раскрытого списка — внутри @media (min-width:1024px)
    assert "body.list-open .scroll" in html, "нужно правило body.list-open .scroll"
    rule = html.split("body.list-open .scroll {")[1].split("}")[0]
    # box-sizing:border-box обязателен — иначе бокс с padding вылезает за края экрана
    assert "box-sizing: border-box" in rule
    assert "max-height: 100dvh" in rule and "height: 100dvh" in rule
    assert "padding-top: 6rem" in rule and "padding-bottom: 2rem" in rule
    assert "justify-content: flex-start" in rule
    # правило действует ТОЛЬКО на десктопе: ближайший @media перед ним — min-width:1024px
    before = html.split("body.list-open .scroll {")[0]
    nearest_media = before.rfind("@media (")
    assert "min-width:1024px" in before[nearest_media:nearest_media + 40], \
        "body.list-open .scroll должно быть в @media (min-width:1024px)"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("\nВсе тесты сайта пройдены:", len(fns))
