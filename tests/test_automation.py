# -*- coding: utf-8 -*-
"""Тесты страниц курса /automation/ (FR-SITE6, SPEC-SITE.md). Без зависимостей —
запускается и как `python3 tests/test_automation.py`, и через pytest.

Область: 4 страницы визарда (welcome, roles, skills, main). Лекции
/automation/1 и /automation/2 — отдельные слайд-страницы, их НЕ проверяем.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAGES = (
    "automation/index.html",
    "automation/roles/index.html",
    "automation/skills/index.html",
    "automation/main/index.html",
)


def _pages():
    for rel in _PAGES:
        with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
            yield rel, f.read()


# ── FR-SITE6: меню убрано полностью ───────────────────────────────────────

def test_no_nav_menu():
    for rel, html in _pages():
        for bad in ("navpill", "mobileMenu", "burger", "AI Strategy"):
            assert bad not in html, "%s: следа меню быть не должно (%s)" % (rel, bad)


# ── FR-SITE6: шрифт как на главной ────────────────────────────────────────

def test_jetbrains_mono_font():
    for rel, html in _pages():
        assert "Montserrat" not in html, rel + ": Montserrat должен быть заменён"
        assert "family=JetBrains+Mono" in html, rel + ": нужен Google Fonts JetBrains Mono"
        assert re.search(r"font-family:'JetBrains Mono'", html), \
            rel + ": body должен использовать JetBrains Mono"


# ── FR-SITE6: без теней за иконками-плитками героя ────────────────────────

def test_no_tile_shadows():
    for rel, html in _pages():
        tile = re.search(r"\.tile\{[^}]*\}", html)
        if tile:  # у main/index.html плиток нет
            assert "box-shadow" not in tile.group(0), rel + ": у .tile не должно быть box-shadow"
        for m in re.finditer(r'class="tile[^"]*" style="([^"]*)"', html):
            assert "box-shadow" not in m.group(1), rel + ": инлайн-тень плитки должна быть убрана"


# ── FR-SITE6: шапка на всю ширину, CTA как на главной ─────────────────────

def test_header_full_width_and_cta():
    for rel, html in _pages():
        row = re.search(r"\.row\{[^}]*\}", html)
        assert row and "max-width" not in row.group(0), \
            rel + ": .row шапки должен быть на всю ширину (без max-width)"
        assert "@media(min-width:1024px){.row{padding:2rem}}" in html, \
            rel + ": десктопный паддинг шапки 2rem (как на главной)"
        assert "height:2.85rem;padding:0 1.4rem;font-size:11.5px;letter-spacing:.15em" in html, \
            rel + ": десктопная CTA «Консультация» = метрики CTA главной"


# ── FR-SITE11: единый рабочий адрес лого на всех страницах ────────────────

LOGO_URL = "https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png"


def test_logo_url():
    for rel, html in _pages():
        assert 'src="%s"' % LOGO_URL in html, rel + ": лого должно грузиться с " + LOGO_URL
        assert "/assets/_ait_logo.png" not in html, \
            rel + ": путь с ведущим «_» Jekyll не публикует (см. FR-SITE11)"


def test_no_underscore_asset_paths():
    """Jekyll (GitHub Pages) не публикует файлы/папки, чьи имена начинаются с «_»."""
    for rel, html in _pages():
        for m in re.finditer(r'(?:src|href)="(/[^"]*)"', html):
            parts = [p for p in m.group(1).split("/") if p]
            assert not any(p.startswith("_") for p in parts), \
                rel + ": ресурс с «_» в пути не будет опубликован: " + m.group(1)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print("\nВсе тесты /automation пройдены:", len(fns))
