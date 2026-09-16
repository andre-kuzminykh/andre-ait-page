# -*- coding: utf-8 -*-
"""FR-SITE41 — лендинг Andre AI Strategy (/strategy/ и /strategy/ru/).

Без зависимостей: `python3 tests/test_strategy.py` или через pytest.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _en():
    return _read("strategy/index.html")


def _ru():
    return _read("strategy/ru/index.html")


def _pages():
    return (("en", _en()), ("ru", _ru()))


# ── страницы, общая вёрстка и поведение ───────────────────────────────────

def test_pages_and_shared_assets_exist():
    for rel in ("strategy/index.html", "strategy/ru/index.html",
                "assets/strategy.css", "assets/strategy.js",
                "tools/build_strategy.py", "tools/strategy_copy.py"):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет файла " + rel


def test_pages_share_css_and_js():
    for lang, html in _pages():
        assert '<link rel="stylesheet" href="/assets/strategy.css">' in html, lang
        assert '<script src="/assets/strategy.js"></script>' in html, lang


def test_html_lang_and_cross_links():
    en, ru = _en(), _ru()
    assert '<html lang="en">' in en and '<html lang="ru">' in ru
    assert '<a class="lang-opt" href="/strategy/ru/">RU</a>' in en
    assert '<a class="lang-opt" href="/strategy/">EN</a>' in ru
    assert '<span class="lang-opt active">EN</span>' in en
    assert '<span class="lang-opt active">RU</span>' in ru


def test_each_page_uses_its_own_video():
    assert 'src="/assets/Andre_AIT_video_compressed.mp4"' in _en()
    assert 'src="/assets/Andre_AIT_video_compressed_ru.mp4"' in _ru()


# ── FR-SITE41: голова слева на вебе, кружок ниже и на мобилке ────────────

def test_head_turns_from_column_into_circle():
    css = _read("assets/strategy.css")
    assert re.search(r"\.head \{[^}]*position: fixed", css), "голова — фиксированный слой"
    assert re.search(r"\.head \{ left: 0; top: 0; width: var\(--head-w\); height: 100dvh", css), \
        "на вебе голова — колонка слева"
    assert ".head.mini" in css and "border-radius: 50%" in css, "ниже по странице голова становится кружком"
    mob = [b for b in re.findall(r"@media \(max-width:1023px\) \{.*?\n\}", css, re.S) if ".head {" in b]
    assert mob and "border-radius: 50%" in mob[0], "на мобилке голова сразу кружок"


def test_head_is_draggable_and_clickable():
    js = _read("assets/strategy.js")
    assert "pointerdown" in js and "pointermove" in js, "кружок должен перетаскиваться"
    assert "drag.moved < 6" in js, "короткое нажатие — это клик, а не перетаскивание"
    assert "ait_strategy_head" in js, "место кружка запоминается"


# ── меню разделов, «назад», язык ──────────────────────────────────────────

SECTIONS = ["questions", "businesses", "deliverables", "process", "model", "learning", "pricing", "start"]


def test_menu_covers_product_sections():
    for lang, html in _pages():
        for sec in SECTIONS:
            assert 'data-go="%s"' % sec in html, "%s: в меню нет раздела %s" % (lang, sec)
            assert 'id="%s"' % sec in html, "%s: нет секции %s" % (lang, sec)
        assert html.count('class="nav-tab"') == len(SECTIONS), lang + ": в меню должно быть 8 разделов"


def test_back_button_and_logo():
    for lang, html in _pages():
        assert 'id="back-btn"' in html, lang + ": нет кнопки «назад»"
        assert 'class="logo-btn" href="/"' in html, lang + ": лого ведёт на главную"
    js = _read("assets/strategy.js")
    assert "location.href = '/'" in js, "при прямом заходе «назад» ведёт на главную"


def test_language_is_stored_for_the_main_site():
    js = _read("assets/strategy.js")
    assert "localStorage.setItem('ait_lang', lang)" in js


# ── структура лендинга ───────────────────────────────────────────────────

def test_hero_and_questions():
    for lang, html in _pages():
        assert html.count('class="q-item"') == 6, lang + ": шесть вопросов по спеке"
        assert 'class="qs-final"' in html, lang + ": нет итоговой строки после вопросов"
        assert html.count('<div class="phrase"') == 3 and html.count('<div class="phrase answer"') == 1, \
            lang + ": три вопроса рядом с Андре и ответ"


def test_numbers_businesses_and_deliverables():
    for lang, html in _pages():
        assert html.count('class="num-val"') == 3, lang + ": три цифры рынка"
        assert html.count('class="biz reveal"') == 8, lang + ": восемь карточек бизнесов"
        assert html.count('class="out"') == 8, lang + ": восемь артефактов"


def test_ten_steps_with_stages_and_rail():
    for lang, html in _pages():
        assert html.count('class="story-step reveal"') == 10, lang + ": десять шагов"
        assert html.count('class="stage-card"') == 10, lang + ": десять сцен продукта"
        assert html.count('class="rail-n"') == 10, lang + ": десять номеров в колонке"
        for n in range(1, 11):
            assert 'data-step="%d"' % n in html, "%s: нет шага %d" % (lang, n)
        assert "data-transform" in html, lang + ": шаг AS-IS → TO-BE должен перестраиваться"


def test_pricing_has_four_plans_with_company_highlighted():
    for lang, html in _pages():
        assert html.count('<article class="plan') == 4, lang + ": четыре тарифа"
        assert 'class="plan best reveal"' in html, lang + ": «Компания» выделена"
        assert "$0" in html and "$59" in html and "$199" in html and "$499" in html, lang + ": цены по спеке"
    assert "1,000 operations" in _en()
    assert "1 000 операций" in _ru()


def test_cta_targets_the_product():
    for lang, html in _pages():
        hrefs = re.findall(r'class="btn btn-[a-z]+[^"]*" href="([^"]+)"', html)
        assert hrefs, lang + ": на странице должны быть кнопки"
        for h in hrefs:
            assert h == "https://strategy.andre.technology/", lang + ": кнопка ведёт мимо продукта: " + h


# ── правила спеки и владельца ────────────────────────────────────────────

def test_no_scroll_jacking():
    js = _read("assets/strategy.js")
    assert "preventDefault" not in js.split("keydown")[0] or "wheel" not in js, \
        "перехват прокрутки запрещён спекой"
    assert "'wheel'" not in js and "touchmove" not in js, "никаких обработчиков колеса и тач-прокрутки"


def test_reduced_motion_is_respected():
    css = _read("assets/strategy.css")
    js = _read("assets/strategy.js")
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "prefers-reduced-motion: reduce" in js, "скрипт тоже должен уважать настройку"


def test_headings_have_no_trailing_dots():
    """Правило владельца: точек в конце строк нет."""
    for lang, html in _pages():
        for tag in ("h1", "h2", "h3"):
            for m in re.finditer(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), html, re.S):
                text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                assert not text.endswith("."), "%s: точка в конце <%s>: %s" % (lang, tag, text[-40:])


def test_copy_follows_the_no_guarantee_rule():
    """Метрики — это то, на что целимся, а не обещанные проценты."""
    assert "not as guaranteed improvement percentages" in _en()
    assert "не как гарантированные проценты улучшения" in _ru()
    # и не обещаем «замену McKinsey за $499»
    for lang, html in _pages():
        assert "replace McKinsey" not in html and "заменяем McKinsey" not in html, lang


if __name__ == "__main__":
    import sys
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   " + name)
            except AssertionError as e:
                fails += 1
                print("FAIL " + name + ": " + str(e))
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not fails else "ПРОВАЛЕНО: %d" % fails)
    sys.exit(1 if fails else 0)
