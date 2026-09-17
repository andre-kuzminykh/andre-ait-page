# -*- coding: utf-8 -*-
"""FR-SITE41 — лендинг AI Strategy (/ai-strategy/ и /ai-strategy/ru/).

Страница листается экранами, как биография и главная. Без зависимостей:
`python3 tests/test_strategy.py` или через pytest.
"""
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(rel):
    with open(os.path.join(_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _en():
    return _read("ai-strategy/index.html")


def _ru():
    return _read("ai-strategy/ru/index.html")


def _pages():
    return (("en", _en()), ("ru", _ru()))


# ── страницы, общая вёрстка, языки ────────────────────────────────────────

def test_pages_and_shared_assets_exist():
    for rel in ("ai-strategy/index.html", "ai-strategy/ru/index.html",
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
    assert '<a class="lang-opt" href="/ai-strategy/ru/">RU</a>' in en
    assert '<a class="lang-opt" href="/ai-strategy/">EN</a>' in ru
    assert '<span class="lang-opt active">EN</span>' in en
    assert '<span class="lang-opt active">RU</span>' in ru


def test_each_page_uses_its_own_video():
    """У лендинга свои ролики — владелец прислал их отдельно от главной."""
    assert 'src="/assets/strategy_en.mp4"' in _en()
    assert 'src="/assets/strategy_ru.mp4"' in _ru()


def test_language_is_stored_for_the_main_site():
    assert "localStorage.setItem('ait_lang', lang)" in _read("assets/strategy.js")


def test_pages_are_generated_not_hand_written():
    """Править ai-strategy/*.html руками нельзя — сборка перезапишет."""
    for lang, html in _pages():
        assert "tools/build_strategy.py" in html, lang + ": в шапке файла нет отметки о сборке"


# ── FR-SITE41: лицо слева на полэкрана, кружок только на мобилке ──────────

def test_face_is_always_half_the_screen_on_web():
    """Колода начинается с половины экрана, а сам ролик ШИРЕ — как на главной
    (там 60% при колонке текста 44%): хвост растушёвки уходит под колоду, и
    лицо не приходится затемнять, чтобы спрятать край кадра."""
    css = _read("assets/strategy.css")
    assert "--head-w: 50%;" in css, "лицо занимает половину экрана"
    assert re.search(r"\.head \{ left: 0; top: 0; width: 60%;[^}]*z-index: 3", css), \
        "ролик шире отступа колоды и лежит ПОД ней"
    assert "50vw" not in css, "рамку страницы нельзя мерить в vw: body{zoom} их умножает"
    assert ".head.mini" not in css, "на вебе голова не сжимается в кружок"
    mob = [b for b in re.findall(r"@media \(max-width:1023px\) \{.*?\n\}", css, re.S) if ".head {" in b]
    assert mob and "border-radius: 50%" in mob[0], "на мобилке голова — кружок"


def test_head_is_draggable_on_mobile_and_clickable():
    js = _read("assets/strategy.js")
    assert "pointerdown" in js and "pointermove" in js, "кружок на мобилке должен перетаскиваться"
    assert "if (mqDesk.matches) return;" in js, "на вебе лицо — колонка, двигать нечего"
    assert "ait_strategy_head" in js, "место кружка запоминается"


# ── лендинг листается экранами, как биография ─────────────────────────────

SCREEN_IDS = ["top", "numbers", "usecases", "solution",
              "learning", "pricing", "start"]


def test_landing_is_a_deck_of_screens():
    """Не простыня и не scroll-snap: экраны сменяют друг друга анимацией."""
    css = _read("assets/strategy.css")
    assert "scroll-snap-type: y" not in css, "вертикальной прокрутки страницы нет — только смена экранов"
    assert "scroll-snap-type: x mandatory" in css, "горизонтальная лента артефактов прилипает по-прежнему"
    assert re.search(r"html, body \{.*?overflow: hidden", css, re.S), "страница сама не прокручивается"
    assert ".screen.active { display: flex; }" in css
    assert ".deck.leaving .screen.active" in css and ".deck.entering .screen.active" in css
    assert "@keyframes slideInScreen" in css
    for lang, html in _pages():
        assert html.count('<section class="screen') == 13, lang + ": тринадцать экранов"
        for sid in SCREEN_IDS:
            assert 'id="%s"' % sid in html, "%s: нет экрана %s" % (lang, sid)


def test_screens_switch_by_wheel_swipe_and_keys():
    js = _read("assets/strategy.js")
    for handler in ("'wheel'", "'touchstart'", "'touchend'", "'keydown'"):
        assert js.count(handler), "нет обработчика " + handler
    assert "innerScroll" in js, "внутри прокручиваемых лент колесо не перехватывается"
    assert re.search(r"now - lastWheel < \d+", js), "один жест = один экран"


def test_menu_lists_six_product_chapters():
    """Экран с вопросами удалён, первый пункт теперь «Solution» (правка владельца)."""
    nav = ["solution", "usecases", "process", "learning", "pricing", "start"]
    for lang, html in _pages():
        header = html[html.index("<header>"):html.index("</header>")]
        for key in nav:
            assert 'data-go="%s"' % key in header, "%s: в меню нет раздела %s" % (lang, key)
        assert header.count('class="nav-tab') == len(nav), lang + ": в меню шесть разделов"
    assert ">Use Cases<" in _en(), "раздел называется Use Cases, а не Businesses"
    assert ">Problem<" not in _en(), "пункта «Problem» в меню быть не должно"
    assert ">Solution<" in _en(), "первый раздел называется Solution"


def test_home_icon_replaces_the_back_button():
    """Правка владельца: «вместо кнопки BACK иконку домой рядом с меню»."""
    css = _read("assets/strategy.css")
    assert ".back {" not in css, "овала «назад» на странице больше нет"
    home = re.search(r"\.nav-home \{(.*?)\}", css, re.S)
    assert home, "нет стиля иконки дома"
    for lang, html in _pages():
        header = html[html.index("<header>"):html.index("</header>")]
        assert header.count('class="nav-home" href="/"') == 1, lang + ": одна иконка дома в шапке"
        assert header.index('class="nav-home"') < header.index('class="nav-tab'), \
            lang + ": иконка дома стоит ПЕРЕД пунктами меню"
        assert 'class="back"' not in html, lang + ": кнопок «назад» на экранах больше нет"
        assert 'class="prod-name"' not in html, lang + ": у лого не пишем название продукта"
    assert "location.href = '/'" not in _read("assets/strategy.js"), \
        "иконка дома — обычная ссылка, скрипт тут не нужен"


def test_header_matches_the_main_site():
    """Кнопки сверху — того же размера и на тех же местах, что на главной."""
    css = _read("assets/strategy.css")
    site = _read("index.html")
    for rule in ("width: clamp(2.85rem, 12vw, 3.7rem)",     # лого
                 "height: 2.85rem",                          # пилюля меню и кнопка
                 "font-size: clamp(12.5px, 1.05vw, 14px); font-weight: 500",        # пункты меню
                 "padding: 0 1.4rem; font-size: 11.5px"):    # кнопка действия
        assert rule in css, "в шапке лендинга нет правила «%s» с главной" % rule
    # палочки между пунктами — как на главной и в биографии
    assert '.nav-divider { display: inline; color: rgba(255,255,255,0.22); font-size: 12px;' in css, \
        "нет разделителей меню с главной"
    for lang, html in _pages():
        assert html.count('<span class="nav-divider" aria-hidden="true">|</span>') == 5, \
            lang + ": палочка стоит между каждой парой из шести пунктов"
        assert rule in site or rule.replace("; ", ";\n") in site, "правило «%s» изменилось на главной" % rule
    assert "location.href = '/'" not in _read("assets/strategy.js"), \
        "«назад» — обычная ссылка на главную, скрипт тут не нужен"


def test_page_scales_like_the_main_site():
    """Масштабирование body zoom — как на главной, чтобы вид совпадал."""
    css = _read("assets/strategy.css")
    site = _read("index.html")
    for w in ("1600px", "1900px", "2300px"):
        assert re.search(r"min-width: ?%s" % w, css), "нет ступени масштаба " + w
        assert re.search(r"min-width: ?%s" % w, site), "ступень %s пропала на главной" % w
    assert css.count("zoom:") >= 3, "масштаб задаётся через zoom, как на главной"


# ── первый экран ──────────────────────────────────────────────────────────

def test_hero_headline_is_two_lines_with_orange_business():
    for lang, html in _pages():
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1)
        assert h1.count('<span class="l">') == 2, lang + ": заголовок ровно в две строки"
        assert 'class="hl-o">' in h1, lang + ": «бизнес» — оранжевым"
    assert "AI Strategy shows how to transform your business with AI" in _en()
    assert 'class="hl-o">business<' in _en()
    assert 'class="hl-o">бизнес' in _ru()


def test_hero_has_two_buttons_of_equal_size():
    css = _read("assets/strategy.css")
    hero = re.search(r"\.hero-cta \.btn \{([^}]*)\}", css).group(1)
    assert "width: 13.5rem" in hero and "flex: 0 0 13.5rem" in hero, \
        "две кнопки первого экрана — ровно одного размера"
    for lang, html in _pages():
        hero = html[html.index('id="top"'):html.index("</section>", html.index('id="top"'))]
        assert hero.count('class="btn btn-') == 2, lang + ": на первом экране ровно две кнопки"


def test_buttons_do_not_move_on_hover():
    """Правка владельца: кнопка не должна ездить под курсором."""
    css, js = _read("assets/strategy.css"), _read("assets/strategy.js")
    assert "magnetic" not in css and "magnetic" not in js, "магнитных кнопок быть не должно"
    for m in re.finditer(r"\.btn[^{]*:hover \{([^}]*)\}", css):
        assert "translate" not in m.group(1), "кнопка не смещается при наведении: " + m.group(1)


# ── экран «Problem» и цифры рынка ─────────────────────────────────────────

def test_questions_screen_is_gone():
    """Владелец убрал экран «The problem is no longer access to AI» целиком."""
    for lang, html in _pages():
        assert 'class="q-item"' not in html, lang + ": экран с вопросами должен быть удалён"
        for mark in ("The problem is no longer", "Проблема больше не в доступе",
                     "That is exactly what AI Strategy", "Именно на эти вопросы"):
            assert mark not in html, "%s: остался текст «%s»" % (lang, mark)
    assert ".q-item" not in _read("assets/strategy.css"), "правила удалённого экрана убраны"


def test_process_intro_screen_is_gone():
    """«От „нам нужен ИИ“…» убран — сразу к зрелости."""
    for lang, html in _pages():
        for mark in ("here’s what to build", "вот что мы строим"):
            assert mark not in html, "%s: вводный экран шагов должен быть удалён" % lang
        first_step = html.index('data-step="1"')
        assert html.index('id="usecases"') < first_step, lang + ": шаги идут после кейсов"


def test_market_numbers_are_four_squares_without_hover_jump():
    css = _read("assets/strategy.css")
    for m in re.finditer(r"\.num-card:hover \{([^}]*)\}", css):
        assert "translate" not in m.group(1), "квадраты не прыгают при наведении"
    for lang, html in _pages():
        assert html.count('class="num-card"') == 4, lang + ": четыре квадрата рынка"
        assert html.count('class="num-val"') == 4, lang + ": четыре цифры"
        for v in ("76", "14", "81", "73"):
            assert ">%s" % v in html, "%s: нет цифры %s" % (lang, v)
        assert 'class="nums-foot"' in html, lang + ": оранжевая строка про конкурентов"
    assert "Don’t let your competitors get ahead with AI" in _en()
    assert "Anthropic" not in _en(), "сноску про Anthropic владелец просил убрать"


# ── Use Cases ─────────────────────────────────────────────────────────────

def test_use_cases_fit_one_screen_with_one_metric_each():
    for lang, html in _pages():
        assert html.count('class="biz"') == 8, lang + ": восемь карточек"
        assert html.count('class="biz-metric"') == 8, lang + ": по одной метрике на карточку"
        assert html.count('class="biz-ic"') == 8, lang + ": иконка слева от названия"
        assert html.count('class="biz-go"') == 8, lang + ": «Explore» справа"
        assert 'class="biz-all"' in html, lang + ": простая ссылка на все типы бизнеса"
    css = _read("assets/strategy.css")
    assert re.search(r"\.biz-grid \{[^}]*minmax\(0, ?1fr\)", css), "карточки не вылезают за экран"
    assert ".rail-wrap::before" in css and ".rail-wrap::after" in css, \
        "края ленты уходят в тёмный градиент"


# ── Solution: восемь артефактов с новыми названиями ───────────────────────

DELIVERABLES_EN = ["AI Maturity Index", "Process Map", "Cognitive Map", "AI Opportunities",
                   "Human + AI", "AI-First Model", "AI Agents", "Roadmap"]


def test_solution_cards_use_the_agreed_names():
    en = _en()
    assert en.count('class="out"') == 8, "восемь артефактов"
    for name in DELIVERABLES_EN:
        assert ">%s<" % name in en, "нет карточки «%s»" % name
    for lang, html in _pages():
        assert html.count('class="out"') == 8, lang + ": восемь артефактов"


# ── How it works: шесть шагов и перелёт оранжевых блоков ──────────────────

def test_six_steps_each_on_its_own_screen():
    for lang, html in _pages():
        assert html.count('class="screen step-screen"') == 6, lang + ": шесть шагов"
        assert html.count('<div class="stage-card"') == 6, lang + ": шесть сцен продукта"
        for n in range(1, 7):
            assert 'data-step="%d"' % n in html, "%s: нет шага %d" % (lang, n)
        assert 'data-step="7"' not in html, lang + ": шагов должно быть шесть, не больше"


def test_orange_blocks_fly_from_process_to_opportunities_to_ai_first():
    """Правка владельца: оранжевые блоки перелетают AS-IS → AI Opportunity → AI-First."""
    for lang, html in _pages():
        keys = re.findall(r'data-flip="([a-zа-яё0-9-]+)"', html)
        trio = [k for k in set(keys) if keys.count(k) == 3]
        assert len(trio) == 3, \
            "%s: три блока должны проходить все три сцены, нашлось %s" % (lang, sorted(trio))
        for cls in ("pnode human", "opnode", "fnode human"):
            assert re.search(r'class="%s" data-seq data-flip="[a-zа-яё0-9-]+"' % cls, html), \
                "%s: нет связанного блока на сцене «%s»" % (lang, cls)
        # то, что забрал ИИ, пары не находит и просто гаснет
        solo = [k for k in set(keys) if keys.count(k) == 1]
        assert solo, lang + ": операции, ушедшие к ИИ, не должны иметь пары"
    js = _read("assets/strategy.js")
    assert "captureFlip" in js and "playFlip" in js, "перелёт блоков должен быть реализован"
    assert "offsetIn" in js, "позиции считаются через offset, чтобы transform не мешал"
    css = _read("assets/strategy.css")
    assert ".deck.morph .screen.active .stage-card" in css, \
        "во время перелёта карточка не въезжает заново"
    assert ".deck.leaving.morph-out .screen.active { transform: none; }" in css, \
        "уходящий экран при перелёте только гаснет"


def test_people_are_orange_and_agents_are_purple():
    css = _read("assets/strategy.css")
    ORANGE, PURPLE = "249,115,22", "136,84,243"
    assert re.search(r"\.pnode\.human \{[^}]*" + ORANGE, css), "люди в процессах — оранжевые"
    assert re.search(r"\.fnode\.human \{[^}]*" + ORANGE, css), "люди в AI-First — оранжевые"
    assert re.search(r"\.fnode\.ai \{[^}]*" + PURPLE, css), "агенты — фиолетовые"


def test_maturity_score_stands_right_above_the_bars():
    """Правка владельца: «оценку выровни с графиками чтобы над ними ровно была».

    Значит оценка живёт в одной колонке с графиками, а не по центру всей
    панели: раньше она стояла отдельным блоком над .maturity."""
    css = _read("assets/strategy.css")
    assert re.search(r"\.score \{[^}]*justify-content: flex-start", css), \
        "оценка выключена по левому краю колонки графиков"
    for lang, html in _pages():
        card = html[html.index('data-step="1"'):html.index('data-step="2"')]
        col = card[card.index('class="dimcol"'):]
        assert col.index('class="score"') < col.index('class="dims"'), \
            lang + ": оценка стоит НАД графиками внутри их колонки"
        assert card.index('class="radar"') < card.index('class="score"'), \
            lang + ": паутина слева, колонка с оценкой и графиками справа"
    en = _en()
    for dim in ("Strategy", "People", "Infrastructure", "Data", "Models", "Implementation", "R&D"):
        assert ">%s<" % dim in en, "нет оси зрелости «%s»" % dim


def test_agent_passport_fields_sit_around_the_agent():
    """Иконка агента — в центре, поля вокруг. Радиусы кольца заданы в CSS
    (--rx/--ry), в вёрстку уходят только косинус и синус: на низком окне поля
    на окружности налезали друг на друга, и кольцо пришлось растянуть по
    горизонтали, оставив саму орбиту круглой."""
    css = _read("assets/strategy.css")
    assert "var(--cx, 0) * var(--rx, 50%)" in css and "var(--cy, 0) * var(--ry, 40%)" in css, \
        "положение поля считается из --cx/--cy и радиусов кольца"
    assert re.search(r"@media \(max-height:799px\) \{[^}]*--rx", css, re.S), \
        "на низком окне кольцо шире по горизонтали"
    for lang, html in _pages():
        spokes = re.findall(r'<span class="spoke" data-seq style="--cx:(-?[\d.]+); --cy:(-?[\d.]+);', html)
        assert len(spokes) == 8, lang + ": восемь полей паспорта агента"
        assert len(set(spokes)) == 8, lang + ": поля не должны слипаться в центре"
        assert 'class="hub-core"' in html, lang + ": агент в центре"


def test_agent_passport_fields_are_opaque_and_have_icons():
    """Правка владельца: «сделай чтобы не прозрачные были эти теги тёмные и
    иконки у каждого тега»."""
    css = _read("assets/strategy.css")
    assert re.search(r"\.spoke \{[^}]*background: #060609", css, re.S), \
        "плашка поля закрашена чёрным, а не полупрозрачная"
    assert re.search(r"\.spoke \{[^}]*z-index: 2", css, re.S), \
        "плашка выше орбиты: ::after у .hub — последний ребёнок и рисовался поверх текста"
    assert ".spoke i { font-size: 0.95em; color: var(--p-l); }" in css, "иконка поля фиолетовая"
    assert ".spoke:nth-of-type(even) i { color: var(--o-l); }" in css, "через одно — оранжевая"
    for lang, html in _pages():
        hub = html[html.index('class="hub"'):html.index('class="hub"') + 3000]
        icons = re.findall(r'<span class="spoke"[^>]*><i class="fa-solid (fa-[a-z-]+)"></i>', hub)
        assert len(icons) == 8, lang + ": иконка у каждого из восьми полей"
        assert len(set(icons)) == 8, lang + ": иконки полей не повторяются"


def test_company_model_and_team_blocks_are_gone():
    """Владелец просил убрать блоки модели компании и команды."""
    for lang, html in _pages():
        assert 'id="model"' not in html, lang + ": блок модели компании удалён"
        assert 'id="team"' not in html, lang + ": блок команды удалён"


# ── Learning ──────────────────────────────────────────────────────────────

def test_learning_has_an_endless_roles_ticker():
    css = _read("assets/strategy.css")
    assert "@keyframes tick" in css and "translateX(-50%)" in css, "лента ролей крутится без конца"
    for lang, html in _pages():
        assert html.count('class="role"') == 24, lang + ": 12 ролей, продублированных для бесшовной ленты"
        roles = html[html.index('class="ticker"'):]
        assert roles.count("fa-solid") >= 24, lang + ": у каждой роли своя иконка"


# ── Pricing ───────────────────────────────────────────────────────────────

def test_pricing_is_one_block_with_strikethrough_comparison():
    for lang, html in _pages():
        assert html.count('<article class="plan') == 4, lang + ": четыре тарифа"
        assert html.count('class="cmp old"') >= 1, lang + ": сравнение зачёркнуто"
        assert "$0" in html and "$59" in html and "$199" in html and "$499" in html, lang
        assert "What is an operation?" not in html and "Что такое операция?" not in html, \
            lang + ": пояснение про операции владелец просил убрать"
    css = _read("assets/strategy.css")
    assert "text-decoration: line-through" in css, "старая цена зачёркнута"
    assert re.search(r"\.plans \{[^}]*minmax\(0, ?1fr\)", css), "тарифы не вылезают за экран"


# ── финал и подвал ────────────────────────────────────────────────────────

def test_final_screen_carries_the_footer():
    for lang, html in _pages():
        final = html[html.index('id="start"'):]
        assert "<footer" in final, lang + ": подвал живёт на последнем экране"
        assert 'class="company"' not in final, \
            lang + ": отдельной строки с названием компании перед иконками быть не должно"
        assert "Andre AI Technologies LTD" in final, lang + ": название компании — в копирайте внизу"
        assert "2026" in final, lang + ": копирайт внизу"
        assert final.count("fa-") >= 3, lang + ": иконки соцсетей внизу"


def test_cta_targets_the_product():
    for lang, html in _pages():
        hrefs = re.findall(r'class="btn btn-[a-z]+[^"]*" href="([^"]+)"', html)
        assert hrefs, lang + ": на странице должны быть кнопки"
        for h in hrefs:
            assert h == "https://strategy.andre.technology/", lang + ": кнопка ведёт мимо продукта: " + h


# ── общие правила спеки и владельца ───────────────────────────────────────

def test_reduced_motion_is_respected():
    css, js = _read("assets/strategy.css"), _read("assets/strategy.js")
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert "prefers-reduced-motion: reduce" in js, "скрипт тоже должен уважать настройку"


def test_headings_have_no_trailing_dots():
    for lang, html in _pages():
        for tag in ("h1", "h2", "h3"):
            for m in re.finditer(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), html, re.S):
                text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                assert not text.endswith("."), "%s: точка в конце <%s>: %s" % (lang, tag, text[-40:])


def test_copy_makes_no_guarantees():
    for lang, html in _pages():
        assert "replace McKinsey" not in html and "заменяем McKinsey" not in html, lang


def test_agent_passport_is_purple_orange():
    """Правка владельца: «где агент давай фиолетово-оранжевый»."""
    css = _read("assets/strategy.css")
    core = re.search(r"\.hub-core \{(.*?)\}", css, re.S).group(1)
    assert "rgba(136,84,243" in core and "rgba(249,115,22" in core, \
        "карточка агента должна быть фиолетово-оранжевой"
    edge = re.search(r"\.hub-core::before \{(.*?)\}", css, re.S).group(1)
    assert "var(--p)" in edge and "var(--o)" in edge, "рамка агента — градиент из двух цветов"
    assert ".spoke:nth-of-type(even) { border-color: rgba(249,115,22" in css, \
        "поля вокруг агента чередуются фиолетовым и оранжевым"


def test_process_chain_has_no_dangling_connectors():
    """Цепочка идёт рядами по три со стрелкой переноса — без висящих чёрточек."""
    css = _read("assets/strategy.css")
    assert ".pnode.linked::after" not in css, "псевдо-соединители убраны"
    assert ".prow {" in css and ".pwrap {" in css, "цепочка рисуется рядами"
    for lang, html in _pages():
        assert html.count('class="prow"') == 2, lang + ": два ряда процессов"
        assert html.count('class="pwrap"') == 1, lang + ": одна стрелка переноса"
        assert html.count('class="frow"') == 2, lang + ": AI-First тоже рядами"


def test_one_line_headings_are_fitted_by_script():
    """clamp в vw не спасал: на 1280–1366px строка вылезала за колонку."""
    js = _read("assets/strategy.js")
    assert "function fitHeadings" in js, "нет подбора кегля"
    assert "fitHeadings(screens[cur])" in js, \
        "подбор обязан работать на показанном экране: у скрытого clientWidth = 0"
    assert "!root.querySelectorAll" in js, \
        "resize передаёт событие — его нельзя принимать за узел"


def test_rail_left_fade_only_after_scrolling():
    """Растушёвка слева гасила первую карточку в покое."""
    css = _read("assets/strategy.css")
    assert ".rail-wrap.scrolled::before { opacity: 1; }" in css
    assert re.search(r"\.rail-wrap::before \{[^}]*opacity: 0", css, re.S), \
        "в покое левой растушёвки нет"
    assert "classList.toggle('scrolled'" in _read("assets/strategy.js")


def test_explore_label_survives_on_mobile():
    """Владелец просил подпись «Explore →», а не голую стрелку."""
    css = _read("assets/strategy.css")
    assert ".biz-go span { display: none; }" not in css, \
        "на мобилке подпись «Explore» не прячем"


def test_final_screen_content_is_centred():
    """На финальном экране между кнопкой и подвалом зияла половина экрана."""
    css = _read("assets/strategy.css")
    wrap = re.search(r"\.final \.wrap \{(.*?)\}", css, re.S).group(1)
    assert "justify-content: center" in wrap, "призыв — по центру экрана"
    assert "flex: 1 1 auto" in wrap, "блок занимает высоту до подвала"
    assert ".final footer { margin-top: auto;" in css, "подвал прижат к низу"


def test_screens_never_clip_their_top_when_content_is_tall():
    """Обе страницы центрируют экран по вертикали (правка владельца «по
    середине всё»), но именно `safe center`: при обычном center содержимое
    выше экрана обрезается сверху и до него не доскроллить."""
    for name in ("assets/strategy.css", "assets/about.css"):
        css = _read(name)
        assert "justify-content: center; justify-content: safe center" in css, \
            name + ": экран центрируется, но именно safe — иначе верх длинного экрана обрезается"


def test_process_blocks_are_the_same_size_on_every_scene():
    """Правка владельца «элементы покрупнее» самонейтрализовалась: в правилах
    .node и .opnode было ПО ДВА объявления font-size, и меньшее побеждало."""
    css = _read("assets/strategy.css")
    for sel in (".node {", ".opnode {"):
        i = css.index(sel)
        body = css[i:css.index("}", i)]
        assert body.count("font-size:") <= 1, \
            "в правиле «%s» два объявления font-size — крупное перебивается мелким" % sel
    assert ".node, .pnode, .opnode, .fnode { font-size: 12px;" in css, \
        "один и тот же шаг обязан быть одного кегля на всех сценах"


def test_step_panel_geometry_is_fixed():
    """Шесть шагов обязаны стоять на одном месте: фиксируем и шапку, и рамку.

    Постоянную высоту шапки держит РЕЗЕРВ ПОДЗАГОЛОВОКА в две строки, а не
    height на всём блоке: с фиксированной высотой под худший случай под
    текстом шага зияла пустота почти в 90px до панели (правка владельца
    «текст поближе надо к карточке, и это во всех таких слайдах»)."""
    css = _read("assets/strategy.css")
    assert ".step-copy { height:" not in css, \
        "фиксированной высоты у шапки шага нет — от неё пустота под текстом"
    assert ".step-copy p { margin-bottom: 0; line-height: 1.6; min-height: 1.6em; }" in css, \
        "высоту шапки держит резерв подзаголовка в одну строку"
    assert re.search(r"\.stage-card \{[^}]*height: min\(", css, re.S), "высота панели фиксирована"
    assert ".stage-card > .ui { width: 100%; height: 100%;" in css, \
        "рамка тянется на всю панель, иначе она скакала со 152 до 414px"
    assert "grid-template-columns: minmax(0, 1fr); grid-template-rows" in css, \
        "неявная колонка грида равна max-content и растягивала шаг за экран"


def test_market_squares_are_equal_height_without_aspect_ratio():
    """aspect-ratio вместе с align-self:stretch считал ШИРИНУ от высоты и
    выбрасывал карточки из ячеек на 86px."""
    css = _read("assets/strategy.css")
    assert "aspect-ratio: 1 / 0.46" not in css, "пропорции у квадратов рынка быть не должно"
    assert ".num-card { align-self: stretch; }" in css, "карточки тянутся на высоту ряда"
    assert re.search(r"\.num-card \{[^}]*min-height:", css, re.S), "высота задана min-height"


def test_grids_never_widen_past_their_column():
    """У 1fr минимум равен min-content: блок в одну строку раздвигал сетку."""
    css = _read("assets/strategy.css")
    assert "repeat(4, 1fr)" not in css and "repeat(2, 1fr)" not in css, \
        "во всех сетках нужен minmax(0, 1fr)"


def test_mobile_hero_headline_is_bigger_than_section_headings():
    """Правка владельца «побольше надо»: на мобилке nowrap зажимал заголовок
    первого экрана до размера обычных заголовков разделов."""
    css = _read("assets/strategy.css")
    blocks = [b for b in re.findall(r"@media \(max-width:1023px\) \{(.*?)\n\}", css, re.S)
              if re.search(r"\bh1 \{", b)]
    assert blocks, "нет мобильного правила для заголовка первого экрана"
    assert any("8.4vw" in b for b in blocks), \
        "кегль заголовка на мобилке считается от ширины окна"
    assert "h1 .l { white-space: normal; }" in css, "на мобилке строки переносятся"
    assert "if (!mqDesk.matches)" in _read("assets/strategy.js"), \
        "подбор кегля не должен трогать мобильный заголовок"


def test_maturity_scene_has_radar_left_and_seven_bars_right():
    """Правка владельца: «слева паутина, справа графики горизонтальные»."""
    css = _read("assets/strategy.css")
    assert ".maturity { display: grid;" in css, "сцена зрелости — две колонки"
    for lang, html in _pages():
        card = html[html.index('data-step="1"'):html.index('data-step="2"')]
        assert card.index('class="radar"') < card.index('class="dims"'), \
            lang + ": паутина слева, графики справа"
        assert card.count('class="dim"') == 7, lang + ": семь показателей"
        assert "/ 5 &middot; " not in card, lang + ": название индекса дублировать не нужно"
        assert 'class="ui-bar"' in card, lang + ": название индекса остаётся на панели"
    assert "<text" not in _en(), "подписей осей на самой паутине нет — они у графиков справа"


def test_scene_animations_start_after_the_screen_is_shown():
    """Переход НЕ стартует для элемента, который в этом же кадре был display:none:
    браузеру не от чего анимировать. Поэтому конечное состояние — на классе .lit."""
    js = _read("assets/strategy.js")
    assert "function sceneIn" in js and "classList.add('lit')" in js, "нет запуска анимаций сцены"
    assert "sceneIn(screens[cur])" in js, "анимации запускаются при показе экрана"
    css = _read("assets/strategy.css")
    for rule in (".screen.lit .dim-fill", ".screen.lit .radar .shape", ".screen.lit .stage-card .prow"):
        assert rule in css, "конечное состояние «%s» должно висеть на .lit" % rule
    assert ".screen.active .radar .shape" not in css, \
        "старое правило на .active зажигало паутину сразу"


def test_quote_is_typed_out():
    """Правка владельца: фраза про заявки с сайта должна ПЕЧАТАТЬСЯ."""
    for lang, html in _pages():
        assert 'class="typing" data-type="' in html, lang + ": цитата набирается скриптом"
        assert 'class="typed"' in html, lang + ": есть место под набираемый текст"
    js = _read("assets/strategy.js")
    assert "function typeIn" in js and "setInterval" in js, "нет печати"
    assert "if (reduce)" in js, "при отключённых анимациях текст ставится сразу"


def test_removed_labels_are_gone():
    """Владелец убрал чипы эффекта/сложности и легенду People / AI agents."""
    css = _read("assets/strategy.css")
    for lang, html in _pages():
        assert 'class="chips"' not in html, lang + ": чипы эффекта и сложности убраны"
        assert 'class="legend"' not in html, lang + ": легенда убрана"
    assert ">Explore<" not in _en() and ">Открыть<" not in _ru(), \
        "у карточек кейсов только стрелка, без подписи"


def test_everything_is_centred_including_buttons():
    css = _read("assets/strategy.css")
    assert re.search(r"\.hero-cta \{[^}]*justify-content: center", css), "кнопки первого экрана по центру"
    assert re.search(r"\.biz-all \{[^}]*margin: 0 auto", css), "ссылка на все типы бизнеса по центру"


def test_opportunities_use_the_same_rows_as_the_other_scenes():
    """Жалоба владельца «не вмещается документ анализ»: жёсткая сетка 4×2
    давала колонку в четверть ширины панели, и длинная подпись не влезала в
    неё даже на минимальном кегле. Теперь сцена собрана такими же рядами,
    как соседние, и блоки стоят своей естественной ширины."""
    css = _read("assets/strategy.css")
    assert ".opgrid" not in css, "жёсткой сетки возможностей больше нет"
    assert re.search(r"\.opnode \{ display: inline-flex", css), "блок занимает свою ширину"
    assert "width: fit-content; max-width: 100%" not in css, \
        "ограничения по ширине колонки быть не должно — оно и обрезало подпись"
    for lang, html in _pages():
        card = html[html.index('data-step="4"'):html.index('data-step="5"')]
        assert 'class="opgrid"' not in card, lang + ": сетки возможностей нет"
        assert card.count('class="opgroup"') == 2, lang + ": две группы — фиолетовая и серая"
        assert card.count('class="prow oprow"') == 3, lang + ": ряды не длиннее трёх блоков"
        assert card.count('class="opnode') == 8, lang + ": восемь операций"
        # правка владельца «сверху фиолетовое, снизу серое»: ряд никогда не
        # смешивает группы, иначе в середине панели стояли блоки обоих цветов
        first, second = card.split('class="opgroup"')[1:3]
        assert second.count("opnode can") == 0, lang + ": во второй группе только серые"
        assert first.count("opnode can") == 5, lang + ": в первой группе только фиолетовые"
    assert "Document analysis" in _en() and "Разбор документов" in _ru(), \
        "подпись операции сохранена целиком, а не урезана ради вёрстки"


def test_process_cascade_runs_through_both_rows():
    """Правка владельца «анимация во всех слайдах с процессами фиговая»:
    задержки висели на :nth-child внутри ряда, поэтому второй ряд начинался
    заново, а сцены возможностей и AI-First вообще не были подключены и
    вспыхивали целиком."""
    css = _read("assets/strategy.css")
    assert "transition-delay: calc(var(--i, 0) * 0.055s)" in css, \
        "задержка считается из сквозного номера элемента"
    assert ".prow > :nth-child(1) { transition-delay" not in css, \
        "порядковых задержек внутри ряда больше нет"
    for sel in (".stage-card .prow > *", ".stage-card .frow > *", ".stage-card .pwrap", ".stage-card .fwrap"):
        assert sel in css, "каскад не подключён к " + sel
    assert ".screen.lit .stage-card .frow > *" in css, \
        "конечное состояние на .lit: переход не стартует для скрытого в этом же кадре элемента"
    assert ".stage-card .flying { opacity: 1 !important; transition-delay: 0s !important; }" in css, \
        "прилетевший с прошлой сцены блок каскад не ждёт"
    for lang, html in _pages():
        for step in (3, 4, 5):
            card = html[html.index('data-step="%d"' % step):html.index('data-step="%d"' % (step + 1))]
            nums = [int(x) for x in re.findall(r'style="--i:(\d+)"', card)]
            assert nums == list(range(len(nums))), \
                "%s: шаг %d — сквозная нумерация без пропусков" % (lang, step)
            assert len(nums) >= 8, "%s: шаг %d — пронумерованы и блоки, и связи" % (lang, step)


def test_chain_keeps_air_at_the_panel_edges():
    """Жалоба владельца «почти за края выходит»: подгонка сравнивала ряд с
    внешней рамкой панели, и цепочка вставала вплотную к ней."""
    js = _read("assets/strategy.js")
    assert "var AIR = 14;" in js, "у ряда остаётся воздух по краям"
    assert "paddingLeft" in js and "paddingRight" in js, \
        "ширина считается по содержимому панели, а не по внешней рамке"
    assert "$$('.pnode, .fnode, .node, .opnode', root)" in js, \
        "кегль блокам возможностей подбирается вместе с остальными"


def test_final_screen_has_the_robot_and_coins_mark():
    """Правка владельца: «просто иконка агента, а слева и справа монетки как
    фонтан появляются и исчезают бесконечно»."""
    css = _read("assets/strategy.css")
    assert re.search(r"\.fm-bot \{[^}]*color: var\(--p-l\)", css), "робот фиолетовый"
    assert re.search(r"\.fm-side i \{[^}]*color: var\(--o-l\)", css), "монеты оранжевые"
    assert "@keyframes coinL" in css and "@keyframes coinR" in css, "монеты летят в обе стороны"
    assert "animation: coinL 2.4s ease-out infinite" in css, "фонтан бесконечный"
    assert "@keyframes markSpin" not in css and ".fm-ring" not in css, \
        "колец вокруг знака больше нет — осталась только иконка агента"
    for lang, html in _pages():
        mark = html[html.index('class="final-mark"'):html.index('class="final-1"')]
        assert "fa-robot" in mark, lang + ": иконка агента"
        assert mark.count("fa-coins") == 6, lang + ": по три монеты с каждой стороны"
        assert 'class="fm-side fm-l"' in mark and 'class="fm-side fm-r"' in mark, \
            lang + ": монеты слева и справа"
        assert len(set(re.findall(r"--d:([\d.]+)s", mark))) == 3, \
            lang + ": монеты вылетают по очереди, а не разом"
        assert html.index('class="final-mark"') < html.index('class="final-1"'), \
            lang + ": знак стоит НАД заголовком финала"


def test_final_lines_are_evenly_spaced():
    """Правка владельца: расстояние между тремя строками финала одинаковое.
    У абзаца свой нижний отступ, и вместе с margin-top третьей строки разрыв
    снизу был вдвое больше верхнего."""
    css = _read("assets/strategy.css")
    assert ".final-1 { margin-bottom: 0.85rem; }" in css
    assert re.search(r"\.final-2 \{ margin-bottom: 0;", css), "у средней строки своего отступа нет"
    assert re.search(r"\.final-3 \{[^}]*margin: 0.85rem 0", css), "сверху столько же, сколько снизу у первой"


def test_titles_paint_ai_purple_and_business_orange():
    """Правка владельца: «AI везде фиолетовый, automate — оранж, business —
    оранж, processes — фиолетовый, you — оранж»."""
    en, ru = _en(), _ru()
    assert '<span class="hl-o">you</span> start with <span class="hl-p">AI</span>?' in en, \
        "на финале you оранжевый, AI фиолетовый"
    assert 'Where should <span class="hl-o">you</span> start' in en, "в шапке первого экрана you оранжевый"
    assert 'can <span class="hl-o">automate</span>' in en, "automate оранжевый"
    assert 'as <span class="hl-p">processes</span>' in en, "processes фиолетовый"
    for html in (en, ru):
        assert 'should work with <span class="hl-p">AI</span>' in html or \
               'работать с <span class="hl-p">ИИ</span>' in html, "AI в заголовке фиолетовый"
    assert ">See how your business" not in en, "из заголовка пятого шага убрано See"
    assert ">Start AI transformation <" in en, "надпись кнопки финала"
    assert "Start AI transformation for free" not in en, \
        "правка владельца: на кнопке финала «бесплатно» больше нет"
    assert ">Начать ИИ-трансформацию <" in ru, "по-русски тоже без «бесплатно»"


def test_use_cases_headline_breaks_before_actually_works():
    """Правка владельца: «your business actually works» — перенос, works фиолетовым."""
    assert 'class="l">actually <span class="hl-p">works</span></span>' in _en(), \
        "перенос перед «actually works» и works фиолетовым"
    assert "h2 .l { display: block; }" in _read("assets/strategy.css"), \
        "спан .l в заголовке действительно переносит строку"


def test_pricing_grid_stays_centred_in_dense_mode():
    """Жалоба владельца «какого хуя всё не по середине»: короткая запись
    margin: 1rem 0 0.8rem в плотном режиме обнуляла боковое auto."""
    css = _read("assets/strategy.css")
    dense = css[css.index("Плотнее на невысоких окнах"):]
    dense = dense[:dense.index("@media (prefers-reduced-motion")]
    for sel in (".nums", ".biz-grid", ".plans"):
        m = re.search(re.escape(sel) + r" \{ (?:gap: [^;]+; )?margin: [^;]+;", dense)
        assert m and " auto " in m.group(0), sel + ": боковое auto в плотном режиме сохранено"


# ── мобильная вёрстка: вторая, самостоятельная ────────────────────────────

def _mobile_block():
    """Последний блок @media (max-width:1023px) — мобильная вёрстка целиком."""
    css = _read("assets/strategy.css")
    i = css.rindex("@media (max-width:1023px)")
    return css[i:]


def test_mobile_layout_is_a_second_layout_not_a_squeeze():
    """Правило владельца: вёрстки ровно две — веб и мобилка, и адаптивен
    только РАЗМЕР, а не формат. Поэтому подгонку кегля скриптом на телефоне
    выключаем: она зажимала заголовки и подписи до 8–10px."""
    js = _read("assets/strategy.js")
    assert "if (!mqDesk.matches)" in js, "на телефоне fitHeadings выходит сразу"
    mob = _mobile_block()
    for sel, size in (("p {", "14px"), (".lead {", "15.5px"), (".biz h3 {", "15px")):
        assert sel in mob, "мобильный размер задан явно: " + sel
    assert "font-size: 14px" in mob and "font-size: 15.5px" in mob


def test_mobile_hero_headline_breaks_into_four_lines():
    """Правка владельца: «Where should / you start / with AI / in your
    business?» — и по-русски так же."""
    for lang, html in _pages():
        h1 = html[html.index("<h1"):html.index("</h1>")]
        assert h1.count('class="lm"') == 4, lang + ": четыре смысловых куска заголовка"
    mob = _mobile_block()
    assert "h1 .lm { display: block; }" in mob, "на телефоне каждый кусок — своя строка"


def test_mobile_chain_is_one_flow_without_dangling_arrows():
    """Правка владельца «видишь и стрелки, и мелкота»: ряды, посчитанные под
    веб, на 390px ломались переносом и в конце строки повисала стрелка,
    указывающая в пустоту. На телефоне связи убраны, а ряды схлопнуты в один
    поток с переносом по ширине экрана."""
    mob = _mobile_block()
    assert ".parrow, .farrow, .pwrap, .fwrap { display: none; }" in mob
    assert ".pchain .prow, .fflow .frow { display: contents; }" in mob
    assert ".opgroup .oprow { display: contents; }" in mob, \
        "на сцене возможностей поток свой у каждой группы"


def test_mobile_maturity_scene_shows_all_seven_bars():
    """Паутина занимает ВЕСЬ остаток панели и потому никогда её не распирает:
    при квадратной svg во всю ширину колонки половина графиков уезжала за
    нижний край панели и просто не показывалась."""
    css = _read("assets/strategy.css")
    assert ".stage-card > .ui > .ui-body { flex: 1; min-height: 0;" in css, \
        "без min-height:0 тело панели растёт под содержимое и графики срезает рамка"
    mob = _mobile_block()
    assert ".maturity { flex: 1; min-height: 0; grid-template-rows: minmax(60px, 1fr) auto;" in mob
    assert ".radar { width: 100%; height: 100%; min-height: 0; }" in mob


def test_mobile_footer_stands_just_above_the_dots():
    """Правка владельца: подвал «должен быть ещё ниже, чуть перед точками»."""
    mob = _mobile_block()
    assert ".final footer { margin-top: auto;" in mob, "подвал прижат к низу экрана"
    assert "padding-left: calc(clamp(100px, 28vw, 128px)" in mob, \
        "колонка подвала смещена правее круглого ролика"
    assert ".legal { font-size: 12px;" in mob and "flex-wrap: wrap" in mob, \
        "ссылки подвала переносятся целыми словами, а не по буквам"


def test_mobile_header_button_keeps_its_own_size():
    """Кнопка шапки не берёт мобильный размер обычных кнопок: с ним «Начать
    бесплатно» распирало шапку и переключатель языка наезжал на логотип."""
    mob = _mobile_block()
    assert ".btn-primary:not(.cta-head), .btn-ghost {" in mob


def test_quote_scene_carries_the_same_six_blocks_as_the_next_one():
    """Правка владельца «тут можно ещё три блока, как на след. слайде»:
    на экране диктовки те же шесть блоков, что и на карте процессов."""
    for lang, html in _pages():
        quote = html[html.index('data-step="2"'):html.index('data-step="3"')]
        proc = html[html.index('data-step="3"'):html.index('data-step="4"')]
        assert quote.count('class="node ') == 6, lang + ": шесть блоков на экране диктовки"
        assert proc.count('class="pnode ') == 6, lang + ": столько же на карте процессов"


def test_solution_cards_have_no_numbers_and_are_centred():
    """Правка владельца: «чтобы внутри карточек чисел не было, а только по
    середине всё внутри выровнено»."""
    css = _read("assets/strategy.css")
    assert ".out-n" not in css, "номера карточек убраны и из стилей"
    assert ".out { text-align: center; }" in css
    assert ".out-ic {" in css, "вместо номера — иконка над заголовком"
    for lang, html in _pages():
        rail = html[html.index('class="rail"'):html.index("</section>", html.index('class="rail"'))]
        assert 'class="out-n"' not in rail, lang + ": в карточках решения чисел нет"
        assert rail.count('class="out-ic"') == 8, lang + ": у каждой карточки своя иконка"


def test_step_subtitles_are_one_line_and_press_to_the_panel():
    """Правка владельца: «тайтл и подтайтл ещё ближе к интерфейсу»."""
    css = _read("assets/strategy.css")
    assert "gap: clamp(0.5rem, 1.1vh, 0.85rem); align-content: start; }" in css, \
        "шапка шага стоит вплотную к панели"


# ── адрес лендинга и вход с главной ───────────────────────────────────────

def _site():
    return _read("index.html")


def test_landing_lives_at_ai_strategy():
    """Правка владельца: лендинг — раздел сайта andre.technology/ai-strategy."""
    import os
    for rel in ("ai-strategy/index.html", "ai-strategy/ru/index.html"):
        assert os.path.exists(os.path.join(_ROOT, rel)), "нет " + rel
    assert '<link rel="canonical" href="https://andre.technology/ai-strategy/">' in _en()
    assert '<link rel="canonical" href="https://andre.technology/ai-strategy/ru/">' in _ru()
    for lang, html in _pages():
        assert '<link rel="alternate" hreflang="en" href="https://andre.technology/ai-strategy/">' in html, lang
        assert '<link rel="alternate" hreflang="ru" href="https://andre.technology/ai-strategy/ru/">' in html, lang
        assert '<link rel="alternate" hreflang="x-default" href="https://andre.technology/ai-strategy/">' in html, lang
        assert "andre.technology/strategy/" not in html, lang + ": старого адреса на странице не осталось"
    assert '<meta property="og:url" content="https://andre.technology/ai-strategy/">' in _en()
    assert '<meta property="og:url" content="https://andre.technology/ai-strategy/ru/">' in _ru()


def test_old_address_redirects_to_the_new_one():
    """Адрес /strategy/ успел постоять живым, поэтому со старого пути ведёт
    страница-переезд: Pages не отдаёт 301, значит canonical + переход скриптом
    и meta refresh как запасной вариант. noindex рядом с canonical не ставим —
    запрет на индексацию может уехать на новый адрес вместе со склейкой."""
    for rel, to, lang in (("strategy/index.html", "/ai-strategy/", "en"),
                          ("strategy/ru/index.html", "/ai-strategy/ru/", "ru")):
        html = _read(rel)
        assert "noindex" not in html, \
            rel + ": noindex рядом с canonical может утащить за собой новый адрес"
        assert '<link rel="canonical" href="https://andre.technology%s">' % to in html, rel
        assert 'content="0; url=%s"' % to in html, rel + ": meta refresh для выключенных скриптов"
        assert "location.replace('%s' + location.search + location.hash)" % to in html, \
            rel + ": переход скриптом сохраняет query и хеш"
        assert '<a href="%s">' % to in html, rel + ": ссылка работает и без скриптов, и без refresh"
        assert '<html lang="%s">' % lang in html, rel + ": язык заглушки совпадает с языком нового адреса"
        assert "tools/build_strategy.py" in html, rel + ": заглушка тоже собирается, а не пишется руками"
    # русского посетителя со старого адреса не встречает английская надпись
    assert "Страница переехала" in _read("strategy/ru/index.html")
    assert "This page has moved" in _read("strategy/index.html")


def test_main_site_opens_the_landing_in_the_right_language():
    """Под кнопкой раздела «AI Strategy» на главной — ссылка «Where to start
    with AI» на лендинг. Ссылка языковая, как вход в курс и «About me»:
    главная переставляет href из data-href-en / data-href-ru."""
    site = _site()
    assert "AI Transformation Cases" not in site, "старой подписи на главной нет"
    # порядок атрибутов в теге значения не имеет — берём тег целиком и
    # разбираем его по одному атрибуту, иначе тест ломает любая перестановка
    m = re.search(r'<a\s[^>]*class="sec-link"[^>]*>([^<]+)</a>', site, re.S)
    while m and 'data-i18n="strategy.link"' not in m.group(0):
        m = re.search(r'<a\s[^>]*class="sec-link"[^>]*>([^<]+)</a>', site[m.end():], re.S)
    assert m, "ссылка раздела AI Strategy не найдена"
    assert m.group(1).strip() == "Where to start with AI", m.group(1)
    el = m.group(0)
    for attr, value in (("href", "https://andre.technology/ai-strategy/"),
                        ("data-href-en", "https://andre.technology/ai-strategy/"),
                        ("data-href-ru", "https://andre.technology/ai-strategy/ru/")):
        got = re.search(r'\b%s="([^"]*)"' % attr, el)
        assert got and got.group(1) == value, "%s: ожидали %s, получили %s" % (attr, value, got and got.group(1))
    assert "querySelectorAll('[data-href-ru]')" in site, \
        "главная должна переставлять такие ссылки вместе с языком"
    ru_dict = re.search(r"'strategy\.link':\s*'([^']*)'", site)
    assert ru_dict and ru_dict.group(1) == "С чего начать внедрять ИИ", \
        "русская подпись ссылки: " + str(ru_dict and ru_dict.group(1))
    # кнопка раздела по-прежнему ведёт в продукт, а не на лендинг
    assert 'class="btn-white" href="https://strategy.andre.technology/"' in site, \
        "кнопка «Get Your AI Strategy» ведёт в кабинет продукта"


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
            except Exception as e:
                fails += 1
                print("ERR  " + name + ": " + type(e).__name__ + ": " + str(e))
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not fails else "ПРОВАЛЕНО: %d" % fails)
    sys.exit(1 if fails else 0)
